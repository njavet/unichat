# project imports
from unichat.widgets.linking.link_contact_widget import LinkContact


class LinkInstagramContact(LinkContact):
    def __init__(self, contact, chat_client):
        """
        link instagram contact constructor
        """
        super().__init__(contact, chat_client)
        self.chat_list = None

    def init_chat(self):
        """
        initializes chat
        """
        self.chat_list = self.chat_client.get_active_chats()
        for (name, url) in self.chat_list:
            self.combo_box.addItem(name)

    def link_contact(self):
        """
        The function `link_contact` links a contact to a UniChat account, 
        saves all messages associated with the contact, and emits a signal 
        with the linked contact's name.
        """
        chat_name = self.combo_box.currentText()
        for (name, url) in self.chat_list:
            if chat_name == name:
                self.chat_client.link_to_unichat_account(name, self.contact, url)
                for msg in self.chat_client.get_all_messages(name, url):
                    self.chat_client.save_message(msg)
