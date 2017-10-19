"Base inheritable for admin commands."

import eb_cmd.eb_cmd as eb_cmd


class AdminCmd(eb_cmd.Cmd):
    def __init__(self, name):
        eb_cmd.Cmd.__init__(self, name)
