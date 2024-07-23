"""
Scraper class for profile pages.
"""

import time

from .common import domain, TimeoutContext
from .scraper import Scraper


class ProfilePage(Scraper):
    """
    Scrapes profile pages.
    """

    def __init__(self, keys: dict, profile_handle: str, max_tweets: int = 10, headless: bool = True):
        super().__init__(keys, headless)  # Initialize Scraper (log in)

        # Load profile page
        self.driver.get(f"{domain}/{profile_handle}")
        self.wait_for_elements("//a[@aria-label='Home']", "//div[@data-testid='User-Name']")

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
                try:
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
                except Exception as e:
                    pass

                # Break if max_tweets reached
                if len(self.tweets) >= max_tweets:
                    break

            # Break if max_tweets reached
            if len(self.tweets) >= max_tweets:
                break


def scrape_profile(keys: dict, profile_handle: str, max_tweets: int = 10, headless: bool = True):
    """
    Scrape profile page.
    :param keys: Keys dict including TWITTER_USERNAME and TWITTER_PASSWORD
    :param profile_handle: Profile handle to scrape
    :param max_tweets: Maximum number of tweets to scrape
    :param headless: Whether to run in headless mode
    :return: List of tweets
    """
    scraper = ProfilePage(keys, profile_handle, max_tweets, headless)
    return scraper.tweets
