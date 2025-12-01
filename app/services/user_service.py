# user_service.py
import bcrypt
from data.users import create_user, get_user_by_username

def hash_password(plain_text_password):
    return bcrypt.hashpw(plain_text_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(plain_text_password, hashed_password):
    # hashed_password stored as text; convert to bytes for bcrypt
    return bcrypt.checkpw(plain_text_password.encode("utf-8"),
                          hashed_password.encode("utf-8") if isinstance(hashed_password, str) else hashed_password)

def register_user_db(username, password, role="user"):
    """
    Registers a new user in the DB. Returns (True, user_id) on success, (False, message) on failure.
    """
    # check exists
    existing = get_user_by_username(username)
    if existing:
        return False, f"Username '{username}' already exists."

    hashed = hash_password(password)
    user_id = create_user(username, hashed, role)
    return True, user_id

def authenticate_user_db(username, password):
    """
    Authenticate user against DB. Returns (True, user_row) if credentials good; else (False, msg).
    """
    user = get_user_by_username(username)
    if not user:
        return False, "Username not found"
    if verify_password(password, user["password_hash"]):
        return True, user
    return False, "Invalid password"