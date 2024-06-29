# external imports
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QPushButton,
)

# project imports
import unichat.db as db


class RemoveContactDialog(QDialog):
    def __init__(self, contact, parent=None):
        """
        remove contact dialog constructor
        """
        super().__init__(parent)
        self.contact = contact
        self.setWindowTitle('Delete Contact')
        layout = QVBoxLayout(self)
        self.add_button = QPushButton('Remove')
        self.add_button.clicked.connect(self.handle_remove_contact)
        layout.addWidget(self.add_button)

    def handle_remove_contact(self):
        """
        removes contact
        """
        db.remove_contact(self.contact.name)
        self.accept()
