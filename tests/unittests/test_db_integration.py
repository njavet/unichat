import unittest
import peewee as pw
import unichat.db as db


test_db = pw.SqliteDatabase(':memory:')
models = [db.Contact,
          db.UniChatMessage]


class TestInitDatabaseIntegration(unittest.TestCase):
    def setUp(self):
        test_db.bind(models)
        test_db.connect()
        test_db.create_tables(models)

    def tearDown(self):
        test_db.drop_tables(models)
        test_db.close()

    def test_init_database(self):
        self.assertTrue(db.Contact.table_exists())
        self.assertTrue(db.UniChatMessage.table_exists())
        self.assertFalse(test_db.is_closed())

    def test_add_contact(self):
        contact0 = db.add_contact('Platon', True)
        self.assertIsNotNone(contact0)

    def test_add_contact_dublicate(self):
        contact0 = db.add_contact('Kant', False)
        self.assertIsNotNone(contact0)
        contact1 = db.add_contact('Kant', False)
        self.assertIsNone(contact1)

    def test_get_unichat_me_exists(self):
        db.add_contact('Platon', True)
        contact = db.get_unichat_me()
        self.assertIsNotNone(contact)

    def test_get_unichat_me_does_not_exist(self):
        contact = db.get_unichat_me()
        self.assertIsNone(contact)
        db.add_contact('Nietzsche')
        contact1 = db.get_unichat_me()
        self.assertIsNone(contact1)


if __name__ == '__main__':
    unittest.main()
