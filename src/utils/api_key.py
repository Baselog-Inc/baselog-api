import secrets
import string
import re
import hashlib
from typing import Optional

def generate_api_key() -> str:
    """Generate a secure unique API key."""
    prefix = "sk_live_"
    random_part = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
    return f"{prefix}{random_part}"

def hash_key(key: str) -> str:
    """Hash API key for secure storage."""
    import hashlib
    return hashlib.sha256(key.encode('utf-8')).hexdigest()

def validate_key_format(key: str) -> bool:
    """Validate API key format."""
    pattern = r'^sk_live_[a-zA-Z0-9]{32}$'
    return bool(re.match(pattern, key))

def verify_key_hash(key: str, stored_hash: str) -> bool:
    """Verify API key hash."""
    return hashlib.sha256(key.encode('utf-8')).hexdigest() == stored_hash

def is_api_key_valid(key: str) -> bool:
    """Basic key validation."""
    if not key or not isinstance(key, str):
        return False

    if len(key) != 39:  # sk_live_ + 32 chars
        return False

    return validate_key_format(key)