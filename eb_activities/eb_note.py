"""activity for receiving multiline input from the user."""

import eb_activity as act


class NoteActivity(act.StateActivity):
    """The activity will read line after line, until it gets a line that says
    "done" and nothing else.

    >>> user = make_test_user()
    >>> note_act = NoteActivity(user)
    >>> print(note_act.start("note"))
    Please enter note. Enter "done" on a line of its own when done.
    >>> print(note_act.handle_text("This is the first line"))
    Line received.
    >>> print(note_act.handle_text("This is the second line"))
    Line received.
    >>> print(note_act.handle_text("done"))
    Note received.
    User entered: This is the first line
    This is the second line
    Done
    """

    def __init__(self, user, require_name=False):
        super().__init__(user)

        self.require_name = require_name
        self.note = ""

    def start(self, user):
        self.state = self.awaiting_line

        return act.ActivityStatus(output='Please enter note. Enter "done" '
                                  'on a line of its own when done.')

    def awaiting_line(self, text):
        """Add some text to the note. If text == "done", then stop."""

        if text == "done":

            print("Note ---------------")
            for line in self.note.split("\n"):
                print(">", line)
            print("--------------------")

            if self.require_name:
                self.state = self.awaiting_name
                name_act = act.AskStringActivity(self.user,
                                                 prompt="Please enter a name "
                                                 "for this note:")
                return name_act.start()
            return act.ActivityStatus(output="Note received.",
                                      result=self.note.strip(),
                                      done=True)
        else:
            self.note += text + "\n"
            return act.ActivityStatus(output="Line received.")

    def awaiting_name(self, text):
        """Wait for a name for the note."""

        name = text

        return act.ActivityStatus(output="Name {} received.".format(name),
                                  result=name + "\n" + self.note.strip(),
                                  done=True)