from abc import ABC

# project imports
import unichat.db as db


class ChatClient(ABC):
    """
    abstract base class for chat clients
    """

    def __init__(self, name: str):
        """ constructor """
        self.name = name
        self.user_data_dir_path = None

    def login(self, *args) -> bool:
        """
        login to the client app

        """
        raise NotImplementedError

    def is_logged_in(self) -> bool:
        """
        return True if the owner is logged in the specific client,
        False otherwise
        """
        raise NotImplementedError

    def is_initiated(self, contact: db.Contact) -> bool:
        """
        return True if the contact is linked to the specific
        chat client, False otherwise
        """
        raise NotImplementedError

    def link_to_unichat_account(self, contact, unichat_contact: db.Contact, *args):
        """
        the account from the specific chat client needs to be linked to
        a unichat contact
        """
        raise NotImplementedError

    def get_active_chats(self):
        """
        returns a list of all active chats of the user
        """
        raise NotImplementedError

    def get_all_messages(self, *args):
        """
        returns a list of all messages from a chat with a specific contact
        """
        raise NotImplementedError

    def get_latest_messages(self, *args):
        """
        returns a list of the latest messages from a chat with a specific contact.
        only returns messages, which have not yet been stored in the database.
        """
        raise NotImplementedError

    def save_message(self, *args) -> db.UniChatMessage:
        """
        different clients have different message objects, so every client
        needs to construct and save a unichat message object
        """
        raise NotImplementedError

    def send_text_message(self, to_contact: db.Contact, text: str) -> None:
        """
        sends a text message to `to_contact`, returns the unichat message on success
        """
        raise NotImplementedError

    def send_photo_message(self, to_contact: db.Contact, photo_file: str):
        """
        sends a photo message to `to_contact`, returns the unichat message on success
        """
        raise NotImplementedError

    def send_video_message(self, to_contact: db.Contact, video_file: str):
        """
        sends a video message to `to_contact`, returns the unichat message on success
        """
        raise NotImplementedError
