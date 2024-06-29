# external imports
from PySide6.QtGui import Qt, QPixmap
from PySide6.QtWidgets import (QWidget,
                               QLineEdit,
                               QMessageBox,
                               QPushButton,
                               QVBoxLayout,
                               QLabel,
                               QHBoxLayout,
                               QDialog)

# project imports
from unichat.helpers import get_icon_path
import unichat.db as db


class SignUpDialog(QDialog):
    def __init__(self):
        """
        sign up dialog constructor
        """
        super().__init__()
        self.me: db.Contact | None = None
        self.name_label = QLabel('Name:')
        self.name_edit = QLineEdit()
        self.sign_up_button = QPushButton(text='Sign Up')
        self.logo_pixmap = QPixmap(get_icon_path('unichat_logo.png'))
        self.title_pixmap = QPixmap(get_icon_path('unichat_titlebar.png'))
        self.init_ui()

    def init_ui(self):
        """
        The `init_ui` function sets up the user interface layout with a logo, 
        title, name label, name edit field, and sign-up button.
        """
        layout = QHBoxLayout(self)

        # left side
        logo_label = QLabel()
        logo_label.setPixmap(self.logo_pixmap)
        layout.addWidget(logo_label)
        layout.setAlignment(Qt.AlignCenter)

        # right side
        right_layout = QVBoxLayout()
        right_widget = QWidget()
        title_label = QLabel()
        title_label.setPixmap(self.title_pixmap)
        right_layout.addWidget(title_label)

        right_layout.addWidget(self.name_label)
        right_layout.addWidget(self.name_edit)
        right_layout.addWidget(self.sign_up_button)
        right_layout.setAlignment(Qt.AlignCenter)
        right_widget.setLayout(right_layout)
        self.sign_up_button.clicked.connect(self.handle_sign_up)
        layout.addWidget(right_widget)

    def handle_sign_up(self):
        """
        The function `handle_sign_up` handles user sign-up by adding a contact to a database and
        displaying an error message if the name is already in use.
        """
        name = self.name_edit.text()
        self.me = db.add_contact(name, is_me=True)
        if self.me is None:
            error_box = QMessageBox()
            error_box.setIcon(QMessageBox.Critical)
            error_box.setText('This name is already used, try another!')
            error_box.setStandardButtons(QMessageBox.Ok)
            error_box.exec()
        else:
            self.accept()
