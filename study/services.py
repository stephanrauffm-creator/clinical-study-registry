import io
import logging
import os
import tempfile
import time
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

from django.conf import settings
from openpyxl import Workbook

from .models import AuditEvent

audit_logger = logging.getLogger("study.audit")
EXPORT_LOCK_STALE_SECONDS = 15 * 60


class ExportLockError(Exception):
    pass


def _cleanup_stale_export_lock(lock_file: Path):
    if not lock_file.exists():
        return

    stale_seconds = int(getattr(settings, "EXPORT_LOCK_STALE_SECONDS", EXPORT_LOCK_STALE_SECONDS))
    if stale_seconds < 1:
        return

    try:
        age_seconds = time.time() - lock_file.stat().st_mtime
    except OSError:
        return

    if age_seconds > stale_seconds:
        try:
            lock_file.unlink()
        except OSError:
            pass


@contextmanager
def advisory_lock(lock_file: Path):
    lock_fd = None
    _cleanup_stale_export_lock(lock_file)
    try:
        lock_fd = os.open(str(lock_file), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(lock_fd, f"pid={os.getpid()} time={datetime.utcnow()}".encode("ascii"))
        yield
    except FileExistsError as exc:
        raise ExportLockError(
            "Another export is currently running. Please try again shortly."
        ) from exc
    finally:
        if lock_fd is not None:
            os.close(lock_fd)
            try:
                lock_file.unlink()
            except FileNotFoundError:
                pass


def build_entries_workbook(entries):
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = "Study Entries"
    worksheet.append(
        [
            "PIZ",
            "Examination Date",
            "Liver Ambulance Link",
            "Fibroscan LSM (kPa)",
            "Fibroscan CAP (dBm)",
            "Created At",
            "Updated At",
            "Created By",
            "Updated By",
        ]
    )

    for entry in entries:
        worksheet.append(
            [
                entry.piz,
                entry.examination_date.isoformat(),
                "yes" if entry.liver_ambulance_link else "no",
                float(entry.fibroscan_lsm_kpa),
                float(entry.fibroscan_cap_dbm),
                entry.created_at.isoformat(),
                entry.updated_at.isoformat(),
                entry.created_by.username if entry.created_by else "",
                entry.updated_by.username if entry.updated_by else "",
            ]
        )

    return workbook


def write_workbook_atomic(workbook, destination_path):
    destination = Path(destination_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    lock_file = destination.with_suffix(destination.suffix + ".lock")

    with advisory_lock(lock_file):
        fd, temp_file = tempfile.mkstemp(
            prefix=f"{destination.name}.",
            suffix=".tmp",
            dir=str(destination.parent),
        )
        os.close(fd)
        try:
            workbook.save(temp_file)
            os.replace(temp_file, destination)
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)


def workbook_to_bytes(workbook):
    content = io.BytesIO()
    workbook.save(content)
    content.seek(0)
    return content.getvalue()


def log_audit_event(action, actor=None, entry=None, instruction=None, details=""):
    AuditEvent.objects.create(
        action=action,
        actor=actor,
        entry=entry,
        instruction=instruction,
        details=details,
    )
    username = actor.username if actor else "system"
    audit_logger.info(
        "action=%s actor=%s entry_id=%s instruction_id=%s details=%s",
        action,
        username,
        entry.id if entry else "",
        instruction.id if instruction else "",
        details,
    )


def export_to_network(entries, actor=None):
    workbook = build_entries_workbook(entries)
    write_workbook_atomic(workbook, settings.DATA_XLSX_PATH)
    log_audit_event(
        action="export_excel",
        actor=actor,
        details=f"rows={len(entries)} path={settings.DATA_XLSX_PATH}",
    )
    return workbook
