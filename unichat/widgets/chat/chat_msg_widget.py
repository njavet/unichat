# external imports
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QGridLayout,
    QFrame
)

# project imports
import unichat.db as db
import unichat.helpers as helpers


class ChatMessageWidget(QWidget):
    """
    A ChatMessageWidget is the typical bubble with a message text.

    """

    def __init__(self, unichat_message: db.UniChatMessage):
        """
        chat message widget constructor
        """
        super().__init__()
        self.unichat_message = unichat_message
        self.from_me = self.unichat_message.from_contact.is_me
        self.message_frame = QFrame()
        self.message_label = QLabel()
        self.timestamp_label = QLabel()
        self.init_ui()

    def setup_frame(self):
        """
        frame for the message bubble

        """
        self.message_frame.setObjectName('MessageBubble')
        self.message_frame.setFrameStyle(QFrame.Box | QFrame.Plain)
        self.message_frame.setLineWidth(0)

    def setup_label(self):
        """
        creates text message bubble

        """
        self.message_label.setObjectName('MessageLabel')
        if self.unichat_message.text:
            msg_text = helpers.format_msg(self.unichat_message.text)
            self.message_label.setText(msg_text)
        elif self.unichat_message.photo_path:
            pixmap = QPixmap(self.unichat_message.photo_path)
            scaled_pixmap = pixmap.scaled(300, 300, aspectMode=Qt.KeepAspectRatio)
            self.message_label.setPixmap(scaled_pixmap)
        elif self.unichat_message.video_path:
            self.message_label.setText('[ Videos are not supported yet ]')
        else:
            self.message_label.setText('[ UNKNOWN MESSAGE TYPE ]')

    def setup_timestamp(self):
        """
        constructs a timestamp under the message bubble

        """
        # this is needed because SQLite saved timestamps as strings
        try:
            # timestamp is a datetime object
            timestamp = self.unichat_message.timestamp.strftime('%H:%M')
        except AttributeError:
            # timestamp is a string from the db
            timestamp = self.unichat_message.timestamp[11:16]

        self.timestamp_label.setText(timestamp)
        self.timestamp_label.setObjectName('TimestampLabel')
        self.timestamp_label.setAlignment(Qt.AlignRight)
        font = QFont()
        font.setPointSizeF(7)
        self.timestamp_label.setFont(font)

    def init_ui(self):
        """
        The `init_ui` function sets up the user interface for displaying 
        chat messages with timestamps and alignment based on the sender.
        """
        layout = QGridLayout()
        self.setup_frame()
        self.setup_label()
        self.setup_timestamp()

        if self.from_me:
            self.message_frame.setProperty('status',
                                           self.unichat_message.chat_client)
            self.message_label.setProperty('status',
                                           self.unichat_message.chat_client)
            alignment = Qt.AlignRight
        else:
            self.message_frame.setProperty('status', 'contact')
            self.message_label.setProperty('status', 'contact')
            alignment = Qt.AlignLeft

        self.message_label.setAlignment(alignment)
        message_frame_layout = QGridLayout()
        message_frame_layout.addWidget(self.message_label)
        message_frame_layout.addWidget(self.timestamp_label)
        self.message_frame.setLayout(message_frame_layout)
        layout.addWidget(self.message_frame, 0, 0, alignment=alignment)
        layout.setContentsMargins(1, 1, 1, 1)
        self.setLayout(layout)
