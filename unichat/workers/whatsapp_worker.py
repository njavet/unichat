import time

# external imports
from PySide6.QtCore import QObject, Signal

# project imports
import unichat.clients.whatsapp_client.whatsapp_db as wdb
import unichat.db as db
from unichat.clients.chat_client import ChatClient


class WhatsappQrCodeWorker(QObject):
    """QObject worker to receive the QR-Code from the Whatsapp WebClient."""
    finished = Signal(str)

    def __init__(self, client: ChatClient) -> None:
        """
        constructor
        """
        super().__init__()
        self.client = client

    def run(self) -> None:
        """
        runs worker

        """
        data = self.client.get_qr_code()
        self.finished.emit(data)


class WhatsappLoginWorker(QObject):
    """QObject worker to check whether the user has logged in successfully."""
    finished = Signal(bool)

    def __init__(self, client: ChatClient) -> None:
        """
        constructor
        """
        super().__init__()
        self.client = client

    def run(self) -> None:
        """
        runs worker
        """
        success = self.client.login()
        self.finished.emit(success)


class WhatsappLoadActiveChatsWorker(QObject):
    finished = Signal(list)

    def __init__(self, client: ChatClient) -> None:
        """ constructor """
        super().__init__()
        self.client = client

    def run(self):
        """ runs worker """
        active_chats = self.client.get_active_chats()
        self.finished.emit(active_chats)


class WhatsappLinkContactWorker(QObject):
    """QObject worker to link a given chat to the unichat contact and download the chat history from Whatsapp"""
    finished = Signal(bool)

    def __init__(self, client: ChatClient, chat_name: str, unichat_contact: db.Contact, qt_signal: Signal) -> None:
        """ constructor """
        super().__init__()
        self.client = client
        self.chat_name = chat_name
        self.unichat_contact = unichat_contact
        self.qt_signal = qt_signal

    def run(self):
        """ runs worker """
        whatsapp_contact: wdb.WhatsAppContact = self.client.link_to_unichat_account(self.chat_name,
                                                                                    self.unichat_contact)

        for msg in self.client.get_all_messages(self.chat_name):
            self.client.save_message(msg)
        self.qt_signal.emit(self.client.name)
        whatsapp_contact.is_linked = True
        whatsapp_contact.save()
        self.finished.emit(True)


class WhatsappAsyncFetcherWorker(QObject):
    """QObject worker to constantly fetch the newest chat history from Whatsapp and store it in the database"""
    finished = Signal(bool)
    msg_receive_signal = Signal(list)

    def __init__(self,
                 client: ChatClient,
                 unichat_contact: db.Contact | None,
                 interval_in_sec: int = 0.5) -> None:
        super().__init__()
        self.client = client
        self.unichat_contact = unichat_contact
        self.chat_name = ""
        self.change_target(unichat_contact)
        self.interval_in_sec = interval_in_sec
        self._is_running = True

    def run(self):
        while self._is_running:
            time.sleep(self.interval_in_sec)
            if self.chat_name:
                latest_messages = self.client.get_latest_messages(self.chat_name)
                if latest_messages:
                    unichat_messages = []
                    for msg in latest_messages:
                        unichat_messages.append(self.client.save_message(msg))
                    self.msg_receive_signal.emit(unichat_messages)
        self.finished.emit(True)

    def stop(self):
        self._is_running = False

    def change_target(self, contact: db.Contact | None) -> None:
        self.unichat_contact = contact
        self.chat_name = wdb.get_whatsapp_contact(contact).chat_name if wdb.get_whatsapp_contact(
            contact) else None
