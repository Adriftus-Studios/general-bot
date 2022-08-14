
import discord
import config
import time
import datetime
from discord import app_commands, ui, ChannelType
from discord.ui import Button, View
from discord.ext import commands
from discord.app_commands import Choice


class UnderReview(View):

    def __init__(self, suggestion_title, suggestion):
        super().__init__(timeout=None)
        self.suggestion_title = suggestion_title
        self.suggestion = suggestion

    async def interaction_check(self, itx):
        if itx.user.get_role(992672581415084032).id in config.SUGGESTION_ROLES:

            return True

    @discord.ui.button(
        label="[Under Review]",
        style=discord.ButtonStyle.green,
        emoji="☑️",
        custom_id="0")
    async def review_callback(self, itx: discord.Interaction, button):
        self.clear_items()
        await itx.response.edit_message(view=ApproveDeny(suggestion_title=self.suggestion_title, suggestion=self.suggestion))
        await itx.channel.edit(
            name=f"[Under Review] - {self.suggestion_title}",
            auto_archive_duration=4320)
        await itx.channel.send('Channel is now under review.')


# Approve / Deny
class ApproveDeny(View):

    def __init__(self, suggestion_title, suggestion):
        super().__init__(timeout=None)
        self.suggestion_title = suggestion_title
        self.suggestion = suggestion

    async def interaction_check(self, interaction):
        if interaction.user.get_role(992672581415084032).id in config.SUGGESTION_ROLES:
            return True

    @discord.ui.button(
        label="[Approved]",
        style=discord.ButtonStyle.green,
        custom_id="1")
    async def approve_callback(self, itx: discord.Interaction, button):
        await itx.channel.edit(
            name=f"[In Dev] - {self.suggestion_title}",
            auto_archive_duration=480,
            locked=True)
        await itx.response.edit_message(view=Finalize(suggestion_title=self.suggestion_title))

    @discord.ui.button(
        label="[Internal Design]",
        style=discord.ButtonStyle.green,
        custom_id="2")
    async def design_callback(self, itx: discord.Interaction, button):
        await itx.channel.edit(
            name=f"[Internal Design] - {self.suggestion_title}",
            auto_archive_duration=4320)
        await itx.response.edit_message(view=Finalize(suggestion_title=self.suggestion_title))
        embed = discord.Embed(
            title=f"Adriftus Suggestion Bot",
            description=f"○○ {itx.user.mention} has moved a suggestion to internal design ○○",
            color=config.success)
        embed.set_thumbnail(url=itx.user.avatar)
        embed.add_field(name=f"Original Channel:", value=f"{itx.message.channel}", inline=False)
        embed.add_field(name=f"Suggestion", value=f"{self.suggestion}", inline=False)
        embed.set_footer(text=f"User ID: {itx.user.id} | {time.ctime(time.time())}")

        channel = itx.client.get_guild(626078288556851230).get_channel(669922990435336216)
        await itx.channel.send(f"This suggestion has been sent to <#669922990435336216>")

        message = await channel.send(embed=embed)

        thread = await message.create_thread(
            name=f"[Internal Design] - {self.suggestion}",
            slowmode_delay=None,
            reason="Suggestion Created")
        await thread.send(view=Finalize(suggestion_title=self.suggestion_title))

    @discord.ui.button(
        label="[Denied]",
        style=discord.ButtonStyle.red,
        custom_id="3")
    async def denied_callback(self, itx: discord.Interaction, button):
        await itx.channel.edit(
            name=f"[Denied] - {self.suggestion_title}",
            auto_archive_duration=60,
            locked=True)

        await itx.response.edit_message(view=None)
        await itx.followup.send_modal(DeniedForm(suggestion_channel=itx.channel))


# In Dev
class Finalize(View):

    def __init__(self, suggestion_title):
        super().__init__(timeout=None)
        self.suggestion_title = suggestion_title

    async def interaction_check(self, interaction):
        if interaction.user.get_role(992672581415084032).id in config.SUGGESTION_ROLES:
            return True

    @discord.ui.button(
        label="[Finalize]",
        style=discord.ButtonStyle.green,
        custom_id="4")
    async def dev_callback(self, itx: discord.Interaction, button):
        button.disabled = True
        await itx.channel.edit(
            name=f"[Implemented] - {self.suggestion_title}",
            auto_archive_duration=4320)
        await itx.response.edit_message(view=self)


