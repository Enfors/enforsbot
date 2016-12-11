"eb_activity.py by Christer Enfors (c) 2016"

from __future__ import print_function

#
# BASE ACTIVITY CLASSES
#

class Activity(object):
    "An activity - interaction between user and bot that spans multiple messages."

    def __init__(self):
        pass

    def handle_text(self, text): # pylint: disable=unused-argument,no-self-use
        "Handle text from a user. This function must be overridden."
        print("Activity.handle_text(): Unimplemented")
        return False



class StateActivity(Activity):
    """An activity which keeps track of which function to call the next time
    it gets input."""

    def __init__(self):
        super(StateActivity, self).__init__()

        self.state = self.start # state = function to call on input.

    def start(self, text): # pylint: disable=no-self-use,unused-argument
        "The default state function. Should be overridden."
        print("StateActivity: start function not implemented error.")
        raise SystemExit # todo: should raise something else

    def handle_text(self, text):
        if not callable(self.state):
            print("StateActivity: Internal error: self.state (%s) is not "
                  "callable." % self.state)
            raise SystemExit # todo: should raise something else

        return self.state(text)



class SelectOneActivity(StateActivity):
    """Have the user select one of a specific range of strings. Useful for menus
    or "please answer yes or no" type situations."""

    def __init__(self, choices, prompt=None, retry_prompt=None):
        super(SelectOneActivity, self).__init__()

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
            return ActivityStatus(output=self.retry_prompt)



class AskYesOrNoActivity(SelectOneActivity):
    """Only accept a "yes" or a "no"."""
    def __init__(self, prompt=None, retry_prompt=None):
        super(AskYesOrNoActivity, self).__init__(["yes", "no"],
                                                 prompt,
                                                 retry_prompt)



class AskStringActivity(Activity):
    """Accept any non-emtpy string."""
    pass



class AskIntActivity(Activity):
    """Only accept strings that can be converted to int."""
    pass


class ActivityStatus(object):
    "Returned from activities."

    def __init__(self, output, result=None, done=False):
        self.output = output
        self.result = result
        self.done = done

