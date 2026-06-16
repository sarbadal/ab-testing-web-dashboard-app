import json
import os
from typing import Dict, Optional

from werkzeug.security import check_password_hash, generate_password_hash


INSTANCE_DIR = os.path.join(os.path.dirname(__file__), "instance")
USERS_FILE = os.path.join(INSTANCE_DIR, "users.json")


def ensure_user_store() -> None:
    """Ensure the instance user store exists."""
    os.makedirs(INSTANCE_DIR, exist_ok=True)
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump({"users": []}, f, indent=2)


def load_user_store() -> Dict[str, list]:
    """Load user store from instance directory."""
    ensure_user_store()
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    if "users" not in data or not isinstance(data["users"], list):
        data = {"users": []}
    return data


def save_user_store(store: Dict[str, list]) -> None:
    """Persist user store to disk."""
    ensure_user_store()
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(store, f, indent=2)


def get_user_by_username(username: str) -> Optional[Dict[str, object]]:
    """Get a user dictionary by username."""
    store = load_user_store()
    return next((u for u in store["users"] if u.get("username") == username), None)


def authenticate_user(username: str, password: str) -> Optional[Dict[str, object]]:
    """Authenticate a user by username and password."""
    user = get_user_by_username(username)
    if not user:
        return None

    password_hash = user.get("password_hash", "")
    if not password_hash or not check_password_hash(password_hash, password):
        return None

    if user.get("is_active", True) is False:
        return None

    return user


def create_user(username: str, password: str, is_admin: bool = False) -> Dict[str, object]:
    """Create a user and store a hashed password."""
    if not username:
        raise ValueError("Username is required")
    if not password:
        raise ValueError("Password is required")

    store = load_user_store()

    if any(u.get("username") == username for u in store["users"]):
        raise ValueError(f"User '{username}' already exists")

    user = {
        "username": username,
        "password_hash": generate_password_hash(password, method="pbkdf2:sha256"),
        "is_admin": bool(is_admin),
        "is_active": True,
    }
    store["users"].append(user)
    save_user_store(store)
    return user


def reset_user_password(username: str, new_password: str) -> Dict[str, object]:
    """Reset password for an existing user."""
    if not username:
        raise ValueError("Username is required")
    if not new_password:
        raise ValueError("New password is required")

    store = load_user_store()
    user = next((u for u in store["users"] if u.get("username") == username), None)
    if not user:
        raise ValueError(f"User '{username}' not found")

    user["password_hash"] = generate_password_hash(new_password, method="pbkdf2:sha256")
    save_user_store(store)
    return user
