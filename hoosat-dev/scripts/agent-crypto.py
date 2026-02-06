#!/usr/bin/env python3
"""
Hoosat Agent Crypto Utilities

Encryption/decryption for secure wallet storage.
Uses Fernet (AES-128-CBC) with PBKDF2 key derivation.
"""

import json
import base64
import hashlib
import os
import time
from typing import Dict, Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2

# Constants
SALT = b'hoosat_agent_salt_v1'
ITERATIONS = 100000
KEY_LENGTH = 32


class AgentCrypto:
    """Handles encryption/decryption of wallet data."""
    
    def __init__(self, password: str):
        """Initialize with master password."""
        self.password = password
        self._key = self._derive_key(password)
        self._fernet = Fernet(self._key)
    
    def _derive_key(self, password: str) -> bytes:
        """Derive encryption key from password using PBKDF2."""
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=KEY_LENGTH,
            salt=SALT,
            iterations=ITERATIONS,
        )
        key = kdf.derive(password.encode())
        return base64.urlsafe_b64encode(key)
    
    def encrypt(self, data: Dict) -> bytes:
        """Encrypt dictionary to bytes."""
        json_data = json.dumps(data).encode()
        encrypted = self._fernet.encrypt(json_data)
        return encrypted
    
    def decrypt(self, encrypted_data: bytes) -> Dict:
        """Decrypt bytes to dictionary."""
        decrypted = self._fernet.decrypt(encrypted_data)
        return json.loads(decrypted.decode())
    
    def verify_password(self, encrypted_data: bytes) -> bool:
        """Verify password can decrypt data."""
        try:
            self.decrypt(encrypted_data)
            return True
        except Exception:
            return False
    
    @staticmethod
    def generate_password(length: int = 24) -> str:
        """Generate a secure random password."""
        import secrets
        import string
        alphabet = string.ascii_letters + string.digits + string.punctuation
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    def clear(self):
        """Clear sensitive data from memory."""
        self.password = None
        self._key = None
        self._fernet = None


class SessionManager:
    """Manages password session with timeout."""
    
    def __init__(self, timeout_seconds: int = 3600):  # 1 hour default
        self.timeout = timeout_seconds
        self._password = None
        self._last_access = None
        self._env_var = 'HOOSAT_AGENT_PASSWORD'
    
    def set_password(self, password: str):
        """Set password and store in environment."""
        self._password = password
        self._last_access = os.time()
        os.environ[self._env_var] = password
    
    def get_password(self) -> Optional[str]:
        """Get password if session is valid."""
        # Check memory first
        if self._password and self._is_session_valid():
            self._last_access = os.time()
            return self._password
        
        # Check environment
        env_password = os.environ.get(self._env_var)
        if env_password:
            self._password = env_password
            self._last_access = os.time()
            return env_password
        
        return None
    
    def _is_session_valid(self) -> bool:
        """Check if session hasn't timed out."""
        if not self._last_access:
            return False
        return (os.time() - self._last_access) < self.timeout
    
    def clear(self):
        """Clear session."""
        self._password = None
        self._last_access = None
        if self._env_var in os.environ:
            del os.environ[self._env_var]
    
    def is_active(self) -> bool:
        """Check if session is currently active."""
        return self.get_password() is not None


def hash_address(address: str) -> str:
    """Hash an address for identification (not for security)."""
    return hashlib.sha256(address.encode()).hexdigest()[:16]


def secure_wipe(data: bytes):
    """Attempt to securely wipe bytes from memory."""
    # Note: Python doesn't guarantee memory wiping due to garbage collection
    # This is a best-effort attempt
    if isinstance(data, bytearray):
        for i in range(len(data)):
            data[i] = 0


if __name__ == '__main__':
    # Test encryption/decryption
    crypto = AgentCrypto('test_password_123')
    
    test_data = {
        'wallets': {
            'mining': {
                'address': 'hoosat:qz7ulu8mmmul6hdcnssmjnt28h2xfer8dz9nfqamvvh86ngef4q8dvzxcjdqe',
                'private_key': 'Kxabc123...'
            }
        }
    }
    
    encrypted = crypto.encrypt(test_data)
    decrypted = crypto.decrypt(encrypted)
    
    print("Encryption test:", "PASSED" if decrypted == test_data else "FAILED")
    print("Password verification:", "PASSED" if crypto.verify_password(encrypted) else "FAILED")
