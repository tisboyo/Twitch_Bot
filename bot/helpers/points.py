from typing import Callable

from twitchbot.message import Message


class Points:
    def __init__(
        self,
        function_to_call_on_success: Callable,
        emojis: int = 0,
        channel_points: int = 0,
        bits: int = 0,
        commands: int = 0,
        mod_commands: int = 0,
        unique_users: int = 0,
        require_all: bool = True,
    ):
        """Create a check for points to activate a function

        Args:
            function_to_call_on_success (Callable): The function to be called on success.
            emojis (int, optional): Number of emojis required. Defaults to 0.
            channel_points (int, optional): Number of channel points required. Defaults to 0.
            bits (int, optional): Number of bits required. Defaults to 0.
            commands (int, optional): Number of commands used. Defaults to 0.
            mod_commands (int, optional): Number of mod commands used. Defaults to 0.
            unique_users (int, optional): Number of unique users needed. Defaults to 0.
            require_all (bool, optional): Require all of the options or False to trigger on any at their threshold . Defaults to True.
        """  # noqa E501

        self.run = function_to_call_on_success
        self.emojis_required = emojis
        self.channel_points_required = channel_points
        self.bits_required = bits
        self.commands_required = commands
        self.mod_commands_required = mod_commands
        self.unique_users_required = unique_users
        self.require_all = require_all

        if (
            self.channel_points_required == 0
            and self.bits_required == 0
            and self.commands_required == 0
            and self.mod_commands_required == 0
        ):
            raise TypeError("One of channel_points, bits, commands or mod_commands required.")

        # Set the default starting values.
        self.reset()

    def reset(self) -> None:
        """Resets the current object"""
        self.emoji = 0
        self.channel_points = 0
        self.bits = 0
        self.commands = 0
        self.mod_commands = 0
        self.unique_users = dict()
        self.unique_users["emojis"] = set()
        self.unique_users["channel_points"] = set()
        self.unique_users["bits"] = set()
        self.unique_users["commands"] = set()
        self.unique_users["mod_commands"] = set()

    def check(
        self, msg: Message, emojis: int = 0, channel_points: int = 0, bits: int = 0, commands: int = 0, mod_commands: int = 0
    ) -> bool:
        """Add the new points to the running total and return True if requirements are met.

        Args:
            emojis (int, optional): How many emojis to add. Defaults to 0.
            channel_points (int, optional): How many channel points to add. Defaults to 0.
            bits (int, optional): How many bits to add. Defaults to 0.
            commands (int, optional): How many commands to add. Defaults to 0.
            mod_commands (int, optional): How many mod commands to add. Defaults to 0.

        Returns:
            bool: True if requirements have been met, False otherwise.
        """
        # Increase the counts
        if self.unique_users_required > 0:  # Track unique users
            # Only increase if the user hasn't been seen yet.
            if emojis and msg.author not in self.unique_users["emojis"]:
                self.emojis += emojis
                self.unique_users["emojis"].add(msg.author)

            if channel_points and msg.author not in self.unique_users["channel_points"]:
                self.channel_points += channel_points
                self.unique_users["channel_points"].add(msg.author)

            if bits and msg.author not in self.unique_users["bits"]:
                self.bits += bits
                self.unique_users["bits"].add(msg.author)

            if commands and msg.author not in self.unique_users["commands"]:
                self.commands += commands
                self.unique_users["commands"].add(msg.author)

            if mod_commands and msg.author not in self.unique_users["mod_commands"]:
                self.mod_commands += mod_commands
                self.unique_users["mod_commands"].add(msg.author)

        else:  # Not tracking unique users
            self.channel_points += channel_points
            self.bits += bits
            self.commands += commands
            self.mod_commands += mod_commands

        # Check if conditions have been met
        if self.require_all and (
            self.channel_points >= self.channel_points_required
            and self.bits >= self.bits_required
            and self.commands >= self.commands_required
            and self.mod_commands >= self.mod_commands_required
        ):  # All conditions have been met
            return True

        elif not self.require_all and (
            self.channel_points >= self.channel_points_required
            or self.bits >= self.bits_required
            or self.commands >= self.commands_required
            or self.mod_commands >= self.mod_commands_required
        ):  # Any of the conditions are met
            return True

        else:  # Conditions not yet met
            return False

    def status(self) -> dict:
        """Get the current point status

        Returns:
            dict: Dictionary containing the current point status
        """

        return dict(
            channel_points=self.channel_points,
            channel_points_required=self.channel_points_required,
            bits=self.bits,
            bits_required=self.bits_required,
            commands=self.commands,
            commands_required=self.commands_required,
            mod_commands=self.mod_commands,
            mod_commands_required=self.mod_commands_required,
        )
