"eb_math.py by Christer Enfors (c) 2016"

from __future__ import print_function

import math_engine.engine as math_engine

import eb_activity

class MathDrill(eb_activity.Activity):
    "Activity for practicing math."

    def __init__(self, user): # pylint: disable=super-init-not-called
        self.user = user
        self.name = "MathDrill"
        math_user = math_engine.User(user.name)
        self.drill = math_engine.MultiplicationDrill(math_user,
                                                     starting_limit=12,
                                                     num_questions=5)

    def start(self, text): # pylint: disable=unused-argument
        "Start the activity."
        return self.drill.start()

    def handle_text(self, text):
        """Handle incoming text from the user, return
        math_engine.ActivityStatus object or None if we don't want to
        repond to this text.
        """
        return self.drill.recv_input(text)

