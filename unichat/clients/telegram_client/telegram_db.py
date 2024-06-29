import logging

# external imports
import peewee as pw

# project imports
import unichat.db as db


class TelegramContact(db.BaseModel):
    """
    represents a telegram contact and contains the fields that
    are provided by telethon / telegram API
    needs a unichat contact as foreign key
    """
    # user_id provided by telegram, will be unique
    user_id = pw.IntegerField(primary_key=True)
    # name that the user has entered for the telegram contact
    first_name = pw.CharField()
    last_name = pw.CharField(null=True)
    # guaranteed to be unique username from telegram
    username = pw.CharField(null=True)
    contact = pw.ForeignKeyField(db.Contact, on_delete='CASCADE')


def get_telegram_me() -> db.Contact | None:
    """
    returns the join table of contact and telegram contact
    # NOTE -> to access the telegram contact, use e.g.:
    me.telegramcontact.user_id

    """
    me = (db.Contact
          .select(db.Contact, TelegramContact)
          .join(TelegramContact)
          .where(db.Contact.is_me))
    try:
        return me.get()
    except pw.DoesNotExist as e:
        logging.info(f'get telegram me failed: {e}')
        return None


def get_telegram_contact(contact: db.Contact) -> TelegramContact | None:
    """
    return the unichat contacts linked telegram contact if it exists

    """
    tg_contact = (TelegramContact
                  .select()
                  .join(db.Contact)
                  .where(TelegramContact.contact == contact))
    try:
        return tg_contact.get()
    except pw.DoesNotExist:
        return None


def get_contact_from_telegram_user_id(user_id: int) -> db.Contact:
    """
    direct access of the unichat contact object from the telegram
    user_id
    """
    contact = (db.Contact
               .select(db.Contact)
               .join(TelegramContact)
               .where(TelegramContact.user_id == user_id))
    return contact.get()
