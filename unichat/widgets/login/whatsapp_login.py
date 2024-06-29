# external imports
from PySide6.QtWidgets import QMessageBox

# project imports
from unichat.helpers import get_icon_path
import unichat.config as config
from unichat.widgets.login.client_login_widget import ClientLoginWidget
from unichat.workers.chat_client_worker import ChatClientWorker
from unichat.workers.whatsapp_worker import WhatsappQrCodeWorker, WhatsappLoginWorker


class WhatsappClientLogin(ClientLoginWidget):
    """
    Whatsapp client login using QR-Code to log into the Whatsapp web client.
    """

    def __init__(self, chat_client) -> None:
        """
        whatsapp client login constructor
        """
        super().__init__(chat_client)
        self.logo_path = get_icon_path('whatsapp_logo.png')
        self.chat_client_worker = None
        self.init_ui()

    def init_ui(self):
        """
        The `init_ui` function sets up various elements for the user 
        interface, including logo, phone
        number, and login elements, and then sets the layout.
        """

        self.set_logo_elements()
        self.set_qr_code_elements()
        self.qr_code_label.clicked.connect(self.on_qr_label_clicked)
        self.set_login_elements(add_login_button=False,
                                add_qr_code_label=True)
        self.set_layout()

    def login(self):
        """
        The `login` function emits a signal to indicate that a user has 
        successfully logged in.
        """

        self.chat_client_worker = ChatClientWorker(
            worker=WhatsappLoginWorker(self.chat_client),
            sub_func=self.is_logged_in
        )
        self.chat_client_worker.execute_worker()

    def on_qr_label_clicked(self):
        """
        event handler for clicking on the QR label
        """
        self.chat_client_worker = ChatClientWorker(
            worker=WhatsappQrCodeWorker(self.chat_client),
            sub_func=self.show_qr_code
        )
        self.chat_client_worker.execute_worker()

    def show_qr_code(self, data):
        """
        displays the generated qr code

        """
        if not data or data != config.logged_in:
            self.set_qr_code_elements(data)
            # Prevent generating QR-Code again
            self.qr_code_label.blockSignals(True)
            self.login()
        elif data == config.logged_in:
            self.logged_in.emit(self.chat_client.name)
        else:
            QMessageBox.warning(self,
                                'QR Code Error',
                                'An error occurred! Please try again.')

    def is_logged_in(self, status: bool):
        """
        check if logged in
        """
        if status:
            self.logged_in.emit(self.chat_client.name)
        else:
            QMessageBox.warning(self,
                                'Whatsapp Login Error',
                                'QR-Code Timeout! Please try again.')
            self.set_qr_code_elements()
            # Enable generating QR-Code again
            self.qr_code_label.blockSignals(False)
