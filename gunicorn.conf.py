import multiprocessing
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

bind = os.getenv("GUNICORN_BIND", "127.0.0.1:5555")
workers = int(
    os.getenv("GUNICORN_WORKERS", str(min(8, multiprocessing.cpu_count() * 2 + 1)))
)
threads = int(os.getenv("GUNICORN_THREADS", "2"))
timeout = int(os.getenv("GUNICORN_TIMEOUT", "60"))
graceful_timeout = int(os.getenv("GUNICORN_GRACEFUL_TIMEOUT", "30"))
keepalive = int(os.getenv("GUNICORN_KEEPALIVE", "5"))

accesslog = os.getenv("GUNICORN_ACCESSLOG", str(LOG_DIR / "gunicorn_access.log"))
errorlog = os.getenv("GUNICORN_ERRORLOG", str(LOG_DIR / "gunicorn_error.log"))
loglevel = os.getenv("GUNICORN_LOGLEVEL", "info")
capture_output = True

chdir = str(BASE_DIR)
wsgi_app = "hospital_study.wsgi:application"
