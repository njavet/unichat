# project imports
from unichat.widgets.linking.link_contact_widget import LinkContact
from unichat.workers.chat_client_worker import ChatClientWorker
from unichat.workers.whatsapp_worker import WhatsappLinkContactWorker, WhatsappLoadActiveChatsWorker


class LinkWhatsAppContact(LinkContact):
    def __init__(self, contact, chat_client):
        """
        link whatsapp contact constructor
        """
        super().__init__(contact, chat_client)
        self.chat_client_worker = None
        self.load_worker = None
        self.link_worker = None

    def init_chat(self):
        """
        initializes chat
        """
        self.load_worker = WhatsappLoadActiveChatsWorker(
            client=self.chat_client
        )
        self.chat_client_worker = ChatClientWorker(
            worker=self.load_worker,
            sub_func=self.load_active_chats
        )
        self.chat_client_worker.execute_worker()
        self.init_button.setDisabled(True)

    def load_active_chats(self, list_of_chats):
        """
        add active chats to the combobox
        """
        self.init_button.setDisabled(False)
        for chat_name in list_of_chats:
            self.combo_box.addItem(chat_name)

    def link_contact(self):
        """
        The function `link_contact` links a contact to a UniChat account, 
        saves all messages associated with the contact, and emits a signal 
        with the linked contact's name.
        """
        chat_name = self.combo_box.currentText()
        self.link_worker = WhatsappLinkContactWorker(client=self.chat_client,
                                                     chat_name=chat_name,
                                                     unichat_contact=self.contact,
                                                     qt_signal=self.linked_contact)
        self.chat_client_worker = ChatClientWorker(worker=self.link_worker,
                                                   sub_func=self.enable_buttons)
        self.chat_client_worker.execute_worker()
        self.init_button.setDisabled(True)
        self.combo_box.setDisabled(True)
        self.choose_contact_button.setDisabled(True)

    def enable_buttons(self):
        self.init_button.setDisabled(False)
        self.combo_box.setDisabled(False)
        self.choose_contact_button.setDisabled(False)
