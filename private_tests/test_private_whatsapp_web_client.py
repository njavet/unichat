# # These tests should only be used in private since it needs the user to be logged in
#
# import unittest
# import os
# import time
# import sys
# import json
# from datetime import datetime
#
# import unichat.db
# import unichat.driver_manager as DM
#
# import unichat.clients.whatsapp_client.whatsapp_client as client
# import unichat.clients.whatsapp_client.whatsapp_db as wdb
#
#
# def is_user_logged_in(client):
#     client.driver.get('https://web.whatsapp.com/')
#     time.sleep(10)
#     return client.is_logged_in()
#
#
# def init_test_contact(contact_name: str, client: client.WhatsAppClient):
#     test_contact = db.add_contact(contact_name)
#     client.link_to_unichat_account(contact_name, test_contact)
#
#
# class TestPrivateWhatsAppClient(unittest.TestCase):
#     """Test class for WhatsApp client. This class should only be used in private with their own user data"""
#
#     driver = None
#     client = None
#     test_dir = None
#
#     test_contact_read = "Unichat-WhatsApp-Test-Read"
#     test_contact_write = "Unichat-WhatsApp-Test-Write"
#     test_expected_file_path = "./resources/test_whatsapp_client_read.json"
#
#     @classmethod
#     def setUpClass(cls):
#         """Sets up the WhatsApp client for testing. Fails test if user is not logged in!"""
#         cls.dm = DM.DriverManager(False)
#         cls.client = client.WhatsAppClient(cls.dm)
#         cls.driver = cls.client.driver
#
#         if not is_user_logged_in(client=cls.client):
#             raise EnvironmentError(f'User is not logged in! Test cancelled!')
#         init_test_contact(cls.test_contact_write, cls.client)
#         init_test_contact(cls.test_contact_read, cls.client)
#
#     @classmethod
#     def tearDownClass(cls):
#         """Tears down the WhatsApp client for testing."""
#
#         cls.driver.quit()
#         time.sleep(1)
#         # Remove all test contacts
#         db.remove_contact(cls.test_contact_write)
#         db.remove_contact(cls.test_contact_read)
#
#     def test_read_messages(self):
#         """Test reading messages from WhatsApp client. Uses a predefined group chat with a predefined chat history.
#         The expected output can be found in ./resources/test_whatsapp_client_read.txt
#         """
#
#         self.client.driver.get('https://web.whatsapp.com/')
#         time.sleep(3)
#
#         chat_messages = self.client.get_all_messages(chat_name=self.test_contact_read)
#
#         time.sleep(5)
#
#         with open(self.test_expected_file_path, 'r') as expected_file:
#             expected_data = json.load(expected_file)
#
#         self.assertTrue(len(chat_messages), len(expected_data))
#
#         for i in range(len(chat_messages)):
#             actual_message = chat_messages[i]
#             expected_message = expected_data[i]
#             whatsapp_contact = wdb.get_whatsapp_contact(actual_message['from_contact'])
#             self.assertEqual(actual_message['timestamp'], expected_message['timestamp'])
#             self.assertEqual(whatsapp_contact.chat_name, expected_message['sender'])
#             self.assertEqual(actual_message['text'], expected_message['message'])
#
#     def test_write_message(self):
#         """Test writing message to WhatsApp client. Sends a message to a predefined group chat."""
#
#         self.client.driver.get('https://web.whatsapp.com/')
#         time.sleep(3)
#
#         current_datetime = datetime.now()
#
#         test_message = 'Lorem ipsum dolor sit amet - ' + current_datetime.strftime("%Y-%m-%d %H:%M:%S")
#         self.client.send_message(chat_name=self.test_contact_write, message=test_message)
#         time.sleep(1)
#         chat_messages = self.client.get_all_messages(chat_name=self.test_contact_write)
#
#         time.sleep(5)
#         actual_data = str(chat_messages)
#
#         self.assertTrue(test_message in actual_data)
#
#     def test_get_username(self):
#         """Test getting username from WhatsApp client."""
#
#         self.client.driver.get('https://web.whatsapp.com/')
#         time.sleep(3)
#         whatsapp_me = self.client.get_me()
#         self.assertTrue(whatsapp_me)
#
#
# if __name__ == '__main__':
#     unittest.main()
