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

## Windows-Schnellstart (Deutsch, ganz einfach erklärt)

Du hast nur Git installiert? Kein Problem. Folge genau diesen Schritten.

### Schritt 0: Python installieren (einmalig)

Warum? Dieses Projekt ist mit Python gebaut. Ohne Python kann es nicht starten.

1. Öffne im Browser: `https://www.python.org/downloads/windows/`
2. Lade die aktuelle Python-Version herunter.
3. Starte die Installationsdatei.
4. **Sehr wichtig:** Häkchen setzen bei **"Add python.exe to PATH"**.
5. Dann auf **Install Now** klicken.
6. Öffne danach **eine neue** PowerShell und tippe:

```powershell
python --version
```

Wenn etwas wie `Python 3.12.x` angezeigt wird, ist alles richtig installiert.

---

### Schritt 1: Projekt herunterladen (klonen)

"Klonen" heißt einfach: Du kopierst das Projekt von GitHub auf deinen PC.

```powershell
cd $HOME
mkdir code -ErrorAction SilentlyContinue
cd code
git clone <DEIN-REPO-URL>
cd clinical-study-registry
```

---

### Schritt 2: Arbeitsumgebung erstellen

Warum? So bleiben Projekt-Pakete sauber getrennt von anderen Python-Projekten.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Wenn links `(.venv)` steht, ist alles korrekt aktiv.

---

### Schritt 3: Benötigte Pakete installieren

"Pakete" sind Zusatzbausteine, die das Projekt braucht.

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

`-r requirements.txt` bedeutet: Installiere genau die Pakete aus dieser Liste.

**Wenn bei dir `No module named django` kommt:**

Das bedeutet fast immer: Django wurde noch nicht installiert **oder** die virtuelle Umgebung ist nicht aktiv.

Führe dann genau diese Befehle aus (im Projektordner):

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip show django
```

Wenn bei `pip show django` Daten angezeigt werden, ist Django korrekt installiert.
Danach erneut starten:

```powershell
python manage.py migrate
python manage.py runserver 127.0.0.1:5555
```

**Wenn bei dir dieser Fehler kommt:**
`ERROR: Could not install packages due to an OSError: Failed to parse: http://USER:PASS@proxy.host:port`

Das bedeutet: In deinen Proxy-Einstellungen steht noch ein Platzhalter (`USER`, `PASS`, `proxy.host`, `port`) statt echter Daten.

Schnelle Lösung (wenn du **keinen** Firmen-Proxy brauchst):

```powershell
setx HTTP_PROXY ""
setx HTTPS_PROXY ""
# PowerShell neu öffnen
```

Dann erneut:

```powershell
python -m pip install -r requirements.txt
```

Wenn du **einen Proxy brauchst**, nutze echte Werte, z. B.:

```powershell
$env:HTTP_PROXY="http://meinuser:meinpass@proxy.meinefirma.de:8080"
$env:HTTPS_PROXY="http://meinuser:meinpass@proxy.meinefirma.de:8080"
python -m pip install -r requirements.txt
```

Wichtig: Falls Benutzername/Passwort Sonderzeichen enthalten (z. B. `@` oder `:`), müssen sie URL-kodiert werden.

**Wenn stattdessen `Cannot connect to proxy` / `getaddrinfo failed` kommt:**

Dann ist die Proxy-Adresse selbst nicht erreichbar oder falsch geschrieben.

Prüfe zuerst, was aktuell gesetzt ist:

```powershell
$env:HTTP_PROXY
$env:HTTPS_PROXY
```

Wenn du zuhause bist oder keinen Firmen-Proxy brauchst, setze beides für die aktuelle Sitzung leer:

```powershell
$env:HTTP_PROXY=""
$env:HTTPS_PROXY=""
python -m pip install -r requirements.txt
```

Wenn du im Firmennetz bist, frage IT nach den **exakten** Proxy-Daten (Host + Port + ggf. Benutzername/Passwort) und setze sie dann neu.

Zusatz zu `WARNING: There was an error checking the latest version of pip.`:
Diese Warnung ist meist unkritisch und kommt oft wegen Proxy/Netzwerk. Du kannst sie vorerst ignorieren und dich auf die Proxy-Einstellungen konzentrieren.

Wenn nach Korrektur des Proxys weiter `No matching distribution found` kommt, liegt es fast immer weiterhin am Netzwerk/Proxy und nicht an Django selbst.

---

### Schritt 4: Lokale Konfigurationsdatei anlegen

Hier wird eine lokale Einstellungsdatei erstellt.

```powershell
Copy-Item instance\config.template.json instance\config.json
```

---

### Schritt 5: Datenbank vorbereiten (migrate)

"Migrieren" heißt hier ganz einfach: Die App erstellt/aktualisiert ihre Tabellen in der Datenbank automatisch.

```powershell
python manage.py migrate
```

---

### Schritt 6: Demo-Login-Benutzer anlegen (einmalig)

```powershell
python manage.py create_demo_users
```

Dadurch werden diese lokalen Test-Logins erstellt oder zurückgesetzt:

- `demo_user` / `DemoUser2026!`
- `demo_admin` / `DemoAdmin2026!`

---

### Schritt 7: Kurz testen, ob alles funktioniert

```powershell
python manage.py test
```

Wenn am Ende `OK` steht, ist das ein gutes Zeichen.

---

### Schritt 8: Projekt starten

```powershell
python manage.py runserver 127.0.0.1:5555
```

Dann im Browser öffnen: `http://127.0.0.1:5555/login/`

---

### Schritt 9: Einloggen (nur lokal)

Nutze jetzt diese Demo-Zugänge:

- `demo_user` / `DemoUser2026!`
- `demo_admin` / `DemoAdmin2026!`

**Wenn Login nicht funktioniert:**

1. Achte auf die richtige URL: `http://127.0.0.1:5555/login/`
2. Prüfe, ob die Tastatur auf richtiges Layout gestellt ist (Y/Z, Sonderzeichen, Groß-/Kleinschreibung).
3. Falls unklar ist, ob die Demo-User bei dir existieren, lege einen neuen Admin-User an:

```powershell
python manage.py createsuperuser
```

Dann Benutzername + Passwort eingeben und mit diesem neuen Konto einloggen.

4. Wenn Passwort vergessen wurde, setze es neu:

```powershell
python manage.py changepassword <BENUTZERNAME>
```

5. Wenn weiterhin "Please enter a correct username and password" kommt, prüfe, ob der User wirklich existiert:

```powershell
python manage.py shell -c "from django.contrib.auth import get_user_model; U=get_user_model(); print(list(U.objects.values_list('username', flat=True)))"
```

---

### Schritt 10: Server stoppen

Im PowerShell-Fenster mit dem laufenden Server drückst du: `STRG + C`

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
