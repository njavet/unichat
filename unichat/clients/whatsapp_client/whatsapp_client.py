import logging
import math
import re
import time
from datetime import datetime

# external imports
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, \
    ElementClickInterceptedException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

# project imports
import unichat.clients.whatsapp_client.whatsapp_db as wdb
import unichat.config as config
import unichat.db as db
import unichat.helpers as helpers
from unichat.clients.chat_client import ChatClient
from unichat.driver_manager import DriverManager


class WhatsAppClient(ChatClient):
    def __init__(self,
                 driver_manager: DriverManager,
                 name='whatsapp',
                 time_sender_regex: str = r'\[(?P<datetime>.+)\]\s(?P<sender>.+):'):
        """ constructor """
        super().__init__(name)
        db.init_database(models=[wdb.WhatsAppContact])
        self.qr_data: str = ''
        self.time_sender_regex = time_sender_regex
        self.dm = driver_manager
        self.driver = self.dm.get_chromedriver()
        self.unichat_me = db.get_unichat_me()
        self.whatsapp_me = ""
        self.driver_window_handle = self.dm.initialize_driver_tab(config.whatsapp_url)

    def get_me(self) -> str:
        """Returns own Whatsapp username.

        :return: Whatsapp username.
        """

        # Get whatsapp me from DB if class attribute is empty
        db_whatsapp_me = wdb.get_whatsapp_me()
        self.whatsapp_me = db_whatsapp_me.chat_name if not self.whatsapp_me and db_whatsapp_me else self.whatsapp_me
        if not self.whatsapp_me:
            try:
                self.dm.switch_driver_window(self.driver_window_handle)

                profile = WebDriverWait(self.driver, config.timeout_limit).until(
                    ec.element_to_be_clickable((By.CLASS_NAME, config.whatsapp_element['profile_element'])))
                profile.click()

                time.sleep(1)  # Needs to sleep, such that Selenium has time to load changes to the page.

                self.whatsapp_me = WebDriverWait(self.driver, config.timeout_limit).until(
                    ec.presence_of_element_located((By.CLASS_NAME, config.whatsapp_element['username']))).text

                self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)  # Exit profile
                self.initialize_db(self.whatsapp_me)
            except (NoSuchElementException, TimeoutException):
                logging.warning('Could not extract WhatsApp username')
        return self.whatsapp_me

    def is_logged_in(self) -> bool:
        """
        Return True if the user is logged in the specific client,
        False otherwise
        """

        result = self.dm.execute_driver_command(self._execute_is_logged_in)
        return result

    def _execute_is_logged_in(self) -> bool:
        """ check if logged in"""
        self.dm.switch_driver_window(self.driver_window_handle)
        try:
            self.driver.find_element(By.CLASS_NAME,
                                     config.whatsapp_element['chat_search_box'])
        except NoSuchElementException:
            return False
        else:
            return True

    def get_qr_code(self) -> str:
        """Returns the qr code data string"""

        result = self.dm.execute_driver_command(self._execute_get_qr_code)
        return result

    def _execute_get_qr_code(self) -> str:
        """ fetches QR login code and returns it as a string """
        self.dm.switch_driver_window(self.driver_window_handle)
        cond0 = self.driver.current_url != config.whatsapp_url
        cond1 = not self._execute_is_logged_in()
        if cond0 or cond1:
            self.driver.get(config.whatsapp_url)
            try:
                # Wait until the site is loaded
                WebDriverWait(self.driver, config.timeout_limit).until(
                    ec.presence_of_element_located(
                        (By.ID, config.whatsapp_element['static_element'])
                    )
                )
                # Check whether the user is logged in
                if self._has_qr_code():
                    logging.info('Waiting to scan QR-Code...')
                    element = WebDriverWait(self.driver, config.timeout_limit).until(
                        helpers.ElementHasAttribute(
                            (By.CLASS_NAME, config.whatsapp_element['qr_code']),
                            config.whatsapp_element['qr_code_data'])
                    )
                    # Store QR data into class field
                    self.qr_data = element.get_attribute(
                        config.whatsapp_element['qr_code_data']
                    )
                elif self._execute_is_logged_in():
                    logging.info('Already logged in...')
                    self.qr_data = config.logged_in
                else:
                    self.qr_data = ''
            except TimeoutException:
                logging.warning('Login failed. Please check the QR-Code and try again.')
                self.qr_data = ''
        return self.qr_data

    def login(self) -> bool:
        """
        Logs in to WhatsApp web client. Returns False if the user has not logged in within a given time.
        """

        logging.info('Logging in to WhatsApp...')
        result = self.dm.execute_driver_command(self._execute_login)
        return result

    def _execute_login(self) -> bool:
        timer = 0
        while timer <= config.timeout_limit and not self._execute_is_logged_in():
            time.sleep(1)
            timer += 1

        if self._execute_is_logged_in():
            self.initialize_db()
            return True
        else:
            return False

    def initialize_db(self, whatsapp_me: str = "") -> None:
        """Initializes the database with the unichat and WhatsApp username."""

        self.unichat_me = db.get_unichat_me()
        if not whatsapp_me:
            whatsapp_me = self.get_me()
        self.link_to_unichat_account(whatsapp_me, self.unichat_me)

    def is_initiated(self, contact: db.Contact) -> bool:
        """
        Return True if the contact is linked to the specific
        chat client, False otherwise
        """
        return True if wdb.get_whatsapp_contact(contact) else False

    def link_to_unichat_account(self, contact, unichat_contact: db.Contact, *args):
        """
        The account from the specific chat client needs to be linked to
        an unichat contact
        """
        existing_contact = wdb.get_whatsapp_contact(unichat_contact)
        if existing_contact:
            return existing_contact
        else:
            wac = wdb.WhatsAppContact.create(phone_nr='-',
                                             chat_name=contact,
                                             is_linked=False,
                                             contact=unichat_contact)
            return wac

    def is_unichat_contact_linked(self, unichat_contact: db.Contact) -> bool:
        """
        Returns true if the given unichat contact has already been linked to the chat client.
        """
        contact = wdb.get_whatsapp_contact(unichat_contact)
        if contact and contact.is_linked:
            return True
        else:
            return False

    def save_message(self, message: dict[str, str | db.Contact]) -> db.UniChatMessage:
        """
        Different clients have different message objects, so every client
        needs to construct and save an unichat message object
        """

        unichat_message = db.UniChatMessage.create(from_contact=message['from_contact'],
                                                   to_contact=message['to_contact'],
                                                   chat_client=self.name,
                                                   text=message['text'],
                                                   timestamp=message['timestamp'])
        return unichat_message

    def send_text_message(self, to_contact: db.Contact, text: str) -> None:
        """
        Send the message
        """
        try:

            whatsapp_contact = (wdb.WhatsAppContact
                                .select()
                                .where(wdb.WhatsAppContact.contact == to_contact)).get()
            contact_name = whatsapp_contact.chat_name

            self.send_message(contact_name,
                              text)
            return None
        except TimeoutException:
            return None

    def send_message(self, chat_name: str, message: str) -> None:
        """Send a message through WhatsApp web client.

        :param chat_name: WhatsApp chat name.
        :param message: message to be sent.
        """

        self.dm.execute_driver_command(self._execute_send_message, chat_name, message)

    def _execute_send_message(self, chat_name: str, message: str) -> None:
        """ sends message """
        self.dm.switch_driver_window(self.driver_window_handle)
        try:
            self.search_and_select_chat(chat_name)
            message_box = WebDriverWait(self.driver, config.timeout_limit).until(
                ec.presence_of_element_located(
                    (By.CLASS_NAME, config.whatsapp_element['chat_message_box']))
            )

            message_box.send_keys(message)
            message_box.send_keys(Keys.ENTER)
        except TimeoutException as e:
            logging.warning(f"An error occurred while sending the WhatsApp message: {str(e)}")
            raise

    def search_and_select_chat(self, chat_name: str) -> None:
        """Search and select a contact from WhatsApp web client.

        :param chat_name: WhatsApp contact name.
        """

        try:

            search_box = WebDriverWait(self.driver, config.timeout_limit).until(
                ec.presence_of_element_located(
                    (By.CLASS_NAME, config.whatsapp_element['chat_search_box']))
            )
            if search_box and search_box.text != chat_name:
                self._clear_search_box()
                search_box.click()
                search_box.send_keys(chat_name)
            WebDriverWait(self.driver, config.timeout_limit_short).until(
                ec.visibility_of_all_elements_located(
                    (By.CLASS_NAME, config.whatsapp_element['chat_list_item'])
                )
            )  # Short pause to load elements

            # Try to find chat with the exact name
            chats_found = self.driver.find_elements(By.XPATH,
                                                    f"//span[@title='{chat_name}']")
            if len(chats_found) == 0:
                raise TimeoutException  # Exception when no chat is found
            else:
                chats_found[0].click()  # Select the first chat found
        except TimeoutException:
            logging.warning(f'Whatsapp Chat "{chat_name}" was not found.')

    def get_all_messages(self, chat_name: str) -> list[dict[str, db.Contact | str]]:
        """ Retrieve a message from WhatsApp web client"""

        return self.dm.execute_driver_command(self._execute_get_messages, chat_name)

    def _execute_get_messages(self,
                              chat_name: str,
                              enable_limit: bool = False,
                              last_message_timestamp: datetime = None) -> list[dict[str, db.Contact | str]]:
        self.dm.switch_driver_window(self.driver_window_handle)
        self.get_me()  # Ensure that whatsapp_me is loaded
        try:
            self.search_and_select_chat(chat_name)
            WebDriverWait(self.driver, config.timeout_limit).until(
                ec.presence_of_element_located(
                    (By.CLASS_NAME, config.whatsapp_element['chat_message_block']))
            )  # Wait for the first message block to load
            if enable_limit:
                self._scroll_to_top(enable_limit, chat_name, last_message_timestamp)
            else:
                self._scroll_to_top()
            message_list = WebDriverWait(self.driver, config.timeout_limit).until(
                ec.presence_of_all_elements_located(
                    (By.CLASS_NAME, config.whatsapp_element['chat_message_block']))
            )
            messages_json = []
            for message_block in message_list:
                message_data = self._convert_messages_block_to_unichat(chat_name, message_block)
                if message_data:  # Deleted Messages are of type None
                    messages_json.append(message_data)
            return messages_json
        except TimeoutException:
            logging.warning(f'Failed to retrieve Whatsapp messages for {chat_name}')

    def get_latest_messages(self, chat_name):
        """ Retrieve the latest messages from WhatsApp web client. Used by the async fetcher"""
        return self.dm.execute_driver_command(self._execute_get_latest_messages, chat_name)

    def _execute_get_latest_messages(self, chat_name: str) -> list[dict[str, db.Contact | str]] | None:
        try:
            last_message_db = self._get_last_db_message(chat_name=chat_name)
            self.search_and_select_chat(chat_name=chat_name)
            message_blocks = WebDriverWait(self.driver, config.timeout_limit).until(
                ec.presence_of_all_elements_located(
                    (By.CLASS_NAME, config.whatsapp_element['chat_message_block']))
            )
            last_message_online = self._convert_messages_block_to_unichat(chat_name, message_blocks[-1])
            timestamp_db = datetime.fromisoformat(last_message_db.timestamp)
            if not self._is_same_message(last_message_db, last_message_online):
                messages = self._execute_get_messages(chat_name=chat_name, enable_limit=True,
                                                      last_message_timestamp=timestamp_db)
                return self._filter_new_messages(messages, timestamp_db)
            else:
                return None
        except ElementClickInterceptedException as e:
            logging.warning(e)

    def get_active_chats(self) -> list:
        """ Returns a list of the active chats

        :return: A list of active chats
        """

        return self.dm.execute_driver_command(self._execute_get_active_chats)

    def _execute_get_active_chats(self, limit: int = 20) -> list:
        """ load active chats helper """
        self.dm.switch_driver_window(self.driver_window_handle)
        self._close_chat()
        scroll_distance = 1000

        current_scroll_distance = 0

        self._clear_search_box()

        try:
            chat_list = WebDriverWait(self.driver, config.timeout_limit).until(
                ec.presence_of_element_located(
                    (By.CLASS_NAME, config.whatsapp_element['chat_list']))
            )
            unique_active_chats = set()
            scroll_height = self._get_scroll_height(chat_list)
            scroll_iterations = math.ceil(scroll_height / scroll_distance)
            for _ in range(0, scroll_iterations):
                self.driver.execute_script(f'arguments[0].scrollTo(0,{current_scroll_distance})',
                                           chat_list)
                chat_list_items = WebDriverWait(self.driver, config.timeout_limit).until(
                    ec.visibility_of_all_elements_located((By.CLASS_NAME, config.whatsapp_element['chat_list_item']))
                )
                chat_names = list(map(helpers.get_text_from_element, chat_list_items))
                unique_active_chats.update(chat_names)
                current_scroll_distance += scroll_distance
                if len(unique_active_chats) >= limit:
                    break

            self.driver.get(config.whatsapp_url)  # Reset the view
            return sorted(helpers.discard_empty_chats(unique_active_chats))
        except TimeoutException:
            logging.warning('Failed to retrieve all active Whatsapp chats')

    def _convert_messages_block_to_unichat(self,
                                           chat_name: str,
                                           message_block: WebElement) -> dict[str, db.Contact | str] | None:
        has_message = True
        message_content = None
        data = None
        try:
            message_content = message_block.find_element(
                By.CLASS_NAME,
                config.whatsapp_element['chat_message_content']
            )
        except NoSuchElementException:
            has_message = False

        if has_message:
            timestamp_sender = message_content.get_attribute(
                config.whatsapp_element['chat_message_data']
            )
            timestamp_sender_match = re.match(self.time_sender_regex,
                                              timestamp_sender)
            message_text = message_block.find_element(
                By.CLASS_NAME, config.whatsapp_element['chat_message_text']).text
            sender = timestamp_sender_match.group('sender')
            data = {'timestamp': helpers.string_to_utc_timestamp(
                timestamp_sender_match.group('datetime')
            ),
                'from_contact': wdb.get_contact_from_whatsapp_name(sender),
                'to_contact': wdb.get_contact_from_whatsapp_name(
                    self.get_me() if sender != self.get_me() else chat_name),
                'text': message_text}

        return data

    def _filter_new_messages(self,
                             messages: list[dict[str, db.Contact | str]],
                             last_message_timestamp: datetime) -> list[dict[str, db.Contact | str]]:
        new_messages = []
        for message in messages:
            message_timestamp = datetime.fromisoformat(message['timestamp'])
            if (last_message_timestamp < message_timestamp
                    or not (db.has_unichat_message(from_contact=message['from_contact'],
                                                   to_contact=message['to_contact'],
                                                   chat_client=self.name,
                                                   text=message['text'],
                                                   timestamp=message['timestamp']))):
                new_messages.append(message)
        return new_messages

    def _get_last_db_message(self, chat_name: str) -> db.UniChatMessage:

        return db.get_unichat_message(contact_a_name=wdb.get_contact_from_whatsapp_name(self.get_me()).name,
                                      contact_b_name=wdb.get_contact_from_whatsapp_name(chat_name).name,
                                      chat_client=self.name, limit=1)[0]

    def _get_scroll_height(self, scroll_element: WebElement) -> float:
        """Gets scroll height of a WebElement and returns it.

        :param scroll_element: WebElement to scroll.
        :return: Scroll height.
        """

        return self.driver.execute_script('return arguments[0].scrollHeight', scroll_element)

    def _has_past_last_stored_message(self,
                                      chat_name: str,
                                      last_message_timestamp: datetime,
                                      message_blocks: list[WebElement]) -> bool:
        oldest_online_message_block = self._convert_messages_block_to_unichat(chat_name, message_blocks[0])
        online_timestamp = datetime.fromisoformat(oldest_online_message_block['timestamp'])
        return last_message_timestamp > online_timestamp

    def _scroll_to_top(self,
                       enable_limit: bool = False,
                       chat_name: str = "",
                       last_message_timestamp: datetime = None) -> None:
        """Scrolls to the top of the WhatsApp chat history
        """

        chat_window = WebDriverWait(self.driver, config.timeout_limit).until(
            ec.presence_of_element_located(
                (By.CLASS_NAME, config.whatsapp_element['chat_window'])
            )
        )

        chat_container = WebDriverWait(self.driver, config.timeout_limit).until(
            ec.presence_of_element_located(
                (By.CLASS_NAME, config.whatsapp_element['chat_container'])
            )
        )

        last_height = self._get_scroll_height(chat_window)

        WebDriverWait(self.driver, config.timeout_limit).until(
            ec.presence_of_element_located(
                (By.CLASS_NAME, config.whatsapp_element['chat_message_content'])
            )
        )  # Wait for the first messages to load

        # Get all message blocks
        message_blocks = WebDriverWait(self.driver, config.timeout_limit).until(
            ec.presence_of_all_elements_located(
                (By.CLASS_NAME, config.whatsapp_element['chat_message_block']))
        )

        # Check if message_blocks already contain the last stored message
        if (enable_limit and self._has_past_last_stored_message(chat_name, last_message_timestamp,
                                                                message_blocks)):
            return  # Exit if already reached

        while True:
            # Scroll up
            self.driver.execute_script("arguments[0].scrollTo(0,0)", chat_container)

            # Wait to load page
            WebDriverWait(self.driver, config.timeout_limit).until(
                ec.visibility_of_all_elements_located(
                    (By.CLASS_NAME, config.whatsapp_element['chat_message_content'])
                )
            )

            # Get all message blocks
            message_blocks = WebDriverWait(self.driver, config.timeout_limit).until(
                ec.presence_of_all_elements_located(
                    (By.CLASS_NAME, config.whatsapp_element['chat_message_block']))
            )

            # Calculate new scroll height and compare with last scroll height
            new_height = self._get_scroll_height(chat_window)
            if (new_height == last_height or
                    (enable_limit and self._has_past_last_stored_message(chat_name, last_message_timestamp,
                                                                         message_blocks))):
                break
            last_height = new_height

    def _clear_search_box(self) -> None:
        """Clears the WhatsApp web client search box."""

        try:
            search_box_cancel = self.driver.find_element(
                By.CLASS_NAME, config.whatsapp_element['chat_search_box_cancel']
            )
            search_box_cancel.click()
        except (NoSuchElementException, StaleElementReferenceException):
            pass

    def _close_chat(self, clear_search_box: bool = True) -> None:
        """Closes the current WhatsApp chat

        :param clear_search_box: Clears the WhatsApp web client search box if set True.
        """

        if clear_search_box:
            self._clear_search_box()
        try:
            chat_container = self.driver.find_element(By.CLASS_NAME,
                                                      config.whatsapp_element['chat_container'])
        except NoSuchElementException:
            pass
        else:
            chat_container.send_keys(Keys.ESCAPE)

    def _has_qr_code(self) -> bool:
        """Checks if the current page has a QR code."""

        try:
            WebDriverWait(self.driver, config.timeout_limit_short).until(
                ec.presence_of_element_located((By.CLASS_NAME, config.whatsapp_element['qr_code']))
            )
        except TimeoutException:
            return False
        else:
            return True

    def _is_same_message(self, db_message: db.UniChatMessage, online_message: dict[str, db.Contact | str]) -> bool:
        return (db_message.from_contact == online_message['from_contact']
                and db_message.to_contact == online_message['to_contact']
                and datetime.fromisoformat(db_message.timestamp) == datetime.fromisoformat(online_message['timestamp'])
                and db_message.text == online_message['text'])
