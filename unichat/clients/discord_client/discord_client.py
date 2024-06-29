import time

# external imports
from selenium import webdriver
from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

# project imports
from unichat.config import discord_url, discord_element, message_url, timeout_limit
from unichat.driver_manager import DriverManager


class DiscordClient:
    """Client to receive and send messages through the discord_client web client."""

    DRIVER = ""
    DATA_DIR = ""
    CHAT_TYPE = "discord_client"

    username = ""
    password = ""

    def __init__(self, headless: bool = False, userdata_dir: str = "") -> None:
        """Creates a DiscordClient instance that will handle all actions
        taken on the web client.

        :param headless: Boolean value that indicates whether to use headless mode.
        :param userdata_dir: Directory where browser userdata will be stored.
        """

        driver_manager = DriverManager(headless=headless, userdata_dir=userdata_dir)
        self.DRIVER = driver_manager.get_chromedriver()

    def login_to_discord(self, driver: webdriver.Chrome, username: str, password: str) -> str:
        """Logs in to discord_client web client with the given credentials.

        :param driver: Selenium webdriver instance.
        :param username: discord_client username.
        :param password: discord_client password.
        :return: Success information on discord_client web client login.
        """

        driver.get(discord_url)
        if len(username) == 0 or len(password) == 0:
            if not (len(self.username) == 0 or len(self.password) == 0):
                username = self.username
                password = self.password
            else:
                return "Please provide username and password!"
        try:
            print("Waiting for website to load")
            time.sleep(2)
            try:
                # Assuming 'zustimmen' is a button to accept cookies or similar
                driver.find_element(By.CLASS_NAME, discord_element["zustimmen"]).click()
            except NoSuchElementException:
                print("no zustimmen popup")

            print("Waiting for login...")

            if discord_element["login_form"] in driver.page_source:
                login_field_username_or_tel = driver.find_element(By.NAME,
                                                                  discord_element["login_field_username_or_telnr"])
                login_field_password = driver.find_element(By.NAME,
                                                           discord_element["login_field_password"])

                login_field_username_or_tel.send_keys(username)
                login_field_password.send_keys(password)

                time.sleep(2)
                driver.find_element(By.CLASS_NAME, discord_element["login_button"]).click()

                time.sleep(3.5)
                print("Current URL after login attempt:", driver.current_url)

                try:
                    WebDriverWait(driver, timeout_limit).until(
                        ec.visibility_of_element_located((By.CLASS_NAME, discord_element["avatar_container"])))
                    print("Login successful")
                    self.username = username
                    self.password = password
                    return "Login successful"
                except TimeoutException:
                    print("Login failed")
                    return "Login failed"
            else:
                print("Login window not visible, Already logged in?")

        except Exception as e:
            print("Error has occurred: \n" + str(e))

    def login_via_qr(self, driver: webdriver.Chrome) -> bool:
        """Logs in to discord_client web client via QR code.

        :return: True if login was successful, False otherwise.
        """

        driver.get(discord_url)
        if not self.wait_for_qrcode(driver):
            print("QR code not loaded. Check for Timeout or URL.")
            return False

        print("Please scan the QR code with your discord_client mobile app to log in.")
        return self.wait_for_login(driver)

    def wait_for_qrcode(self, driver: webdriver.Chrome) -> bool:
        """Wait for the QR code to appear on the discord_client login page.

        :return: True if QR code element is visible, False otherwise.
        """

        try:
            (WebDriverWait(driver, timeout_limit).until(
                ec.visibility_of_element_located((By.CLASS_NAME, discord_element["qr_code_container"])))
            )
            return True
        except TimeoutException:
            return False

    def wait_for_login(self, driver: webdriver.Chrome) -> bool:
        """Asks for changes on the website that indicate a successful login.

        return: True if login was successful, False otherwise.
        """

        try:
            WebDriverWait(driver, timeout_limit).until(
                lambda driver: driver.current_url != discord_url
            )
            WebDriverWait(driver, timeout_limit).until(
                ec.presence_of_element_located((By.CLASS_NAME, discord_element["avatar_container"]))
            )
            print("Login succesful.")
            return True
        except TimeoutException:
            print("Login failed or timed out after scanning QR code.")
            return False

    def check_if_logged_in(self, driver: webdriver.Chrome, url: str) -> None:
        """Checks if the user is logged in. Initiates login if necessary.

        :param driver: Selenium webdriver instance.
        :param url: discord_client web url.
        """
        time.sleep(2)
        if driver.current_url != url:
            print("User not Logged in")
            username = ""
            password = ""
            self.login_to_discord(driver, username, password)
            driver.get(message_url)

    def close_pop_up(self, driver: webdriver.Chrome, pop_up_element: str, close_button_element: str) -> None:
        """Helper that checks if the pop-up element exists and if so, closes it.

        :param driver: Selenium webdriver instance.
        :param pop_up_element: discord_client pop-up element.
        :param close_button_element: discord_client pop-up button.
        """

        if (len(pop_up_element) == 0):
            print("Pop-up element name not valid.")

        try:
            pop_up_element = driver.find_element(By.CLASS_NAME, pop_up_element)
            close_button_element = pop_up_element.find_element(By.CLASS_NAME, close_button_element)
            close_button_element.click()
            print("Closed pop-up element")
        except NoSuchElementException:
            print("Pop-up element not found.")
        except Exception as e:
            print("Error has occurred: \n" + str(e))

    def retrieve_all_active_chats(self, driver: webdriver.Chrome) -> list[tuple[str, str]]:
        """Retrieve all active chats from discord_client web client.

        :param driver: Selenium webdriver instance.
        :return: List of all active chats.
        """

        driver.get(message_url)
        time.sleep(2)

        # In the HTML tree, after locating scroller it only
        # contains one node, where the chats are displayed.
        scroll_chats = driver.find_element(By.CLASS_NAME, "scroller__89969")
        ul_node = scroll_chats.find_element(By.XPATH, "./*")
        possible_chats = ul_node.find_elements(By.XPATH, "./*")

        # Locate the H2 element index.j
        index_h2 = 0
        for possible_chat in possible_chats:
            if possible_chat.tag_name == "h2":
                break
            index_h2 += 1

        chats_html = possible_chats[index_h2 + 1:]

        chats = []
        for chat in chats_html:
            div_element = chat.find_element(By.XPATH, "./*")
            children = div_element.find_elements(By.XPATH, "./*")

            a_link = None
            for child in children:
                if child.tag_name == "a":
                    a_link = child
                    break

            name = a_link.get_attribute("aria-label")
            if name.startswith("discord_client"):
                continue

            url = a_link.get_attribute("href")
            chats.append((name, url))

        return chats

    def retrieve_message(self, driver: webdriver.Chrome, contact_url: str) -> list[dict[str, str]]:
        """Retrieve a message from discord_client web client and returns them.

        :param driver: Selenium webdriver instance.
        :param contact_url: discord_client chat url.
        :return: list of dictionaries containing all messages.
        """

        driver.get(contact_url)
        time.sleep(3)

        messages_wrapper = driver.find_element(By.XPATH, "//div[starts-with(@class, 'messagesWrapper')]")
        scroller = messages_wrapper.find_element(By.XPATH, "./*")

        # Scroll to top, to load in the html all the elements.
        self.scroll_chat_to_top(driver, scroller.get_attribute("class").split(" ")[0])

        chat_messages_elements = messages_wrapper.find_elements(By.XPATH, ".//li[starts-with(@id, 'chat-messages')]")
        msgs = []

        sender = None
        for chat_element in chat_messages_elements:
            msg = {}
            content = chat_element.find_element(By.XPATH, ".//div[starts-with(@class, 'contents')]")
            message_content = content.find_element(By.XPATH, ".//div[starts-with(@id, 'message-content')]")
            possible_sender = content.find_elements(By.XPATH, "./h3")
            if len(possible_sender) == 1:
                sender = possible_sender[0].find_element(By.XPATH, "./span/span").text
            msg["sender"] = sender
            msg["message"] = DiscordClient.get_text_from_message_content(message_content)
            msg["timestamp"] = content.find_element(By.XPATH, ".//time").get_attribute("datetime")
            msgs.append(msg)

        return msgs

    def scroll_chat_to_top(self, driver, scroll_element: str) -> None:
        """Scrolls to the top of the discord_client chat history

        :param driver: Selenium webdriver instance.
        :param scroll_element: Element to scroll in.
        """

        while driver.execute_script(
                'return document.getElementsByClassName("' + scroll_element + '")[0].scrollTop') > 0:
            driver.execute_script('document.getElementsByClassName("' + scroll_element + '")[0].scrollTo(0,0)')
            time.sleep(1)

    @staticmethod
    def get_text_from_message_content(message_content: WebElement) -> str:
        """Gets text from message content block.

        :param message_content: Message content.
        :return: Text from message content.
        """

        return message_content.text

    def send_message(self, driver: webdriver.Chrome, contact_url: str, message: str) -> None:
        """Send a message through discord_client web client.

        :param driver: Selenium webdriver instance.
        :param contact_url: discord_client chat url.
        :param message: Message to send.
        """

        driver.get(contact_url)
        time.sleep(3)
        # self.check_if_logged_in()
        try:
            # find the respective message box and send the message
            message_box = driver.find_element(By.CLASS_NAME, discord_element["message_box"])
            message_box.click()
            message_box.send_keys(message)
            message_box.send_keys(Keys.ENTER)
            time.sleep(5)

            print(f"Sent message: {message}")
        except NoSuchElementException:
            print(f"Failed to send message: {message}")
        except Exception as e:
            print(f"An error occurred: {e}")
        return message_content.text
