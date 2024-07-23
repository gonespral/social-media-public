"""
Content generation functions.
"""

import os

import random
import emoji as em

from modules import prompts, openai_api, vector_db, image_editor


class TwitterBot:
    _book_paths = [
        "../databases/vector/apology-of-socrates/apology-of-socrates.pickle.gz",
        "../databases/vector/meditations/meditations.pickle.gz",
        "../databases/vector/beyond-good-and-evil/beyond-good-and-evil.pickle.gz",
        "../databases/vector/nicomachaen/nicomachaen.pickle.gz"
    ]

    _emoji_vector_db_path = "../databases/vector/emoji/emoji.pickle.gz"

    _topics = ["honesty", "leadership", "virtue", "courage", "justice", "hard work", "family", "friends", "death",
               "rationality", "fame", "pleasure", "nature", "sex", "love", "happiness", "life", "freedom",
               "equality", "wealth", "power", "religion", "god", "morality", "wisdom", "knowledge", "education",
               "politics"]

    _writing_styles = ["casual", "friendly", "professional", "academic", "humorous", "satirical", "ironic",
                       "extremely sarcastic", "serious", "scary", "optimistic", "pessimistic", "motivational",
                       "inspirational"]

    _text_styles = ["bullet points", "short sentences with newlines", "single sentence", "single question", "poem"]

    @classmethod
    def quote_with_explanation(cls, keys):
        """
        Generate a quote and explanation.
        """
        topic = random.choice(cls._topics)

        vdb = vector_db.VectorDB(keys["OPENAI_API_KEY"])
        vdb.load(random.choice(cls._book_paths))

        text = vdb.query(query_text=topic, top_k=1)[0]

        prompt = prompts.Templates.extract_from_text(
            guidelines=["The quote must be about {topic}.",
                        "The quote must be EXTREMELY SHORT, RELEVANT AND EASY TO READ.",
                        "Summarize the quote if necessary. It must be a single sentence."
                        "Quote must be provided in plain text, with no quotation marks or attribution.",
                        "Rewrite the quote if necessary, making it concise, and removing stylization.",
                        "THE QUOTE WILL APPEAR ON AN IMAGE, AND THEREFORE MUST BE SHORT AND EASY TO READ."],

            text=text
        )

        quote = openai_api.completion(content=prompt, api_key=keys["OPENAI_API_KEY"], temperature=0.1).strip().strip(
            '"')

        prompt = prompts.Templates.rewrite_text(
            guidelines=["Generate an extremely creative and unique variation of the text.",
                        "If no author is known, do not mention the author."],
            text=f"What did {vdb.metadata['author']} mean by this?"
        )

        tweet_bottom_text = openai_api.completion(content=prompt, api_key=keys["OPENAI_API_KEY"],
                                                  temperature=1).strip().strip('"')

        prompt = prompts.Templates.explain_quote(
            author=vdb.metadata["author"],
            quote=quote
        )

        explanation = openai_api.completion(content=prompt, api_key=keys["OPENAI_API_KEY"],
                                            temperature=0.1).strip().strip(
            '"')

        prompt = prompts.Templates.select_emoji(
            guidelines=[f"MUST be relevant to the topic: {topic}."],
            text=quote
        )

        emoji_vdb = vector_db.VectorDB(keys["OPENAI_API_KEY"])

        emoji_vdb.load(cls._emoji_vector_db_path)

        emoji_query = openai_api.completion(content=prompt, api_key=keys["OPENAI_API_KEY"],
                                            temperature=0.1).strip().strip(
            '"')

        emoji = emoji_vdb.query(query_text=emoji_query, top_k=1)[0]

        tweet = em.emojize(f"'{quote}'\n\n{tweet_bottom_text}\n\n:thread::backhand_index_pointing_down:")
        thread = em.emojize(f"{emoji}{explanation}")

        return {"text": tweet,
                "thread": thread}

    @classmethod
    def image_with_quote(cls, keys):
        """
        Generate a quote and image.
        """

        topic = random.choice(cls._topics)

        vdb = vector_db.VectorDB(keys["OPENAI_API_KEY"])
        vdb.load(random.choice(cls._book_paths))

        text = vdb.query(query_text=topic, top_k=1)[0]

        prompt = prompts.Templates.extract_from_text(
            guidelines=["The quote must be about {topic}.",
                        "The quote must be EXTREMELY SHORT, RELEVANT AND EASY TO READ.",
                        "Quote must be provided in plain text, with no quotation marks or attribution.",
                        "Rewrite the quote if necessary, making it concise, and removing stylization.",
                        "REWRITE THE QUOTE SO IT IS EXTREMELY SHORT, AS THERE IS A CHARACTER LIMIT OF 280 CHARACTERS."],
            text=text
        )

        quote = openai_api.completion(content=prompt, api_key=keys["OPENAI_API_KEY"], temperature=0.1).strip().strip(
            '"')

        prompt = prompts.Templates.generate_text(
            guidelines=[
                f"You must write a single short sentence based on the following quote.",
                f"The quote is '{quote}'.",
                f"The sentence must be EXTREMELY SHORT, RELEVANT AND EASY TO READ.",
                f"Write as if you are a gen-z teenager, replying to the quote on Twitter.",
                f"For example, if you agree with the quote, you could write 'So true' or 'this.'.",
                f"DO NOT DISAGREE WITH THE QUOTE, AS THIS IS YOUR OWN ACCOUNT.",
                f"You may write questions, but they must be rhetorical.",
                f"BE CREATIVE",
                f"There is a character limit of 240. If you exceed this, you will be TERMINATED."]
        )

        text = openai_api.completion(content=prompt, api_key=keys["OPENAI_API_KEY"], temperature=0.1).strip().strip('"')

        # Get all available images
        files_in_directory = os.listdir("../assets/images")

        image = image_editor.Templates.image_with_text(
            image_file_path="../assets/images/" + random.choice(files_in_directory),
            text=quote,
            output_path="../assets/generated/",
        )

        return {"text": text,
                "media": image}

    @classmethod
    def random_thought(cls, keys):
        """
        Generate a random philosophical thought.
        """
        topic = random.choice(cls._topics)
        writing_style = random.choice(cls._writing_styles)

        prompt = prompts.Templates.generate_text(
            guidelines=[f"The text must be about {topic}.",
                        f"Writing style must be: {writing_style}.",
                        f"The text must be VERY SHORT, RELEVANT AND EASY TO READ.",
                        f"The text must be a PHILOSOPHICAL THOUGHT.",
                        f"The text must NOT contain a question.",
                        f"The text must be a STATEMENT about your, the world, etc.",
                        f"The text must be short, as there is a character limit of 280 characters. Do not approach the "
                        f"character limit, or you will be PERMANENTLY TERMINATED."]
        )

        tweet = openai_api.completion(content=prompt, api_key=keys["OPENAI_API_KEY"], temperature=1).strip().strip('"')

        return {"text": tweet,
                "thread": None}

    @classmethod
    def random_opinion(cls, keys):
        """
        Generate a random philosophical opinion.
        """
        topic = random.choice(cls._topics)
        writing_style = random.choice(cls._writing_styles)
        random_bool = random.choice([True, False])  # 50% chance of generating a thread

        prompt = prompts.Templates.generate_text(
            guidelines=[f"The text must be about {topic}.",
                        f"Writing style must be: {writing_style}.",
                        f"Text must express a PHILOSOPHICAL OPINION ABOUT THE TOPIC.",
                        f"The text must be VERY SHORT, RELEVANT AND EASY TO READ.",
                        f"The text must be a STATEMENT about your, the world, etc.",
                        f"The text must be short, as there is a character limit of 280 characters. Do not approach the "
                        f"character limit, or you will be PERMANENTLY TERMINATED."]
        )

        tweet = openai_api.completion(content=prompt, api_key=keys["OPENAI_API_KEY"], temperature=1).strip().strip('"')

        thread = None
        if random_bool:
            prompt = prompts.Templates.generate_text(
                guidelines=[f"Text must be a QUESTION about the topic.",
                            f"The text must be VERY SHORT, RELEVANT AND EASY TO READ.",
                            f"The topic is: {topic}.",
                            f"The question must stem from the text: {tweet}.",
                            f"The text must be short, as there is a character limit of 280 characters. Do not "
                            f"approach the character limit, or you will be PERMANENTLY TERMINATED."]
            )

            thread = openai_api.completion(content=prompt, api_key=keys["OPENAI_API_KEY"], temperature=1).strip().strip(
                '"')

        return {"text": tweet,
                "thread": thread}

