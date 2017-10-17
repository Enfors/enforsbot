"""eb_activity.py by Christer Enfors (c) 2016

Activities are a way for EnforsBot to have an "activity" for a user that
lasts several "rounds" - as opposed to a "hello" input that would result
in a "hello yourself" response and then be done. What this means in practice
is that when a user has an active activity, any input from that user is sent
to that activity, and not to the ordinary command parser.
"""

from __future__ import print_function

#
# BASE ACTIVITY CLASSES
#

def make_test_user():
    """Create a test user for use in tests."""
    import sqlite3
    import eb_config
    import eb_user
    config = eb_config.Config()
    database = sqlite3.connect("enforsbot.db",
                               detect_types=sqlite3.PARSE_DECLTYPES)
    return eb_user.User(config, database, name="Enfors")


class Activity(object):
    """An activity - interaction between user and bot that spans
    multiple messages.
    
    This is a base class, and is not usually used directly.

    >>> activity = Activity(make_test_user())
    >>> activity
    Activity(User(config, database, name="Enfors", userid=None))
    """

    def __init__(self, user):
        self.user = user

    def __repr__(self):
        return 'Activity(%s)' % str(self.user)

    def handle_text(self, text):  # pylint: disable=unused-argument,no-self-use
        "Handle text from a user. This function must be overridden."
        print("Activity.handle_text(): Unimplemented")
        return False


class StateActivity(Activity):
    """An activity which keeps track of which function to call the next time
    it gets input."""

    def __init__(self, user):
        super(StateActivity, self).__init__(user)

        self.state = self.start  # state = function to call on input.

    def __repr__(self):
        return "StateActivity (state='%s')" % self.state

    def start(self, text):  # pylint: disable=no-self-use,unused-argument
        "The default state function. Should be overridden."
        print("StateActivity: start function not implemented error.")
        raise SystemExit  # todo: should raise something else

    def handle_text(self, text):
        if not callable(self.state):
            print("StateActivity: Internal error: self.state (%s) is not "
                  "callable." % self.state)
            raise SystemExit  # todo: should raise something else

        return self.state(text)


class SelectOneActivity(StateActivity):
    """Have the user select one of a specific range of strings. Useful for menus
    or "please answer yes or no" type situations.

    Let's make an activity where we ask the user whether or not to continue:

    >>> activity = SelectOneActivity(make_test_user, choices=["yes", "no"],
    ...                              prompt="Continue?",
    ...                              retry_prompt="Please answer yes or no.")
    >>> activity
    SelectOneActivity(prompt="Continue?",
                      retry_prompt="Please answer yes or no.",
                      choices=['yes', 'no'])

    Okay, let's start the activity. The text argument should be the text
    user entered to trigger this activity, but it doesn't really matter.

    >>> activity.start("some irrelevant text")
    ActivityStatus(output='Continue?',
                   result=None,
                   choices=[],
                   done=False)

    What happens if we give it an incorrect result?

    >>> activity.handle_text("foo")
    ActivityStatus(output='Please answer yes or no.',
                   result=None,
                   choices=['yes', 'no'],
                   done=False)

    What happens if we give it a correct result?

    >>> activity.handle_text("yes")
    ActivityStatus(output='Thank you.',
                   result=yes,
                   choices=[],
                   done=True)
    """
    def __init__(self, user, choices, prompt=None, retry_prompt=None):
        super(SelectOneActivity, self).__init__(user)

        self.choices = choices
        if prompt:
            self.prompt = prompt
        else:
            self.prompt = "Please select one of the following:\n%s" %\
                          ", ".join(choices)
        if retry_prompt is not None:
            self.retry_prompt = retry_prompt
        else:
            self.retry_prompt = self.prompt

    def __repr__(self):
        return """
SelectOneActivity(prompt="%s",
                  retry_prompt="%s",
                  choices=%s)""".strip() % \
            (self.prompt, self.retry_prompt, self.choices)

    def start(self, text):
        self.state = self.validate_choice
        return ActivityStatus(output=self.prompt)

    def validate_choice(self, text):
        "Called to validate the choice the user made."
        if text in self.choices:
            return ActivityStatus(output="Thank you.",
                                  result=text,
                                  done=True)
        else:
            return ActivityStatus(output=self.retry_prompt, choices=self.choices)


class AskYesOrNoActivity(SelectOneActivity):
    """Only accept a "yes" or a "no"."""
    def __init__(self, user, prompt=None, retry_prompt=None):
        super(AskYesOrNoActivity, self).__init__(user,
                                                 ["yes", "no"],
                                                 prompt,
                                                 retry_prompt)

    def __repr__(self):
        return "AskYesOrNoActivity (prompt='%s')" % self.prompt


class AskStringActivity(StateActivity):
    """Accept any non-emtpy string."""

    def __init__(self, user, prompt):
        super(AskStringActivity, self).__init__(user)
        self.prompt = prompt

    def __repr__(self):
        return "AskStringActivity (prompt='%s')" % self.prompt

    def start(self, text):
        self.state = self.validate_choice
        return ActivityStatus(output=self.prompt)

    def validate_choice(self, text):
        "Make sure the string isn't empty."

        # pylint: disable=no-self-use
        # This is meant to be inherited by something that might use self.

        if len(text):
            return ActivityStatus(output="Thanks.",
                                  result=text,
                                  done=True)
        else:
            return ActivityStatus(output="Please write something.")


class AskIntActivity(Activity):
    """Only accept strings that can be converted to int."""
    def __repr__(self):
        return "AskIntActivity"


class ActivityStatus(object):
    """Returned from activities.

    >>> act_s = ActivityStatus("some output", choices=["foo", "bar"])
    >>> act_s
    ActivityStatus(output='some output',
                   result=None,
                   choices=['foo', 'bar'],
                   done=False)
    >>> print(act_s)
    some output
    Choices: foo, bar

    We can also make an ActivityStatus without choices:

    >>> print(ActivityStatus("That's all!"))
    That's all!
    """

    def __init__(self, output, result=None, choices=[], done=False):
        self.output = output
        self.result = result
        self.choices = choices
        self.done = done

    def __str__(self):
        output = self.output
        if self.result:
            output += "\nUser entered: %s."

        if self.choices:
            output += "\nChoices: %s" % str.join(", ", self.choices)

        if self.done:
            output += "\nDone"

        return output

    def __repr__(self):
        return """
ActivityStatus(output='%s',
               result=%s,
               choices=%s,
               done=%s)""".strip() %\
                   (str(self.output), str(self.result), str(self.choices),
                    str(self.done))

#
# NON-BASE CLASSES
#


class AskUserNameActivity(AskStringActivity):
    "Ask a user for their name."
    def __init__(self, user):
        super(AskUserNameActivity, self).__init__(user,
                                                  "Hello there! "
                                                  "I don't believe we've met. "
                                                  "What's your name?")

    def validate_choice(self, text):
        status = super(AskUserNameActivity, self).validate_choice(text)
        if status.done:
            name = status.result.title()
            status.output = "Nice to meet you, %s. " % name
            self.user.name = name
            self.user.save()
        return status

