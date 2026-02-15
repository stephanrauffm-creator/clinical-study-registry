import logging
import os
import re
import sqlite3
import shutil
import time
from contextlib import contextmanager
from datetime import date
from pathlib import Path

from django.conf import settings

DATE_FOLDER_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
LOCK_STALE_SECONDS = 15 * 60
logger = logging.getLogger("study.audit")


def _is_sqlite_database() -> bool:
    default_db = settings.DATABASES.get("default", {})
    return default_db.get("ENGINE") == "django.db.backends.sqlite3"


def _database_file() -> Path | None:
    default_db = settings.DATABASES.get("default", {})
    db_name = str(default_db.get("NAME", ""))
    if not db_name or db_name == ":memory:" or db_name.startswith("file:"):
        return None
    return Path(db_name)


def _target_backup_file(day: date) -> Path:
    return Path(settings.BACKUP_DIR) / day.isoformat() / "db.sqlite3"


def _cleanup_old_backups(root: Path, keep_days: int) -> None:
    candidates = [
        item
        for item in root.iterdir()
        if item.is_dir() and DATE_FOLDER_PATTERN.match(item.name)
    ]
    ordered = sorted(candidates, key=lambda item: item.name, reverse=True)
    to_remove = ordered[keep_days:]
    for item in to_remove:
        shutil.rmtree(item, ignore_errors=True)


@contextmanager
def _backup_lock(lock_file: Path):
    lock_file.parent.mkdir(parents=True, exist_ok=True)
    file_descriptor = None

    if lock_file.exists():
        age = time.time() - lock_file.stat().st_mtime
        if age > LOCK_STALE_SECONDS:
            try:
                lock_file.unlink()
            except OSError:
                pass

    try:
        file_descriptor = os.open(str(lock_file), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(file_descriptor, str(os.getpid()).encode("ascii"))
        yield True
    except FileExistsError:
        yield False
    finally:
        if file_descriptor is not None:
            os.close(file_descriptor)
            try:
                lock_file.unlink()
            except OSError:
                pass


def ensure_daily_backup(day: date | None = None) -> str:
    if not settings.BACKUP_ENABLED:
        return "disabled"
    if not _is_sqlite_database():
        return "non_sqlite"

    database_file = _database_file()
    if database_file is None or not database_file.exists():
        return "missing_db"

    today = day or date.today()
    target_file = _target_backup_file(today)
    if target_file.exists():
        return "exists"

    backup_root = Path(settings.BACKUP_DIR)
    lock_file = backup_root / ".daily_backup.lock"
    with _backup_lock(lock_file) as has_lock:
        if not has_lock:
            return "locked"

        target_file.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(str(database_file)) as source_connection:
            with sqlite3.connect(str(target_file)) as target_connection:
                source_connection.backup(target_connection)
        _cleanup_old_backups(backup_root, settings.BACKUP_KEEP_DAYS)
        logger.info(
            "daily_db_backup status=created path=%s keep_days=%s",
            target_file,
            settings.BACKUP_KEEP_DAYS,
        )
        return "created"
