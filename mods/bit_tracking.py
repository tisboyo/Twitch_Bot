from data import load_data, save_data

from twitchbot import Mod, PubSubData


class BitTracking(Mod):
    def __init__(self) -> None:
        super().__init__()
        print("BitTracking loaded")
        self.user_data = dict()
        self.file_name = "bit_tracking"

    async def on_pubsub_bits(self, raw: PubSubData, data) -> None:
        self.user_data = await load_data(self.file_name)

        user = self.user_data.get(data.username, False) or dict()

        user["total_bits_used"] = data.total_bits_used
        user["total_bits_seen_by_bot"] = data.bits_used + user.get("total_bits_seen_by_bot", 0)

        self.user_data[data.username] = user

        await save_data(self.file_name, self.user_data)
        print(self.user_data)
