import secrets
import hashlib
import string
from typing import Tuple

API_KEY_PREFIX = "sk_proj_"
API_KEY_LENGTH = 32
HASH_ALGORITHM = "sha256"

def generate_api_key() -> Tuple[str, str, str]:
    random_part = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(API_KEY_LENGTH))
    full_key = f"{API_KEY_PREFIX}{random_part}"
    key_hash = hash_api_key(full_key)
    masked_key = create_masked_key(full_key)
    return full_key, key_hash, masked_key

def hash_api_key(key: str) -> str:
    return hashlib.new(HASH_ALGORITHM, key.encode()).hexdigest()

def create_masked_key(full_key: str) -> str:
    if len(full_key) < len(API_KEY_PREFIX) + 8:
        return full_key
    prefix = full_key[:len(API_KEY_PREFIX)]
    first_part = full_key[len(API_KEY_PREFIX):len(API_KEY_PREFIX) + 4]
    last_part = full_key[-4:]
    masked_part = "*" * (len(full_key) - len(prefix) - 8)
    return f"{prefix}{first_part}{masked_part}{last_part}"

def verify_api_key(key: str, key_hash: str) -> bool:
    return hash_api_key(key) == key_hash

def is_api_key_valid(api_key_record) -> bool:
    return api_key_record.is_active