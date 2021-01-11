from helpers.ResistorColourCode import COLOUR_NAMES
from helpers.ResistorColourCode import ResistorDecoder
from main import AddOhmsBot
from twitchbot import Command


@Command("resistor")
async def resistor(msg, *colors):
    # Check to make sure all of the colors are in the list of valid colors
    for color in colors:
        if color not in COLOUR_NAMES:
            await msg.reply(f"{color} is not a valid color")
            return

    r = ResistorDecoder()

    try:
        a = r.decode(list(colors))
        if len(a) == 0:
            await msg.reply(f"{AddOhmsBot.msg_prefix} Invalid combination.")
    except ValueError as e:
        await msg.reply(e)
        return

    q = str(a[0])
    await msg.reply(q)
