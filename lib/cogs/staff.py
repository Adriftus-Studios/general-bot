
import os
import traceback

import discord
from discord import app_commands, ui
from discord.ui import Select, View
from discord.ext import commands
import config
import asyncio
import datetime


# Main cog class
class Staff(commands.Cog, name="staff"):
    def __init__(self, bot):
        self.bot = bot

    """
    Main staff commands. These should be run with caution, and infrequently. 
    
    creload: Atomically reloads an extension. This replaces the extension with the same extension, only refreshed.
        If the extension fails to reload successfully, then the reload will roll back to a working state.
    
    gsync: Syncs all guilds that have the bot member. This should only be run after you creload, as the guilds will
        not know the changes until then.
    """

    @app_commands.checks.has_any_role(992669093545136189, 976324993229139999)  # Role IDs for Administrator in Staff Discord
    @app_commands.checks.cooldown(1, 10.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.command(
        name="creload",
        description="Reload Command Cogs")
    async def reload(
            self,
            itx: discord.Interaction):
        view = ReloadView()
        try:
            # Only add the children objects to the View class if they aren't in there already.
            # TODO: Make a better way of doing this.
            if len(view.children[0].options) == 0:
                for file in os.listdir("lib/cogs"):
                    if file.endswith(".py"):
                        c = file[:-3]
                        print(f"Cog Found: {c}")
                        if c not in view.children[0].options:  # c will never be in view.children[0]. Needs a facelift.
                            # The child object to add to the view
                            view.children[0].options.append(discord.SelectOption(
                                label=f'{c.title()}',
                                value=f"{c}",
                                emoji='<:other_left:747195307925831710>'))
            await itx.response.send_message(
                "Select the cog you wish to reload",
                ephemeral=True, view=view)
        except Exception as err:
            traceback.format_exc()
            await itx.response.send_message(f'An error has occurred: {err}')

    # TODO: Remove boilerplate error handling, and move into main.py
    @reload.error
    async def reload_error_handler(self, itx: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            time_remaining = str(datetime.timedelta(seconds=int(error.retry_after)))
            await itx.response.send_message(
                f"Please wait `{time_remaining}` to execute this command again.",
                ephemeral=True)
        if isinstance(error, app_commands.MissingRole):
            await itx.response.send_message("You do not have permission to run this command!", ephemeral=True)

    @app_commands.checks.has_any_role(992669093545136189, 976324993229139999)  # Role IDs for Administrator in Staff Discord
    @app_commands.checks.cooldown(1, 10.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.command(
        name="gsync",
        description="Sync guilds that the bot will run in")
    async def sync(
            self,
            itx: discord.Interaction):
        """
        Guild Sync Command
        """
        guilds = [626078288556851230, 601677205445279744]
        synced_guilds = []
        try:
            for g in guilds:
                try:
                    await itx.client.tree.sync(guild=discord.Object(id=g))
                    print(f"{g} was synced....")
                    synced_guilds.append(g)
                    await asyncio.sleep(5)
                except Exception as err:
                    traceback.print_exc()
                    print(f"Skipped {g} for error: {err}")
                    await itx.response.send_message(f'An error has occurred: {err}')
                    return
            print(f"Guilds have been synced")
            embed = discord.Embed(
                title=f"Success!  -",
                description=f"The following guilds have been synced successfully",
                color=config.success
            )
            for s in synced_guilds:
                embed.add_field(name=f"Guild:", value=f"{s}", inline=True)

            await itx.response.send(embed=embed)
        except Exception as err:
            traceback.print_exc()
            await itx.response.send_message(f'An error has occurred: {err}')

    # TODO: Remove boilerplate error handling, and move into main.py
    @sync.error
    async def sync_error_handler(self, itx: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            time_remaining = str(datetime.timedelta(seconds=int(error.retry_after)))
            await itx.response.send_message(
                f"Please wait `{time_remaining}` to execute this command again.",
                ephemeral=True)

        if isinstance(error, app_commands.MissingRole):
            await itx.response.send_message("You do not have permission to run this command!", ephemeral=True)

        else:
            await itx.response.send_message(f"An internal error has occurred: {error}")


# Views for Staff Commands -----------------

# Creload View
class ReloadView(View):
    @discord.ui.select(
            min_values=1,
            max_values=1,
            placeholder="Select cog to reload",
            options=[],)
    async def reload_callback(self, itx: discord.Interaction, select: discord.ui.Select):
        select.disabled = True
        ext = select.values[0]
        await itx.response.defer()
        try:
            await itx.client.reload_extension(f"lib.cogs.{ext}")
            # print(itx.client.get_cog(f"lib.cogs.{ext}").get_listeners())
            embed = discord.Embed(
                title=f"Success!  -",
                description=f"{ext.title()} cog was reloaded successfully.",
                color=config.success
            )
            await itx.followup.send(embed=embed)

        except Exception as err:
            embed = discord.Embed(
                title=f"Error!",
                description=f"{err}",
                color=config.error
            )
            for file in os.listdir("lib/cogs"):
                if not file.endswith(".py"):
                    return
                c = file[:-3]
                embed.add_field(name=f"Cog:", value=f"{c}", inline=True)
            traceback.format_exc()
            await itx.followup.send(embed=embed)
        await itx.edit_original_message(view=None)


async def setup(bot: commands.Bot):
    await bot.add_cog(
        Staff(bot),
        guilds=[
            discord.Object(id=626078288556851230),
            discord.Object(id=601677205445279744)
        ]
    )
