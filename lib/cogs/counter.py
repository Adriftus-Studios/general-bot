import traceback

import discord
import config
import json
import asyncio

from discord.ext import commands


class Counter(commands.Cog, name="counter"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.id == 970208822754963486 and not message.author.bot:
            try:
                with open('./ignored/counter.json', 'r') as file:
                    data = json.load(file)

                current_number = data['count']

                if int(message.content) == int(current_number)+1 and message.author.id != data['last_member']:
                    with open('./ignored/counter.json', 'r+') as file:
                        data = json.load(file)
                        data['count'] = int(current_number)+1
                        data['last_member'] = message.author.id
                        file.seek(0)
                        file.write(json.dumps(data))
                        file.truncate()
                    await message.channel.edit(name=f'📈stonks-{current_number+1}')
                    if int(message.content) % 100 == 0:
                        await message.channel.send(f"{message.author.mention} has just helped reach a milestone!")
                        await message.pin(reason="Milestone Reached")
                else:
                    try:
                        await asyncio.sleep(0.2)
                        await asyncio.wait_for(message.delete(), timeout=3)
                        print(f"Message deleted")
                    except asyncio.TimeoutError:
                        print(f"Message delete failed. Time-out")

            except Exception as err:
                await message.delete()
                print(f"An error has occurred in counter: {err}")
                traceback.format_exc(err)


async def setup(bot: commands.Bot):
    await bot.add_cog(
        Counter(bot),
        guilds=[
            discord.Object(id=626078288556851230),
            discord.Object(id=601677205445279744)
        ]
    )
