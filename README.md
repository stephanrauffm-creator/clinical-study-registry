# Clinical Study Registry

Django web app for authenticated clinical research teams to:

- Enter and edit pseudonymized study records (PIZ only).
- Export filtered entries to Excel with atomic write and lock protection.
- Upload/download instruction PDFs.
- Keep an audit trail for create, update, export, upload, and download actions.

## Features

- Auth-protected pages: `/login`, `/entries`, `/entries/new`, `/entries/<id>/edit`, `/export/excel`, `/instructions`, `/instructions/upload`.
- `StudyEntry` uniqueness on `(piz, examination_date)`.
- Validation:
  - Exam date cannot be more than 30 days in the future.
  - `fibroscan_lsm_kpa` in `0..200`.
  - `fibroscan_cap_dbm` in `0..500`.
- Audit in DB (`AuditEvent`) and file log (`LOG_DIR/audit.log`).
- Safe PDF filenames in `MEDIA_ROOT/instructions/`.

## Local Setup (venv)

Run all commands in this section from the project directory:

```powershell
cd C:\Users\Max\code\sr
```

1. Create and activate a virtual environment:

```powershell
python -m venv sr_venv
.\sr_venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

3. Create local config:

```powershell
Copy-Item instance\config.template.json instance\config.json
```

4. Apply migrations and run:

```powershell
python manage.py migrate
python manage.py runserver 127.0.0.1:5555
```

Open `http://127.0.0.1:5555/login/`.

Windows one-liner without activating the venv:

```powershell
C:\Users\Max\code\sr\sr_venv\Scripts\python.exe C:\Users\Max\code\sr\manage.py runserver 127.0.0.1:5555
```

## Local Setup (Conda)

This repository includes `environment.yml` for Conda users.

```powershell
conda env create -f environment.yml
conda activate clinical-study-registry
python manage.py migrate
python manage.py runserver 127.0.0.1:5555
```

`requirements.txt` remains the source for Python package pins and works for both venv and Conda+pip workflows.

## Demo Accounts (Local Only)

- Basic user: `demo_user` / `DemoUser2026!`
- Admin user: `demo_admin` / `DemoAdmin2026!`

Change or remove demo credentials before sharing any non-local environment.

## Screenshots

Login

![Login screen](docs/screenshots/login.png)

Entries workspace

![Entries screen](docs/screenshots/entries.png)

Instructions

![Instructions screen](docs/screenshots/instructions.png)

## Configuration

Settings resolve in this order:

1. `instance/config.json`
2. Environment variables
3. Safe development defaults

Important keys in `instance/config.json`:

- `SECRET_KEY`
- `DEBUG`
- `ALLOWED_HOSTS` (JSON list)
- `DATA_XLSX_PATH`
- `MEDIA_ROOT`
- `LOG_DIR`
- `DATABASE_URL` (optional; e.g. sqlite or postgres URL)

`DATABASE_URL` examples:

- SQLite: `sqlite:///db.sqlite3`
- PostgreSQL: `postgresql://user:password@localhost:5432/studydb`

## Database Backups (SQLite)

The app performs automatic daily SQLite backups internally (no OS scheduler required).
Backup runs on incoming requests and creates one backup set per day.

Auto-backup behavior:

- Copies `db.sqlite3` to `backups\YYYY-MM-DD\db.sqlite3`
- Keeps the newest `N` daily folders (default `14`)
- Removes older daily backup folders automatically

Config keys (optional) in `instance/config.json`:

- `BACKUP_ENABLED` (default `true`)
- `BACKUP_KEEP_DAYS` (default `14`)
- `BACKUP_DIR` (default `./backups`)

Manual backup (optional):

```powershell
pwsh -File .\scripts\backup_db.ps1 -KeepDays 14
```

## Deployment Notes (Linux)

One-line startup (from project root):

```bash
bash ./scripts/start_gunicorn.sh
```

The script loads `gunicorn.conf.py` and starts `hospital_study.wsgi:application`.

Windows note:

- Gunicorn is Linux/Unix-only in this setup.
- On Windows, use Django dev server:
  `.\sr_venv\Scripts\python.exe .\manage.py runserver 127.0.0.1:5555`

Gunicorn example:

```bash
python -m pip install -r requirements.txt
python manage.py migrate
gunicorn hospital_study.wsgi:application --bind 127.0.0.1:5555 --workers 3
```

Config file provided: `gunicorn.conf.py`

Example `systemd` service (`/etc/systemd/system/clinical-study-registry.service`):

```ini
[Unit]
Description=Clinical Study Registry Django App
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/clinical-study-registry
ExecStart=/usr/bin/env gunicorn hospital_study.wsgi:application --bind 127.0.0.1:5555 --workers 3
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
```

Run behind nginx (or another reverse proxy) in front of gunicorn.

## Tests and Checks

```powershell
python -m compileall .
python manage.py test
```
