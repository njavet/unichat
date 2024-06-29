import collections

# external imports
from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QWidget,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QFileDialog,
    QPushButton,
    QHBoxLayout,
    QSizePolicy
)

# project imports
import unichat.db as db
import unichat.helpers as helpers
from unichat.clients.chat_client import ChatClient
from unichat.widgets.chat.chat_msg_widget import ChatMessageWidget
from unichat.widgets.chat.date_bubble_widget import DateBubbleWidget


class ChatClientWidget(QWidget):
    """
    A ChatClientWidget is a container of a chat of a user from
    a single chat client.

    """

    def __init__(self, contact: db.Contact, chat_client: ChatClient):
        """
        ChatClientWidget constructor
        """
        super().__init__()
        self.contact = contact
        self.chat_client = chat_client
        self.me = db.get_unichat_me()
        self.chat_widget = QWidget()
        self.chat_message_history = QListWidget()
        self.send_file_button = QPushButton()
        self.chat_input = QLineEdit()
        self.init_ui()

    def init_ui(self):
        """
        init layout of the Chat Container
        """
        layout = QVBoxLayout(self)
        layout.addWidget(self.chat_widget)
        layout.addWidget(self.chat_message_history)

        # text input and send file button
        container_widget = QWidget()
        input_layout = QHBoxLayout()

        self.send_file_button.setIcon(QIcon(helpers.get_icon_path('send_photo.png')))
        self.send_file_button.setIconSize(QSize(32, 32))
        self.send_file_button.setFixedSize(32, 32)
        self.send_file_button.clicked.connect(self.launch_send_photo_message_process)
        input_layout.addWidget(self.send_file_button)
        self.chat_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.chat_input.setPlaceholderText('Write a message...')
        self.chat_input.returnPressed.connect(self.launch_send_text_message_process)
        input_layout.addWidget(self.chat_input)
        container_widget.setLayout(input_layout)
        layout.addWidget(container_widget)

        self.init_chat_display()

    def launch_send_text_message_process(self):
        """
        function for preparing the send message process:
        get the text from the input widget,
        send the message via the specific chat client
        add the message to the chat history in the GUI
        clear the input field
        """
        text = self.chat_input.text()
        self.chat_client.send_text_message(self.contact, text)
        self.chat_input.clear()

    def launch_send_photo_message_process(self):
        """
        function for preparing the send photo process:
        select the photo file from the file dialog
        send the photo via the specific chat client
        add the photo to the chat history in the GUI

        """
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        file_dialog = QFileDialog()
        file_dialog.setNameFilter('Images (*.png *.jpg *.jpeg)')
        file_dialog.setViewMode(QFileDialog.List)
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                photo = self.chat_client.upload_file(selected_files[0])
                ucm = self.chat_client.send_photo_message(self.contact, photo)
                self.add_message_to_chat_history(ucm)
                self._scroll_to_last_message()

    def _scroll_to_last_message(self):
        """
        scrolling to the last message in the chat history

        """
        item_count = self.chat_message_history.count()
        last_item = self.chat_message_history.item(item_count - 1)
        self.chat_message_history.scrollToItem(last_item)

    def init_chat_display(self):
        """
        loads messages from the contact from the database and
        sets up the chat history in the GUI

        """
        self.chat_message_history.clear()
        messages = self.load_messages()
        dates = collections.defaultdict(int)
        for ucm in messages:
            date = helpers.convert_timestamp_to_date(ucm.timestamp)
            # insert 'date' to the chat history
            if dates[date] == 0:
                self.insert_day_separator(date)
            dates[date] += 1
            self.add_message_to_chat_history(ucm)
        vb = self.chat_message_history.verticalScrollBar()
        self.chat_message_history.verticalScrollBar().setValue(vb.maximum())
        self._scroll_to_last_message()
        self.setContentsMargins(2, 2, 3, 4)

    def insert_day_separator(self, day):
        """
        inserts a date bubble so the user can see the date of
        the messages.

        """
        list_item = QListWidgetItem(self.chat_message_history)
        date_widget = DateBubbleWidget(day)
        list_item.setSizeHint(date_widget.sizeHint())
        self.chat_message_history.addItem(list_item)
        self.chat_message_history.setItemWidget(list_item, date_widget)

    def add_message_to_chat_history(self, unichat_message: db.UniChatMessage):
        """
        adds a single message to the chat history

        """
        list_item = QListWidgetItem(self.chat_message_history)
        message_widget = ChatMessageWidget(unichat_message)
        list_item.setSizeHint(message_widget.sizeHint())
        self.chat_message_history.addItem(list_item)
        self.chat_message_history.setItemWidget(list_item, message_widget)
        self._scroll_to_last_message()

    def load_messages(self):
        """
        This function loads messages based on the contact,
        filtering by whether the contact is the user or not.
        :return: The `load_messages` method returns a result containing
        UniChatMessage objects based on the conditions specified in the method.
        If the contact is the user themselves (is_me), it retrieves messages
        where the from_contact and to_contact are the same contact and orders them
        by timestamp. If the contact is not the user, it retrieves messages
        where the contact is either the from_contact or the to_contact and orders
        """
        if self.contact.is_me:
            messages = (db.UniChatMessage
                        .select()
                        .where((db.UniChatMessage.from_contact == self.contact) &
                               (db.UniChatMessage.to_contact == self.contact) &
                               (db.UniChatMessage.chat_client == self.chat_client.name))
                        .order_by(db.UniChatMessage.timestamp))
        else:
            messages = (db.UniChatMessage
                        .select()
                        .where(((db.UniChatMessage.from_contact == self.contact) |
                                (db.UniChatMessage.to_contact == self.contact)) &
                               (db.UniChatMessage.chat_client == self.chat_client.name))
                        .order_by(db.UniChatMessage.timestamp))
        return messages
