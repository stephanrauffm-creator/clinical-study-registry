import json
import os
from pathlib import Path
from urllib.parse import unquote, urlparse

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

INSTANCE_CONFIG_PATH = BASE_DIR / "instance" / "config.json"


def _read_instance_config(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _to_bool(value, default=False):
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _to_list(value, default=None):
    if value is None:
        return default or []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [item.strip() for item in str(value).split(",") if item.strip()]


def _to_int(value, default=0, minimum=None):
    try:
        result = int(value)
    except (TypeError, ValueError):
        result = default
    if minimum is not None:
        return max(minimum, result)
    return result


def _to_path(value, default: Path) -> Path:
    raw_value = value if value is not None and value != "" else default
    path = Path(raw_value).expanduser()
    if not path.is_absolute():
        path = (BASE_DIR / path).resolve()
    return path


def _get_setting(config: dict, key: str, default=None):
    if key in config:
        return config[key]
    return os.environ.get(key, default)


def _database_config(database_url: str | None) -> dict:
    if not database_url:
        return {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }

    parsed = urlparse(database_url)
    scheme = parsed.scheme.lower()

    if scheme in {"sqlite", "sqlite3"}:
        db_path = unquote(parsed.path or "")
        if db_path in {"", "/:memory:"}:
            name = ":memory:"
        elif db_path.startswith("//"):
            name = db_path[1:]
        else:
            name = db_path
            if parsed.netloc:
                name = f"//{parsed.netloc}{db_path}"
            elif db_path.startswith("/"):
                name = db_path[1:]
            if not Path(name).is_absolute():
                name = str(BASE_DIR / name)
        return {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": name,
        }

    if scheme in {"postgres", "postgresql"}:
        return {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": unquote(parsed.path.lstrip("/")),
            "USER": unquote(parsed.username or ""),
            "PASSWORD": unquote(parsed.password or ""),
            "HOST": parsed.hostname or "",
            "PORT": str(parsed.port or ""),
        }

    return {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }


INSTANCE_CONFIG = _read_instance_config(INSTANCE_CONFIG_PATH)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = _get_setting(
    INSTANCE_CONFIG,
    "SECRET_KEY",
    "dev-only-change-me",
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = _to_bool(_get_setting(INSTANCE_CONFIG, "DEBUG", True), True)

ALLOWED_HOSTS = _to_list(_get_setting(INSTANCE_CONFIG, "ALLOWED_HOSTS", []), [])


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    "study",
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "study.middleware.DailyBackupMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'hospital_study.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'hospital_study.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    "default": _database_config(_get_setting(INSTANCE_CONFIG, "DATABASE_URL")),
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_ROOT = _to_path(_get_setting(INSTANCE_CONFIG, "MEDIA_ROOT"), BASE_DIR / "media")
MEDIA_URL = "/media/"

DATA_XLSX_PATH = str(
    _to_path(
        _get_setting(INSTANCE_CONFIG, "DATA_XLSX_PATH"),
        BASE_DIR / "exports" / "study_entries.xlsx",
    )
)

LOG_DIR = _to_path(_get_setting(INSTANCE_CONFIG, "LOG_DIR"), BASE_DIR / "logs")
BACKUP_ENABLED = _to_bool(_get_setting(INSTANCE_CONFIG, "BACKUP_ENABLED", True), True)
BACKUP_KEEP_DAYS = _to_int(_get_setting(INSTANCE_CONFIG, "BACKUP_KEEP_DAYS", 14), 14, minimum=1)
BACKUP_DIR = _to_path(_get_setting(INSTANCE_CONFIG, "BACKUP_DIR"), BASE_DIR / "backups")
EXPORT_LOCK_STALE_SECONDS = _to_int(
    _get_setting(INSTANCE_CONFIG, "EXPORT_LOCK_STALE_SECONDS", 900),
    900,
    minimum=1,
)

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/entries"
LOGOUT_REDIRECT_URL = "/login"

MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        }
    },
    "handlers": {
        "audit_file": {
            "class": "logging.FileHandler",
            "filename": str(LOG_DIR / "audit.log"),
            "formatter": "standard",
        }
    },
    "loggers": {
        "study.audit": {
            "handlers": ["audit_file"],
            "level": "INFO",
            "propagate": False,
        }
    },
}

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
