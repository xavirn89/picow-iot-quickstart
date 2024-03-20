from ucryptolib import aes
import uos

#Using AES-CBC cipher

class Crypto:
    def __init__(self, key, mode, iv):
        self.key = key
        self.mode = mode
        self.iv = iv

    def encrypt(self, plain):
        cipher = aes(self.key, self.mode, self.iv)
        # Padding for block size (AES works in 16-byte blocks)
        padded = plain.encode('utf-8') + b"\0" * (16 - len(plain) % 16)
        encrypted = cipher.encrypt(padded)
        return encrypted

    def decrypt(self, encrypted):
        decipher = aes(self.key, self.mode, self.iv)
        decrypted = decipher.decrypt(encrypted)
        # Remove null byte padding and decode
        return decrypted.rstrip(b"\0").decode('utf-8')

    def parse(self, encrypted):
        return encrypted.hex()

    def deparse(self, hexdata):
        return bytes.fromhex(hexdata)

