#!/usr/bin/env python3
import secrets
import discord
from discord.ext import commands
import os
import sys
import time
import random
from datetime import date
import aiohttp
import aiofiles
import zipfile
import json
from discord import app_commands
from utils import Logger

# Does not allow bot to start without config file
if not os.path.isfile("config.py"):
    sys.exit("'config.py' not found! Please add it and restart the bot")
else:
    import config


class GeneralBot(commands.Bot):
    '''
    General bot for Adriftus.
    '''

    def __init__(self):
        super().__init__(
            command_prefix=",",
            intents=discord.Intents.all(),
            application_id=config.APPLICATION_ID)

        self.session = None
        self.initial_extensions = []

        for file in os.listdir("lib/cogs"):
            if file.endswith(".py"):
                extension = file[:-3]
                try:
                    self.initial_extensions.append(f"lib.cogs.{extension}")
                    print(f"Added extension: '{extension}'")
                except Exception as e:
                    exception = f"{type(e).__name__}: {e}"
                    print(f"Failed to load extension {extension}\n{exception}")
                    pass

        print(f'Full List: {self.initial_extensions}')

        self.root = "/home/minecraft/bots/AdriftusGeneral/"

    async def setup_hook(self):
        for ext in self.initial_extensions:
            await self.load_extension(ext)
        self.session = aiohttp.ClientSession()
        print(f'Syncing Guilds -')

    async def close(self):
        await super().close()
        await self.session.close()

    async def on_ready(self):
        print(f'GMT Local Time: {time.ctime(time.time())}')
        print(f'Successfully logged in as {self.user} -- Awaiting Commands')

    async def on_connect(self):
        await self.change_presence(status=discord.Status.online, activity=discord.Game(config.GAME_STATUS))
        print(f"\nBot Connected Successfully... Logging in ---")


bot = GeneralBot()


async def zip_check():
    current_time = time.ctime(time.time())
    file_size = os.stat('message_log.txt')
    if file_size.st_size >= 100000:
        output = f'message_log[{current_time}].zip'
        input = 'message_log.txt'
        with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as zip_f:
            zip_f.write(input)
        os.remove(input)
        print(f"Logs have been compressed to: {output}")


# Member counter
@bot.event
async def on_member_join(member):
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
                await bot.get_channel(c).send(embed=embed)

        except Exception as err:
            print(f'An error has occured: {err}')
        print(f'{member} joined {member.guild.name} ( Current Members: {member.guild.member_count} )')

    else:
        await bot.get_channel(626084615660109824).send(embed=embed)


@bot.event
async def on_member_remove(member):
    channel = member.guild.get_channel(619175785772875808)
    await channel.edit(name=f'👦 Member Count: {member.guild.member_count}')

    embed = discord.Embed(
        title=f"{member} Has left!",
        description=f"The door hit {member} on the ass on the way out!",
        color=config.error
    )
    embed.set_author(name=member.name, icon_url=member.avatar)
    try:
        await bot.get_channel(743476824763269150).send(embed=embed)
    except Exception as err:
        print(f'An error has occured: {err}')
    print(f'{member} left {member.guild.name} ( Current Members: {member.guild.member_count} )')


# Log Events --
@bot.event
async def on_raw_message_delete(payload):
    admin_channels = [626086306606350366, 651870920599928862]
    blacklist_channels = [965027742154358814]
    date_as_path = await current_date_to_path()

    mID = f"{payload.channel_id}_{payload.message_id}"

    serialize_data = {
        "author_id": f"{payload.cached_message.author.id}",
        "author_name": f"{payload.cached_message.author.name}",
        "author_full_name": f"{payload.cached_message.author.name}#{payload.cached_message.author.discriminator}",
        "channel_id": f"{payload.cached_message.channel.id}",
        "server_name": f"{payload.cached_message.guild.name}",
        "contents": f"{payload.cached_message.content}"
    }
    try:
        if payload.cached_message is not None:
            serialize_data = serialize_data
        elif os.path.isfile(f"{bot.root}cache/{date_as_path}/{mID}"):
            serialize_data = await deserialize_from_disc(payload.channel_id, payload.message_id)

        if payload.channel_id in admin_channels:
            await message_sender(payload, serialize_data, 712309385019523155)
        elif payload.channel_id in blacklist_channels:
            await message_sender(payload, serialize_data, 965027742154358814)
        else:
            await message_sender(payload, serialize_data, 965027742154358814)
    except Exception as err:
        print(f'An error has occurred: {err}')


@bot.event
async def on_message(message):

    if message.channel.id == 969954602051055636:
        return

    try:
        await serialize_to_disk(message)

        slash_command_channels = [677175985174478869]
        if message.channel.id in slash_command_channels:
            if not isinstance(message, discord.MessageType.chat_input_command) and not message.author.bot:
                await bot.get_channel(965027742154358814).send("You are only allowed to send commands here.")
                await message.delete()
    except Exception as err:
        print(f"An error has occurred: {err}")


@bot.event
async def on_guild_channel_delete(channel):
    print(channel)


