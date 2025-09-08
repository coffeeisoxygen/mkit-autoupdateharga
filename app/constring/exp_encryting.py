"""enkripsi dan dekripsi

using cryptography.fernet library with machine as key to encrypt
"""

import base64
import hashlib
import os
import uuid

from cryptography.fernet import Fernet


def get_machine_id() -> str:
    """Get a machine-specific identifier (MAC address)."""
    mac = uuid.getnode()
    return str(mac)


def get_salt() -> str:
    """Get or generate a secure random salt, stored in salt.bin."""
    salt_file = "salt.bin"
    if os.path.exists(salt_file):
        with open(salt_file, "rb") as f:
            salt = f.read()
    else:
        salt = os.urandom(16)  # 16 bytes = 128 bits
        with open(salt_file, "wb") as f:
            f.write(salt)
    return base64.urlsafe_b64encode(salt).decode()


def generate_key() -> str:
    """Generate a key for encryption/decryption based on machine ID and secure salt."""
    machine_id = get_machine_id()
    salt = get_salt()
    # Hash the machine ID and salt to get a fixed-length key
    hash_digest = hashlib.sha256(f"{machine_id}{salt}".encode()).digest()
    key = base64.urlsafe_b64encode(hash_digest).decode()
    return key


class Encryptor:
    def __init__(self):
        # Always use machine-specific key derived from MAC address
        machine_key = generate_key()
        self.fernet = Fernet(machine_key)

    def encrypt(self, data: str) -> str:
        """Encrypt data using the machine-specific key."""
        encrypted = self.fernet.encrypt(data.encode())
        return encrypted.decode()

    def decrypt(self, token: str) -> str:
        """Decrypt data using the machine-specific key."""
        decrypted = self.fernet.decrypt(token.encode())
        return decrypted.decode()


# # Example usage:
# if __name__ == "__main__":
#     builder = Encryptor()
#     original = "Server=myserver;Database=mydb;UID=myuser;PWD=mypassword;"
#     encrypted = builder.encrypt(original)
#     decrypted = builder.decrypt(encrypted)

#     print(f"Original:  {original}")
#     print(f"Encrypted: {encrypted}")
#     print(f"Decrypted: {decrypted}")
