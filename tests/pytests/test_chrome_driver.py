import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from unichat.driver_manager import DriverManager


@pytest.fixture(scope="module")
def chrome_driver():
    driver_manager = DriverManager(True)
    driver = driver_manager.get_chromedriver()
    yield driver
    driver.quit()


def test_chrome_driver_compatibility(chrome_driver):
    driver = chrome_driver
    driver.get("https://www.google.com")
    assert "Google" in driver.title


if __name__ == "__main__":
    pytest.main([__file__])

