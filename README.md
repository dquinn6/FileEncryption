# FileEncryption
Python tool for encrypting and decrypting local files. 

To test, try decrypting top_secret.jpg.encrypted with password 1234

## Binary Executable

arg1: name of file(s) to use

arg2: specify encryption or decrypton | valid inputs: ['encrypt', 'decrypt']
  
arg3: password for encryption/decryption

arg4: specify whether to keep original file(s) | valid inputs: ['keep', 'remove']
  
### Command Line Example

run_encryption.exe **.jpg encrypt 1234 remove* 

### Without Command Line

1. Right click run_encryption.exe -> create shortcut
2. Right click shortcut -> properties -> target: add args after .exe path -> apply
3. Double click shortcut

