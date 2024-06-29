# external imports
from PySide6.QtCore import Signal, Qt
from PySide6.QtWidgets import (
    QVBoxLayout,
    QPushButton,
    QComboBox,
    QWidget)


class LinkContact(QWidget):
    """
    Base class for contact linking

    """
    linked_contact = Signal(str)

    def __init__(self, contact, chat_client):
        """
        link contact constructor
        """
        super().__init__()
        self.contact = contact
        self.chat_client = chat_client
        self.init_button = QPushButton('Load Contacts')
        self.combo_box = QComboBox()
        self.choose_contact_button = QPushButton('Select Contact')
        self.possible_contacts: dict = {}
        self.init_ui()

    def init_ui(self):
        """
        The `init_ui` function sets up the user interface layout and connects button clicks to
        corresponding functions.
        """
        layout = QVBoxLayout()
        self.init_button.clicked.connect(self.init_chat)
        self.choose_contact_button.clicked.connect(self.link_contact)
        layout.addWidget(self.init_button)
        layout.addWidget(self.combo_box)
        layout.addWidget(self.choose_contact_button)
        layout.setAlignment(Qt.AlignCenter)
        self.setLayout(layout)

    def init_chat(self):
        """
        child widgets need to implement this for initialize the chat
        after selecting a contact
        """
        raise NotImplementedError

    def link_contact(self):
        """
        child widgets need to implement this for linking a contact
        """
        raise NotImplementedError
