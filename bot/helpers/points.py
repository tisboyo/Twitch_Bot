from dataclasses import dataclass

from twitchbot.message import Message


@dataclass
class Status:
    emojis: int
    emojis_required: int
    channel_points: int
    channel_points_required: int
    bits: int
    bits_required: int
    commands: int
    commands_required: int
    mod_commands: int
    mod_commands_required: int
    unique_users: dict


class Points:
    def __init__(
        self,
        emojis: int = -1,
        channel_points: int = -1,
        bits: int = -1,
        commands: int = -1,
        mod_commands: int = -1,
        unique_users: int = -1,
        require_all: bool = False,
        emoji_cap: int = -1,
    ):
        """Create a check for points to activate a function

        Args:
            emojis (int, optional): Number of emojis required. Defaults to -1.
            channel_points (int, optional): Number of channel points required. Defaults to -1.
            bits (int, optional): Number of bits required. Defaults to -1.
            commands (int, optional): Number of commands used. Defaults to -1.
            mod_commands (int, optional): Number of mod commands used. Defaults to -1.
            unique_users (int, optional): Number of unique users needed. Defaults to -1. Must be > 1
            require_all (bool, optional): Require all of the options or False to trigger on any at their threshold . Defaults to False.
            emoji_cap (int, optional): Number of emojis a user can send. Defaults to -1.
        """  # noqa E501

        self.emojis_required = emojis
        self.channel_points_required = channel_points
        self.bits_required = bits
        self.commands_required = commands
        self.mod_commands_required = mod_commands
        self.unique_users_required = unique_users
        self.require_all = require_all
        self.emoji_cap = emoji_cap

        if (
            self.emojis_required == 0
            and self.channel_points_required == 0
            and self.bits_required == 0
            and self.commands_required == 0
            and self.mod_commands_required == 0
        ):
            raise TypeError("One of emojis, channel_points, bits, commands or mod_commands required.")

        elif self.emojis_required <= self.emoji_cap and self.unique_users_required > 0:
            raise TypeError("One user can trigger event. Clear unique_users or raise emojis_required or lower emoji_cap")
        elif self.unique_users_required == 1:
            raise TypeError("unique_users must be either -1 or > 1. Defaults to -1 when not supplied.")

        # Set the default starting values.
        self.reset()

    def reset(self) -> None:
        """Resets the current object"""
        self.emojis = 0
        self.channel_points = 0
        self.bits = 0
        self.commands = 0
        self.mod_commands = 0
        self.unique_users = dict()
        self.unique_users["emojis"] = dict()
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
            if emojis:
                if msg.author not in self.unique_users["emojis"].keys():
                    self.emojis += emojis
                    self.unique_users["emojis"][msg.author] = emojis
                elif (
                    self.unique_users["emojis"][msg.author] < self.emoji_cap
                ):  # We've seen this user before, but check to see if they are capped yet
                    # Remove their previous counts
                    self.emojis -= self.unique_users["emojis"][msg.author]

                    new_emoji_count = self.unique_users["emojis"][msg.author] + emojis

                    # Set new count for this user at new count or max if they exceeded it
                    self.unique_users["emojis"][msg.author] = (
                        new_emoji_count if new_emoji_count <= self.emoji_cap else self.emoji_cap
                    )

                    # Add the new count
                    self.emojis += self.unique_users["emojis"][msg.author]

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
            self.emojis += emojis
            self.channel_points += channel_points
            self.bits += bits
            self.commands += commands
            self.mod_commands += mod_commands

        # Check if conditions have been met
        if self.require_all and (
            self.check_emoji()
            and self.check_channel_points()
            and self.check_bits()
            and self.check_commands()
            and self.check_mod_commands()
        ):  # All conditions have been met
            self.reset()
            return True

        elif not self.require_all and (
            self.check_emoji()
            or self.check_channel_points()
            or self.check_bits()
            or self.check_commands()
            or self.check_mod_commands()
        ):  # Any of the conditions are met
            self.reset()
            return True

        else:  # Conditions not yet met
            return False

    def check_emoji(self) -> bool:
        """Check if the emoji requirement has been met"""
        # Check to make sure we actually require this, and if it's the trigger number
        if self.emojis >= self.emojis_required and self.emojis_required != -1:
            return True
        else:
            return False

    def check_channel_points(self) -> bool:
        """Check if the channel_points requirement has been met"""
        # Check to make sure we actually require this, and if it's the trigger number
        if self.channel_points >= self.channel_points_required and self.channel_points_required != -1:
            return True
        else:
            return False

    def check_bits(self) -> bool:
        """Check if the bits requirement has been met"""
        # Check to make sure we actually require this, and if it's the trigger number
        if self.bits >= self.bits_required and self.bits_required != -1:
            return True
        else:
            return False

    def check_commands(self) -> bool:
        """Check if the commands requirement has been met"""
        # Check to make sure we actually require this, and if it's the trigger number
        if self.commands >= self.commands_required and self.commands_required != -1:
            return True
        else:
            return False

    def check_mod_commands(self) -> bool:
        """Check if the mod_commands requirement has been met"""
        # Check to make sure we actually require this, and if it's the trigger number
        if self.mod_commands >= self.mod_commands_required and self.mod_commands_required != -1:
            return True
        else:
            return False

    def status(self) -> Status:
        """Get the current point status

        Returns:
            Status: Status dataclass
        """
        status = Status(
            emojis=self.emojis,
            emojis_required=self.emojis_required,
            channel_points=self.channel_points,
            channel_points_required=self.channel_points_required,
            bits=self.bits,
            bits_required=self.bits_required,
            commands=self.commands,
            commands_required=self.commands_required,
            mod_commands=self.mod_commands,
            mod_commands_required=self.mod_commands_required,
            unique_users=self.unique_users,
        )

        return status
