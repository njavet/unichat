"""
Here we have an async telethon client that will run in a
separate QThread. So we have a separate event loop to the
QT app event loop. This is for fetching incoming telegram
messages

"""
import asyncio
import os

# external imports
from PySide6.QtCore import QObject, Signal
from dotenv import load_dotenv
from telethon import TelegramClient, events

# project imports
import unichat.config as config
import unichat.helpers as helpers


class AsyncTelegramClientWorker(QObject):
    """
    wrapper around the async telethon client with
    a message handler for incoming telegram messages.
    When a message is received the object will emit a
    signal so the main app can process the message.

    """
    msg_receive_signal = Signal(events.newmessage.NewMessage)
    finished = Signal()

    def __init__(self):
        """
        async telegram client worker constructor
        """
        super().__init__()
        # load telegram api keys
        load_dotenv()
        self.api_id = int(os.getenv('API_ID'))
        self.api_hash = os.getenv('API_HASH')
        self.telethon_client = self.init_telethon_client()

    def init_telethon_client(self):
        """
        asyncio event loop
        """
        session = os.path.join(helpers.get_user_data_dir_path(),
                               config.telegram_async_session)
        telethon_client = TelegramClient(session=session,
                                         api_id=self.api_id,
                                         api_hash=self.api_hash)

        telethon_client.add_event_handler(self.msg_handler,
                                          events.newmessage.NewMessage(incoming=True))
        telethon_client.add_event_handler(self.msg_handler,
                                          events.newmessage.NewMessage(outgoing=True))

        return telethon_client

    async def msg_handler(self, event):
        """
        telegram message event handler, called when a
        new message arrives.
        returns a telethon message object
        """
        self.msg_receive_signal.emit(event.message)

    def run(self):
        """
        called from the qt app
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self.telethon_client.start()

        with self.telethon_client:
            self.telethon_client.run_until_disconnected()

        self.finished.emit()
