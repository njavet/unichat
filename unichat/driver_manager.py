import os
import socket
import threading
import logging
from typing import Callable, Any

# external imports
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

# project imports
import unichat.config as config
import unichat.helpers as helpers


class DriverManager:
    """Driver Manager class to create Selenium webdriver instances."""

    def __init__(self,
                 headless: bool = True,
                 default_driver_port: int = 9222,
                 host: str = 'localhost') -> None:
        """Initialize DriverManager instance with the given configurations.

        :param headless: Boolean to enable headless mode.
        """

        self.userdata_dir = os.path.join(helpers.get_user_data_dir_path(),
                                         'chromedriver-userdata')
        self.headless = headless
        self.default_driver_port = default_driver_port
        self.host = host
        self.driver = None
        self.driver = self.get_chromedriver()
        self.mutexLock = threading.Lock()

    def get_chromedriver(self) -> webdriver.Chrome:
        """Creates and returns a ChromeDriver instance with the given configurations.

        :return: Selenium webdriver instance.
        """
        if not self.driver:
            self.driver = self.initialize_driver()
        return self.driver

    def initialize_driver(self) -> webdriver.Chrome:
        """Initialize ChromeDriver instance with the given configurations.

        :return: Selenium webdriver instance.
        """

        # requires google-chrome driver installation -> OS dependent
        options = self._get_chrome_options()
        services = webdriver.ChromeService(ChromeDriverManager().install())
        # Suppress DevTools listening message by redirecting stderr to null
        services.log_path = os.devnull
        driver = webdriver.Chrome(options=options, service=services)
        return driver

    def initialize_driver_tab(self, client_url: str) -> str:
        """Initialize the driver tab with the web client url.
        Stores the driver window handle in order to quickly switch to it.

        :param client_url: Web client url.
        :return: the driver window handle.
        """
        # Check whether the web client is already open
        for handle in self.driver.window_handles:
            self.driver.switch_to.window(handle)
            if client_url in self.driver.current_url:
                return handle
        # Switch to the last tab
        self.driver.switch_to.window(self.driver.window_handles[-1])
        # Create new tab to open a new web client
        if self.driver.current_url != config.driver_new_page:
            self.driver.switch_to.new_window('tab')
        self.driver.get(client_url)
        return self.driver.current_window_handle

    def switch_driver_window(self, driver_window_handle: str) -> None:
        """Switches to the web client tab

        :param driver_window_handle: Window handle of the web client.
        """

        self.driver.switch_to.window(driver_window_handle)

    def execute_driver_command(self, func: Callable, *args) -> Any:
        """ executes the driver command """
        with self.mutexLock:
            if len(args) > 0:
                return func(*args)
            else:
                return func(*args)

    def close_driver(self) -> None:
        """Closes the driver and window."""

        if self.driver:
            self.driver.quit()
            self.driver = None

    def _get_chrome_options(self) -> webdriver.ChromeOptions:
        """Creates and returns a ChromeOptions instance with the given configurations.

        :return: ChromeOptions instance.
        """

        options = webdriver.ChromeOptions()

        if self._is_driver_running():
            options.debugger_address = f"localhost:{self.default_driver_port}"

            logging.info('Getting old driver session...')
            return options

        if self.headless:
            options.add_argument("--headless")
            options.add_argument("--window-size=1920,1080")
            # change the user-agent to avoid being detected as headless
            options.add_argument(
                "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/64.0.3282.140 Safari/537.36")

        options.add_argument("--lang=en")  # Force browser to display in English
        options.add_argument("--accept-lang=en")
        options.add_argument(f"--user-data-dir={self.userdata_dir}")
        options.add_argument(f'--remote-debugging-port={self.default_driver_port}')
        options.add_argument("--log-level=3")
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_argument("--profile-directory=Default")

        logging.info('Getting new driver session...')
        return options

    def _is_driver_running(self) -> bool:
        """Checks whether Selenium webdriver is running.

        :return: Returns true if Selenium webdriver is running.
        """

        try:
            # Try to connect to Chrome's remote debugging port
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.host, self.default_driver_port))
            return True
        except ConnectionRefusedError:
            return False
