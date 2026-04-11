from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import os

def encrypt_data(data: bytes, key: bytes) -> bytes:
    """AES-256 ile veriyi şifreler"""
    iv = bytes(16)  # Fixed IV for compatibility with Android
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data) + padder.finalize()
    
    encrypted = encryptor.update(padded_data) + encryptor.finalize()
    return encrypted  # Don't prepend IV since it's fixed

def decrypt_data(encrypted_data: bytes, key: bytes) -> bytes:
    """AES-256 ile veriyi çözer"""
    try:
        iv = bytes(16)  # Fixed IV for compatibility with Android
        
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        
        padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
        
        unpadder = padding.PKCS7(128).unpadder()
        data = unpadder.update(padded_data) + unpadder.finalize()
        
        return data
    except Exception as e:
        raise ValueError("Şifre çözme hatası - Parolalar eşleşmiyor")
