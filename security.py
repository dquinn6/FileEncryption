from cryptography.fernet import Fernet
import hashlib
import base64
from io import StringIO
import os
import pandas as pd


def generate_key(password):

    if isinstance(password, str):
        password = str.encode(password)

    sha256 = hashlib.sha256()
    sha256.update(password)
    hash = sha256.digest()

    return base64.urlsafe_b64encode(hash)


def convert_decryption_to_df(decrypted_bytes):

        s = str(decrypted_bytes,'utf-8')
        data = StringIO(s) 

        return pd.read_csv(data)


class Encryptor():

    def __init__(self, password):
        self.key = generate_key(password)

    def encrypt_file(self, file, write_name='encoded_data.txt', keep_original=True):

        f = Fernet(self.key)

        with open(file, 'rb') as original_file:
            original = original_file.read()

        encrypted_bytes = f.encrypt(original)

        with open (f'{write_name}', 'wb') as encrypted_file:
            encrypted_file.write(encrypted_bytes)

        if not keep_original:
            os.remove(file)
            
        print(f'encrypted data written to {write_name}')


class Decryptor():

    def __init__(self, password):
        self.key = generate_key(password)
        self.decrypted_bytes = None

    def decrypt_file(self, file='encoded_data.txt', write_name='decoded_data.txt', save=True, keep_original=True):

        f = Fernet(self.key)

        with open(f'{file}', 'rb') as encrypted_file:
            encrypted = encrypted_file.read()

        self.decrypted_bytes = f.decrypt(encrypted)

        if not keep_original:
            os.remove(file)

        if save:
            with open (f'{write_name}', 'wb') as decrypted_file:
                decrypted_file.write(self.decrypted_bytes)

            print(f'decrypted data written to {write_name}')
