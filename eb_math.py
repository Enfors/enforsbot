"eb_math.py by Christer Enfors (c) 2016"

from __future__ import print_function

import time

import math_engine.engine as math_engine

import eb_activity

class MathDrill(eb_activity.Activity):
    "Activity for practicing math."

    def __init__(self, user): # pylint: disable=super-init-not-called
        self.user = user
        self.name = "MathDrill"
        math_user = math_engine.User(user.name)
        self.drill = math_engine.MultiplicationDrill(math_user,
                                                     limit=12,
                                                     num_questions=5)
        self.last_answer_time = None
        self.elapsed_time = 0
        self.score = None
        self.started = False

    def start(self, text): # pylint: disable=unused-argument
        "Start the activity."
        pass

    def end(self):
        "Called at end of drill. Returns a string to the user."

        minutes = int(self.elapsed_time / 60)
        if minutes is 1:
            time_output = "1 minute, "
        elif minutes is not 0:
            time_output = "%d minutes, " % minutes
        else:
            time_output = ""

        time_output += "%d seconds. " % (self.elapsed_time % 60)

        output = "\nTime: " + time_output

        self.score = self.calc_score()
        output += "\nScore: %d points." % self.score
        return output

    def handle_text(self, text):
        """Handle incoming text from the user, return
        math_engine.ActivityStatus object or None if we don't want to
        repond to this text.
        """
        if self.last_answer_time:
            used_time = time.time() - self.last_answer_time
            if used_time > 30:
                used_time = 30
            self.elapsed_time += used_time

        self.last_answer_time = time.time()

        if not self.started:
            self.started = True
            return self.drill.start()
        else:
            status = self.drill.recv_input(text)
            if status.done:
                end_ret = self.end()

                if end_ret is not None:
                    status.output += end_ret
            return status

    def calc_score(self):
        "Calculate a score for the user and the end of the drill."

        avg_time = self.elapsed_time / self.drill.num_questions

        score = (30 - avg_time) * (self.drill.num_questions /
                                   self.drill.num_correct)
        score *= self.drill.limit
        return score

