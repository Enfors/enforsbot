#!/usr/bin/env python3
"""
Loads commands from specified directories.
"""

import doctest
import importlib
import os


class CmdsLoader():
    """Loads commands from the specified directories.

    If you instanciate it without arguments, it will not automatically
    load any commands:

    >>> loader = CmdsLoader()
    >>> len(loader)
    0

    But you can load commands manually later:

    >>> loader.load_cmds(["user"])
    >>> len(loader)
    3

    Also, you can load commands directly upon instanciation, by specifying
    in which directories to look for commands:

    >>> loader = CmdsLoader(["user"])

    Once commands are loaded, you can look for a specific command in a
    list of directories. Here, we look for the foo command in the user
    directory:

    >>> loader.find_cmd("foo", ["user"])
    Cmd("foo")
    >>> loader.find_cmd("ping", ["user"])
    Cmd("ping")

    None will be returned if we look for something which doesn't exist,
    or which doesn't exist where we look for it.

    >>> loader.find_cmd("flap", ["user"])
    >>> loader.find_cmd("foo", ["admin"])
    """

    def __init__(self, cmd_types=None):
        if cmd_types is None:
            cmd_types = []
        self.cmds_dicts = {}

        self.load_cmds(cmd_types)

    def load_cmds(self, cmd_types):
        """Load all commands of all types in cmd_types."""

        for cmd_type in cmd_types:
            self.load_cmd_type(cmd_type)

    def load_cmd_type(self, cmd_type):
        """Load all commands of the type specified with cmd_type."""

        cmd_dict = {}

        file_names = [name[:-3] for name in os.listdir("eb_cmd/" + cmd_type)
                      if name.endswith(".py")
                      if not name.startswith("_")
                      if not name.startswith("eb_")]

        for file_name in file_names:
            mod = importlib.import_module("eb_cmd.%s.%s" %
                                          (cmd_type, file_name))
            cmd_dict[file_name] = mod.Cmd()

        self.cmds_dicts[cmd_type] = cmd_dict

    def find_cmd(self, cmd_name, cmd_types):
        """Look for the command cmd_name among cmd_types."""

        for cmd_type in cmd_types:
            try:
                cmd = self.cmds_dicts[cmd_type][cmd_name]
                return cmd
            except KeyError:
                pass

    def __len__(self):
        num_cmds = 0
        for cmd_type in self.cmds_dicts:
            num_cmds += len(self.cmds_dicts[cmd_type])

        return num_cmds


if __name__ == "__main__":
    doctest.testmod()
