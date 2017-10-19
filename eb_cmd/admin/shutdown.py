"Shutdown command, to terminate the bot."

import eb_activity
import eb_cmd.admin.eb_admin_cmd as eb_admin_cmd


class Cmd(eb_admin_cmd.AdminCmd):
    "Shutdown the bot, after verification."

    def __init__(self):
        eb_admin_cmd.AdminCmd.__init__(self, "shutdown")

        self.add_rule("shutdown")

    def rule_shutdown(self, user, args):
        print("Shutdown command called.")
        ShutdownActivity(user)
        return "Shutdown command recognized. "


class ShutdownActivity(eb_activity.StateActivity):
    """Activity to shutdown the bot after verification."""

    def __init__(self, user):
        super().__init__(user)

    def start(self, text):
        act = eb_activity.AskYesOrNoActivity(self.user,
                                             prompt="Shutdown EnforsBot?")
        self.state = self.awaiting_confirmation
        return act.start()

    def awaiting_confirmation(self, text):
        "Activity is waiting for yes or no from user."

        if text == "yes":
            raise SystemExit

        return eb_activity.ActivityStatus("Shutdown cancelled.",
                                          done=True)
