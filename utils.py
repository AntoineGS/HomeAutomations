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


def celsius_to_fahrenheit(celsius: float) -> float:
    return (celsius * 9/5) + 32


def fahrenheit_to_celsius(fahrenheit: float) -> float:
    return (fahrenheit - 32) * 5/9
