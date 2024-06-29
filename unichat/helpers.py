"""
collection of helper functions
"""
import itertools
import os
from importlib import resources
from datetime import datetime, timezone

# external imports
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel
from selenium.common import StaleElementReferenceException
from selenium.webdriver.remote.webelement import WebElement

# project imports
import unichat.config as config


def format_msg(message: str, line_length: int = 64) -> str:
    """
    The `format_msg` function splits a text message into lines of maximum
    line_length characters each.
    """
    m_len = len(message)
    # message is smaller than line length and don't need to be changed
    if m_len <= line_length:
        return message

    words = message.split()
    first_word = words[0]
    len_first_word = len(first_word)
    # the first word of the message is longer than the line length
    if line_length <= len_first_word:
        first_word_part0 = first_word[:line_length]
        first_word_part1 = first_word[line_length:]
        msg_rest = ' '.join([first_word_part1] + words[1:])
        return '\n'.join([first_word_part0, format_msg(msg_rest)])

    # take as many words as possible for a line and solve the rest with recursion
    words_length = [len(word) + 1 for word in words]
    ac = itertools.accumulate(words_length, initial=-1)
    tw = itertools.takewhile(lambda wl: wl <= line_length, ac)
    ind = len(list(tw)) - 1
    first_part = ' '.join(words[:ind])
    second_part = format_msg(' '.join(words[ind:]))
    return '\n'.join([first_part, second_part])


def convert_timestamp_to_date(timestamp) -> str:
    """
    since sqlite stores datetime objects as string, timestamp can either be
    a string or a datetime object
    """
    try:
        timestamp = timestamp.strftime('%Y-%m-%d')
    except AttributeError:
        timestamp = timestamp[:10]

    day = timestamp[8:]
    month = timestamp[5:7]
    year = timestamp[2:4]
    return '.'.join([day, month, year])


def get_user_data_dir_path() -> str:
    """
        returns absolut path of userdata directory
    """
    home = os.path.expanduser('~')
    user_data_dir_path = os.path.join(home, config.user_data_dir)
    return user_data_dir_path


def get_log_file_path() -> str:
    """
        returns absolut path of log file
    """
    user_data_dir_path = get_user_data_dir_path()

    log_dir_path = os.path.join(user_data_dir_path, config.log_dir)
    if not os.path.exists(log_dir_path):
        os.makedirs(log_dir_path)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_filename = f"unichat_{timestamp}.log"
    log_file_path = os.path.join(log_dir_path, log_filename)

    return log_file_path


def get_database_path():
    """
      returns the path of the database
      user_data_dir is created here, probably not good practice
    """
    data_dir_path = get_user_data_dir_path()
    return os.path.join(data_dir_path, config.db_name)


def string_to_utc_timestamp(date_string: str) -> str:
    """Convert a date string to a UTC timestamp.

    Args:
        date_string (str): Date string in various formats.

    Returns:
        str: UTC timestamp in ISO 8601 format.
    """

    formats = ['%I:%M %p, %m/%d/%Y', '%H:%M, %d.%m.%Y', '%H:%M, %m/%d/%Y', '%H:%M, %d.%m.%Y']

    for fmt in formats:
        try:
            date_object = datetime.strptime(date_string, fmt)
            date_utc = date_object.replace(tzinfo=timezone.utc)
            return date_utc.isoformat()
        except ValueError:
            pass

    return f'Invalid date format: {date_string}'


def find_xpath_with_class(class_name: str) -> str:
    """Helper to find xpath elements in Instagram web client.

    :param class_name: Instagram html class name.
    :return: string to xpath elements.
    """

    return './/*[@class="' + class_name + '"]'


def get_text_from_element(element: WebElement) -> str:
    """Returns the text of an element. Returns None if the WebElement is stale."""
    try:
        return element.text
    except StaleElementReferenceException:
        return ''


def discard_empty_chats(unique_active_chats: set) -> set:
    """Removes irrelevant chats from the active chats list.

    :param unique_active_chats: List of active chats.
    :return: List of unique active chats.
    """

    unique_active_chats.discard('Archived')
    unique_active_chats.discard('Archiviert')
    unique_active_chats.discard('')
    return unique_active_chats


class ElementHasAttribute:
    """An expectation for checking that an element has a particular attribute.

    locator - used to find the element
    returns the WebElement once it has the particular attribute
    """

    def __init__(self, locator, attribute_name):
        self.locator = locator
        self.attribute_name = attribute_name

    def __call__(self, driver):
        # Finding the referenced element
        element = driver.find_element(*self.locator)
        cond = element.get_attribute(self.attribute_name)
        return element if cond is not None else None


class ClickableLabel(QLabel):
    """Creates a QLabel that can be clicked."""

    clicked = Signal()

    def mousePressEvent(self, event):
        self.clicked.emit()
        QLabel.mousePressEvent(self, event)


def get_icon_path(icon_file):
    return str(resources.files('unichat.assets.icons').joinpath(icon_file))


def get_image_path(image_file):
    return str(resources.files('unichat.assets.images').joinpath(image_file))


def load_stylesheet(stylesheet_file):
    path = resources.files('unichat.assets.stylesheets').joinpath(stylesheet_file)
    with path.open('r') as style_file:
        stylesheet = style_file.read()
    return stylesheet
