"""
Twitter API Module
"""

import time
import random
import logging
import tweepy

# Enable logging
logger = logging.getLogger(__name__)


def _get_twitter_conn_v1_1(api_key, api_secret, access_token, access_token_secret) -> tweepy.API:
    """
    Get twitter connection (V1.1 API)
    :param api_key: TWITTER_API_KEY
    :param api_secret: TWITTER_API_KEY_SECRET
    :param access_token: TWITTER_ACCESS_TOKEN
    :param access_token_secret: TWITTER_ACCESS_TOKEN_SECRET
    :return: tweepy.API object
    """

    auth = tweepy.OAuth1UserHandler(api_key, api_secret)
    auth.set_access_token(access_token, access_token_secret)
    return tweepy.API(auth)


def _upload_media_v1_1(media: str, api_key, api_secret, access_token, access_token_secret) -> str:
    """
    Upload media to twitter (V1.1 API)
    :param media: Media to upload
    :param api_key: TWITTER_API_KEY
    :param api_secret: TWITTER_API_KEY_SECRET
    :param access_token: TWITTER_ACCESS_TOKEN
    :param access_token_secret: TWITTER_ACCESS_TOKEN_SECRET
    :return: media_id
    """
    client_v1 = _get_twitter_conn_v1_1(
        api_key,
        api_secret,
        access_token,
        access_token_secret
    )
    logger.info(media)
    media = client_v1.media_upload(filename=media)
    media_id = media.media_id

    return media_id


def create_tweet(content_dict: dict, keys: dict) -> None:
    """
    Post tweet and thread to Twitter. Thread is optional.
    :param content_dict: Content dict
    :param keys: Keys dict
    """

    tweet = content_dict["text"]
    thread = content_dict["thread"]
    media = content_dict["media"]
    in_reply_to_tweet_id = content_dict["in_reply_to_tweet_id"]

    api_key = keys["TWITTER_API_KEY"]
    api_key_secret = keys["TWITTER_API_KEY_SECRET"]
    access_token = keys["TWITTER_ACCESS_TOKEN"]
    access_token_secret = keys["TWITTER_ACCESS_TOKEN_SECRET"]
    logger.info(f"Received tweet post request with params: "
                f"{tweet = }, {thread = }, {media = }, {in_reply_to_tweet_id = }")

    client = tweepy.Client(
        consumer_key=api_key,
        consumer_secret=api_key_secret,
        access_token=access_token,
        access_token_secret=access_token_secret
    )

    if media is not None:
        media_id = _upload_media_v1_1(
            media=media,
            api_key=api_key,
            api_secret=api_key_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )
        response = client.create_tweet(text=tweet, in_reply_to_tweet_id=in_reply_to_tweet_id, media_ids=[media_id])
    else:
        response = client.create_tweet(text=tweet, in_reply_to_tweet_id=in_reply_to_tweet_id)

    id_ = response.data["id"]
    logger.info(f"Posted tweet with id = {id_}")

    # Split thread into 280 character chunks WITHOUT splitting words
    if thread:
        thread = thread.split()
        thread_list = []
        for word in thread:
            if len(thread_list) == 0:
                thread_list.append(word)
            elif len(thread_list[-1]) + len(word) + 1 <= 250:
                thread_list[-1] += f" {word}"
            else:
                thread_list.append(word)
        for i, chunk in enumerate(thread_list):
            response = client.create_tweet(text=chunk, in_reply_to_tweet_id=id_)
            id_ = response.data["id"]
            time.sleep(random.randint(5, 10))
