import logging

# external imports
import peewee as pw

# project imports
import unichat.db as db


class InstagramContact(db.BaseModel):
    """ db table for instagram contacts """
    web_link = pw.CharField()
    chat_name = pw.CharField()
    contact = pw.ForeignKeyField(db.Contact, on_delete='CASCADE')


def get_instagram_me() -> InstagramContact | None:
    """ returns instagram me """
    me = (InstagramContact
          .select(db.Contact, InstagramContact)
          .join(db.Contact)
          .where(db.Contact.is_me))
    try:
        return me.get()
    except pw.DoesNotExist as e:
        logging.info(f'get instagram me failed: {e}')
        return None


def get_instagram_contact(contact: db.Contact) -> InstagramContact | None:
    """
    return the unichat contacts linked instagram contact if it exists
    """

    in_contact = (InstagramContact
                  .select()
                  .join(db.Contact)
                  .where(InstagramContact.contact == contact))
    try:
        return in_contact.get()
    except pw.DoesNotExist:
        return None


def get_contact_from_instagram_name(contact_name: str) -> db.Contact:
    """ returns contact with `contact_name` """
    contact = (db.Contact
               .select(db.Contact, InstagramContact)
               .join(InstagramContact, on=(db.Contact.name == InstagramContact.contact))
               .where(InstagramContact.chat_name == contact_name))
    return contact.get()
