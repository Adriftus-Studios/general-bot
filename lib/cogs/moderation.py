
import os
import sys
import datetime
import traceback

import discord
from discord import app_commands
from discord.ext import commands

if not os.path.isfile("config.py"):
    sys.exit("'config.py' not found! Please add it and try again.")
else:
    import config


class Moderation(commands.Cog, name="moderation"):
    """
    Moderation tools designed by Adriftus Moderation staff.

    Banned:
    Banned message will jail a user who the moderator replies to, as well as making it so that every other instance
    of that message that gets pasted, will result in the user being jailed. This is to prevent, or slow down raid
    or spam attacks.

    Jail:
    Jail a user for their actions. If the moderator decides that the action warranted punishment, but needs to consult
    another moderator, or if the action was bad, though not bad enough for a ban, then jailing the user is the second
    best action to take.

    Kick:
    Kicks the user from the discord this is run in. This will send them a message telling them the exact reason they
    were kicked for.

    Ban:
    Bans the user in the same way that kick does; sending a message to the user, letting them know that they were
    banned from the discord.

    """
    # TODO: Add moderation actions to the database. This will help to determine if the person who has committed the
    #   offence is a repeat offender, or first time. This might be best done through a decorator.

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="jail",
        description="Jail a user")
    @app_commands.describe(
        member='User you wish to jail.',
        reason='Reason given to jail the user.')
    @app_commands.checks.has_permissions(ban_members=True)
    async def jail(self, itx: discord.Interaction, member: discord.Member, *, reason: str):
        """
        Jail a user. Gives the jailed role if within the main discord.
        """

        if member.guild_permissions.administrator:
            embed = discord.Embed(
                title="Error!",
                description="You can't jail an admin",
                color=config.error
            )
            await itx.response.send_message(embed=embed)
        else:
            try:
                jail_role = itx.guild.get_role(1007407892925788260)
                member_role = itx.guild.get_role(732771947338793030)
                await member.remove_roles(member_role, reason=f'Jailed by an admin: {itx.user}')
                await member.add_roles(jail_role, reason=f"Jailed by an admin: {itx.user}")

                embed = discord.Embed(
                    title="Jailed!",
                    description=f"{member} has been jailed!",
                    color=config.error
                )
                embed.add_field(name="Reason:", value=reason)
                embed.set_author(name="- Adriftus Moderation Team",
                                 icon_url="https://cdn.discordapp.com/emojis/934732958521241680")
                await itx.response.send_message(embed=embed)
                print(f"**{member}** was jailed by **{itx.user}**!")
                try:
                    await member.send(
                        f"You were jailed by **{itx.user}**!\nReason: {reason}"
                    )
                except Exception as err:
                    traceback.format_exc()
                    print(f'Error: {err}')
            except Exception as err:
                traceback.format_exc()
                await itx.response.send_message(f"Error: {err}")

    @app_commands.command(
        name="release",
        description="Un-jail a user")
    @app_commands.describe(
        member='User you wish to un-jail.')
    @app_commands.checks.has_permissions(ban_members=True)
    async def unjail(self, itx: discord.Interaction, member: discord.Member):
        """
        Un-jail a user. Removes the jailed role if within the main discord.
        """

        try:
            jail_role = itx.guild.get_role(1007407892925788260)
            member_role = itx.guild.get_role(732771947338793030)
            await member.add_roles(member_role, reason=f'Jailed by an admin: {itx.user}')
            await member.remove_roles(jail_role, reason=f"Jailed by an admin: {itx.user}")

            embed = discord.Embed(
                title="Jailed!",
                description=f"{member} has been released!",
                color=config.error
            )
            embed.set_author(name="- Adriftus Moderation Team",
                             icon_url="https://cdn.discordapp.com/emojis/934732958521241680")
            await itx.response.send_message(embed=embed)
            print(f"**{member}** was un-jailed by **{itx.user}**!")
            try:
                await member.send(
                    f"You were released from jail by **{itx.user}**!"
                )
            except Exception as err:
                traceback.format_exc()
                print(f'Error: {err}')
        except Exception as err:
            traceback.format_exc()
            await itx.response.send_message(f"Error: {err}")

    # # Kick Command
    @app_commands.command(name='kick',
                          description="Kick a user.")
    @app_commands.describe(
        user="Who are you kicking?",
        reason="Reason for kicking the user?")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, itx: discord.Interaction, user: discord.Member, *, reason: str = None):
        embed = discord.Embed(title=f"{user.name}", color=0x7289da)
        embed.add_field(name=f'Kick Successful',
                        value=f"User **{user.name}#{user.discriminator}** was kicked for\n- `{reason}`\n\nTimestamp: <t:{datetime.datetime.now().strftime('%s')}:F>")
        await itx.response.send_message(embed=embed)
        await user.kick(reason=reason)

    # Ban Command
    @app_commands.command(name='ban',
                          description="Ban a user.")
    @app_commands.describe(
        user="Who are you banning?",
        reason="Reason for banning the user?")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, itx: discord.Interaction, user: discord.Member, *, reason: str = None):
        embed = discord.Embed(title=f"{user.name}", color=0x7289da)
        embed.add_field(name=f'Ban Successful',
                        value=f"**{user.name}** has been banned for\n- `{reason}`\n\nTimestamp: <t:{datetime.datetime.now().strftime('%s')}:F>")
        await itx.response.send_message(embed=embed)
        await user.ban(reason=reason)

    # # Warn Command
    @app_commands.command(name='warn',
                          description="Warns a specified user.")
    @app_commands.describe(
        user="Who are you warning?",
        reason="Reason for the warning?")
    @app_commands.checks.has_permissions(kick_members=True)
    async def warn(self, itx: discord.Interaction, user: discord.Member, *, reason: str = None):

        embed = discord.Embed(title="WARNED", color=0xB321AA)
        embed.add_field(name=f"You have been warned in **{itx.guild}** by **{itx.user}** for\n- `{reason}`\n\nTimestamp: <t:{datetime.datetime.now().strftime('%s')}:F>",
                        value=f'\u200b')
        await user.send(embed=embed)
        embed = discord.Embed(title="WARNED", color=0xB321AA)
        embed.add_field(name=f"**{user}** has been **warned** for\n- `{reason}`\n\nTimestamp: <t:{datetime.datetime.now().strftime('%s')}:F>",
                        value=f'\u200b')
        await itx.response.send_message(embed=embed)

    # Clear Command
    @app_commands.command(name='purge',
                          description="Clear a specified amount of messages.")
    @app_commands.describe(
        amount="How many messages should be deleted?")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def purge(self, itx: discord.Interaction, amount: int):
        """
        Delete X number of messages.
        """
        if amount < 1:
            embed = discord.Embed(
                title="Error!",
                description=f"`{amount}` is not a valid number.",
                color=config.error
            )
            await itx.response.send_message(embed=embed)
            return

        purged_messages = await itx.channel.purge(limit=amount+1)
        embed = discord.Embed(
            title="Chat Cleared!",
            description=f"**{itx.user}** cleared **{len(purged_messages)-1}** messages!",
            color=config.success
        )
        await itx.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(
        Moderation(bot),
        guilds=[
            discord.Object(id=626078288556851230),
            discord.Object(id=601677205445279744)
        ]
    )
