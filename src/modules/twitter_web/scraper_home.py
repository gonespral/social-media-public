"""
Scraper class for the "For You" and "Following" pages. Inherits from Scraper class. __init__ methods scrape the page
and store Tweet and Profile objects in the tweets and profiles lists.
"""

import time

from .common import domain, TimeoutContext
from .scraper import Scraper


class HomePage(Scraper):
    """
    Scrapes the "For You" tab.
    """

    def __init__(self, keys: dict, tab: str = "For you", max_tweets: int = 10, headless: bool = True):

        super().__init__(keys, headless)  # Initialize Scraper (log in)

        if tab not in ["For you", "Following"]:
            raise ValueError("tab must be 'ForYou' or 'Following'")

        # Load home page
        self.driver.get(f"{domain}/home")
        self.wait_for_elements("//a[@aria-label='Home']", "//div[@data-testid='User-Name']")

        # -> div with role='presentation' -> nested span with text=tab
        for_you_tab_button = self.find_element(f"//div[@role='presentation']//span[text()='{tab}']")
        for_you_tab_button.click()
        self.wait_for_element("//div[@data-testid='User-Name']")

        # Scrape cards
        while True:
            # Scroll down after first iteration
            if len(self.tweets) != 0:
                self.scroll_down()

            # Get cards on page
            cards = self.find_elements("//article[@data-testid='tweet']")

            # Scrape cards
            for card in cards:
                # -> div with data-testid='User-Name'
                _user_name = card.find_element(".//div[@data-testid='User-Name']")

                # -> user_name -> second div -> first div -> third div -> first a with role='link'
                tweet_url = card.find_element(".//div[2]/div[1]/div[3]/a[@role='link']").get_attribute("href")
                tweet_id = tweet_url.split("/")[-1] if tweet_url else None

                # card -> div with data-testid="tweetText" -> first span (text)
                tweet_text = card.find_element(".//div[@data-testid='tweetText']").text

                # Append if not duplicate (by tweet_id)
                if tweet_id not in [tweet["tweet_id"] for tweet in self.tweets]:
                    self.tweets.append(
                        {
                            "tweet_id": tweet_id if tweet_id else "",
                            "tweet_url": tweet_url if tweet_url else "",
                            "tweet_text": tweet_text if tweet_text else "",
                            "tweet_media": "",
                            "profile_handle": tweet_url.split("/")[-3] if tweet_url else ""
                        }
                    )

                # Break if max_tweets reached
                if len(self.tweets) >= max_tweets:
                    break

            # Break if max_tweets reached
            if len(self.tweets) >= max_tweets:
                break


def scrape_for_you_page(keys: dict, max_tweets: int = 10, headless: bool = True):
    """
    Scrape the "For You" tab.
    :param keys: Keys dict including TWITTER_USERNAME and TWITTER_PASSWORD
    :param max_tweets: Maximum number of tweets to scrape
    :param headless: Whether to run Chrome in headless mode
    :return: List of Tweet objects
    """
    scraper = HomePage(keys, tab="For you", max_tweets=max_tweets, headless=headless)
    return scraper.tweets


def scrape_following_page(keys: dict, max_tweets: int = 10, headless: bool = True):
    """
    Scrape the "Following" tab.
    :param keys: Keys dict including TWITTER_USERNAME and TWITTER_PASSWORD
    :param max_tweets: Maximum number of tweets to scrape
    :param headless: Whether to run Chrome in headless mode
    :return: List of Tweet objects
    """
    scraper = HomePage(keys, tab="Following", max_tweets=max_tweets, headless=headless)
    return scraper.tweets
