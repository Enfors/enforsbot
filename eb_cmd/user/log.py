"""Make a log entry, like a diary."""

import eb_activities.eb_note as eb_note
import eb_cmd.admin.eb_admin_cmd as eb_admin_cmd


class Cmd(eb_admin_cmd.AdminCmd):
    "Make a log entry."

    def __init__(self):
        super().__init__("log")

        self.add_rule("log")

    def rule_log(self, user, args):
        eb_note.NoteActivity(user, require_name=True)
        return "Log entry started. "
