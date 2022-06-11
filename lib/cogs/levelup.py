import discord
import config
import secrets
from discord import app_commands
from discord.ext import commands, tasks


class LevelUp(commands.Cog, name="levelup"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db_client = secrets.MONGO_CLIENT
        self.db = self.db_client.Stats

    @commands.Cog.listener()
    async def on_message(self, message):
        author_id = message.user.id

        user_id = {"_id": author_id}

        if message.author.bot:
            return



# Level-up Check Command
    @app_commands.command(name="level",
                          description="See your server level, and other information!")
    async def level(
            self,
            itx: discord.Interaction):
        """
        View your server level. This command will show the level that you are in the server, your nitro boost rank,
        your total messages since the bot was initiated, and more statistical information. Things like boosting the
        server, or taking part in special events will level up your server level even faster, with 2x boosts!
        """

        # Connect to DB, and pull user information
        # Check if user has db entry, if not, create one.
        await itx.response.send_message("Works")

        pass
