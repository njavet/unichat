"""
base database models and functions
"""
import logging
import os
import sys

# external imports
import peewee as pw

# project imports
import unichat.config as config
import unichat.helpers as helpers


def get_database():
    """
    initiates and returns an SQLite database in the user data directory

    """
    user_data_dir_path = helpers.get_user_data_dir_path()
    db_path = os.path.join(user_data_dir_path, config.db_name)
    database = pw.SqliteDatabase(db_path, pragmas={
        'foreign_keys': 1,  # Enforce foreign-key constraints
    })
    return database


class BaseModel(pw.Model):
    """
    base model for all others
    """

    class Meta:
        """ database config """
        database = get_database()


class Contact(BaseModel):
    """ unichat contact (will include the user itself) """
    name = pw.CharField(primary_key=True)
    profile_pic_path = pw.CharField(default=helpers.get_image_path('default_profile_pic.png'))
    # field for determining if it is the owner
    is_me = pw.BooleanField(default=False)


class UniChatMessage(BaseModel):
    """
    this is the message object from unichat, how the
    chat messages are stored

    """
    from_contact = pw.ForeignKeyField(Contact, on_delete='CASCADE')
    to_contact = pw.ForeignKeyField(Contact, on_delete='CASCADE')
    chat_client = pw.CharField()
    text = pw.TextField(null=True)
    photo_path = pw.TextField(null=True)
    video_path = pw.TextField(null=True)
    timestamp = pw.DateTimeField()


def create_user_data_dir():
    """
    creation of the user data dir. this will only be called in the
    init_storage function. and only once

    """
    user_data_dir_path = helpers.get_user_data_dir_path()
    if not os.path.exists(user_data_dir_path):
        os.makedirs(user_data_dir_path)


def init_database(models: list) -> None:
    """
    create the database tables

    """
    database = get_database()
    try:
        database.connect()
    except pw.OperationalError as e:
        logging.error('peewee operational error: %s', e)
        sys.exit(1)
    database.create_tables(models=models, safe=True)
    database.close()


def init_storage():
    """
    This is the interface for the database / user data directory
    to the outside world.
    """
    create_user_data_dir()
    logging.info('user data directory created...')
    init_database([Contact, UniChatMessage])
    logging.info('database initiated...')


def add_contact(name: str, is_me: bool = False) -> Contact | None:
    """
    adds an unichat contact with name as the database key
    """
    try:
        return Contact.create(name=name,
                              is_me=is_me)
    except pw.IntegrityError as e:
        logging.info('add_contacted failed: %s', e)
        return None


def remove_contact(name: str) -> bool:
    """
    deletes a contact with `name` if it exists
    """
    try:
        # Check if Contact exists in Contact table
        Contact.select().where(Contact.name == name).get()
        # Remove Contact from table
        Contact.delete().where(Contact.name == name).execute()
        return True
    except pw.DoesNotExist:
        logging.info('Contact %s does not exist in Contact table.', name)
        return False


def get_unichat_me() -> Contact | None:
    """
    contact object of the owner
    """
    try:
        return Contact.select().where(Contact.is_me).get()
    except pw.DoesNotExist as e:
        logging.info('get unichat me failed: %s', e)
        return None
    except pw.OperationalError as e:
        logging.info('get unichat me failed: %s', e)
        return None


def get_unichat_message(
        contact_a_name: str,
        contact_b_name: str,
        chat_client: str,
        limit: int = -1) -> list[UniChatMessage]:
    contact_a = Contact.get(Contact.name == contact_a_name)
    contact_b = Contact.get(Contact.name == contact_b_name)

    query = (UniChatMessage
             .select()
             .where((UniChatMessage.chat_client == chat_client) &
                    (
                            ((UniChatMessage.from_contact == contact_a) & (UniChatMessage.to_contact == contact_b)) |
                            ((UniChatMessage.from_contact == contact_b) & (UniChatMessage.to_contact == contact_a)))
                    )
             .order_by(UniChatMessage.id.desc()))  # timestamp is not precise enough, changed to id, i.e. add order

    query = query if limit < 1 else query.limit(limit)

    return list(query)


def has_unichat_message(
        from_contact: Contact,
        to_contact: Contact,
        chat_client: str,
        timestamp: str,
        text: str) -> bool:
    """ Returns true if an unichat message matches all given parameters """
    try:
        (UniChatMessage
         .select()
         .where((UniChatMessage.from_contact == from_contact) &
                (UniChatMessage.to_contact == to_contact) &
                (UniChatMessage.chat_client == chat_client) &
                (UniChatMessage.timestamp == timestamp) &
                (UniChatMessage.text == text))
         .get())
        return True
    except pw.DoesNotExist:
        return False