# def random_copycat():
#     """
#     Generate a copycat tweet.
#     :return: (tweet, thread)
#     """
#
#     # Get profiles in the database
#     profiles_in_db = list(csv_db["profile_handle"].tolist()))
#
#     # Intersect with profiles to copy and pick
#     profiles_in_db = list(set(profiles_in_db).intersect_profiles_to_copy))
#     profile_to_copy = random.choice(profiles_in_db)
#
#     # Get profile tweets and pick random row
#     profile_tweetcsvcsv_db["profile_handle"] == profile_to_copy]
#     profile_tweet = profile_tweets.sample(n=1).iloc[0]
#
#     # Get tweet text
#     tweet_text = profile_tweet["tweet_text"]
#
#     writing_style = random.choice(prompts.writing_styles)
#
#     prompt = prompts.Templates.rewrite_text(
#         guidelines=[f"The text must be a copy of the original text.",
#                     f"Writing style must be: {writing_style}.",
#                     f"The text must be VERY SHORT, RELEVANT AND EASY TO READ.",
#                     f"The text must be short, as there is a character limit of 280 characters. Do not approach the "
#                     f"character limit, or you will be PERMANENTLY TERMINATED.",
#                     f"You must NOT include commercial offers, deals or website links in the text."],
#         text=tweet_text
#     )
#
#     tweet = openai_api.completion(content=prompt, kkeys, temperature=1).strip().strip('"')
#
#     # Set tweet as used
# csv_db.csv_db["tweet_id"] == profile_tweet["tweet_id"], "last_used_by"handle
# csv_db.csv_db["tweet_id"] == profile_tweet["tweet_id"], "last_used_on"] = str(
#         datetime.datetime.now())
# csv_db.csv_db["tweet_id"] == profile_tweet["tweet_id"], "last_used_to"] = "copycat"
# csv_db.to_csv_db_path, index=False)
#
#     return {"tweet": tweet,
#             "image": None,
#             "tweet_id": None}
#
# def random_reply():
#     """
#     Generate a reply to a tweet.
#     :return: (tweet, thread)
#     """
#
#     # Get profiles in the database
#     profiles_in_db = list(csv_db["profile_handle"].tolist()))
#
#     # Intersect with profiles to reply and pick
#     profiles_in_db = list(set(profiles_in_db).intersect_profiles_to_reply))
#     profile_to_reply = random.choice(profiles_in_db)
#
#     # Get profile tweets and pick random row
#     profile_tweetcsvcsv_db["profile_handle"] == profile_to_reply]
#     profile_tweet = profile_tweets.sample(n=1).iloc[0]
#
#     # Get tweet text
#     tweet_text = profile_tweet["tweet_text"]
#     tweet_id = profile_tweet["tweet_id"]
#
#     writing_style = random.choice(prompts.writing_styles)
#
#     prompt = prompts.Templates.generate_text(
#         guidelines=[f"The text must be a reply to the original text (which is a Tweet on Twitter).",
#                     f"Writing style must be: {writing_style}.",
#                     f"The text must be VERY SHORT, RELEVANT AND EASY TO READ.",
#                     f"The text must be short, as there is a character limit of 280 characters. Do not approach the "
#                     f"character limit, or you will be PERMANENTLY TERMINATED.",
#                     f"You must NOT include commercial offers, deals or website links in the text.",
#                     f"TEXT TO REPLY TO: {tweet_text}"]
#     )
#
#     tweet = openai_api.completion(content=prompt, kkeys, temperature=1).strip().strip('"')
#
#     # Set tweet as used
# csv_db.csv_db["tweet_id"] == profile_tweet["tweet_id"], "last_used_by"handle
# csv_db.csv_db["tweet_id"] == profile_tweet["tweet_id"], "last_used_on"] = str(
#         datetime.datetime.now())
# csv_db.csv_db["tweet_id"] == profile_tweet["tweet_id"], "last_used_to"] = "reply"
# csv_db.to_csv_db_path, index=False)
#
#     return {"tweet": tweet,
#             "image": None,
#             "tweet_id": tweet_id}

