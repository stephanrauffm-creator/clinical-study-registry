import os
import shutil
import time
import uuid
from pathlib import Path

from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase, override_settings
from openpyxl import Workbook

from .models import StudyEntry
from .services import ExportLockError, write_workbook_atomic


class StudyAppTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="testpass123")

    def test_create_entry(self):
        self.client.login(username="alice", password="testpass123")
        response = self.client.post(
            "/entries/new",
            data={
                "piz": "PIZ-001",
                "examination_date": "2026-01-10",
                "liver_ambulance_link": "on",
                "fibroscan_lsm_kpa": "12.3",
                "fibroscan_cap_dbm": "245.0",
            },
        )
        self.assertEqual(response.status_code, 302)
        entry = StudyEntry.objects.get(piz="PIZ-001")
        self.assertEqual(entry.created_by, self.user)
        self.assertTrue(entry.liver_ambulance_link)

    def test_unique_constraint(self):
        StudyEntry.objects.create(
            piz="PIZ-002",
            examination_date="2026-01-11",
            liver_ambulance_link=False,
            fibroscan_lsm_kpa="10.0",
            fibroscan_cap_dbm="220.0",
            created_by=self.user,
            updated_by=self.user,
        )
        with self.assertRaises(IntegrityError):
            StudyEntry.objects.create(
                piz="PIZ-002",
                examination_date="2026-01-11",
                liver_ambulance_link=True,
                fibroscan_lsm_kpa="13.0",
                fibroscan_cap_dbm="240.0",
                created_by=self.user,
                updated_by=self.user,
            )

    def test_authenticated_access_required(self):
        for path in ["/entries", "/entries/new", "/export/excel", "/instructions"]:
            response = self.client.get(path)
            self.assertEqual(response.status_code, 302)
            self.assertIn("/login", response.url)

    def test_export_endpoint_returns_xlsx(self):
        StudyEntry.objects.create(
            piz="PIZ-003",
            examination_date="2026-01-12",
            liver_ambulance_link=False,
            fibroscan_lsm_kpa="8.5",
            fibroscan_cap_dbm="210.0",
            created_by=self.user,
            updated_by=self.user,
        )
        self.client.login(username="alice", password="testpass123")

        export_root = os.path.join(os.getcwd(), "test_artifacts", str(uuid.uuid4()))
        export_path = os.path.join(export_root, "network_share", "study.xlsx")
        try:
            with override_settings(DATA_XLSX_PATH=export_path):
                response = self.client.get("/export/excel")
        finally:
            shutil.rmtree(export_root, ignore_errors=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Content-Type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        self.assertTrue(response.content.startswith(b"PK"))

    def test_logout_post_works_and_protects_entries(self):
        self.client.login(username="alice", password="testpass123")
        response = self.client.post("/logout")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.url)

        protected = self.client.get("/entries")
        self.assertEqual(protected.status_code, 302)
        self.assertIn("/login", protected.url)

    def test_write_workbook_atomic_removes_stale_lock(self):
        export_root = os.path.join(os.getcwd(), "test_artifacts", str(uuid.uuid4()))
        destination = Path(export_root) / "stale_lock.xlsx"
        lock_file = destination.with_suffix(destination.suffix + ".lock")
        workbook = Workbook()
        workbook.active.append(["header"])
        created = False
        lock_removed = False
        try:
            lock_file.parent.mkdir(parents=True, exist_ok=True)
            lock_file.write_text("stale")
            old_mtime = time.time() - 3600
            os.utime(lock_file, (old_mtime, old_mtime))

            with override_settings(EXPORT_LOCK_STALE_SECONDS=60):
                write_workbook_atomic(workbook, destination)
            created = destination.exists()
            lock_removed = not lock_file.exists()
        finally:
            shutil.rmtree(export_root, ignore_errors=True)

        self.assertTrue(created)
        self.assertTrue(lock_removed)

    def test_write_workbook_atomic_blocks_active_lock(self):
        export_root = os.path.join(os.getcwd(), "test_artifacts", str(uuid.uuid4()))
        destination = Path(export_root) / "active_lock.xlsx"
        lock_file = destination.with_suffix(destination.suffix + ".lock")
        workbook = Workbook()
        workbook.active.append(["header"])
        blocked = False
        created = False
        try:
            lock_file.parent.mkdir(parents=True, exist_ok=True)
            lock_file.write_text("active")
            with override_settings(EXPORT_LOCK_STALE_SECONDS=3600):
                try:
                    write_workbook_atomic(workbook, destination)
                except ExportLockError:
                    blocked = True
            created = destination.exists()
        finally:
            shutil.rmtree(export_root, ignore_errors=True)

        self.assertTrue(blocked)
        self.assertFalse(created)
