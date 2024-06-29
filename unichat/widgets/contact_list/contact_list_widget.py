# external imports
from PySide6.QtWidgets import (
    QWidget,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout
)

# project imports
import unichat.db as db
from unichat.widgets.contact_list.contact_item_widget import ContactItemWidget
from unichat.widgets.dialogs.add_contact_dialog import AddContactDialog


class ContactListWidget(QWidget):
    """
    display of unichat contacts on the left side of the main window

    """

    def __init__(self, parent=None):
        """
        contact list widget constructor
        """
        super().__init__(parent=parent)
        self.list_widget = QListWidget()
        self.list_widget.setMinimumHeight(650)
        self.new_contact_button = QPushButton('Add new Contact')
        self.new_contact_button.clicked.connect(self.open_add_contact_dialog)
        self.init_ui()

    def init_ui(self):
        """
        The `init_ui` function sets up the user interface layout by adding a 
        list widget and a new contact button to a vertical layout.
        """
        layout = QVBoxLayout()
        layout.addWidget(self.list_widget)
        layout.addWidget(self.new_contact_button)
        self.setLayout(layout)
        self.init_contact_list()

    def refresh_contact_list(self):
        """
        The function `refresh_contact_list` clears the list widget and 
        initializes the contact list.
        """
        self.list_widget.clear()
        self.init_contact_list()

    def init_contact_list(self):
        """
        The `init_contact_list` function populates a list of widgets with 
        items representing contacts retrieved from a database.
        """
        for contact in db.Contact.select():
            self.add_contact_to_list(contact)

    def open_add_contact_dialog(self):
        """
        The function `open_add_contact_window` creates and displays a 
        dialog window for adding a new contact.
        """
        add_contact_dialog = AddContactDialog()
        if add_contact_dialog.exec():
            self.add_contact_to_list(add_contact_dialog.new_contact)

    def add_contact_to_list(self, contact):
        """
        The function adds a contact item to a list widget in a PyQt 
        application.
        
        :param contact: It looks like the `add_contact_to_list` method is used
        to add a contact to a list widget in a graphical user interface. The 
        `contact` parameter seems to represent the
        contact information that you want to add to the list
        """
        item = QListWidgetItem()
        contact_item = ContactItemWidget(contact)
        contact_item.contact_removed.connect(self.refresh_contact_list)
        item.setSizeHint(contact_item.sizeHint())
        item.setData(101, contact_item)
        self.list_widget.addItem(item)
        self.list_widget.setItemWidget(item, contact_item)
