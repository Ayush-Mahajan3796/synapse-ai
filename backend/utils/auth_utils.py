import hashlib
import os
import secrets

def generate_salt() -> str:
    """Generate a random 16-character hexadecimal salt."""
    return secrets.token_hex(8)

def hash_password(password: str, salt: str) -> str:
    """Hash the password with the provided salt using SHA-256."""
    salted_pass = password + salt
    return hashlib.sha256(salted_pass.encode("utf-8")).hexdigest()

def verify_password(password: str, salt: str, password_hash: str) -> bool:
    """Verify a password by checking its hash against the stored hash."""
    return hash_password(password, salt) == password_hash
