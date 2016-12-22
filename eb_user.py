#!/usr/bin/env python3

"eb_user.py by Christer Enfors (c) 2016"

from __future__ import print_function

import datetime
import sqlite3

class User(object):
    "Keep track of the same human across multiple protocols."

    known_protocols = ("Twitter", "Telegram", "IRC")

    def __init__(self, config, database, user_id=None, name=None,
                 password=None, protocols={}):
        # pylint: disable=dangerous-default-value
        self.config = config
        self.database = database
        self.user_id = user_id
        self.name = name
        self.password = password

        for protocol in self.known_protocols:
            try:
                protocols[protocol]
            except KeyError:
                protocols[protocol] = None

        self.protocols = protocols
        self.activities = []

    def identify(self, name, password=None):
        "Called when the user manually identifies themselves."
        self.name = name.lower()
        self.password = password

    def find_identifier_by_protocol(self, protocol):
        "Given a protocol, return the identifier."
        try:
            return self.protocols[protocol]
        except KeyError:
            return None

    def add_protocol(self, protocol, identifier):
        """
        Called to connect this user to a new protcol.
        Example:
        # Add the Twitter user @enfors to this user:
        user.add_protocol("Twitter", "Enfors")
        """
        self.protocols[protocol] = identifier

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

    def save(self):
        "Save the user."
        print("Saving user '%s'" % self.name)

        with self.config.lock, self.database:
            cur = self.database.cursor()

            cur.execute("insert or replace into USER "
                        "(USER_ID, NAME, TWITTER_ID, TELEGRAM_ID, IRC_ID, " \
                        "CREATED) values "
                        "((select USER_ID from USER where NAME = '?'), "
                        "?, ?, ?, ?, ?);",
                        (self.name,
                         self.protocols["Twitter"],
                         self.protocols["Telegram"],
                         self.protocols["IRC"],
                         datetime.datetime.now()))

            # The user is saved. Now, find it's user_id number.
            cur.execute("select USER_ID from USER " \
                        "where NAME=?", (self.name,))
            self.user_id = cur.fetchone()

    def save_data(self, field, val):
        "Save arbitrary value for the user to the database."

        field = str(field)
        val = str(val)

        print("Saving %s=%s" % (field, val))
        with self.config.lock, self.database:
            cur = self.database.cursor()

            cur.execute("select FIELD from USER_DATA "
                        "where USER_ID=? and FIELD=?",
                        (self.user_id, field))
            row = cur.fetchone()

            if row is None:
                cur.execute("insert into USER_DATA "
                            "values (?, ?, ?, ?)",
                            (self.user_id, field, val,
                             datetime.datetime.now()))
            else:
                cur.execute("update USER_DATA "
                            "set VAL=?, LAST_UPDATE=? "
                            "where USER_ID=? and FIELD=?",
                            (val, datetime.datetime.now(),
                             self.user_id, field))

    def load_data(self, field):
        "Load arbitrary user data, previously saved with save_data."

        field = str(field)

        with self.config.lock, self.database:
            cur = self.database.cursor()

            cur.execute("select VAL from USER_DATA "
                        "where USER_ID=? and FIELD=?",
                        (self.user_id, field))
            val = cur.fetchone()

        return val

    def __repr__(self):
        output = "User: %s[%s]" % (self.name, str(self.user_id))
        #output += "\n- Protocols:" % self.name
        #for protocol in self.protocols.keys():
        #    output += "\n  - %s:%s" % (protocol, self.protocols[protocol])

        return output


class UserHandler(object):
    "Keep track of all users."

    def __init__(self, config, database):
        self.config = config
        self.database = database

        christer = User(self.config, self.database, None, "Christer",
                        protocols={"Twitter": "Enfors",
                                   "Telegram": "167773515",
                                   "IRC": "Enfors"})

        indra = User(self.config, self.database, None, "Indra",
                     protocols={"Twitter": "IndraEnfors"})

        self.users = []
        #self.users = [christer, indra]

    def find_user_by_identifier(self, protocol, identifier):
        "Given a protocol and identifier, find and return a user."

        identifier = str(identifier)

        # If the user is online, return them.
        user = self.find_online_user_by_identifier(protocol, identifier)
        if user:
            return user

        # The user is not online. Load them from the database, or create
        # them if they're not already there.
        name = None
        twitter_id = None
        telegram_id = None
        irc_id = None
        password = None

        if protocol.lower() == "twitter":
            col = "TWITTER_ID"
        elif protocol.lower() == "telegram":
            col = "TELEGRAM_ID"
        elif protocol.lower() == "irc":
            col = "IRC_ID"
        else:
            print("find_user_by_identifier(): Unknown protocol '%s'" %
                  protocol)

        query = "select USER_ID, NAME, PASSWORD, TWITTER_ID, TELEGRAM_ID, " \
                "IRC_ID from USER where %s=?" % col

        with self.config.lock, self.database:
            cur = self.database.cursor()
            cur.execute(query, (identifier,))

            try:
                (user_id, name, password, twitter_id, telegram_id, \
                 irc_id) = cur.fetchone()
                user = User(self.config, self.database, user_id, name,
                            password,
                            {"Twitter": twitter_id,
                             "Telegram": telegram_id,
                             "IRC": irc_id})
            except TypeError:
                protocols = {"Twitter": twitter_id,
                             "Telegram": telegram_id,
                             "IRC": irc_id}
                protocols[protocol] = identifier

                user = User(self.config, self.database, None, name, password,
                            protocols)
                # Don't save the user now; wait until they have given
                # us their name.

        self.users.append(user)
        return user

    def find_online_user_by_identifier(self, protocol, identifier):
        "Find a user we've talked to previously, since last restart."

        for user in self.users:
            if user.protocols[protocol] == identifier:
                return user

        return None

    def test(self):
        "For testing only."
        for user in self.users:
            print(user)

        print("Looking for Enfors:")
        print(self.find_user_by_identifier("Twitter", "Enfors"))

        print("Looking for Indra:")
        print(self.find_user_by_identifier("Twitter", "IndraEnfors"))



