import os
from datetime import datetime

# external imports
import pytz
import telethon
from dotenv import load_dotenv
from telethon.sync import TelegramClient
from telethon.types import Message, InputFile

# project imports
import unichat.clients.telegram_client.telegram_db as tdb
import unichat.config as config
import unichat.db as db
import unichat.helpers as helpers
from unichat.clients.chat_client import ChatClient


class SyncTelegramClient(ChatClient, TelegramClient):
    """
    multiple inheritance, so the sync client inherits from the telethon
    client and also from our abstract class
    """
    session = 'telethon_sync'

    def __init__(self, name='telegram'):
        """ constructor """
        db.init_database(models=[tdb.TelegramContact])
        load_dotenv()
        # call the ChatClient constructor
        super().__init__(name)
        self.user_data_dir_path = helpers.get_user_data_dir_path()
        session = os.path.join(self.user_data_dir_path,
                               config.telegram_sync_session)
        # call the sync.TelegramClient constructor
        super(TelegramClient, self).__init__(
            session=session,
            api_id=os.getenv('API_ID'),
            api_hash=os.getenv('API_HASH')
        )
        self.connect()
        self.unichat_me = db.get_unichat_me()

    def login(self, phone_number, auth_code, password=None) -> bool:
        """
        login to the telegram client, returns `telegram_me` on success, None
        otherwise.
        """
        if password:
            self.sign_in(phone=phone_number,
                         code=auth_code,
                         password=password)
        else:
            self.sign_in(phone=phone_number,
                         code=auth_code)
        self.unichat_me = db.get_unichat_me()
        tg_me = self.link_to_unichat_account(self.get_me(), self.unichat_me)
        return tg_me is not None

    def is_logged_in(self) -> bool:
        """
        check if the user is logged in with the telethon function
        """
        return self.is_user_authorized()

    def is_initiated(self, contact: db.Contact) -> bool:
        """
        check if the owner telegram user db entry exists

        """
        return True if tdb.get_telegram_contact(contact) else False

    def link_to_unichat_account(self,
                                contact,
                                unichat_contact: db.Contact,
                                *args):
        """
        create a telegram user db entry that is linked to the main unichat account
        """
        tg_contact = tdb.TelegramContact.create(user_id=contact.id,
                                                first_name=contact.first_name,
                                                last_name=contact.last_name,
                                                username=contact.username,
                                                contact=unichat_contact)
        pic_path = str(contact.id) + '.jpg'
        file_path = os.path.join(self.user_data_dir_path, pic_path)
        new_path = self.download_profile_photo(contact.id, file=file_path)
        if new_path:
            unichat_contact.profile_pic_path = new_path
            unichat_contact.save()
        return tg_contact

    def save_message(self, message: Message) -> db.UniChatMessage:
        """
        saves a telegram message object to a unichat message database entry
        """
        try:
            from_id = message.from_id.user_id
        except AttributeError:
            from_id = message.sender.id

        to_id = message.peer_id.user_id
        from_contact = tdb.get_contact_from_telegram_user_id(from_id)
        to_contact = tdb.get_contact_from_telegram_user_id(to_id)

        try:
            postfix = str(message.media.photo.id) + '.jpg'
            save_to_file_path = os.path.join(self.user_data_dir_path, postfix)
            photo_path = self.download_media(message=message.media,
                                             file=save_to_file_path)
        except AttributeError:
            photo_path = None

        timestamp = message.date.astimezone(pytz.timezone('CET'))
        unichat_message = db.UniChatMessage.create(from_contact=from_contact,
                                                   to_contact=to_contact,
                                                   chat_client=self.name,
                                                   text=message.message,
                                                   photo_path=photo_path,
                                                   timestamp=timestamp)
        return unichat_message

    def get_active_chats(self):
        """
        returns a list of all active telegram chats of the user
        """
        active_chats = []
        for dialog in self.get_dialogs():
            if dialog.is_user:
                entity = self.get_entity(dialog)
                active_chats.append((dialog.name, entity))
        return active_chats

    def get_all_messages(self, contact):
        """
        returns a list of `limit` number of messages from a chat with `contact`
        """
        return self.get_messages(contact, limit=64)

    def _save_outgoing_text_message(self, to_contact: db.Contact, text: str):
        """
        helper function for saving an outgoing text message
        """
        ucm = db.UniChatMessage.create(from_contact=db.get_unichat_me(),
                                       to_contact=to_contact,
                                       chat_client=self.name,
                                       text=text,
                                       timestamp=datetime.now())
        return ucm

    def _save_outgoing_photo_message(self, to_contact: db.Contact, photo_path: str):
        """
        helper function for saving an outgoing photo message

        """
        ucm = db.UniChatMessage.create(from_contact=db.get_unichat_me(),
                                       to_contact=to_contact,
                                       chat_client=self.name,
                                       photo_path=photo_path,
                                       timestamp=datetime.now())
        return ucm

    def send_text_message(self, to_contact: db.Contact, text: str):
        """
        sends a text message, returns the message on success
        """
        tg_contact = tdb.get_telegram_contact(to_contact)
        try:
            self.send_message(entity=tg_contact.user_id,
                              message=text)
        except telethon.errors.rpcerrorlist.UserIsBotError:
            # TODO fix this
            pass
        except ValueError:
            # TODO this too
            pass

    def send_photo_message(self, to_contact: db.Contact, file: InputFile):
        """
        sends a png image file, returns the message on success
        """
        tg_contact = tdb.get_telegram_contact(to_contact)
        message = self.send_message(tg_contact.user_id, file=file)
        # successfully sent message will be returned TODO exception handling
        postfix = str(message.media.photo.id) + '.jpg'
        save_to_file_path = os.path.join(self.user_data_dir_path, postfix)
        photo_path = self.download_media(message=message.media,
                                         file=save_to_file_path)
        ucm = self._save_outgoing_photo_message(to_contact=to_contact,
                                                photo_path=photo_path)
        return ucm
