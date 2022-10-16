import discord
import json

GUILD_ID = 989875050264002560

TOKEN_FILE="discord_token.json"

class SingleMessageSender(discord.Client):
    def __init__(self, channel_name, message='Hello, World'):
        super().__init__(intents=discord.Intents.default())
        self.channel_name = channel_name
        self.message = message
        self.__loadToken()
        self.run(self.token)

    def __loadToken(self):
        with open(TOKEN_FILE) as json_data:
            self.token = json.load(json_data)["bot_token"]

    async def on_ready(self):
        channel = discord.utils.get(self.get_all_channels(), name=self.channel_name)

        if (channel == None):
            #Creates channel in exercises category if it doesnt exist
            guild = await self.fetch_guild(int(GUILD_ID))
            category = discord.utils.get(self.get_all_channels(), name="exercises")
            channel = await guild.create_text_channel(self.channel_name, category=category)

        await channel.send(self.message)
        await self.close()
        self.loop.stop()