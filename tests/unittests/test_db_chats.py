from peewee import SqliteDatabase
import datetime
import unittest
import unichat.db as db
import unichat.clients.telegram_client.telegram_db as tdb
import json

test_db = SqliteDatabase(':memory:')
models = [db.Contact, tdb.TelegramContact, db.UniChatMessage]


class TestDatabaseChats(unittest.TestCase):
    """

    """
    def setUp(self):
        test_db.bind(models)
        test_db.connect()
        test_db.create_tables(models)
        self.me = db.add_contact('Neo', is_me=True)
        tdb.TelegramContact.create(user_id=0,
                                   first_name='Neo',
                                   contact=self.me)
        self.contact = db.add_contact('AgentSmith')
        tdb.TelegramContact.create(user_id=1,
                                   first_name='AgentSmith',
                                   contact=self.contact)
        with open('tests/resources/mock_chat.json') as f:
            messages = json.load(f)

        start = datetime.datetime(2024, 1, 1, 1, 1)
        for message in messages:
            db.UniChatMessage.create(from_contact=message['from_contact'],
                                     to_contact=message['to_contact'],
                                     chat_client='telegram',
                                     text=message['text'],
                                     timestamp=start)
            start += datetime.timedelta(seconds=64)

    def tearDown(self):
        test_db.drop_tables(models)
        test_db.close()


if __name__ == '__main__':
    unittest.main()

