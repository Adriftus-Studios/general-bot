
import discord
import config
import time
import datetime
from discord import app_commands, ui, ChannelType
from discord.ui import Button, View
from discord.ext import commands
from discord.app_commands import Choice


class ButtonView1(View):

    def __init__(self, suggestion_title):
        super().__init__(timeout=None)
        self.suggestion_title = suggestion_title

    @discord.ui.button(
        label="[Under Review]",
        style=discord.ButtonStyle.green,
        emoji="☑️",
        custom_id="0")
    async def interaction_check(self, interaction):
        roles = [992672581415084032]
        if interaction.user.get_role(992672581415084032).id in roles:
            return True

    async def claim_callback(self, interaction: discord.Interaction, button):
        self.clear_items()
        await interaction.response.edit_message(view=self)
        await interaction.channel.edit(
            name=f"[Under Review] - {self.suggestion_title}",
            auto_archive_duration=4320)
        await interaction.channel.send('Channel is now under review.')


# Approve / Deny
class ButtonView2(View):

    def __init__(self, suggestion_title):
        super().__init__(timeout=None)
        self.suggestion_title = suggestion_title

    @discord.ui.button(
        label="[Approved]",
        style=discord.ButtonStyle.green,
        custom_id="1")
    @discord.ui.button(
        label="[Denied]",
        style=discord.ButtonStyle.red,
        custom_id="2")
    async def interaction_check(self, interaction):
        roles = [992672581415084032]
        if interaction.user.get_role(992672581415084032).id in roles:
            return True

    async def claim_callback(self, interaction: discord.Interaction, button):
        button = self.clear_items()
        await interaction.response.edit_message(view=self)
        await interaction.channel.edit(
            name=f"[Under Review] - {self.suggestion_title}",
            auto_archive_duration=4320)
        await interaction.channel.send('Channel is now under review.')


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
        embed.add_field(name=f"Submitter ", value=f"Discord: {itx.user}| IGN: {self.name}", inline=False)
        embed.add_field(name=f"Suggestion", value=f"{self.suggestion}", inline=False)
        embed.set_footer(text=f"User ID: {itx.user.id} | sID: /suggest to make your own • \n{time.ctime(time.time())}")

        channel = itx.client.get_guild(601677205445279744).get_channel(939225790481047683)
        await itx.response.send_message(
            f"Thank you {itx.user.mention} for your suggestion! Your suggestion has been sent to <#939225790481047683>")

        message = await channel.send(embed=embed)

        await message.add_reaction("<:knightup:548680151882399745>")
        await message.add_reaction("<:knightdown:550025111235985410>")
        # TODO: Change to private thread
        thread = await message.create_thread(
            name=f"[Pending] - {self.sug_title}",
            slowmode_delay=None,
            reason="Suggestion Created")
        # <@&992672581415084032>
        await thread.send(f"Thank you for the suggestion {itx.user.mention}!\n "
                          f"Members of  will review this suggestion shortly.")
        await thread.send(view=ButtonView1(suggestion_title=self.sug_title))


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
        description="Create any suggestion that you would like to see on our server")
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

    # TODO: Remove boilerplate error handling, and move into main.py
    @suggest.error
    async def suggest_timeout_error(self, itx: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            time_remaining = str(datetime.timedelta(seconds=int(error.retry_after)))
            await itx.response.send_message(
                f"Please wait `{time_remaining}` to execute this command again.",
                ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(
        Suggest(bot),
        guilds=[
            discord.Object(id=601677205445279744)
        ]
    )