# date path creator
async def current_date_to_path():
    current_date = date.today().strftime("%d")
    current_month = date.today().strftime("%b")
    current_year = date.today().strftime("%Y")
    return f"{current_year}/{current_month}/{current_date}"


# Path creator
async def check_or_create_folder_structure(path):
    parts = path.split("/")
    base = bot.root
    for part in parts:
        if not os.path.exists(base + part):
            os.mkdir(f"{base}{part}")
        base = f"{base}{part}/"


# Disk serializer/deserializer
async def serialize_to_disk(message):
    channel_id = message.channel.id
    message_id = message.id

    mID = f"{channel_id}_{message_id}"

    date_as_path = await current_date_to_path()
    await check_or_create_folder_structure("cache/"+date_as_path)
    with open(f"cache/{date_as_path}/{mID}", "w") as file:
        await dump(message, file)


async def deserialize_from_disc(channel_id, message_id):
    mID = f"{channel_id}_{message_id}"
    date_as_path = await current_date_to_path()
    if os.path.exists(f"cache/{date_as_path}/{mID}"):
        with open(f"cache/{date_as_path}/{mID}", "r") as file:
            return await load(file)


async def dump(message, file):
    serialize_data = {
        "author_id": f"{message.author.id}",
        "author_name": f"{message.author.name}",
        "author_full_name": f"{message.author.name}#{message.author.discriminator}",
        "channel_id": f"{message.channel.id}",
        "server_name": f"{message.guild.name}",
        "contents": f"{message.content}"
    }
    json.dump(serialize_data, file, indent=4)


async def load(file):
    return json.load(file)


# Capability to add/remove blacklist channels, and change sent logs to what channel
async def message_sender(payload, serialize_data, payload_guild_id):
    current_time = time.ctime(time.time())
    guild = bot.get_guild(payload.guild_id)

    async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.message_delete):
        deleted_channel_id = entry.extra.channel.id
        deleted_owner = entry.target.id
        deleter = entry.user

    if int(payload.channel_id) != int(deleted_channel_id) or int(serialize_data["author_id"]) != int(deleted_owner):
        deleter = bot.get_user(int(serialize_data["author_id"]))
 
    message_content = f"""
            *** Message Log Entry - {current_time} ***
            - {serialize_data["author_full_name"]} had their message deleted -
              **__Deleted By__**: {deleter.name}#{deleter.discriminator}
              **__Message Author__**: {serialize_data["author_full_name"]}
              **__Author ID__**: {serialize_data["author_id"]}
              **__Channel Info__**: <#{serialize_data["channel_id"]}> / {serialize_data["channel_id"]}
              **__Server Name__**: {serialize_data["server_name"]}

              **__Message:__**\n{serialize_data["contents"]}
            ----------------------------------------------------------------\n
            """
    async with aiofiles.open("message_log.txt", "a") as f:
        await f.writelines(message_content)

    if len(message_content) > 1000:
            message_content = f"{message_content[:1000]}...[Continued]"

    embed = discord.Embed(
        title=f"*** Message Log Entry ***",
        description=f"○○○○○○○○○○○○○○○○○○○○○○○○○○○",
        color=config.success)
    embed.add_field(name=f"Message Deleted - ", value=f"{message_content}", inline=False)
    embed.set_footer(text=f"• {time.ctime(time.time())}")

    try:
        await bot.get_channel(payload_guild_id).send(embed=embed)
    except Exception as err:
        print(f'An error has occurred: {err}')
    print(
        f'{serialize_data["author_name"]} had their message deleted in {serialize_data["server_name"]} - Action logged')
    await zip_check()


@bot.event
async def on_interaction(
        ctx: discord.Interaction):
    try:
        executed_command = ctx.command.name
        message_content = f"""
        - Executed **{executed_command}** command in {ctx.guild} (ID: {ctx.guild.id}) by {ctx.user} (ID: {ctx.user.id})\n
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
            await bot.get_channel(965027742154358814).send(embed=embed)
        except Exception as err:
            print(f'An error has occured: {err}')
        print(f"Executed {executed_command} command in {ctx.guild} (ID: {ctx.guild.id}) by {ctx.user} (ID: {ctx.user.id})")
        await zip_check()
    except Exception as err:
        print(err)
        await zip_check()


# Error handling in chat
@bot.event
async def on_command_error(
        ctx: discord.Interaction,
        error):
    if isinstance(error, app_commands.errors.CommandOnCooldown):
        embed = discord.Embed(
            title="Error!",
            description=f"This command is on a {error.retry_after}s cool down",
            color=config.error
        )
        await ctx.response.send_message(embed=embed)

    elif isinstance(error, commands.errors.MissingRequiredArgument):
        embed = discord.Embed(
            title='Error!',
            description=f'Parameter missing: {commands.errors.MissingRequiredArgument.args}',
            color=config.error
        )
        await ctx.response.send_message(embed=embed)

    elif isinstance(error, commands.errors.CommandInvokeError):
        embed = discord.Embed(
            title='Error!',
            description=f'{error}',
            color=config.error
        )
        await ctx.response.send_message(embed=embed)

    elif not isinstance(error, commands.errors.CommandNotFound):
        raise error

bot.run(secrets.TOKEN)
