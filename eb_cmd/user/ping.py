"Ping command, for verifying connection."
import eb_cmd.user.eb_user_cmd as eb_user_cmd

class Cmd(eb_user_cmd.UserCmd):
    "Ping command. Does very little."

    def __init__(self):
        eb_user_cmd.UserCmd.__init__(self, "ping")

        self.add_rule("ping")

    def rule_ping(self, user, args):
        print("Command ping called.")
        return "Pong."
