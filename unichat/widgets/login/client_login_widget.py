import io

# external imports
import qrcode
from PySide6.QtCore import Signal
from PySide6.QtGui import QPixmap, QRegularExpressionValidator
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QLineEdit,
    QPushButton)

# project imports
import unichat.helpers as helpers


class ClientLoginWidget(QWidget):
    """
    Base class for logins

    """
    logged_in = Signal(str)

    def __init__(self, chat_client):
        """
        ChatClient Login constructor
        """
        super().__init__()
        self.chat_client = chat_client
        self.phone_number = None
        self.logo_path = None
        self.main_layout = QHBoxLayout()
        self.right_layout = QVBoxLayout()
        # phone number input fields
        self.phone_number_label = QLabel('Phone number:')
        self.phone_number_edit = QLineEdit()
        # username and password input fields
        self.username_edit = QLineEdit()
        self.password_edit = QLineEdit()
        # button to login
        self.button_login = QPushButton('Login')
        # qr code
        self.qr_code_label = helpers.ClickableLabel(parent=self)

    def set_logo_elements(self):
        """
        The function `set_logo_elements` creates a QLabel with a logo image and adds it to the main
        layout.
        """
        # logo on the left side
        logo_label = QLabel()
        logo_label.setPixmap(QPixmap(self.logo_path))
        self.main_layout.addWidget(logo_label)

    def set_phone_number_elements(self):
        """
        The function sets up a phone number validator for a QLineEdit widget in a PyQt application.
        """
        self.right_layout.addStretch(1)

        # phone number validator
        phone_number_pattern = "^[+]?[0-9]{1,3}[-]?[0-9]{5,14}$"
        phone_number_validator = QRegularExpressionValidator(phone_number_pattern)
        self.phone_number_edit.setValidator(phone_number_validator)

        self.right_layout.addWidget(self.phone_number_label)
        self.right_layout.addWidget(self.phone_number_edit)

    def set_username_password_elements(self):
        """
            add username / password inputs to the layout
        """
        # Username/Phone Number Input
        self.username_edit.setPlaceholderText("Username or Phone Number")
        # Password Input
        self.password_edit.setPlaceholderText("Password")
        # Hide password characters
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)

    def set_qr_code_elements(self, data: str = "") -> None:
        """Sets a QRCode image to the QPixmap label. If the given data is empty,
        a placeholder will be set instead.

        :param data: the qr code data string
        """

        if not data:
            self.qr_code_label.setPixmap(QPixmap(
                helpers.get_image_path('qr_code_placeholder.png')
            ).scaled(400, 400))
        else:
            qr_image = qrcode.make(data)
            buffer = io.BytesIO()
            qr_image.save(buffer)
            qr_pixmap = QPixmap()
            qr_pixmap.loadFromData(buffer.getvalue())
            self.qr_code_label.setPixmap(qr_pixmap.scaled(400, 400))

    def set_login_elements(self,
                           add_login_button: bool = True,
                           add_qr_code_label: bool = False,
                           add_username_password_field: bool = False) -> None:
        """Sets the login elements to the main layout of the QWidget

        :param add_login_button: Adds the login button if True
        :param add_qr_code_label: Adds the qr code label if True
        :param add_username_password_field: Adds the username and password fields if True
        """
        if add_qr_code_label:
            self.right_layout.addWidget(self.qr_code_label)
        if add_username_password_field:
            self.right_layout.addWidget(self.username_edit)
            self.right_layout.addWidget(self.password_edit)
        if add_login_button:
            self.right_layout.addWidget(self.button_login)
            self.button_login.clicked.connect(self.qt_login)

        self.main_layout.addLayout(self.right_layout)

    def set_layout(self):
        """
        sets the widget layout

        """
        self.setLayout(self.main_layout)

    def qt_login(self):
        """
        child widgets need to implement their specific code for the
        Gui login widget

        """
        raise NotImplementedError
