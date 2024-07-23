"""
Discord API module
Important notes:
    - client.run() manages the event loop for you and is blocking
    - client.start() does not manage the event loop for you and is non-blocking
    - Threading is complicated and I don't want to deal with it
    - I cannot figure it out, so I will just bring the bot up and down as needed
"""

import discord

content_authorized: bool = False


class Channels:
    """
    Channel IDs
    """
    GENERAL = 1144379626441945203
    APPROVAL = 1145039433003970571
    STATUS = 1145128516610953238


class StatusClient(discord.AutoShardedClient):

    def __init__(self, status_dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.status_dict = status_dict
        discord.Game(name="Sending status message...")

    async def on_ready(self):
        channel = self.get_channel(Channels.STATUS)
        embed = discord.Embed(title="Status update",
                              colour=discord.Colour(0x3e038c))
        for k, v in self.status_dict.items():
            embed.add_field(name=k, value=v, inline=False)
        await channel.send(embed=embed)
        await self.close()


class ContentApprovalClient(discord.AutoShardedClient):

    def __init__(self, content_dict: dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.content_dict = content_dict
        discord.Game(name="Authorizing content...")

        global content_authorized
        content_authorized = False

    async def on_ready(self):
        channel = self.get_channel(Channels.APPROVAL)

        embed = discord.Embed(title=f"New Content Generated", description="*Awaiting authorization. Read the "
                                                                          "ContentObject details and authorize it by "
                                                                          "reacting with 👍🏻 or reject it by reacting "
                                                                          "with 👎🏻.*",
                              colour=discord.Colour(0x3e038c))
        for k, v in self.content_dict.items():
            embed.add_field(name=k, value=v, inline=False)
        embed.add_field(name="Tags", value="@everyone", inline=True)
        if "media" in self.content_dict and self.content_dict["media"] is not None:
            with open(self.content_dict["media"], "rb") as f:
                file = discord.File(f)
                embed.set_image(url=f"attachment://{self.content_dict['media']}")
                msg = await channel.send(file=file, embed=embed)
        else:
            msg = await channel.send(embed=embed)
        await msg.add_reaction("👍🏻")
        await msg.add_reaction("👎🏻")

    async def on_raw_reaction_add(self, payload):
        global content_authorized
        if payload.emoji.name == '👍🏻':
            channel = self.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            reaction = discord.utils.get(message.reactions, emoji=payload.emoji.name)
            if reaction and reaction.count >= 2:
                await message.create_thread(name="✅ Content authorized")
                content_authorized = True
                await self.close()

        if payload.emoji.name == '👎🏻':
            channel = self.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            reaction = discord.utils.get(message.reactions, emoji=payload.emoji.name)
            if reaction and reaction.count >= 2:
                await message.create_thread(name="🔁 Regenerating content")
                content_authorized = False
                await self.close()


def authorize_content(content_dict, keys):
    token = keys["DISCORD_TOKEN"]
    intents = discord.Intents.default()
    intents.message_content = True

    client = ContentApprovalClient(content_dict=content_dict,
                                   intents=intents)

    client.run(token)

    return content_authorized


def update_status(status_dict, keys):
    token = keys["DISCORD_TOKEN"]
    intents = discord.Intents.default()
    intents.message_content = True

    client = StatusClient(status_dict=status_dict,
                          intents=intents)

    client.run(token)
