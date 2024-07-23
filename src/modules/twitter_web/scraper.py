"""
Twitter scraper base class. Contains methods for logging in to Twitter and wrappers for Selenium methods.
"""

import time

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

from .common import domain, TimeoutContext


class Element:
    """
    Wrapper for Selenium WebElement class. Allows for NoneType checks.
    """

    def __init__(self, element):
        self.element = element

    def find_element(self, xpath):
        try:
            return Element(self.element.find_element(By.XPATH, xpath))
        except NoSuchElementException:
            return Element(None)

    def find_elements(self, xpath):
        try:
            return [Element(element) for element in self.element.find_elements(By.XPATH, xpath)]
        except NoSuchElementException:
            return []

    def get_attribute(self, attribute_name):
        if self.element is not None:
            return self.element.get_attribute(attribute_name)
        return None

    def send_keys(self, *keys):
        if self.element is not None:
            self.element.send_keys(*keys)

    def click(self):
        if self.element is not None:
            self.element.click()

    @property
    def text(self):
        if self.element is not None:
            return self.element.text
        return None


class Scraper:
    """
    Base class for all Twitter scrapers.
    """
    keys: dict
    tweets: list
    profiles: list

    def __init__(self, keys: dict, headless: bool = True):
        """
        Initialize driver and log in to Twitter.
        :param keys: Keys dict including TWITTER_USERNAME and TWITTER_PASSWORD
        """
        self.keys = keys
        self.tweets = []
        self.profiles = []

        chrome_options = webdriver.ChromeOptions()
        chrome_options.headless = headless
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.set_window_size(width=1080, height=1080)
        self.driver.get(f"{domain}/login")

        # Enter username
        self.wait_for_element("//input[@autocomplete='username']")
        username_input = self.find_element("//input[@autocomplete='username']")
        username_input.send_keys(self.keys['TWITTER_USERNAME'])
        time.sleep(0.2)
        username_input.send_keys(Keys.RETURN)

        # Enter password
        self.wait_for_element("//input[@autocomplete='current-password']")
        password_input = self.find_element("//input[@autocomplete='current-password']")
        password_input.send_keys(self.keys['TWITTER_PASSWORD'])
        time.sleep(0.2)
        password_input.send_keys(Keys.RETURN)

        # Reload page
        self.wait_for_elements("//a[@aria-label='Home']", "//div[@data-testid='User-Name']")

        # Reject cookies
        # div with data-testid="BottomBar" -> first div -> second div -> second div
        self.wait_for_element("//div[@data-testid='BottomBar']/div/div[2]/div")
        refuse_cookies_button = self.find_element("//div[@data-testid='BottomBar']/div/div[2]/div")
        refuse_cookies_button.click()

    def wait_for_element(self, element_xpath: str):
        """
        Wait for element to load.
        :param element_xpath: XPATH of element to wait for
        """
        WebDriverWait(self.driver, 10).until(
            expected_conditions.presence_of_element_located(
                (By.XPATH, element_xpath)
            )
        )

    def wait_for_elements(self, *args: str):
        """
        Wait for each element to load.
        :param args: element XPATHs to wait for
        """
        for element_xpath in args:
            self.wait_for_element(element_xpath)

    def find_element(self, element_xpath: str):
        """
        Get element by XPATH.
        :param element_xpath: XPATH of element to get
        """
        try:
            element = self.driver.find_element(By.XPATH, element_xpath)
        except NoSuchElementException:
            element = None

        return element

    def find_elements(self, elements_xpath: str):
        """
        Get elements by XPATH. Waits for all elements with same xpath to load by checking if the number of elements has
        changed.
        :param elements_xpath: XPATH of elements to get
        """
        try:
            elements = lambda: self.driver.find_elements(By.XPATH, elements_xpath)
            with TimeoutContext(10):
                while True:
                    elements_before = elements()
                    time.sleep(1.25)
                    elements_after = elements()
                    if len(elements_before) == len(elements_after):
                        break
                    else:
                        elements_before = elements_after
        except NoSuchElementException:
            elements = []

        return [Element(element) for element in elements()]

    def scroll_to_bottom(self):
        """
        Scroll to bottom of page.
        """
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    def scroll_down(self):
        """
        Scroll down by 1000 pixels.
        """
        self.driver.execute_script("window.scrollBy(0, 1000);")

    def scroll_to_top(self):
        """
        Scroll to top of page.
        """
        self.driver.execute_script("window.scrollTo(0, 0);")

    def scroll_up(self):
        """
        Scroll up by 1000 pixels.
        """
        self.driver.execute_script("window.scrollBy(0, -1000);")
