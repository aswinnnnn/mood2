import base64
import os

def generate_encryption_key():
    # Generate a 32-byte random key
    key = os.urandom(32)
    # Convert to base64 for storage
    encoded_key = base64.urlsafe_b64encode(key)
    print(f"Generated encryption key: {encoded_key.decode()}")
    return encoded_key

if __name__ == "__main__":
    generate_encryption_key() 