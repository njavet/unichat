"""
entry point to the app
"""
import sys
import logging
import traceback

# external imports
import telethon.tl.custom.message
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QStackedWidget,
    QHBoxLayout,
)

# project imports
import unichat.db as db
from unichat.clients.telegram_client.telegram_client import SyncTelegramClient
from unichat.clients.whatsapp_client.whatsapp_client import WhatsAppClient
from unichat.config import WINDOW_WIDTH, WINDOW_HEIGHT
from unichat.driver_manager import DriverManager
from unichat.helpers import load_stylesheet, get_log_file_path
from unichat.widgets.chat.chat_container_widget import ChatContainerWidget
from unichat.widgets.contact_list.contact_list_widget import ContactListWidget
from unichat.widgets.dialogs.sign_up_dialog import SignUpDialog
from unichat.workers.chat_client_worker import ChatClientWorker
from unichat.workers.telegram_async_worker import AsyncTelegramClientWorker
from unichat.workers.whatsapp_worker import WhatsappAsyncFetcherWorker

# initialize logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename=get_log_file_path(),
    filemode='w'
)

class UniChat(QMainWindow):
    """
    app window. opens per default with the chat window, a user can
    add clients and log into them with the 'add_client_action'
    """

    def __init__(self):
        """
        QMainWindow constructor
        """
        super().__init__()
        # unichat code
        db.init_storage()
        # contacts is used for tab switching and maps contact name to indexes
        self.contacts: dict = {}
        # chats maps the contact name to the chat container
        self.chats: dict = {}

        # telegram code
        self.sync_telegram_client = SyncTelegramClient()
        self.async_telegram_client = None
        self.telethon_thread = None
        self.init_telegram_event_loop()

        # selenium driver code
        self.selenium_driver_manager = DriverManager()

        # whatsapp code
        self.sync_whatsapp_client = WhatsAppClient(self.selenium_driver_manager)
        self.async_whatsapp_target = None
        self.async_whatsapp_fetcher = ChatClientWorker(
            worker=WhatsappAsyncFetcherWorker(self.sync_whatsapp_client, self.async_whatsapp_target),
            sub_func=self.handle_whatsapp_recv_msg
        )
        self.async_whatsapp_fetcher.execute_async_worker()

        # gui code
        self.central_widget = QWidget()
        self.contact_list = ContactListWidget()
        self.chat_containers = QStackedWidget()
        self.init_ui()

    def init_ui(self):
        """
        sets up the layout of the main window
        """
        # title and placement
        self.setWindowTitle('UniChat')
        self.setGeometry(100, 100, WINDOW_WIDTH, WINDOW_HEIGHT)

        # unichat icon
        icon = QIcon()
        icon.addFile('assets/icons/unichat_logo_window_icon.png')
        self.setWindowIcon(icon)

        # main window central widget
        self.setCentralWidget(self.central_widget)
        layout = QHBoxLayout(self.central_widget)
        self.contact_list.list_widget.itemClicked.connect(
            self.handle_contact_list_signal
        )
        layout.addWidget(self.contact_list)
        self.contact_list.setMinimumWidth(300)
        self.contact_list.setMaximumWidth(300)
        layout.addWidget(self.chat_containers)
        self.setLayout(layout)

        if not db.get_unichat_me():
            sign_up_dialog = SignUpDialog()
            sign_up_dialog.resize(self.size())
            if sign_up_dialog.exec():
                self.contact_list.add_contact_to_list(sign_up_dialog.me)
            else:
                sys.exit(0)

    def setup_chats(self, contact):
        """
        sets up datastructures for the chat widgets

        """
        self.contacts[contact.name] = len(self.contacts)
        chat_clients = [self.sync_telegram_client,
                        self.sync_whatsapp_client]
        self.chats[contact.name] = ChatContainerWidget(contact, chat_clients)
        self.chat_containers.addWidget(self.chats[contact.name])
        self.chats[contact.name].profile_pic_update.connect(
            self.contact_list.refresh_contact_list
        )

    def handle_contact_list_signal(self, contact_item):
        """
        event handler for reacting to mouse clicks on contact items

        """
        contact = contact_item.data(101).contact
        if contact.name not in self.chats:
            self.setup_chats(contact)

        self.start_whatsapp_async_fetcher(contact)

        ind = self.contacts[contact.name]
        self.chat_containers.setCurrentIndex(ind)

    def start_whatsapp_async_fetcher(self, contact):
        """
        starts the whatsapp async fetcher.
        dynamically changes target, depending on which contact has been switched to.
        """
        # Change target if the new target chat is initialized and linked
        if (not contact.is_me
                and (self.async_whatsapp_target != contact)
                and (self.sync_whatsapp_client.is_initiated(contact)
                     and self.sync_whatsapp_client.is_unichat_contact_linked(contact))):
            self.async_whatsapp_target = contact
            self.async_whatsapp_fetcher.change_target(self.async_whatsapp_target)

        # Change target to None, such that the fetcher is idle
        elif (contact.is_me
              or (self.async_whatsapp_target != contact
                  and not (self.sync_whatsapp_client.is_initiated(contact)
                           and self.sync_whatsapp_client.is_unichat_contact_linked(contact)))):
            self.async_whatsapp_target = None
            self.async_whatsapp_fetcher.change_target(self.async_whatsapp_target)

    def handle_whatsapp_recv_msg(self, unichat_messages: list[db.UniChatMessage]):
        """ handler for incoming whatsapp messages """
        try:
            for uc_msg in unichat_messages:
                chat_contact = uc_msg.from_contact if uc_msg.to_contact == db.get_unichat_me() else uc_msg.to_contact
                self.chats[chat_contact.name].update_chat_history(uc_msg, 'whatsapp')
        except Exception as e:
            logging.error(traceback.format_exc())

    def init_telegram_event_loop(self):
        """
        setup Qthread with the async telegram client
        """

        self.async_telegram_client = ChatClientWorker(
            worker=AsyncTelegramClientWorker(),
            sub_func=self.handle_telegram_recv_msg
        )
        self.async_telegram_client.execute_async_worker()

    def handle_telegram_recv_msg(self, message: telethon.tl.custom.message.Message):
        """ handler for incoming telegram messages """
        try:
            uc_msg = self.sync_telegram_client.save_message(message)
            chat_contact = uc_msg.from_contact if uc_msg.to_contact == db.get_unichat_me() else uc_msg.to_contact
            self.chats[chat_contact.name].update_chat_history(uc_msg, 'telegram')
        except Exception as e:
            logging.error(traceback.format_exc())

    def close_event(self, event):
        """ clean up code for selenium driver and async workers"""
        self.async_whatsapp_fetcher.stop_worker()
        self.selenium_driver_manager.close_driver()
        # Accept the close event to proceed with closing the window
        event.accept()


def run_app():
    app = QApplication(sys.argv)
    app.setStyleSheet(load_stylesheet('main.qss'))
    try:
        unichat = UniChat()
    except ValueError:
        print('you have to create an .env file with credentials')
        sys.exit(1)
    unichat.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    run_app()

