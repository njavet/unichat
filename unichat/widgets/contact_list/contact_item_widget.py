# external imports
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QPainter, QBrush
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QHBoxLayout,
    QSizePolicy,
)

# project imports
import unichat.db as db
from unichat.widgets.dialogs.remove_contact_dialog import RemoveContactDialog


class ContactItemWidget(QWidget):
    contact_removed = Signal(str)

    """
    widget with a profile pic and a name that will be displayed
    on the left side (contact list)
    """

    def __init__(self, contact: db.Contact):
        """
        contact item widget constructor
        """
        super().__init__()
        self.contact = contact
        self.init_ui()

    def init_ui(self):
        """
        The `init_ui` function sets up a user interface layout with an 
        image and text for a contact.
        """
        layout = QHBoxLayout()
        pixmap = QPixmap(self.contact.profile_pic_path)
        pixmap = pixmap.scaledToWidth(50)
        rounded_pixmap = self.round_pixmap(pixmap)
        label_image = QLabel()
        label_image.setPixmap(rounded_pixmap)
        label_image.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        layout.addWidget(label_image)
        label_text = QLabel(self.contact.name)
        layout.addWidget(label_text)
        layout.setContentsMargins(1, 1, 0, 0)
        self.setLayout(layout)

    @staticmethod
    def round_pixmap(pixmap):
        """
        The `round_pixmap` function takes a `pixmap` image, rounds its corners
        with antialiasing, and returns the rounded image as a new `QPixmap`.
        
        :param pixmap: The `pixmap` parameter in the `round_pixmap` method is 
        expected to be an instance of the QPixmap class. This method takes a 
        QPixmap object, creates a new QPixmap with rounded corners based on 
        the input pixmap, and returns the rounded QPixmap
        :return: The `round_pixmap` method returns a rounded version of the 
        input `pixmap`. It creates a new `QPixmap` object with the same size 
        as the input pixmap, fills it with a transparent color,
        and then draws a rounded rectangle using antialiasing to create a 
        rounded effect. Finally, it returns the rounded pixmap.
        """
        rounded_pixmap = QPixmap(pixmap.size())
        rounded_pixmap.fill(Qt.transparent)
        painter = QPainter(rounded_pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rounded_rect = pixmap.rect().adjusted(1, 1, -1, -1)
        painter.setBrush(QBrush(pixmap))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rounded_rect, 50, 50)
        painter.end()
        return rounded_pixmap

    def mousePressEvent(self, event):
        """ handle right click for contact removal """
        if event.button() == Qt.RightButton:
            rd = RemoveContactDialog(self.contact)
            if rd.exec():
                self.contact_removed.emit(self.contact.name)
        else:
            super().mousePressEvent(event)
