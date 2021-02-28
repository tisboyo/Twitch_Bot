from helpers.ResistorColourCode import COLOUR_NAMES
from helpers.ResistorColourCode import ResistorDecoder
from main import bot
from twitchbot import Command


@Command("resistor")
async def resistor(msg, *colors):

    if len(colors) == 0:
        await msg.reply(f"{bot.msg_prefix}Try: !resistor brown black red gold")
        return

    # Check to make sure all of the colors are in the list of valid colors
    for color in colors:
        if color not in COLOUR_NAMES:
            await msg.reply(f"{color} is not a valid color")
            return

    r = ResistorDecoder()

    reply = "@tisboyo, something unexpected happened here."
    try:
        decoded = r.decode(list(colors))
        len_decoded = len(decoded)
        if len_decoded == 0:
            reply = "Invalid combination."
        elif len_decoded == 1:
            reply = str(decoded[0])
        elif len_decoded > 1:
            reply = "Multiple possible values. "
            for value in decoded:
                reply += str(value) + ", "

    except ValueError as e:
        reply = e

    await msg.reply(f"{bot.msg_prefix}{reply}")
