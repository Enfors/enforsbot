#!/usr/bin/env python3

"eb_user.py by Christer Enfors (c) 2016"

from __future__ import print_function

class User(object):
    "Keep track of the same human across multiple protocols."

    def __init__(self, config, name=None, password=None, protocols={}):
        self.config = config
        self.name = name
        self.password = password
        self.protocols = protocols
        self.activities = []

    def identify(self, name, password=None):
        "Called when the user manually identifies themselves."
        self.name = name.lower()
        self.password = password

    def find_identifier_by_protocol(self, protocol):
        "Given a protocol, return the identifier."
        try:
            return self.protocols[protocol]["identifier"]
        except KeyError:
            return None

    def add_protocol(self, protocol, identifier):
        """
        Called to connect this user to a new protcol.
        Example:
        # Add the Twitter user @enfors to this user:
        user.add_protocol("Twitter", "Enfors")
        """
        self.protocols[protocol]["identifier"] = identifier

    def insert_activity(self, activity):
        "Add an activity to the start of the queue."
        self.activities.insert(0, activity)

    def push_activity(self, activity):
        "Add an activity to the end of the queue."
        self.activities.append(activity)

    def remove_activity(self):
        "Remove and return the first activity on the queue."
        if len(self.activities) < 1:
            return None
        activity = self.activities[0]
        del self.activities[0]
        return activity

    def pop_activity(self):
        "Remove and return the activity at the end of the list."
        if len(self.activities) < 1:
            return None
        return self.activities.pop()

    def current_activity(self):
        "Return the current (read: first) activity on the queue."
        if len(self.activities) < 1:
            return None
        else:
            return self.activities[0]

    def __repr__(self):
        output = "User: %s\n- Protocols:" % self.name
        for protocol in self.protocols.keys():
            output += "\n  - %s:" % protocol

            for data in self.protocols[protocol]:
                output += "\n    - %-14s: %s" % (data,
                                                 self.protocols[protocol][data])

        return output


class UserHandler(object):
    "Keep track of all users."

    def __init__(self, config):
        self.config = config
        enfors = User(config=self.config,
                      protocols={"Twitter":
                                 {"identifier": "Enfors"},
                                 "Telegram":
                                 {"identifier": "167773515"},
                                 "IRC":
                                 {"identifier": "Enfors"}})
        indra = User("Indra", self.config,
                     protocols={"Twitter":
                                {"identifier": "IndraEnfors"}})
        self.users = [enfors, indra]

    def find_user_by_identifier(self, protocol, identifier):
        "Given a protocol and identifier, find and return a user."

        identifier = str(identifier)

        for user in self.users:
            try:
                if user.protocols[protocol]["identifier"].lower() == \
                   identifier.lower():
                    return user
            except KeyError:
                continue

        return None

    def test(self):
        "For testing only."
        for user in self.users:
            print(user)

        print("Looking for Enfors:")
        print(self.find_user_by_identifier("Twitter", "Enfors"))

        print("Looking for Indra:")
        print(self.find_user_by_identifier("Twitter", "IndraEnfors"))



if __name__ == "__main__":
    UserHandler().test()
