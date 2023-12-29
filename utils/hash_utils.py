'''
    Author: Mohamed Niyaz M
    Description: This file is expected to contain the helper functions for hasing purpose
                 Encrypting by AES in ECB mode. 
'''
import typing
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

def encrypt_input(ip_str: str, master_password: str) -> str:
    '''
        takes value to be encrypted and master password as input 
        returns the hex value of encrypted cyphertext
    '''
    try:
        key = bytes(master_password, 'utf-8')
        padded_key = key + b'\x00' * (16 - len(key))
        cipher = AES.new(padded_key, AES.MODE_ECB)
        data = bytes(ip_str, 'utf-8')
        padded_message = pad(data, AES.block_size)
        result = cipher.encrypt(padded_message)

        return result.hex()
    except Exception as e:
        print(e)
        return "Something went wrong when encrypting"

def decrypt_input(cyphertext_hex: str, master_password: str) -> str | None:
    '''
        takes hex value of cyphertext and master password as input 
        returns the decrypted value of cyphertext

        TODO: Check if it is wrong master password when Padding is incorrect. 
    '''
    try:
        key =bytes(master_password, 'utf-8')
        padded_key = key + b'\x00' * (16 - len(key))
        ciphertext = bytes.fromhex(cyphertext_hex)
        cipher = AES.new(padded_key, AES.MODE_ECB)
        decrypted_bytes = cipher.decrypt(ciphertext)
        decrypted_message = unpad(decrypted_bytes, AES.block_size)
        return decrypted_message.decode('utf-8')
    
    except Exception as e:
        print("problem decrypting")
        print(e)
        return None
