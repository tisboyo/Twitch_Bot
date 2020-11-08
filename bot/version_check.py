from twitchbot import BOT_VERSION

# Check to make sure the library is new enough for all needed functions
NEEDED_VERSION = (1, 16, 10)

if NEEDED_VERSION > BOT_VERSION:
    from os import _exit

    print("".center(80, "*"))
    print("PythonTwitchBotFramework needs to be updated ")
    print(f"Current version: {BOT_VERSION}")
    print(f"Needed version: {NEEDED_VERSION}")
    print("Run pipenv install")
    print("".center(80, "*"))
    _exit(0)
