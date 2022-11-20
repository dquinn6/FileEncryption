import sys
import os
from cryptography.fernet import Fernet
import hashlib
import base64

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


def generate_key(password):

    if isinstance(password, str):
        password = str.encode(password)

    sha256 = hashlib.sha256()
    sha256.update(password)
    hash = sha256.digest()

    return base64.urlsafe_b64encode(hash)


def main():
    '''
    argv[1] = file to use
    argv[2] = encrypt/decrypt
    argv[3] = password
    argv[4] = keep/remove
    '''

    file = str(sys.argv[1])
    mode = str(sys.argv[2]).lower()
    mode_space = ['encrypt', 'decrypt']
    if mode not in mode_space :
        raise ValueError(f"ERROR: invalid input for second argument 'mode'; valid inputs include: {mode_space}")

    password = str(sys.argv[3])
    keep = str(sys.argv[4]).lower()
    keep_space = ['keep', 'remove']
    if keep not in keep_space:
        raise ValueError(f"ERROR: invalid input for fourth argument 'keep'; valid inputs include: {keep_space}")

    if keep == 'keep':
        keep_original = True
    else:
        keep_original=False

    yes_space = ['y', 'yes']
    no_space = ['n', 'no']

    if os.sep in file:
        if file[0] == '.': #relative path
            relpath = f'{os.sep}'.join(file.split(os.sep)[:-1])+os.sep
            path = os.path.dirname(__file__) + relpath[1:]
        else: #absolute path 
            path = f'{os.sep}'.join(file.split(os.sep)[:-1])+os.sep

        file_name = file.split(os.sep)[-1]
    else:
        path = os.getcwd()+os.sep
        file_name = file

    '''
    Encryption
    '''
    if mode == 'encrypt':

        if not keep_original:
            confirm_del = None
            while True:
                confirm_del = input('WARNING: original unencrypted file(s) with be DELETED - proceed? (Y/N): ')
                if confirm_del.lower() in yes_space:
                    proceed=True
                    break
                elif confirm_del.lower() in no_space:
                    proceed=False
                    break
                else:
                    print('Invalid response; please type YES (Y) or NO (N) to proceed')
                    continue

            if not proceed:
                sys.exit('ABORTING \n- if you wish to keep original, run with --keep_original')

        enc = Encryptor(password)

        if file_name[0] == '*':
            file_ext = file.split('.')[-1]
            files_to_encrypt = []
            for dir_file in os.listdir(path):
                if dir_file.endswith(file_ext): 
                    files_to_encrypt.append(dir_file)
            
            for file in files_to_encrypt:
                enc.encrypt_file(file=path+file, 
                                write_name=f'{path}{file}.encrypted', 
                                keep_original=keep_original)

        else: #single file
            enc.encrypt_file(file=path+file_name, 
                            write_name=f'{path}{file_name}.encrypted', 
                            keep_original=keep_original)

    '''
    Decryption
    '''
    if mode == 'decrypt':

        file_ext = file.split('.')[-1]
        if file_ext != 'encrypted':
            raise ValueError('ERROR: can only decrypt files with .encrypted extension')

        attempts = 0
        max_attempts = 5

        while attempts < max_attempts:
            attempts += 1
            
            try:
                dec = Decryptor(password) 

                if file_name[0] == '*':
                    files_to_decrypt = []
                    for dir_file in os.listdir(path):
                        if dir_file.endswith(file_ext):
                            files_to_decrypt.append(dir_file)

                    for file in files_to_decrypt:
                        write_name='.'.join(f'{path}{file}'.split('.')[:-1]) #remove .encrypted ext
                        dec.decrypt_file(file=path+file, 
                                        write_name=write_name, 
                                        save=True,
                                        keep_original=keep_original)

                else: #single file
                    write_name='.'.join(f'{path}{file_name}'.split('.')[:-1])
                    dec.decrypt_file(file=path+file_name, 
                                    write_name=write_name,
                                    save=True,
                                    keep_original=keep_original)
                break

            except:
                print('CANNOT DECRYPT; PASSWORD DOES NOT MATCH ONE USED FOR ENCRYPTION')
                print(f'FOR SAKE OF SECURITY, FILE(S) WILL BE DELETED AFTER {max_attempts-attempts+1} MORE ATTEMPTS')

                if attempts == 1 or attempts == max_attempts:
                    while True:
                        confirm_continue = input('DO YOU WISH TO CONTINUE DECRYPTING? (Y/N): ')
                        if confirm_continue.lower() in yes_space:
                            proceed=True
                            break
                        elif confirm_continue.lower() in no_space:
                            proceed=False
                            break
                        else:
                            print('Invalid response; please type YES (Y) or NO (N) to proceed')
                            continue

                    if not proceed:
                        sys.exit('ABORTING')

                password = str(input('re-enter password: '))

        if attempts == max_attempts:
            if file_name[0] == '*':
                for _file in os.listdir(path):
                    if _file.endswith(file_ext):
                        os.remove(path+_file)
            else:
                os.remove(path+file_name)
            print('MAX NUMBER OF ATTEMPTS REACHED - FOR SAKE OF SECURITY, ENCRYPTED FILE(S) HAS BEEN DELETED')
        

if __name__ == "__main__":
    main()