"Base inheritable for commands by Christer Enfors (c) 2017"

class Cmd:
    "Base inheritable for commands."

    def __init__(self):
        self.rules = [ ]
        self.setup()

    def setup(self):
        "Probably meant for specific command setup...?"
        pass

    def add_rule(self, rule):
        "Add a parsing rule."
        rule = rule.split()
        func_name = "rule_" + "_".join(rule)

        if not func_name in dir(self):
            print("Function missing for rule '%s'." % rule)
            return False

        self.rules.append(rule)
