from base64 import b64decode
from nacl.secret import SecretBox
import configparser
import os


def do_decrypt(string, env):
    if string is None:
        return None
    config = configparser.ConfigParser(interpolation=None)
    config.read(os.path.join("..", "config.ini"))
    secret_key = config.get(env, 'secret_key')
    encrypted = string
    encrypted = encrypted.split(':')
    if len(encrypted) != 2:
        raise Exception('String given does not look encrypted')
    # We decode the two bits independently
    nonce = b64decode(encrypted[0])
    encrypted = b64decode(encrypted[1])
    # We create a SecretBox, making sure that out secret_key is in bytes
    box = SecretBox(bytes(secret_key, encoding='utf8'))
    decrypted = box.decrypt(encrypted, nonce).decode('utf-8')
    return decrypted
