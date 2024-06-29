import os

# external imports
from cryptography.fernet import Fernet

# project imports
import unichat.helpers as helpers


class EncryptionUtility:
    def __init__(self,
                 data_dir=helpers.get_user_data_dir_path(),
                 key_path="secret.key"):
        self.data_dir = data_dir
        self.key_path = os.path.join(data_dir, key_path)  # Store the key in the Unichat directory

        try:
            with open(self.key_path, "rb") as key_file:
                self.key = key_file.read()
        except FileNotFoundError:
            self.key = Fernet.generate_key()
            with open(self.key_path, "wb") as key_file:
                key_file.write(self.key)
        self.cipher_suite = Fernet(self.key)

    def encrypt(self, data: str) -> bytes:
        return self.cipher_suite.encrypt(data.encode())

    def decrypt(self, data: bytes) -> str:
        return self.cipher_suite.decrypt(data).decode()

    def save_encrypted(self, data: str, file_name: str):
        try:
            file_path = os.path.join(self.data_dir, file_name)
            encrypted_data = self.encrypt(data)
            with open(file_path, "wb") as file:
                file.write(encrypted_data)
            return True
        except FileNotFoundError:
            return False

    def load_encrypted(self, file_name: str) -> str:
        file_path = os.path.join(self.data_dir, file_name)
        with open(file_path, "rb") as file:
            encrypted_data = file.read()
        return self.decrypt(encrypted_data)
