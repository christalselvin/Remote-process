
from Cryptodome import Random
from Cryptodome.Cipher import AES
import base64
from hashlib import md5

BLOCK_SIZE = 16

def pad(data):
    length = BLOCK_SIZE - (len(data) % BLOCK_SIZE)
    return data + (chr(length)*length).encode()

def unpad(data):
    return data[:-(data[-1] if type(data[-1]) == int else ord(data[-1]))]

def bytes_to_key(data, salt, output=48):
    # extended from https://gist.github.com/gsakkis/4546068
    assert len(salt) == 8, len(salt)
    data += salt
    key = md5(data).digest()
    final_key = key
    while len(final_key) < output:
        key = md5(key + data).digest()
        final_key += key
    return final_key[:output]

def encrypt(message, passphrase):
    try:
        salt = Random.new().read(8)
        key_iv = bytes_to_key(passphrase, salt, 32 + 16)
        key = key_iv[:32]
        iv = key_iv[32:]
        aes = AES.new(key, AES.MODE_CBC, iv)
        return base64.b64encode(b"Salted__" + salt + aes.encrypt(pad(message)))
    except Exception as e:
        return str(e).encode('utf-8')

def decrypt(encrypted, passphrase):
    try:
        encrypted = base64.b64decode(encrypted)
        assert encrypted[0:8] == b"Salted__"
        salt = encrypted[8:16]
        key_iv = bytes_to_key(passphrase, salt, 32 + 16)
        key = key_iv[:32]
        iv = key_iv[32:]
        aes = AES.new(key, AES.MODE_CBC, iv)
        return unpad(aes.decrypt(encrypted[16:]))
    except Exception as e:
        return str(e).encode('utf-8')




#password = "@ut0!ntell!".encode()
#ct_b64 = "U2FsdGVkX1+nHaXwubZ3iV0Cjbb76oXYjxj5lOWspME="
#pt = decrypt(ct_b64, password)
#print(pt.decode('UTF-8'))
#print(encrypt(pt, password).decode('UTF-8'))
#print(encrypt('admin', '@ur0!ntelli'))
