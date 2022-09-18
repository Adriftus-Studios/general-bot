
import discord
import pymongo.errors
import config
import time
import datetime
import random
from secrets import MONGO_CLIENT
from discord import errors
from discord.ext import commands, tasks

db_client = MONGO_CLIENT
message_db = db_client.Messages
user_db = db_client.Users
minecraft_db = db_client.Minecraft


# TODO: Create collection of channel names with messages in them instead of collections of messages
class EventLogger(commands.Cog, name="Event Logger"):
    """
    A class cog that holds the EventLogger object.

    ...
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

        Parameters:
            bot : DiscordObject
                Discord object for the bot class
        """
        self.bot = bot

    # Log Events --
    @commands.Cog.listener()
    async def on_message(self, message):
        # Reporting channel (Avoid circular logs)
        log_channels = [989509544218611753, 712309385019523155]
        ignore_channels = [970208822754963486]
        remove_channels = [992655402825162763]
        pg_channels = [866445773860372500, 979785769986191380, 979785805524529214]
        if message.channel.id in pg_channels:
            with open('bad_words.txt') as b:
                if message.content.contains(i for i in b):
                    message.delete()
        if message.channel.id in log_channels or message.channel.id in ignore_channels:
            return
        if message.channel.id in remove_channels:
            try:
                await message.delete()
            except discord.errors.NotFound:
                print(f'Error not found. Is this an ephemeral message?')
        advert_channel = [1001609798875365396]
        if message.channel.id not in advert_channel:
            if "discord.gg" in message.content:
                await message.delete()
        try:
            await self.serialize_to_db(message)

        except ValueError:
            print("Was not able to serialize message. Contents empty")
        except Exception as err:
            print(f"An error has occurred: {err}")

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        """
        channel_id [int]
        The channel ID where the deletion took place.

        guild_id [int]
        The guild ID where the deletion took place, if applicable.

        message_id [int]
        The message ID that got deleted.

        cached_message Optional[Message]
        The cached message, if found in the internal message cache.
        """
        admin_channels = [626086306606350366, 651870920599928862]
        #  ignorelist Stonks channel
        ignorelist_channels = [970208822754963486]
        # Send full db.Messages collection info to logging channel
        message_col = message_db[f"A_{payload.message_id}"]
        try:
            message_data = message_col.find_one({"_id": f"{payload.message_id}"})
            if payload.cached_message is not None:
                message_data = message_data
            elif message_col.find_one({'_id': f'{payload.message_id}'}):
                message_data = await self.deserialize_from_db(payload)

            if payload.channel_id in admin_channels:
                await self.message_to_discord(payload, message_data, 712309385019523155)
                await message_col.drop()
                print("Message Collection removed from DB")
            elif payload.channel_id in ignorelist_channels:
                pass
            else:
                await self.message_to_discord(payload, message_data, 965027742154358814)
                await self.message_to_discord(payload, message_data, 989509544218611753)
                await message_col.drop()
                print("Message Collection removed from DB")

        except Exception as err:
            print(f'An error has occurred: {err}')

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        print(f"Channel Deleted - {channel}")

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        if before.id != after.id:
            channel_col = message_db[f'C_{before.id}']
            channel_col.rename(f'C_{after.id}')

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        if before.avatar != after.avatar:
            print(f'{after.user} has changed their avatar!')
        elif before.user != after.user:
            print(f'{after.user} as changed their username from {before.user} to {after.user}')
        # before/after discriminator

    @commands.Cog.listener()
    async def on_guild_emojis_update(self, guild, before, after):
        removed_emojis = [x for x in before if x not in after]
        added_emojis = [x for x in after if x not in before]
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.emoji_update):
            emoji_updater = entry.user.name
        if before.len() == after.len():
            return
        embed = discord.Embed(
            title=f"*** Emojis Updated in {guild.name}***",
            description=f"○○○○○○○○○○○○○○○○○○○○○○○○○○○",
            color=config.success)

        try:
            for e in removed_emojis:
                embed.add_field(name=f'{emoji_updater} Removed: {e}', value=f'`{str(e)}`', inline=False)
                embed.add_field(name='ID: ', value=f'{e.id}', inline=True)
            for e in added_emojis:
                embed.add_field(name=f'{emoji_updater} Added: {e}', value=f'`{str(e)}`', inline=False)
                embed.add_field(name='ID: ', value=f'{e.id}', inline=True)
        except Exception as err:
            print(err)
        embed.set_footer(text=f"• {time.ctime(time.time())}")

        await self.bot.get_channel(989509544218611753).send(embed=embed)

    @commands.Cog.listener()
    async def on_interaction(self, itx: discord.Interaction):
        try:
            executed_command = itx.command.name
            message_content = f"""
            *** Command Log Entry - {time.ctime(time.time())} ***
                  **__Command Executed__**: **/{executed_command}**
                  **__Executed By__**: {itx.user}
                  **__User ID__**: {itx.user.id}
                  **__Channel Info__**: {itx.channel.name}
                  **__Server Name__**: {itx.guild}

            ----------------------------------------------------------------\n
            """

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
                f"Executed {executed_command} command in {itx.guild}"
                f"(ID: {itx.guild.id}) by {itx.user} (ID: {itx.user.id})")
        except Exception as err:
            print(err)

    async def message_to_discord(self, payload, message_data, send_channel):
        """
        Parameters
        ----------
            payload : channel_id [int], guild_id [Optional[int]], message_id [int], cached_message [Optional[Message]]
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

                  **__Deleted By__**: {deleter}
                  **__Message Author__**: {message_data["author_full_name"]}
                  **__Author ID__**: {message_data["author_id"]}
                  **__Channel Info__**: <#{message_data["channel_id"]}> / {message_data["channel_id"]}
                  **__Server Name__**: {message_data["server_name"]}

                  **__Message:__**\n```{message_data["contents"]}```
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

        # user_data = {"_id": f"{message.author.id}"}, {'$push': {"message_ids": f"{message.id}"}}, {'upsert': True}
        user_col = user_db[f"U_{message.author.id}"]
        message_col = message_db[f"A_{message.id}"]

        try:
            user_col.update_one({
                "_id": f"{message.author.id}"},
                {'$push': {"message_ids": f"{message.id}"}},
                upsert=True)
            message_col.insert_one(message_data)
        except Exception as err:
            print(err)
            await self.bot.get_channel(989509544218611753).send(f"{err}")

        print(f"Message logged - Message ID: {message.id}")
        return message_data

    @staticmethod
    async def deserialize_from_db(payload):
        """
        Parameters
        ----------
            payload : https://discordpy.readthedocs.io/en/latest/api.html?highlight=message#discord.Message
                The message object being passed to deserialize_from_db().
                    channel_id [int]
                    The channel ID where the deletion took place.

                    guild_id [int]
                    The guild ID where the deletion took place, if applicable.

                    message_id [int]
                    The message ID that got deleted.

                    cached_message Optional[Message]
                    The cached message, if found in the internal message cache.
        """
        message_col = message_db[f"A_{payload.message_id}"]
        x = message_col.find({"_id": f"{payload.message_id}"})

        return x

    # Member counter ###################################################################################################
    # @tasks.loop(seconds=600.0)
    # async def update_member_count(self):
    #     channel = self.bot.get_channel(619175785772875808)
    #     await channel.edit(name=f'👦 Member Count: {self.bot.get_guild(601677205445279744).member_count}')
    #     print(f"Member count channel updated to: {self.bot.get_guild(601677205445279744).member_count}")

    async def numify(self, number: int):
        ending = {1: 'st', 2: 'nd', 3: 'rd'}
        string_num = str(number)
        return_value = int(string_num[-1])
        return f'{number}{ending.get(return_value, "th")}'

    @commands.Cog.listener()
    async def on_member_join(self, member):
        member_count: int = self.bot.get_guild(601677205445279744).member_count

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
        user_col = user_db[f"A_{member.id}"]
        try:
            user_col.insert_one(user_data)

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
            title=f"{member.name} is the {self.numify(member_count)} member to join!",
            description=f"{random.choice(welcome_messages)}\n\n- Thank you for joining us {member.mention}",
            color=config.level_up
        )
        embed.set_author(name=f"{member.name}", icon_url=member.avatar)
        embed.add_field(name=f"Account Created:", value=f"<t:{member.created_at.strftime('%s')}:R>", inline=False)

        if member.guild.id == 601677205445279744:
            try:
                role = member.guild.get_role(732771947338793030)
                await member.add_roles(role, reason=f"Initial Role")
                print(f"{member} was assigned Server Member role in Public Discord")
            except Exception as err:
                print(f"An error has occurred: {err}")

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
        embed = discord.Embed(
            title=f"{member} Has left {member.guild.name}!",
            description=f"The door hit {member} on the ass on the way out!",
            color=config.error
        )
        embed.set_author(name=member.name, icon_url=member.avatar)
        try:
            if not member.guild.id == 771099589713199145:
                await self.bot.get_channel(743476824763269150).send(embed=embed)
        except Exception as err:
            print(f'An error has occurred: {err}')

        channel = self.bot.get_channel(619175785772875808)
        try:
            await channel.edit(name=f'👦 Member Count: {self.bot.get_guild(601677205445279744).member_count}')
        except Exception as err:
            print(f"There was an error changing member count: {err}")
        print(f'{member} left {member.guild.name} ( Current Members: {member.guild.member_count} )')


# Starts the member count updater loop
# EventLogger.update_member_count.start()

async def setup(bot: commands.Bot):
    await bot.add_cog(
        EventLogger(bot),
        guilds=[
            discord.Object(id=626078288556851230),
            discord.Object(id=601677205445279744)
        ]
    )
