#!/usr/bin/python3
from secrets import TOKEN

import discord
from discord.ext import commands
import os
import sys
import time
import datetime
import aiohttp
from discord import Interaction, app_commands
from discord.app_commands import AppCommandError

# Does not allow bot to start without config file
if not os.path.isfile("config.py"):
    sys.exit("'config.py' not found! Please add it and restart the bot")
else:
    import config


class GeneralBot(commands.Bot):
    """
    General bot for Adriftus.
    """

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


# Error handling in chat
@bot.tree.error
async def on_app_command_error(itx: Interaction, error: AppCommandError):
    embed = discord.Embed(
        title="Error!",
        description=f"This command raised an error: \n{error}",
        color=config.error
    )
    await itx.response.send_message(embed=embed)
    if isinstance(error, app_commands.CommandOnCooldown):
        time_remaining = str(datetime.timedelta(
            seconds=int(error.retry_after)))
        await itx.response.send_message(
            f"Please wait `{time_remaining}` to execute this command again.",
            ephemeral=True)

bot.run(TOKEN)
