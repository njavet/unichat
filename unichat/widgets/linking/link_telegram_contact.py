# project imports
from unichat.widgets.linking.link_contact_widget import LinkContact


class LinkTelegramContact(LinkContact):
    def __init__(self, contact, chat_client):
        """
        link telegram contact constructor
        """
        super().__init__(contact, chat_client)

    def init_chat(self):
        """
        The `init_chat` function initializes the chat by populating a combo box with active chat
        contacts.
        """
        for t in self.chat_client.get_active_chats():
            self.possible_contacts[t[0]] = t
            self.combo_box.addItem(t[0])

    def link_contact(self):
        """
        The function `link_contact` links a contact to a UniChat account and saves all messages
        associated with that contact.
        """
        name = self.combo_box.currentText()
        _, entity = self.possible_contacts[name]
        self.chat_client.link_to_unichat_account(entity, self.contact)
        for msg in self.chat_client.get_all_messages(entity.id):
            self.chat_client.save_message(msg)
        self.linked_contact.emit(self.chat_client.name)
