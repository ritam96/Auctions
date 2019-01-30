import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.backends import default_backend

def encryptWithRandomKey(data):
    ret = {}
    key = os.urandom(32)
    ret['key'] = key
    iv = os.urandom(16)
    ret['iv'] = iv
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    ct = encryptor.update(data) + encryptor.finalize()
    ret['cipheredData'] = ct

    return ret

def encryptWithDH(data, key):
    ret = {}
    nonce = os.urandom(16)
    ret['nonce'] = nonce
    algorithm = algorithms.ChaCha20(key, nonce)
    cipher = Cipher(algorithm, mode=None, backend=default_backend())
    encryptor = cipher.encryptor()
    ct = encryptor.update(data)
    ret['cipheredData'] = ct
    return ret


def integrity(data, key):
    h = hmac.HMAC(key, hashes.SHA256(), backend=default_backend())
    h.update(data)
    return h.finalize()

def decryptWithRandomKey(data, iv, key):
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    ret = decryptor.update(data) + decryptor.finalize()
    return ret

def decryptWithDH(data, key, nonce):
    algorithm = algorithms.ChaCha20(key, nonce)
    cipher = Cipher(algorithm, mode=None, backend=default_backend())
    decryptor = cipher.decryptor()
    ret = decryptor.update(data)
    return ret

