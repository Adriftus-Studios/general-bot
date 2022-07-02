import traceback

import discord
import config
import time
import datetime
import uuid
from discord import app_commands, ui
from discord.ui import View
from discord.ext import commands
from secrets import MONGO_CLIENT

db_client = MONGO_CLIENT
message_db = db_client.Messages
user_db = db_client.Users


class ButtonView(View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Claim Ticket [Staff]",
        style=discord.ButtonStyle.danger,
        emoji="✅",
        custom_id="0")
    async def claim_callback(self, itx: discord.Interaction, button):
        button.disabled = True
        button.emoji = "✅"
        button.label = f"Claimed by {itx.user}"

        overwrites = discord.PermissionOverwrite(
                manage_messages=True,
                read_messages=True,
                add_reactions=True,
                read_message_history=True,
                send_messages=True,
                use_application_commands=False,
                attach_files=True)
        role_ids = [992669093545136189, 992670439644090428, 992664721125806191, 992671030143352912]
        member = itx.user
        for role_id in role_ids:
            if member.get_role(role_id):
                await itx.channel.set_permissions(itx.user, overwrite=overwrites)
                await itx.response.edit_message(view=self)
            else:
                itx.channel.send("Only a member of staff may claim a ticket.")

    async def interaction_check(self, interaction: claim_callback):
        # return True to allow the interaction to call the related ui.Item
        return True

    @discord.ui.button(
        label="Close Ticket [User]",
        style=discord.ButtonStyle.danger,
        emoji="<:open_lock:965662978588413972>",
        custom_id="1")
    async def close_callback(self, itx: discord.Interaction, button):
        button.disabled = True
        button.emoji = "<:closed_lock:965662987790741535>"
        await itx.response.edit_message(view=self)

        overwrites = {
            itx.user: discord.PermissionOverwrite(send_messages=True)}
        await itx.channel.set_permissions(itx.user, overwrite=overwrites)

    @discord.ui.button(
        label="Lock Ticket [Staff]",
        style=discord.ButtonStyle.danger,
        emoji="<:open_lock:965662978588413972>",
        custom_id="2")
    async def lock_callback(self, itx: discord.Interaction, button):

        role_ids = [992669093545136189, 992670439644090428, 992664721125806191, 992671030143352912]
        member = itx.user
        for role_id in role_ids:
            if member.get_role(role_id):
                await itx.response.send_modal(TicketReason(ticket_name=itx.channel.name, admin_name=itx.user))
                await itx.channel.delete()
            else:
                itx.channel.send("Only a member of staff may lock a ticket.")


class TicketView(View):
    @discord.ui.select(
            min_values=1,
            max_values=1,
            placeholder="Select a Ticket Category",
            options=[
                discord.SelectOption(
                    label='Bug',
                    value="Bug",
                    emoji='🐛',
                    description='Server related issue'),
                discord.SelectOption(
                    label='Player',
                    value="Player",
                    emoji='🧑‍🤝‍🧑',
                    description='Player conduct issues'),
                discord.SelectOption(
                    label='Store',
                    value="Store",
                    emoji='🏪',
                    description='Purchase related issues'),
                discord.SelectOption(
                    label='Staff',
                    value="Staff",
                    emoji='🧑‍💼',
                    description='Staff related issues. (This will go to Admins, not Moderators)'),
                discord.SelectOption(
                    label='Other',
                    value="Other",
                    emoji='<:other_left:747195307925831710>',
                    description='Other issues not specified.')
            ],)
    async def select_callback(self, itx: discord.Interaction, select: discord.ui.Select):
        select.disabled = True
        label = select.values[0]
        await itx.response.send_modal(TicketForm(ticket_name=label))
        await TicketForm(ticket_name=label).wait()
        await itx.edit_original_message(view=None)


