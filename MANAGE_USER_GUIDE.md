## User Management Commands

Use the project virtual environment Python to run all user management commands.

### Base Python Command

.venv/bin/python

## Create Users

### Create a normal user

.venv/bin/python user_init.py create-user --username analyst --password analyst123

### Create an admin user

.venv/bin/python user_init.py create-admin --username admin --password admin123

### Create user with interactive password prompt

.venv/bin/python user_init.py create-user --username analyst

## Reset Password

### Reset password with command argument

.venv/bin/python user_init.py reset-password --username analyst --password NewStrongPassword

### Reset password with interactive prompt

.venv/bin/python user_init.py reset-password --username analyst

## Notes

- Passwords are stored as secure hashes in app/instance/users.json and cannot be read back in plain text.
- If username already exists, create-user and create-admin return an error.
- reset-password fails if the username does not exist.
