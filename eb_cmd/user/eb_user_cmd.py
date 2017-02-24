"Base inheritable for user commands."

import eb_cmd.eb_cmd as eb_cmd

class UserCmd(eb_cmd.Cmd):
    def __init__(self):
        cmd.Cmd.__init__(self)
