## A/B Testing Dashboard (Flask)

A Flask-based dashboard for visualizing A/B test performance, statistical significance, and segment-level insights.

## Features

- Session-based login using username and password
- Role flag support for admin and normal users (`is_admin`)
- User store in `app/instance/users.json`
- Dashboard with conversion metrics, significance, and segment charts
- SQLite-backed data source for test data (`app/data.db`)
- Dynamic footer year in the UI

## Project Structure

- `main.py`: Application entry point
- `app/`: Flask app package
- `app/routes/`: Route modules
- `app/data.db`: SQLite database
- `app/instance/users.json`: User store (hashed passwords)
- `db_utils/`: Data access and statistical calculations
- `templates/`: HTML templates

## Requirements

- Python 3.9+
- Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the App

```bash
python main.py
```

Default local URL: `http://localhost:5000` (or configured via environment variables).

## Deploy To GCP Cloud Functions (With Static Bucket Upload)

Use the Python deployment helper to:

- upload `static/` assets (JS/CSS/images/fonts) to a GCS bucket
- set production `STATIC_BASE_URL` for templates
- deploy the function with production env vars

Install dependencies first:

```bash
pip install -r requirements.txt
```

Example:

```bash
python deployment.py \
	--project-id your-project-id \
	--function-name ab-testing-dashboard \
	--region us-central1 \
	--bucket your-static-assets-bucket \
	--allow-unauthenticated
```

What this command does:

- creates the bucket if it does not exist
- uploads static files to a versioned prefix (for cache-safe releases)
- writes `.env.prod` with resolved production variables
- runs `gcloud functions deploy ... --gen2 --set-env-vars ...`

To preview without deploying, add `--dry-run`.

## Environment Variables

Use `.env` for configuration. Common values:

- `FLASK_DEBUG`
- `FLASK_HOST`
- `FLASK_PORT`
- `URL_PREFIX`
- `ENV_TYPE`

Database path now defaults to:

- `app/data.db`

## Authentication

Login uses:

- `username`
- `password`

Passwords are stored as secure hashes and cannot be recovered in plain text.

## User Management Commands

Use your environment Python command. Examples below use `python`.

Create a normal user:

```bash
python user_init.py create-user --username analyst --password analyst123
```

Create an admin user:

```bash
python user_init.py create-admin --username admin --password admin123
```

Create user with interactive password prompt:

```bash
python user_init.py create-user --username analyst
```

Reset password with explicit value:

```bash
python user_init.py reset-password --username analyst --password NewStrongPassword
```

Reset password interactively:

```bash
python user_init.py reset-password --username analyst
```

## Notes

- `create-user` and `create-admin` fail if the username already exists.
- `reset-password` fails if the user is not found.
- User roles are available in session as `is_admin` after successful login.
