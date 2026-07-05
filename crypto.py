import base64
import secrets

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Vault entries are encrypted with a key derived from the user's master
# password. The key is never stored — it only exists in memory while a
# request that supplied the master password is being handled.

KDF_ITERATIONS = 600_000  # OWASP recommendation for PBKDF2-HMAC-SHA256


def new_salt():
    return base64.b64encode(secrets.token_bytes(16)).decode('ascii')


def derive_key(master_password, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=base64.b64decode(salt),
        iterations=KDF_ITERATIONS,
    )
    key = kdf.derive(master_password.encode('utf-8'))
    return base64.urlsafe_b64encode(key)


def encrypt_secret(key, plaintext):
    return Fernet(key).encrypt(plaintext.encode('utf-8')).decode('ascii')


def decrypt_secret(key, token):
    return Fernet(key).decrypt(token.encode('ascii')).decode('utf-8')


def is_encrypted(value):
    # Fernet tokens always begin with the version byte 0x80, which
    # base64-encodes to "gAAAA". Entries saved before encryption was
    # added are plaintext and won't match.
    return value.startswith('gAAAA')


__all__ = [
    'new_salt', 'derive_key', 'encrypt_secret', 'decrypt_secret',
    'is_encrypted', 'InvalidToken', 'KDF_ITERATIONS',
]
