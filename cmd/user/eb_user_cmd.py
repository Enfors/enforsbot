"Base inheritable for user commands."

import cmd.eb_cmd as eb_cmd

class UserCmd(cmd.Cmd):
    def __init__(self):
        cmd.Cmd.__init__(self)
