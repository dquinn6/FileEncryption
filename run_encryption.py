import security
import argparse
import sys
import os

parser = argparse.ArgumentParser()
parser.add_argument('--file', type=str, required=True)
parser.add_argument('--password', type=str, required=True)
parser.add_argument('--keep_original', action='store_true')
group1 = parser.add_mutually_exclusive_group() 
group1.add_argument('--encrypt', action='store_true')
group1.add_argument('--decrypt', action='store_true')
args = parser.parse_args()

yes_choices = ['y', 'yes']
no_choices = ['n', 'no']

password = str(args.password)

if os.sep in args.file:
    if args.file[0] == '.': #relative path
        relpath = f'{os.sep}'.join(args.file.split(os.sep)[:-1])+os.sep
        path = os.path.dirname(__file__) + relpath[1:]
    else: #absolute path 
        path = f'{os.sep}'.join(args.file.split(os.sep)[:-1])+os.sep

    file_name = args.file.split(os.sep)[-1]
else:
    path = os.getcwd()+os.sep
    file_name = args.file
    
if args.encrypt:

    if not args.keep_original:
        confirm_del = None

        while True:
            confirm_del = input('WARNING: original unencrypted file(s) with be DELETED - proceed? (Y/N): ')
            if confirm_del.lower() in yes_choices:
                proceed=True
                break
            elif confirm_del.lower() in no_choices:
                proceed=False
                break
            else:
                print('Invalid response; please type YES (Y) or NO (N) to proceed')
                continue

        if not proceed:
            sys.exit('ABORTING \n- if you wish to keep original, run with --keep_original')

    enc = security.Encryptor(password)

    if file_name[0] == '*':
        file_ext = args.file.split('.')[-1]
        files_to_encrypt = []
        for dir_file in os.listdir(path):
            if dir_file.endswith(file_ext): 
                files_to_encrypt.append(dir_file)
        
        for file in files_to_encrypt:
            enc.encrypt_file(file=path+file, 
                            write_name=f'{path}{file}.encrypted', 
                            keep_original=args.keep_original)

    else: #single file
        enc.encrypt_file(file=path+file_name, 
                        write_name=f'{path}{file_name}.encrypted', 
                        keep_original=args.keep_original)

if args.decrypt:

    file_ext = args.file.split('.')[-1]
    if file_ext != 'encrypted':
        raise ValueError('ERROR: can only decrypt files with .encrypted extension')

    attempts = 0
    max_attempts = 5

    while attempts < max_attempts:
        attempts += 1
        
        try:
            dec = security.Decryptor(password) 

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
                                    keep_original=args.keep_original)

            else: #single file
                write_name='.'.join(f'{path}{file_name}'.split('.')[:-1])
                dec.decrypt_file(file=path+file_name, 
                                write_name=write_name,
                                save=True,
                                keep_original=args.keep_original)
            break

        except:
            print('CANNOT DECRYPT; PASSWORD DOES NOT MATCH ONE USED FOR ENCRYPTION')
            print(f'FOR SAKE OF SECURITY, FILE(S) WILL BE DELETED AFTER {max_attempts-attempts+1} MORE ATTEMPTS')

            if attempts == 1 or attempts == max_attempts:
                while True:
                    confirm_continue = input('DO YOU WISH TO CONTINUE DECRYPTING? (Y/N): ')
                    if confirm_continue.lower() in yes_choices:
                        proceed=True
                        break
                    elif confirm_continue.lower() in no_choices:
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
        