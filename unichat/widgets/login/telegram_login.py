# external imports
from PySide6.QtWidgets import (
    QLabel,
    QLineEdit,
    QPushButton
)

# project imports
from unichat.helpers import get_icon_path
from unichat.widgets.login.client_login_widget import ClientLoginWidget


class TelegramClientLogin(ClientLoginWidget):
    """
    Telegram login client. Uses the username/tel.number to log in to the telegram api.
    """

    def __init__(self, chat_client):
        """
        telegram client login constructor
        """
        super().__init__(chat_client)
        # request access code for the sync telegram client
        self.logo_path = get_icon_path('telegram_logo.png')
        self.sync_button_tg = QPushButton('Request Access code for the sync client')
        self.sync_telegram_code_label = QLabel('Sync client Access Code:')
        self.sync_telegram_code = QLineEdit()
        self.password_2fa_label = QLabel('Password for 2FA')
        self.password_2fa = QLineEdit()
        self.init_ui()

    def init_ui(self):
        """
        The `init_ui` function sets up various UI elements including logo, phone number,
        Telegram-specific elements, login elements, and layout.
        """
        self.set_logo_elements()
        self.set_phone_number_elements()
        # telegram specific code
        self.sync_button_tg.clicked.connect(self.request_code)
        self.right_layout.addWidget(self.sync_button_tg)
        self.right_layout.addWidget(self.sync_telegram_code_label)
        self.right_layout.addWidget(self.sync_telegram_code)
        self.right_layout.addWidget(self.password_2fa_label)
        self.right_layout.addWidget(self.password_2fa)

        self.set_login_elements()
        self.set_layout()

    def qt_login(self):
        """
        The `qt_login` function logs in a user using a chat client with provided phone number,
        authentication code, and password.
        """
        self.chat_client.login(phone_number=self.phone_number,
                               auth_code=self.sync_telegram_code.text(),
                               password=self.password_2fa.text())
        self.logged_in.emit(self.chat_client.name)

    def request_code(self):
        """
        This function sets the phone number from user input and sends a code request using a chat
        client.
        """
        self.phone_number = self.phone_number_edit.text()
        self.chat_client.send_code_request(self.phone_number)
