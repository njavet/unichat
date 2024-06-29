import time

# external imports
from selenium.common import NoSuchElementException, ElementClickInterceptedException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

# project imports
import unichat.clients.instagram_client.instagram_db as idb
import unichat.config as config
import unichat.db as db
import unichat.helpers as helpers
from unichat.clients.chat_client import ChatClient
from unichat.driver_manager import DriverManager
from unichat.encryption.utility import EncryptionUtility


class InstagramClient(ChatClient):
    """Instagram Client Class"""

    def __init__(self,
                 driver_manager: DriverManager,
                 name='instagram'):
        """ constructor """
        super().__init__(name)
        db.init_database(models=[idb.InstagramContact])
        self.dm = driver_manager
        self.driver = self.dm.get_chromedriver()
        self.unichat_me = db.get_unichat_me()
        self.instagram_me = config.instagram_me
        self.encryption_util = EncryptionUtility()
        self.username = ''
        self.password = ''
        self.driver_window_handle = self.dm.initialize_driver_tab(config.instagram_url)

    def login(self, *args) -> bool:
        """Logs in to Instagram web client with the given credentials.

        :param args: Instagram username and password.
        :return: Success information on Instagram web client login.
        """
        username = args[0]
        password = args[1]
        self.dm.switch_driver_window(self.driver_window_handle)
        self.driver.get(config.instagram_url)
        if len(username) == 0 or len(password) == 0:
            if not (len(self.username) == 0 or len(self.password) == 0):
                username = self.username
                password = self.password
            else:
                return False
        try:
            print('Waiting for website to load...')
            time.sleep(2)
            try:
                self.driver.find_element(
                    By.CLASS_NAME, config.instagram_element['decline_cookies']).click()
            except NoSuchElementException:
                print('no cookie popup')

            print('Waiting for Login...')

            if config.instagram_element['login_form'] in self.driver.page_source:
                login_boxes = self.driver.find_elements(
                    By.CLASS_NAME, config.instagram_element['login_fields'])
                login_boxes[0].send_keys(username)
                login_boxes[1].send_keys(password)
                time.sleep(0.5)
                self.driver.find_element(By.CLASS_NAME,
                                         config.instagram_element['login_button']).click()
                time.sleep(3.5)
                print('Logged in successfully!')
            else:
                print('Already logged in...')
            self.username = username
            self.password = password
            time.sleep(5)
            self.driver.get(config.instagram_message_url)
            time.sleep(2)
            self.decline_notifications()
            self.initialize_db()
            return True
        except (NoSuchElementException, ElementClickInterceptedException) as e:
            print('Error has occurred\n' + str(e))
            return False

    def initialize_db(self) -> None:
        """Initializes the database with the unichat and instagram username."""
        self.unichat_me = db.get_unichat_me()
        self.link_to_unichat_account(self.instagram_me, self.unichat_me, '')

    def is_logged_in(self) -> bool:
        """Checks if the user is logged in.
        """
        self.dm.switch_driver_window(self.driver_window_handle)
        if config.instagram_message_url not in self.driver.current_url:
            self.driver.get(config.instagram_message_url)
        try:
            self.driver.find_element(By.CLASS_NAME,
                                     config.instagram_element['contacts'])
        except NoSuchElementException:
            return False
        else:
            return True

    def decline_notifications(self):
        try:
            decline_button = self.driver.find_element(
                By.CLASS_NAME,
                config.instagram_element['decline_notifications']
            )
            print('Declining notifications...')
            decline_button.click()
        except NoSuchElementException:
            print('No notifications found')
            pass

    def check_if_logged_in(self) -> None:
        """Checks if the user is logged in. Initiates login if necessary.
        """
        if not self.is_logged_in():
            print('User not Logged in')
            username = self.encryption_util.load_encrypted('instagram_username.enc')
            password = self.encryption_util.load_encrypted('instagram_password.enc')
            self.login(username, password)
            self.driver.get(config.instagram_message_url)
            time.sleep(2)

    def is_initiated(self, contact: db.Contact) -> bool:
        """
        return True if the contact is linked to the specific
        chat client, False otherwise
        """
        return True if idb.get_instagram_contact(contact) else False

    def link_to_unichat_account(self, contact, unichat_contact: db.Contact, *args):
        """
        the account from the specific chat client needs to be linked to
        an unichat contact
        """
        existing_contact = idb.get_instagram_contact(unichat_contact)
        if existing_contact:
            return existing_contact
        else:
            inc = idb.InstagramContact.create(web_link=args[0],
                                              chat_name=contact,
                                              contact=unichat_contact)
            return inc

    def get_active_chats(self) -> list[tuple[str, str]]:
        """Retrieve all active chats from Instagram web client.

        :return: List of all active chats.
        """

        self.check_if_logged_in()
        self.driver.get(config.instagram_message_url)
        time.sleep(2)
        contacts = self.driver.find_elements(
            By.CLASS_NAME, config.instagram_element['contacts'])
        active_chats = []
        for contact in contacts:
            WebDriverWait(self.driver, config.timeout_limit).until(
                ec.element_to_be_clickable(contact))
            self.driver.execute_script('arguments[0].scrollIntoView(true);',
                                       contact)
            contact.click()
            time.sleep(1)
            name = self.driver.find_element(
                By.CLASS_NAME, config.instagram_element['name']).text.split('\n')[0]

            url = self.driver.current_url
            active_chats.append((name, url))
        return active_chats

    def save_message(self, message: dict[str, str | db.Contact]) -> db.UniChatMessage:
        """
        different clients have different message objects, so every client
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
        send the message

        """

        try:
            instagram_contact = (idb.InstagramContact
                                 .select()
                                 .where(idb.InstagramContact.contact == to_contact)).get()
            contact_url = instagram_contact.web_link

            self.send_message(contact_url=contact_url, message=text)
            return None
        except TimeoutException:
            return None

    def send_message(self, contact_url: str, message: str) -> None:
        """Send a message through Instagram web client.

        :param contact_url: Instagram chat url.
        :param message: message to be sent.
        """
        self.check_if_logged_in()
        self.driver.get(contact_url)
        time.sleep(2)
        self.driver.find_element(
            By.CLASS_NAME, config.instagram_element['input_box']).click()
        actions = ActionChains(self.driver)
        actions.send_keys(message)
        actions.send_keys(Keys.ENTER)
        actions.perform()

    def get_all_messages(self, contact_name: str, contact_url: str) -> list[dict[str, str | db.Contact]]:
        """Retrieve a message from Instagram web client and returns them.

                :param contact_name: Instagram contact name.
                :param contact_url: Instagram chat url.
                :return: list of dictionaries containing all messages.
                """
        self.check_if_logged_in()
        self.driver.get(contact_url)
        WebDriverWait(self.driver, config.timeout_limit).until(
            ec.presence_of_element_located(
                (By.CLASS_NAME, config.instagram_element['chat_window']))
        )
        # scrolls to top of page, this will fail if time until messages is loaded is greater than 2s
        self._scroll_chat_to_top(wait_time=0.5)

        msgs = self.driver.find_elements(
            By.XPATH, helpers.find_xpath_with_class(config.instagram_element['msg_blobs']))

        chat_msgs = []
        time_stamp = ""
        for msg in msgs:
            # this scrolls so that msg is in the view, this ensures the relevant html items are loaded
            self.driver.execute_script('arguments[0].scrollIntoView(true);',
                                       msg)

            data = {}
            try:
                time_stamp = msg.find_element(By.XPATH,
                                              helpers.find_xpath_with_class(config.instagram_element["msg_time"])).text
            except NoSuchElementException:
                pass
            data['timestamp'] = time_stamp
            try:
                sender = msg.find_element(By.XPATH,
                                          helpers.find_xpath_with_class(config.instagram_element['msg_sender'])).text
            except NoSuchElementException:
                sender = 'NA'
            data['from_contact'] = idb.get_contact_from_instagram_name(sender)
            data['to_contact'] = idb.get_contact_from_instagram_name(
                self.instagram_me if sender != self.instagram_me else contact_name)
            try:
                message = msg.find_element(By.XPATH,
                                           helpers.find_xpath_with_class(config.instagram_element['own_msg'])).text
            except NoSuchElementException:
                try:
                    message = msg.find_element(By.XPATH,
                                               helpers.find_xpath_with_class(
                                                   config.instagram_element['other_msg'])).text
                except NoSuchElementException:
                    message = 'NO TEXT'
            data['text'] = message

            chat_msgs.append(data)
        return chat_msgs

    def _scroll_chat_to_top(self, wait_time: float = 1.0) -> None:
        """Scrolls to the top of the Instagram chat history

        :param wait_time: Time in seconds between scrolls.
        """
        chat_window = WebDriverWait(self.driver, config.timeout_limit).until(
            ec.presence_of_all_elements_located(
                (By.CLASS_NAME, config.instagram_element['chat_window'])
            )
        )[1]

        last_height = self.driver.execute_script('return arguments[0].scrollHeight', chat_window)

        while True:
            # Scroll up
            self.driver.execute_script('arguments[0].scrollTo(0,0)', chat_window)

            # Wait to load page
            time.sleep(wait_time)

            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script('return arguments[0].scrollHeight', chat_window)
            if new_height == last_height:
                break
            last_height = new_height
