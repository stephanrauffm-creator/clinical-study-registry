# Clinical Study Registry User Guide

This guide is for onboarding new study staff and gives hands-on examples for daily use.

## 1. What This App Is For

Clinical Study Registry is an internal app to:

- Capture pseudonymized study entries (`PIZ` only)
- Review and edit existing entries
- Export filtered data to Excel (`.xlsx`)
- Share instruction PDFs
- Keep an audit log of key actions

Do not enter patient-identifying information.

## 2. Access and Roles

### Standard User

Can:

- View entries
- Create entries
- Edit own entries
- Export filtered data
- View/download instruction PDFs

Cannot:

- Upload instruction PDFs
- Access Django admin

### Admin/Staff User

Can do everything above, plus:

- Upload instruction PDFs
- Access `/admin/`
- Edit entries beyond own records (based on app permissions)

## 3. Start the App (Windows)

Run from any terminal:

```powershell
C:\Users\Max\code\sr\sr_venv\Scripts\python.exe C:\Users\Max\code\sr\manage.py runserver 127.0.0.1:5555 --noreload
```

Open:

`http://127.0.0.1:5555/login/`

## 4. Demo Accounts (Training Only)

- Basic user: `demo_user` / `DemoUser2026!`
- Admin user: `demo_admin` / `DemoAdmin2026!`

Change/remove these credentials before using any shared environment.

## 5. Main Screens

### Login

![Login](screenshots/login.png)

### Entries

![Entries](screenshots/entries.png)

### Instructions

![Instructions](screenshots/instructions.png)

## 6. Core Workflow: End-to-End Example

Use this scenario to train new staff.

### Step A: Login

1. Open `/login/`
2. Enter username and password
3. Click `Sign In`

Expected result:

- You are redirected to `Browse Entries`

### Step B: Create a New Entry

1. Click `Create Entry`
2. Fill fields:
   - `PIZ`: `PIZ-TRAIN-1001`
   - `Examination Date`: today or a past date
   - `Liver Ambulance Link`: optional checkbox
   - `FibroScan LSM (kPa)`: e.g. `9.8`
   - `FibroScan CAP (dBm)`: e.g. `236.0`
3. Click `Create Entry`

Expected result:

- Success message shown
- Entry appears in the entries list

### Step C: Filter and Review

1. In `Browse Entries`, set:
   - `PIZ`: `PIZ-TRAIN-1001`
2. Click `Filter`

Expected result:

- Only matching entry/entries shown

### Step D: Edit an Entry

1. Click `Edit` on a visible row
2. Change one numeric value (example: LSM `9.8` -> `10.2`)
3. Click `Save Changes`

Expected result:

- Success message shown
- Updated value is visible in list
- Audit record created

### Step E: Export Filtered Data

1. Keep filter active
2. Click `Export XLSX`

Expected result:

- Browser downloads a `.xlsx` file
- Export action logged in audit

### Step F: Instructions (Admin Example)

1. Log in as `demo_admin`
2. Open `Instruction PDFs`
3. Click `Upload PDF`
4. Upload a PDF with a clear title (example: `Operator SOP v1`)

Expected result:

- File appears in list with uploader and timestamp

## 7. Validation Rules (What Users Must Know)

When entering data:

- `Examination Date` cannot be more than 30 days in the future
- `FibroScan LSM (kPa)` must be between `0` and `200`
- `FibroScan CAP (dBm)` must be between `0` and `500`
- `PIZ + Examination Date` must be unique

If a save fails, check these first.

## 8. Data Handling Summary

- Source of truth: database (SQLite/PostgreSQL depending on deployment)
- Export format: Excel (`.xlsx`)
- No CSV workflow is required in current scope
- Backups: automatic daily SQLite backups to `backups\YYYY-MM-DD\db.sqlite3`

## 9. Common Errors and Fixes

### "Method Not Allowed" on logout

Use the in-app `Logout` button only. Direct URL GET to `/logout` is not valid.

### Cannot see Admin link

You are logged in as a non-staff account. Use `demo_admin` (or assigned staff account).

### Export blocked by lock

Another export is in progress. Wait briefly and retry.

### Login works but session appears lost

Check browser cookie settings or private/incognito mode behavior.

## 10. Training Checklist for New Staff

Use this as a short practical assessment:

1. Log in and out successfully.
2. Create one valid entry.
3. Trigger one validation error intentionally (future date or invalid range).
4. Correct the error and save.
5. Filter by PIZ and date range.
6. Export filtered list to `.xlsx`.
7. (Admin) Upload one instruction PDF.
8. Explain what data is allowed (pseudonymized only).

## 11. Quick Reference

- App URL: `http://127.0.0.1:5555/login/`
- Entries: `/entries`
- New entry: `/entries/new`
- Instructions: `/instructions`
- Admin: `/admin/` (staff only)
