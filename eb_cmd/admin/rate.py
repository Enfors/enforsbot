"""Rate tweets for sentiment analysis.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import eb_activity
import eb_cmd.admin.eb_admin_cmd as eb_admin_cmd

from twitgrep.twitsent import TweetPart

Base = declarative_base()


class Cmd(eb_admin_cmd.AdminCmd):
    """Ask for tweets to rate the sentiment of.
    """

    def __init__(self):
        eb_admin_cmd.AdminCmd.__init__(self, "rate")

        self.add_rule("rate")

    def rule_rate(self, user, args):
        RateActivity(user)
        return ""


class RateActivity(eb_activity.StateActivity):
    """Activity for rating the sentiment of tweets.
    """

    def __init__(self, user):
        super().__init__(user)
        self.choices = [
            ["+10", "+8", "+6", "+5", "+4", "+3"],
            ["+2", "+1", "Zero", "-1", "-2"],
            ["-3", "-4", "-5", "-6", "-8", "-10"],
            ["Delete", "Done"],
            ]

        self.engine = create_engine("sqlite:////home/enfors/devel/" +
                                    "python/TwitGrep/twitgrep/tweets.sqlite")
        self.session = sessionmaker()
        self.session.configure(bind=self.engine)
        self.s = self.session()

    def start(self, text):
        self.state = self.rating
        self.load_unrated_tweet_part()

        self.tweet_part = self.load_unrated_tweet_part()

        if self.tweet_part is None:
            return eb_activity.ActivityStatus(output="There are no new "
                                              "tweets to rate at this time. ",
                                              done=True)

        self.update_prompt()

        return eb_activity.ActivityStatus(output=self.prompt,
                                          choices=self.choices)

    def rating(self, text):
        """Waiting for rating of a tweet from the user.
        """

        if text == "done":
            return eb_activity.ActivityStatus("Done rating.",
                                              done=True)

        if text == "delete":
            self.s.delete(self.tweet_part)
            self.s.commit()
        else:
            text = text.replace("+", "")
            text = text.replace("zero", "0")
            rate_value = int(text)

            self.tweet_part.target = rate_value
            self.s.commit()

        self.tweet_part = self.load_unrated_tweet_part()

        if not self.tweet_part:
            return eb_activity.ActivityStatus(output="No more tweets to rate.",
                                              done=True)

        self.update_prompt()

        return eb_activity.ActivityStatus(output=self.prompt,
                                          choices=self.choices)

    def update_prompt(self):
        """Set the prompt based on the current tweet.
        """

        self.prompt = "Tweet part from %s:\n%s" % (self.tweet_part.user,
                                                   self.tweet_part.post_text)

    def load_unrated_tweet_part(self):
        """Load an unrated tweet part from the database, and store it
        in self.
        """

        tweet_part = self.s.query(TweetPart).filter(TweetPart.target == None).first()

        return tweet_part
