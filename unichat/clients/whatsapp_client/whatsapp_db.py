import logging

# external imports
import peewee as pw

# project imports
import unichat.db as db


class WhatsAppContact(db.BaseModel):
    """ db table for a whatsapp contact """
    phone_nr = pw.CharField()
    chat_name = pw.CharField()
    is_linked = pw.BooleanField()
    contact = pw.ForeignKeyField(db.Contact, on_delete='CASCADE')


def get_whatsapp_me() -> WhatsAppContact | None:
    """ returns whatsapp me """
    me = (WhatsAppContact
          .select(db.Contact, WhatsAppContact)
          .join(db.Contact)
          .where(db.Contact.is_me))
    try:
        return me.get()
    except pw.DoesNotExist as e:
        logging.info(f'get Whatsapp me failed: {e}')
        return None


def get_whatsapp_contact(contact: db.Contact) -> WhatsAppContact | None:
    """
    return the unichat contacts linked whatsapp contact if it exists

    """

    wa_contact = (WhatsAppContact
                  .select()
                  .join(db.Contact)
                  .where(WhatsAppContact.contact == contact))
    try:
        return wa_contact.get()
    except pw.DoesNotExist:
        return None


def get_contact_from_whatsapp_name(contact_name: str) -> db.Contact:
    """ returns whatsapp contact with `contact_name` """
    contact = (db.Contact
               .select(db.Contact, WhatsAppContact)
               .join(WhatsAppContact, on=(db.Contact.name == WhatsAppContact.contact))
               .where(WhatsAppContact.chat_name == contact_name))
    return contact.get()
