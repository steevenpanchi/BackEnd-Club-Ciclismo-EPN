import os
from base64 import b64encode, b64decode

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from dotenv import load_dotenv
from passlib.context import CryptContext

load_dotenv()

# Configuración de bcrypt para hashear contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# Obtención de la clave de cifrado
AES_KEY = os.getenv("AES_KEY").encode()


def verify_password(original_password, hashed_password):
    return pwd_context.verify(original_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def generate_iv():
    return os.urandom(16)


def encrypt_str_data(data: str):
    iv = generate_iv()
    cipher = Cipher(algorithms.AES(AES_KEY), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    # padder
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data.encode()) + padder.finalize()

    # cifrado
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()
    return b64encode(iv + encrypted_data).decode()


def decrypt_str_data(encrypted_data: str):
    raw_data = b64decode(encrypted_data)
    iv = raw_data[:16]  # Extraer IV
    encrypted_data = raw_data[16:]  # Extraer datos cifrados

    cipher = Cipher(algorithms.AES(AES_KEY), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    # Descifrar y eliminar padding
    padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    data = unpadder.update(padded_data) + unpadder.finalize()
    return data.decode()