# Twitter Scraper Methods
# """
#
# from generator import ContentObject, TwitterContentObject
# from ..modules import twitter_web
#
# keys_path = "../../keys/twitter_scraper.json"
# log_path = "../../logs/twitter_scout.log"
#
# _profiles_to_scrape = [
#     "lawsofaurelius",
#     "TheStoicEmperor",
#     "SenecaQuote",
#     "elonmusk",
#     "lexfridman",
#     "billionair_key"
# ]
#
#
# def scrape_fyp():
#     """
#     Scrape the "For You" Twitter feed for new tweets.
#     """
#     for i in range(3):
#         try:
#             tweets = twitter_web.scrape_for_you_page(keys=keys, max_tweets=25)
#             break
#         except Exception as e:
#             logger.error(e)
#             if i < 2:
#                 logger.error("Retrying...")
#             else:
#                 raise e
#
#     for tweet in tweets:
#         # Filter out ads and media only tweets
#         if tweet["tweet_id"] and tweet["tweet_text"]:
#             ...
#
#
# def scrape_profiles(self):
#     """
#     Scrape _profiles_to_scrape for new tweets.
#     """
#     for profile in self._profiles_to_scrape:
#
#         for i in range(3):
#             try:
#                 tweets = twitter_web.scrape_profile(keys=self.keys, profile_handle=profile, max_tweets=25)
#                 break
#             except Exception as e:
#                 self.logger.error(e)
#                 if i < 2:
#                     self.logger.error("Retrying...")
#                 else:
#                     raise e
#
#         for tweet in tweets:
#             # Filter out ads and media only tweets
#             if tweet["tweet_id"] and tweet["tweet_text"]:
#                 ...
