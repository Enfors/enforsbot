"""handle a user's inbox
(not mail - just to keep things you don't want to forget).
"""

import eb_cmd.user.eb_user_cmd as eb_user_cmd
import eb_activity


class Cmd(eb_user_cmd.UserCmd):
    """Activity for maintaining a user's inbox."""

    def __init__(self):
        eb_user_cmd.UserCmd.__init__(self, "inbox")

        self.add_rule("inbox")

    def rule_inbox(self, user, args):
        print("Command inbox called.")
        user.push_activity(InboxActivity(user))
        return "inbox.Cmd: starting inbox activity..."


class InboxActivity(eb_activity.StateActivity):
    """An activity to keep track of a user's inbox."""

    def start(self, text):
        output = "Items currently in your inbox:"
        choices = [["Add", "Delete"],
                   ["Clear", "Done"]]
        # We'll leave self.state as self.start.

        return eb_activity.ActivityStatus(output=output, choices=choices)

    def handle_text(self, text):
        done = False
        choices = [["Add", "Delete"],
                   ["Clear", "Done"]]
        if text == "inbox":
            output = "Inbox:"
        elif text == "done":
            done = True
            output = "Exiting the inbox."
        else:
            done = False
            output = "%s: not implemented." % text

        return eb_activity.ActivityStatus(output=output, choices=choices,
                                          done=done)
