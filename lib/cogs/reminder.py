
import discord
import config
from discord import app_commands
from discord.ext import commands, tasks
from secrets import MONGO_CLIENT

db_client = MONGO_CLIENT
reminders_db = db_client.Reminders
reminders_col = db_client.Reminders["reminders"]


class Reminder(commands.Cog, name="reminder"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        # self._check_loop.start()

    # def cog_unload(self):
    #     self._check_loop.cancel()

# Remind Me - Reminder
    @app_commands.command(name="remindme",
                          description="Create a reminder for a set amount of time")
    @app_commands.describe(
        duration="ex: 1.5h -> 1 1/2 hours",
        note="What should I remind you of?")
    async def remind_me(
            self,
            itx: discord.Interaction,
            duration: str,
            *, note: str):
        """
        Set a reminder for yourself!
        """

        try:
            # dur = datetime.now() + sum([int(dur[0]) * {
            #     "m": 60, "h": 3600, "d": 86400, "s": 1, "w": 604800}[dur[-1].lower()]
            #                          for dur in duration])
            dur = int(duration[-1])

            # Insert the reminder information into the db, creates user collection if none exist
            reminders_col.update_one({
                "_id": f"{itx.user.id}"
            }, {
                "_id": f"{itx.user.id}",
                "user": f"{itx.user}",
                "$push": {
                    "reminders": {
                        "note": note,
                        "time": dur
                    }
                }
            }, upsert=True)

            embed = discord.Embed(
                title=f"Reminder!",
                description=f"I'Il remind you at <t:{dur.strftime('%s')}:R>.",
                # description=f"I'Il remind you at <t:65465464:R>.",
                color=config.level_up
            )
            await itx.user.send(embed=embed)
            await itx.response.send_message(f"Sure! I'll remind you in {dur}")

        except Exception as err:
            await itx.response.send_message(f"An error has occurred: {err}")

    # @tasks.loop(seconds=0.2)
    # async def check_loop(self):
    #
    #     for g in [r for r in reminders_col.find_one({"time": {"$in": "reminders"}}) if time.time() >= float(r["time"])]:
    #         embed = discord.Embed(description=f'**Reminder:**\r\r`{g["note"]}`', colour=self.bot.main_color)
    #         embed.add_field(name='Message:', value=f'[Click here]({g["reminders"]})')
    #
    #         embed.set_footer(text=f"Reminder ID: {reminders_col.find()}")
    #
    #         await g["author"].send(embed=embed)
    #         del self.data[g["id"]]
    #
    #
    #         try:
    #
    #             await asyncio.sleep(dur)
    #             u = itx.user
    #             c = itx.channel
    #             try:
    #                 await c.send(f"{u.mention}, Here is your reminder\n```{note}```")
    #             except Exception as err:
    #                 await discord.send(f'An error has occurred: {err}')
    #         except Exception as err:
    #             exception = f"{type(err).__name__}: {err}"
    #             print(f"Error: {exception}")
    #             await itx.response.send_message(f'An error has occurred: {err}')


async def setup(bot: commands.Bot):
    await bot.add_cog(
        Reminder(bot),
        guilds=[
            discord.Object(id=626078288556851230),
            discord.Object(id=601677205445279744)
        ]
    )
