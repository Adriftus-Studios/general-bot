
import discord
import pymongo.errors

import config
import time
import datetime
import aiofiles
import random
from secrets import MONGO_CLIENT

from discord.ext import commands

db_client = MONGO_CLIENT
message_db = db_client.Messages
user_db = db_client.Users
minecraft_db = db_client.Minecraft


class EventLogger(commands.Cog, name="Event Logger"):
    """
    A class cog that holds the EventLogger object.

    ...

    Attributes
    ----------
    name : str
        name of the cog, used in reporting

    Methods
    -------
    message_to_discord(payload, message_data, payload_guild_id):
        Sends a log message to discord.

    serialize_to_db(message):
        Writes data to the database for later retrieval.

    deserialize_from_db(message):
        Returns full message from the messages_db
    """
    def __init__(self, bot: commands.Bot):
        """
        Constructs all the necessary attributes for the EventLogger object.

        Parameters
        ----------
            bot : DiscordObject
                Discord object for the bot class
        """
        self.bot = bot

    # Log Events --
    @commands.Cog.listener()
    async def on_message(self, message):
        print(message.content)
        # Reporting channel (Avoid circular logs)
        if message.channel.id == 989509544218611753:
            return

        try:
            await self.serialize_to_db(message)

        except Exception as err:
            print(f"An error has occurred: {err}")

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        """
        channel_id¶ [int]
        The channel ID where the deletion took place.

        guild_id [int]
        The guild ID where the deletion took place, if applicable.

        message_id [int]
        The message ID that got deleted.

        cached_message Optional[Message]
        The cached message, if found in the internal message cache.
        """
        admin_channels = [626086306606350366, 651870920599928862]
        blacklist_channels = []
        # Send full db.Messages collection info to logging channel
        try:
            # message_data = self.serialize_to_db(payload)
            message_data = message_db.find_one({"_id": f"{payload.id}"})
            if payload.cached_message is not None:
                message_data = message_data
            elif message_db.find({'_id': f'{payload.message_id}'}).count() > 0:
                message_data = await self.deserialize_from_db(payload)

            if payload.channel_id in admin_channels:
                await self.message_to_discord(payload, message_data, 712309385019523155)
            elif payload.channel_id in blacklist_channels:
                pass
            else:
                await self.message_to_discord(payload, message_data, 989509544218611753)
        except Exception as err:
            print(f'An error has occurred: {err}')

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        print(f"Channel Deleted - {channel}")

    @commands.Cog.listener()
    async def on_interaction(self, ctx: discord.Interaction):
        try:
            executed_command = ctx.command.name
            message_content = f"""
            - Executed **{executed_command}** command in {ctx.guild} 
            - (ID: {ctx.guild.id}) by {ctx.user} (ID: {ctx.user.id})\n
            ----------------------------------------------------------------\n
            """
            async with aiofiles.open("message_log.txt", "a") as f:
                await f.writelines(message_content)

            if len(message_content) > 1000:
                message_content = f"{message_content[:1000]}...[Continued]"

            embed = discord.Embed(
                title=f"*** Command Log Entry ***",
                description=f"○○○○○○○○○○○○○○○○○○○○○○○○○○○",
                color=config.success)
            embed.add_field(name=f"Command Executed - ", value=f"{message_content}", inline=False)
            embed.set_footer(text=f"• {time.ctime(time.time())}")

            try:
                # Sends to discord-logs channel
                await self.bot.get_channel(989509544218611753).send(embed=embed)
            except Exception as err:
                print(f'An error has occurred: {err}')
            print(
                f"Executed {executed_command} command in {ctx.guild}"
                f"(ID: {ctx.guild.id}) by {ctx.user} (ID: {ctx.user.id})")
        except Exception as err:
            print(err)

    async def message_to_discord(self, payload, message_data, send_channel):
        """
        Parameters
        ----------
            payload : channel_id [int], guild_id [Otional[int]], message_id [int], cached_message [Optional[Message]]
                The channel ID where the deletion took place.

            message_data : returned from EventLogger.serialize_to_db(message) [str]
                Message Data information saved to a dictionary.

            send_channel : channel_id [int]
                Channel ID that the logged information will be sent to.
                    Currently, this will go to #discord-logs (989509544218611753)

        """
        current_time = time.ctime(time.time())
        guild = self.bot.get_guild(payload.guild_id)
        deleter = ""
        deleted_channel_id = 0
        deleted_owner = 0

        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.message_delete):
            deleted_channel_id = entry.extra.channel.id
            deleted_owner = entry.target.id
            deleter = entry.user

        # Change this to query the db
        if int(payload.channel_id) != int(deleted_channel_id) or int(message_data["author_id"]) != int(deleted_owner):
            deleter = self.bot.get_user(int(message_data["author_id"]))

        message_content = f"""
                *** Message Log Entry - {current_time} ***
                - {message_data["author_full_name"]} had their message deleted -
                  **__Deleted By__**: {deleter}#{deleter.discriminator}
                  **__Message Author__**: {message_data["author_full_name"]}
                  **__Author ID__**: {message_data["author_id"]}
                  **__Channel Info__**: <#{message_data["channel_id"]}> / {message_data["channel_id"]}
                  **__Server Name__**: {message_data["server_name"]}

                  **__Message:__**\n{message_data["contents"]}
                ----------------------------------------------------------------\n
                """

        if len(message_content) > 1000:
            message_content = f"{message_content[:1000]}...[Continued]"

        embed = discord.Embed(
            title=f"*** Message Log Entry ***",
            description=f"○○○○○○○○○○○○○○○○○○○○○○○○○○○",
            color=config.success)
        embed.add_field(name=f"Message Deleted - ", value=f"{message_content}", inline=False)
        embed.set_footer(text=f"• {time.ctime(time.time())}")

        try:
            await self.bot.get_channel(send_channel).send(embed=embed)
        except Exception as err:
            print(f'An error has occurred: {err}')

    # DB serializer/deserializer
    async def serialize_to_db(self, message):
        """
        Parameters
        ----------
            message : https://discordpy.readthedocs.io/en/latest/api.html?highlight=message#discord.Message
                The message object being passed to serialize_to_db().
                    author [Member, abc.User]
                    channel [Channel]
                    content [str]
                    guild [GuildObject]
                    id [int]
        """
        current_time = datetime.datetime.utcnow()

        message_data = {
            "_id": f"{message.id}",
            "time": current_time,
            "author_id": f"{message.author.id}",
            "author_name": f"{message.author.name}",
            "author_full_name": f"{message.author}",
            "channel_id": f"{message.channel.id}",
            "server_name": f"{message.guild.name}",
            "contents": f"{message.content}"
        }

        user_data = {"_id": f"{message.author.id}"}, {'$push': {"message_ids": f"{message.id}"}}, {'upsert': True}

        try:
            user_db.update_one(user_data)
        except Exception as err:
            print(err)
            await self.bot.get_channel(989509544218611753).send(err)

        message_sent = message_db.insert_one(message_data)
        print(f"Message logged - Message ID: {message_sent.inserted_id}")
        return message_data

    @staticmethod
    async def deserialize_from_db(message):
        """
        Parameters
        ----------
            message : https://discordpy.readthedocs.io/en/latest/api.html?highlight=message#discord.Message
                The message object being passed to deserialize_from_db().
                    author [Member, abc.User]
                    id [int]
        """
        x = message_db.find({"_id": f"{message.message_id}"})

        return x

    # Member counter ###################################################################################################
    @commands.Cog.listener()
    async def on_member_join(self, member):

        user_data = {
            "_id": f"{member.id}",
            "linked_accounts": {
                "minecraft": "none",
                "twitch": "none",
                "steam": "none"
            },
            "message_ids": [],
            "joined_date": f"{datetime.datetime.utcnow()}"
        }
        try:
            user_db.insert_one(user_data, upsert=True)

        except pymongo.errors.WriteError:
            print(f"User {member.name} already exists in the database with _id: {member.id}")
        except Exception as err:
            print(err)

        welcome_messages = [
            f"{member.name} is here to kick butt and chew bubblegum. And {member.name} is all out of gum.",
            f"We've been expecting you {member.name}",
            f"Big {member.name} showed up!",
            f"Swoooosh. {member.name} just landed.",
            f"Ermagherd. {member.name} is here."
        ]

        embed = discord.Embed(
            title=f"{member.name} Joined!",
            description=f"{random.choice(welcome_messages)}\n\n- Thank you for joining us {member.mention}",
            color=config.level_up
        )
        embed.set_author(name=f"{member.name}", icon_url=member.avatar)
        embed.add_field(name=f"Account Created:", value=f"<t:{member.created_at.strftime('%s')}:R>", inline=False)

        if member.guild.id == 601677205445279744:
            channel = member.guild.get_channel(619175785772875808)
            await channel.edit(name=f'👦 Member Count: {member.guild.member_count}')

            try:
                channels = [743476824763269150, 601677205445279746]
                for c in channels:
                    await self.bot.get_channel(c).send(embed=embed)

            except Exception as err:
                print(f'An error has occurred: {err}')
            print(f'{member} joined {member.guild.name} ( Current Members: {member.guild.member_count} )')

        else:
            await self.bot.get_channel(626084615660109824).send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel = member.guild.get_channel(619175785772875808)
        await channel.edit(name=f'👦 Member Count: {member.guild.member_count}')

        embed = discord.Embed(
            title=f"{member} Has left!",
            description=f"The door hit {member} on the ass on the way out!",
            color=config.error
        )
        embed.set_author(name=member.name, icon_url=member.avatar)
        try:
            await self.bot.get_channel(743476824763269150).send(embed=embed)
        except Exception as err:
            print(f'An error has occurred: {err}')
        print(f'{member} left {member.guild.name} ( Current Members: {member.guild.member_count} )')


async def setup(bot: commands.Bot):
    await bot.add_cog(
        EventLogger(bot),
        guilds=[
            discord.Object(id=626078288556851230),
            discord.Object(id=601677205445279744)
        ]
    )
