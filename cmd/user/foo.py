"Foo command, for testing only."
import cmd.user.eb_user_cmd as eb_user_cmd

class Cmd(eb_user_cmd.UserCmd):
    "Foo command. Does nothing useful."
    def __init__(self):
        eb_user_cmd.UserCmd.__init__(self)

        self.add_rule("foo")

    def rule_foo(self, user, args):
        print("Command foo called.")
        return "Bar."