class TicketForm(ui.Modal, title="Submit your Ticket"):
    
    def __init__(self, ticket_name):
        super(TicketForm, self).__init__(timeout=None)
        self.ticket_name = ticket_name

    ign = ui.TextInput(
        label="What is your in game name?",
        style=discord.TextStyle.short,
        placeholder="ex: Notch",
        max_length=25,
        required=True)
    issue = ui.TextInput(
        label="Describe your issue",
        style=discord.TextStyle.paragraph,
        placeholder="Be as descriptive as possible",
        max_length=1000,
        required=True)

    async def on_submit(self, itx: discord.Interaction):
        ticket_number = uuid.uuid1()
        embed = discord.Embed(
            title=f"<:support_ticket:965647477548138566> Support Ticket - [{self.ticket_name}]",
            description=f"Thank you for opening a support ticket\nA member of <@&625686951382745089> will be available to help you shortly.",
            color=config.success)
        embed.add_field(name=f"Submitter ", value=f"Discord: {itx.user} | IGN: {self.ign}", inline=False)
        embed.add_field(name=f"Issue", value=f"{self.issue}", inline=False)
        embed.set_footer(text=f"User ID: {itx.user.id} | Ticket Number • {ticket_number}")

        overwrites = {
            itx.user.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            itx.user.guild.me: discord.PermissionOverwrite(read_messages=True),
            itx.user: discord.PermissionOverwrite(
                read_messages=True,
                add_reactions=True,
                read_message_history=True,
                send_messages=True,
                use_application_commands=False,
                attach_files=True)
        }

        channel = await itx.user.guild.get_channel(985201287488499752).create_text_channel(f'Ticket - {itx.user.name}', overwrites=overwrites)

        await itx.response.send_message(f"Your ticket has been created at {channel.mention}!", ephemeral=True)
        message = await channel.send(content=itx.user.mention, embed=embed, view=ButtonView())
        await message.pin(reason="User Created Ticket")


class TicketReason(ui.Modal, title="Reason for Closing Ticket"):

    def __init__(self, ticket_name, admin_name):
        super(TicketReason, self).__init__(timeout=None)
        self.ticket_name = ticket_name
        self.admin_name = admin_name

    reason = ui.TextInput(
        label="Describe the Reason for Closure",
        style=discord.TextStyle.paragraph,
        placeholder="Please give a detailed description",
        max_length=1000,
        required=True)

    async def on_submit(self, itx: discord.Interaction):
        embed = discord.Embed(
            title=f"<:support_ticket:965647477548138566> Support Ticket Closed - [{self.ticket_name}]",
            description=f"Ticket has been successfully closed by {self.admin_name}",
            color=config.success)
        embed.add_field(name=f"Reason", value=f"{self.reason}", inline=False)
        embed.set_footer(text=f"User ID: {itx.user.id} | iID:  • {time.ctime(time.time())}")

        channel = itx.user.guild.get_channel(965027742154358814)
        await itx.response.defer()
        await channel.send(embed=embed)


class Tickets(commands.Cog, name="ticket"):
    def __init__(self, bot):
        self.bot = bot
    """
    Ticket Class. Takes input from TicketForm() and TicketView().
    
    Sends the user a drop-down menu so they can select their issue category. When they select their category, 
    they will get a TicketForm. 
    
    This info is sent to logs, and a ticket channel with '{user.name}-ticket'
    
    Make a ticket.
    """

    @app_commands.checks.cooldown(1, 600.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.command(
        name="ticket",
        description="Create a support ticket.")
    async def ticket(
            self,
            itx: discord.Interaction):
        """
        Ticket
        """
        try:
            view = TicketView()
            await itx.response.send_message(
                "Select the proper category for your ticket. If you're unsure, select 'Other'",
                ephemeral=True, view=view)
        except Exception as err:
            traceback.format_exc()
            await itx.response.send_message(f'An error has occurred: {err}')

    # TODO: Remove boilerplate error handling, and move into main.py
    @ticket.error
    async def ticket_error_handler(self, itx: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            time_remaining = str(datetime.timedelta(seconds=int(error.retry_after)))
            await itx.response.send_message(
                f"Please wait `{time_remaining}` to execute this command again.",
                ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(
        Tickets(bot),
        guilds=[
            discord.Object(id=626078288556851230),
            discord.Object(id=601677205445279744)
        ]
    )
