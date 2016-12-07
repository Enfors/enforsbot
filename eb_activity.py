"eb_activity.py by Christer Enfors (c) 2016"

from __future__ import print_function

class Activity(object):
    "An activity - interaction between user and bot that spans multiple messages."

    def __init__(self):
        pass

    def handle_text(self, text): # pylint: disable=unused-argument,no-self-use
        "Handle text from a user. This function must be overridden."
        print("Activity.handle_text(): Unimplemented")
        return False
