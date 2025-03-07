from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv
import base64

load_dotenv()

def get_encryption_key():
    key = os.getenv('ENCRYPTION_KEY')
    if not key:
        # Generate a new key if none exists
        key = Fernet.generate_key().decode()
    try:
        # Validate the key format
        Fernet(key.encode())
        return key
    except Exception:
        # If the key is invalid, generate a new one
        return Fernet.generate_key().decode()

ENCRYPTION_KEY = get_encryption_key()
fernet = Fernet(ENCRYPTION_KEY.encode())

def encrypt_data(data: str) -> str:
    if not data:
        return None
    return fernet.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data: str) -> str:
    if not encrypted_data:
        return None
    return fernet.decrypt(encrypted_data.encode()).decode() 