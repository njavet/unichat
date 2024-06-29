# external imports
from PySide6.QtCore import QObject, Signal

# project imports
from unichat.clients.chat_client import ChatClient
from unichat.encryption.utility import EncryptionUtility


class InstagramStoreCredentialsWorker(QObject):
    finished = Signal()

    def __init__(self,
                 encryption_util: EncryptionUtility,
                 username: str,
                 password: str) -> None:
        """
        Credentials worker constructor
        """
        super().__init__()
        self.encryption_util = encryption_util
        self.username = username
        self.password = password

    def run(self) -> None:
        """
        execute worker

        """
        self.encryption_util.save_encrypted(self.username,
                                            'instagram_username.enc')
        self.encryption_util.save_encrypted(self.password,
                                            'instagram_password.enc')
        self.finished.emit()


class InstagramLoginWorker(QObject):
    """QObject worker to check whether the user has logged in successfully."""
    finished = Signal(bool)

    def __init__(self, client: ChatClient, username: str, password: str) -> None:
        """
        instagram login worker constructor
        """
        super().__init__()
        self.client = client
        self.username = username
        self.password = password

    def run(self) -> None:
        """
        run worker
        """
        success_login = self.client.login(self.username, self.password)
        check_login = self.client.is_logged_in()
        self.finished.emit(success_login and check_login)
