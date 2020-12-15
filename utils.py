from cryptography.fernet import Fernet
from config import config


cipher_suite = Fernet(config.encryption_key)


# Helper to generate the key, not actually used in the code
def generate_key():
    print(Fernet.generate_key())


def encrypt(value: str) -> str:
    return cipher_suite.encrypt(value.encode('utf-8')).decode('utf-8')


def decrypt(value: str) -> str:
    return cipher_suite.decrypt(value.encode('utf-8')).decode('utf-8')