class DeniedForm(ui.Modal, title="Denial Form"):

    def __init__(self, suggestion_channel):
        super(DeniedForm, self).__init__()
        self.suggestion_channel = suggestion_channel

    deny_reason = ui.TextInput(
        label="Reason for Denying",
        style=discord.TextStyle.paragraph,
        placeholder="Please be as descriptive as possible.",
        max_length=1000,
        required=True)

    async def on_submit(self, itx: discord.Interaction):
        embed = discord.Embed(
            title=f"Suggestion Denied",
            description=f"○○ {itx.user.mention} has denied your suggestion. ○○",
            color=config.error)
        embed.set_thumbnail(url=itx.user.avatar)
        embed.add_field(
            name=f"Reason:",
            value=f"{self.deny_reason}\n\nThis channel will archive in 1 hour.",
            inline=False)

        embed.set_footer(text=f"User ID: {itx.user.id} | sID: • \n{time.ctime(time.time())}")

        message = await self.suggestion_channel.send(embed=embed)
        await message.pin()
        await itx.response.send_message("You have denied this suggestion", ephemeral=True)


class SuggestionForm(ui.Modal, title="Suggestions Form"):

    name = ui.TextInput(
        label="What is your in game name?",
        style=discord.TextStyle.short,
        placeholder="ex: Notch",
        max_length=25,
        required=True)
    sug_title = ui.TextInput(
        label="Set the title of your thread",
        style=discord.TextStyle.short,
        placeholder="Brief 25 char description",
        max_length=25,
        required=True)
    suggestion = ui.TextInput(
        label="Describe your suggestion",
        style=discord.TextStyle.paragraph,
        placeholder="Please be as descriptive as possible. Staff will then discuss the suggestion.",
        max_length=1000,
        required=True)

    async def on_submit(self, itx: discord.Interaction):
        embed = discord.Embed(
            title=f"Adriftus Suggestion Bot",
            description=f"○○ {itx.user.mention} has dropped a suggestion! ○○",
            color=config.success)
        embed.set_thumbnail(url=itx.user.avatar)
        embed.add_field(name=f"Submitter ", value=f"Discord: {itx.user} | IGN: {self.name}", inline=False)
        embed.add_field(name=f"Suggestion", value=f"{self.suggestion}", inline=False)
        embed.set_footer(text=f"User ID: {itx.user.id} | sID: /suggest to make your own • \n{time.ctime(time.time())}")

        channel = itx.client.get_guild(601677205445279744).get_channel(939225790481047683)
        await itx.response.send_message(
            f"Thank you {itx.user.mention} for your suggestion! Your suggestion has been sent to <#939225790481047683>")

        message = await channel.send(embed=embed)

        await message.add_reaction("<:knightup:548680151882399745>")
        await message.add_reaction("<:knightdown:550025111235985410>")
        thread = await message.create_thread(
            name=f"[Pending] - {self.sug_title}",
            slowmode_delay=None,
            reason="Suggestion Created")

        welcome_message = await thread.send(f"Thank you for the suggestion {itx.user.mention}!\n "
                                            f"Members of <@&992672581415084032> will review this suggestion shortly.")
        await welcome_message.pin()
        await thread.send(view=UnderReview(suggestion_title=self.sug_title, suggestion=self.suggestion))


class Suggest(commands.Cog, name="suggest"):
    def __init__(self, bot):
        self.bot = bot
    """
    Suggestion Class. Takes input from SuggestionForm() and SuggestionView()
    
    Make a suggestion, and get it approved, or denied! Votes are final.
    """
    @app_commands.checks.cooldown(1, 1200.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.command(
        name="suggest",
        description="Create any suggestion that you would like to see on our server!")
    async def suggest(
            self,
            itx: discord.Interaction):
        """
        Suggest
        """
        try:
            await itx.response.send_modal(SuggestionForm())
        except Exception as err:
            await itx.response.send_message(f'An error has occurred: {err}')


async def setup(bot: commands.Bot):
    await bot.add_cog(
        Suggest(bot),
        guilds=[
            discord.Object(id=601677205445279744)
        ]
    )
