import threading
from datetime import date

from .backup import ensure_daily_backup


class DailyBackupMiddleware:
    _state_lock = threading.Lock()
    _completed_for_day = None

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self._maybe_run_backup()
        return self.get_response(request)

    @classmethod
    def _maybe_run_backup(cls):
        today = date.today()
        if cls._completed_for_day == today:
            return

        with cls._state_lock:
            if cls._completed_for_day == today:
                return
            status = ensure_daily_backup(today)
            if status in {"created", "exists", "disabled", "non_sqlite"}:
                cls._completed_for_day = today
