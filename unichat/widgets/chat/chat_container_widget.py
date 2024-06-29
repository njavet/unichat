# external imports
from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QWidget,
    QTabWidget,
    QVBoxLayout,
)

# project imports
import unichat.db as db
from unichat.clients.chat_client import ChatClient
from unichat.widgets.chat.chat_client_widget import ChatClientWidget
from unichat.widgets.linking.link_instagram_contact import LinkInstagramContact
from unichat.widgets.linking.link_telegram_contact import LinkTelegramContact
from unichat.widgets.linking.link_whatsapp_contact import LinkWhatsAppContact
from unichat.widgets.login.instagram_login import InstagramClientLogin
from unichat.widgets.login.telegram_login import TelegramClientLogin
from unichat.widgets.login.whatsapp_login import WhatsappClientLogin


class ChatContainerWidget(QWidget):
    """
    The ChatContainer widget is a container for every unichat
    contact and contains tabbed widgets which are containers for
    the supported chat clients
    """
    profile_pic_update = Signal()

    def __init__(self, contact: db.Contact, chat_clients: list[ChatClient]):
        """
        ChatContainer Widget constructor
        """
        super().__init__()
        self.contact = contact
        self.chat_clients = chat_clients
        self.client_name2client: dict = {}
        self.client_name2widget_index: dict = {}
        self.tab_widget = QTabWidget()
        self.init_ui()

    def init_ui(self):
        """
        The `init_ui` function sets up the user interface by adding tabs for 
        different chat clients and connecting signals to initialize chat 
        functionality.
        """
        layout = QVBoxLayout(self)
        layout.addWidget(self.tab_widget)
        for i, chat_client in enumerate(self.chat_clients):
            self.client_name2widget_index[chat_client.name] = i
            self.client_name2client[chat_client.name] = chat_client
            # the user is not logged into the specific chat client yet
            if not chat_client.is_logged_in():
                if chat_client.name == 'telegram':
                    tab = TelegramClientLogin(chat_client)
                elif chat_client.name == 'whatsapp':
                    tab = WhatsappClientLogin(chat_client)
                else:
                    tab = InstagramClientLogin(chat_client)
                tab.logged_in.connect(self.init_linking)
                self.tab_widget.addTab(tab, chat_client.name)
            # the user is logged in, but the specific contact is not linked yet
            elif not chat_client.is_initiated(self.contact):
                if chat_client.name == 'telegram':
                    tab = LinkTelegramContact(self.contact, chat_client)
                elif chat_client.name == 'whatsapp':
                    tab = LinkWhatsAppContact(self.contact, chat_client)
                else:
                    tab = LinkInstagramContact(self.contact, chat_client)
                tab.linked_contact.connect(self.init_chat)
                self.tab_widget.addTab(tab, chat_client.name)
            # the user is logged in and the contact is linked
            else:
                tab = ChatClientWidget(self.contact, chat_client)
                self.tab_widget.addTab(tab, chat_client.name)
        self.tab_widget.setCurrentWidget(self.tab_widget.widget(0))

    def init_linking(self, chat_client_name):
        """
        sets up the contact linking widget
        """
        chat_client = self.client_name2client[chat_client_name]
        if chat_client_name == 'telegram':
            self.profile_pic_update.emit()
            tab = LinkTelegramContact(self.contact, chat_client)
        elif chat_client.name == 'whatsapp':
            tab = LinkWhatsAppContact(self.contact, chat_client)
        else:
            tab = LinkInstagramContact(self.contact, chat_client)
        i = self.client_name2widget_index[chat_client_name]
        self.tab_widget.removeTab(i)
        self.tab_widget.insertTab(i, tab, chat_client_name)
        self.tab_widget.setCurrentWidget(self.tab_widget.widget(i))

    def init_chat(self, chat_client_name):
        """
        The function initializes a chat client widget based on the specified 
        chat client name.
        
        :param chat_client_name: The `chat_client_name` parameter is a string 
        that represents the name of the chat client being initialized. In the 
        provided code snippet, the function `init_chat`
        uses this parameter to determine the type of chat client being 
        initialized (e.g., 'telegram') and perform specific actions based on 
        the client
        """
        if chat_client_name == 'telegram':
            self.profile_pic_update.emit()
        i = self.client_name2widget_index[chat_client_name]
        chat_client = self.client_name2client[chat_client_name]
        tab = ChatClientWidget(self.contact, chat_client)
        self.tab_widget.removeTab(i)
        self.tab_widget.insertTab(i, tab, chat_client_name)
        self.tab_widget.setCurrentWidget(self.tab_widget.widget(i))

    def update_chat_history(self, ucm: db.UniChatMessage, chat_client_name: str):
        """
        This function updates the chat history display in a Telegram widget 
        with a new UniChatMessage.
        
        :param ucm: The `unichat_message` parameter is an instance
        of the `UniChatMessage` class from the `db` module. It is used to 
        represent a message in a chat conversation
        :param chat_client_name: name of the client
        """
        index = self.client_name2widget_index[chat_client_name]
        self.tab_widget.widget(index).add_message_to_chat_history(ucm)

