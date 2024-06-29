# external imports
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
)

# project imports
import unichat.db as db


class AddContactDialog(QDialog):
    def __init__(self, parent=None):
        """
        add contact dialog constructor
        """
        super().__init__(parent)
        self.setWindowTitle('Add Contact')
        layout = QVBoxLayout(self)
        self.name_label = QLabel('Name:')
        self.name_edit = QLineEdit()
        self.add_button = QPushButton('Add')
        self.add_button.clicked.connect(self.handle_add_contact)
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_edit)
        layout.addWidget(self.add_button)
        self.new_contact: db.Contact | None = None

    def handle_add_contact(self):
        """
        The function `handle_add_contact` adds a new contact to a database, 
        displaying an error message if the name is already in use.
        """
        name = self.name_edit.text()
        self.new_contact = db.add_contact(name)
        if self.new_contact is None:
            error_box = QMessageBox()
            error_box.setIcon(QMessageBox.Critical)
            error_box.setText('This name is already used, try another!')
            error_box.setStandardButtons(QMessageBox.Ok)
            error_box.exec()
        else:
            self.accept()
