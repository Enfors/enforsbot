"""eb_parser.py - parse commands from users, by Christer Enfors (c) 2017.
Based on my parser for DannilMUD."""

import os

import eb_update

user_cmds_dir = "eb_cmd/user"
admin_cmds_dir = "eb_cmd/admin"

class ParseError(BaseException):
    "A parse error exception."
    pass

class ParseWrongRule(BaseException):
    pass

class IncorrectInput(BaseException):
    pass

class CmdParser(object):
    "Command parser object."
    def __init__(self):
        self.user_cmds = []
        self.admin_cmds = []

        self.load_all_cmd_lists()

    def parse(self, orig_input, user):
        "Parse input from a user."
        match_found = False
        orig_input = orig_input.split()
        cmd_name = orig_input[0]
        fail_explanation = "then it went downhill from there."

        cmd_path = self.find_cmd_path(cmd_name, user)

        try:
            if not cmd_path:
                raise ParseError("I have no idea what \"%s\" means." %
                                 cmd_name)

            print("parser: cmd_path='%s'" % cmd_path)
            cmd = eb_update.update.request_obj(cmd_path, "Cmd")

            if len(cmd.rules) == 0:
                # todo: raise exception
                print("[cmd_parser] The %s command has no rules." % cmd_name)

            for orig_rule in cmd.rules:
                inp = orig_input[:]
                rule = orig_rule[:]
                print("\nChecking rule %s..." % rule)
                try:
                    args = self.match_input_to_rule(inp, rule, user)

                    func_name = "cmd.rule_%s(user, args)" % \
                                "_".join(orig_rule)
                    try:
                        return eval(func_name)
                    except CmdFailed as e:
                        return str(e)
                except ParseWrongRule:
                    continue
                except IncorrectInput as e:
                    fail_explanation = str(e)
            raise ParseError("I understood \"%s\", but %s" %
                             (cmd_name, fail_explanation))
        except ParseError as e:
            return str(e)

    def match_input_to_rule(self, inp, rule, user):
        args = [ ]

        while len(rule):
            print("+-Checking token %s..." % rule[0])
            if not rule[0].isupper():
                inp, rule, args = self.match_plain_word(inp, rule, args)
            elif rule[0] == "STR":
                inp, rule, args = self.match_STR(inp, rule, args)

        if len(inp):
            raise IncorrectInput("I didn't understand the last part.")
        else:
            return args

    def match_plain_word(self, inp, rule, args):
        print("+---Matching plain word '%s'..." % rule[0])
        rule_word, rule = self.pop_first(rule)

        if len(inp) == 0:
            raise IncorrectInput("I was expecting a \"%s\" somewhere "
                                 "in there." % rule_word)

        entered_word, inp = self.pop_first(inp)

        return inp, rule, args

    def match_STR(self, inp, rule, args):
        print("+---Matching string '%s'..." % " ".join(inp))
        tmp, rule = self.pop_first(rule)

        if len(inp) == 0:
            raise IncorrectInput("I was expecting more.")

        args.append(" ".join(inp))
        inp = []

        return input, rule, args

    def find_cmd_path(self, cmd_name, user):
        cmd_lists = [self.user_cmds]

        # todo: Add admin cmd_list here if user is admin
        for cmd_list in cmd_lists:
            if cmd_name in cmd_list:
                cmd_path = cmd_list[cmd_name] + "." + cmd_name
                return cmd_path

    def load_all_cmd_lists(self):
        "Load all command lists."

        self.user_cmds = self.load_cmd_list(user_cmds_dir)
        self.admin_cmds = self.load_cmd_list(admin_cmds_dir)

    def load_cmd_list(self, path):
        "Load a command list from the specified path."
        cmd_list = { }
        file_names = os.listdir(path)
        
        path = path.replace("/", ".")

        print("Loading commands.")
        for file_name in file_names:
            print("- considering %s..." % file_name)
            # Skip inheritable base files
            if file_name[:3] == "eb_":
                continue

            # Skip files names not ending with .py
            if file_name[-3:] != ".py":
                continue

            # Remove the .py from the file name
            file_name = file_name[:-3]
            cmd_list[file_name] = path
            print("  loaded.")

        return cmd_list

    def pop_first(self, entries):
        if len(entries) == 0:
            return None, [ ]
        elif len(entries) == 1:
            return entries[0], [ ]
        else:
            return entries[0], entries[1:]
