"""Rate tweets for sentiment analysis.
"""

import eb_activity
import eb_cmd.admin.eb_admin_cmd as eb_admin_cmd


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
            ["Done"],
            ]

    def start(self, text):
        self.state = self.rating
        self.prompt = "Please rate the sentiment of this tweet " \
                      "(not implemented):"

        return eb_activity.ActivityStatus(output=self.prompt,
                                          choices=self.choices)

    def rating(self, text):
        """Waiting for rating of a tweet from the user.
        """

        if text == "done":
            return eb_activity.ActivityStatus("Done rating.",
                                              done=True)

        return eb_activity.ActivityStatus(output=self.prompt,
                                          choices=self.choices)
