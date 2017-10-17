"""eb_parser.py - parse commands from users, by Christer Enfors (c) 2017.
Based on my parser for DannilMUD."""


class ParserError(BaseException):
    "Generic parser error."
    pass


class ParseError(ParserError):
    "A parse error exception."
    pass


class ParseWrongRule(ParserError):
    pass


class IncorrectInput(ParserError):
    pass


class CmdFailed(ParserError):
    pass


class UnknownCmd(ParserError):
    pass


class CmdParser(object):
    "Command parser object."
    def __init__(self, cmds_loader):
        self.cmds_loader = cmds_loader

    def parse(self, orig_input, user):
        "Parse input from a user."

        orig_input = orig_input.split()
        cmd_name = orig_input[0]
        fail_explanation = "then it went downhill from there."

        cmd = self.cmds_loader.find_cmd(cmd_name, ["user"])

        try:
            if not cmd:
                raise UnknownCmd("I have no idea what \"%s\" means." %
                                 cmd_name)

            print("parser: cmd_name='%s'" % cmd_name)

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
                        parse_retval = eval(func_name)
                        if isinstance(parse_retval, str):
                            return parse_retval, []
                        else:
                            return parse_retval

                    except CmdFailed as e:
                        return str(e), []
                except ParseWrongRule:
                    continue
                except IncorrectInput as e:
                    fail_explanation = str(e)
            raise ParseError("I understood \"%s\", but %s" %
                             (cmd_name, fail_explanation))
        except ParserError as e:
            return str(e), []

    def match_input_to_rule(self, inp, rule, user):
        args = []

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

    def pop_first(self, entries):
        if len(entries) == 0:
            return None, []
        elif len(entries) == 1:
            return entries[0], []
        else:
            return entries[0], entries[1:]
