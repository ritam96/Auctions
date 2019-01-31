import os
import json
from cryptography import x509
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, hmac, serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.primitives.asymmetric import padding
from OpenSSL import crypto

def cipher(data, DHKey, certObj):
    DHK = int(list(DHKey)[:len(DHKey)//2])
    DHIntegrity = int(list(DHKey)[(len(DHKey)//2):])
    firstEncryption = encryptWithRandomKey(data)
    keyAndIV = {}
    keyAndIV['key'] = firstEncryption['key']
    keyAndIV['iv'] = firstEncryption['iv']
    (auxiliaryCryptogram, secondEncryption) = encryptWithCertServerSide(json.loads(keyAndIV), certObj, 'AuctionRepoPKey.pem')
    final, nonce = encryptWithDH('{"data":' + firstEncryption + ', "2ndEncryption":' + secondEncryption + ', "auxCryptogram":' + auxiliaryCryptogram + '}', DHK)
    hmac = integrity(final, DHIntegrity)

    return {'data': final, 'integrity': hmac, 'nonce': nonce}

def decipher(parameters, DHKey, certObj):
    DHK = int(list(DHKey)[:len(DHKey)//2])
    DHIntegrity = int(list(DHKey)[(len(DHKey)//2):])
    hmac = integrity(parameters['data'], DHIntegrity)
    if hmac != parameters['integrity']:
        return "{'error': 'FAILED INTEGRITY CHECK'}"
    
    data = json.loads(decryptWithDH(parameters['data'], DHK, parameters['nonce']))
    aux = {'key1': data['2ndEncryption'], 'key2': data['auxCryptogram']}

    key = decryptWithCertServerSide(aux, certObj, 'AuctionRepoPKey.pem')
    if key == None:
        return "{'error': 'FAILED SINATURE TEST'}"
    finalKey = json.loads(key)
    finalData = decryptWithRandomKey(data['data'], finalKey['iv'], finalKey['key'])
    return finalData

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
    nonce = os.urandom(16)
    algorithm = algorithms.ChaCha20(key, nonce)
    cipher = Cipher(algorithm, mode=None, backend=default_backend())
    encryptor = cipher.encryptor()
    ct = encryptor.update(data)
    return ct, nonce

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

def loadPrivateKey(path):
    with open(path, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )
    return private_key

def loadTrustedCerts(directory):
    certs = []
    for filename in os.listdir(directory):
        with open(os.path.join(directory, filename), "rb") as cert_file:
            cert = x509.load_pem_x509_certificate(cert_file.read(), default_backend())
            certs.append(cert)
    return certs

def encryptWithCertServerSide(data, certObj, privateKeyPath):
    privateKey = loadPrivateKey(privateKeyPath)
    cert = x509.load_pem_x509_certificate(certObj, default_backend())
    publicKey = cert.public_key()
    cipher = publicKey.encrypt(
        data,
        padding.PKCS1v15()
    )
    signature = privateKey.sign(
        cipher,
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    return (cipher, signature)

def decryptWithCertServerSide(data, certObj, privateKeyPath):
    privateKey = loadPrivateKey(privateKeyPath)
    certificate = x509.load_pem_x509_certificate(certObj, default_backend())
    encryptedKey = data['key2']
    signedKey = data['key1']

    trustedCerts = loadTrustedCerts('pathToCerts')
    if not validateCertificateChain(certObj, trustedCerts):
        return None
    
    clientPubKey = certificate.public_key()
    try:
        clientPubKey.verify(
            signedKey,
            encryptedKey,
            padding.PKCS1v15(),
            hashes.SHA1()
        )
    except:
        return None


    plaintext = privateKey.decrypt(
        encryptedKey,
        padding.PKCS1v15()
    )

    return plaintext

def validateCertificateChain(certObj, trustedCerts):
    certificate = x509.load_pem_x509_certificate(certObj, default_backend())
    try:
        store = crypto.X509Store()
        for c in trustedCerts:
            store.add_cert(c)

        store_ctx = crypto.X509StoreContext(store, certificate)

        # Validar certificado
        store_ctx.verify_certificate()

        return True

    except Exception as e:
        print(e)
        return False

