# external imports
from PySide6.QtWidgets import QMessageBox

# project imports
import unichat.config as config
from unichat.widgets.login.client_login_widget import ClientLoginWidget
from unichat.workers.chat_client_worker import ChatClientWorker
from unichat.workers.instagram_worker import InstagramLoginWorker, InstagramStoreCredentialsWorker


class InstagramClientLogin(ClientLoginWidget):

    def __init__(self, chat_client) -> None:
        """
        Instagram client login constructor
        """
        super().__init__(chat_client)
        self.logo_path = config.instagram_logo
        self.login_worker = None
        self.chat_client_worker = None
        self.credentials_worker = None
        self.init_ui()

    def init_ui(self):
        """
        The `init_ui` function sets up various elements for the user interface, including logo, phone
        number, and login elements, and then sets the layout.
        """

        self.set_logo_elements()
        self.set_username_password_elements()
        self.set_login_elements(add_login_button=True,
                                add_qr_code_label=False,
                                add_username_password_field=True)
        self.set_layout()

    def qt_login(self):
        """
        gui login code
        """
        username = self.username_edit.text()
        password = self.password_edit.text()
        self.store_credentials(username, password)
        self.login_worker = InstagramLoginWorker(client=self.chat_client,
                                                 username=username,
                                                 password=password)

        self.chat_client_worker = ChatClientWorker(worker=self.login_worker,
                                                   sub_func=self.is_logged_in)
        self.chat_client_worker.execute_worker()
        self.set_input_enable(False)

    def is_logged_in(self, status: bool):
        """
            sends signal if logged in
        """
        if status:
            self.logged_in.emit(self.chat_client.name)

        else:
            QMessageBox.warning(self, "Instagram Login Error", "An error occurred! Please try again.")
            self.username_edit.clear()
            self.password_edit.clear()
        self.set_input_enable(True)

    def store_credentials(self, username: str, password: str):
        """
        stores instagram credentials

        """
        self.credentials_worker = InstagramStoreCredentialsWorker(encryption_util=self.chat_client.encryption_util,
                                                                  username=username,
                                                                  password=password)
        self.chat_client_worker = ChatClientWorker(worker=self.credentials_worker,
                                                   sub_func=None)
        self.chat_client_worker.execute_worker()

    def set_input_enable(self, enable: bool) -> None:
        """
        enable input

        """
        self.username_edit.setEnabled(enable)
        self.password_edit.setEnabled(enable)
        self.button_login.setEnabled(enable)
