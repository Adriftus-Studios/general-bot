
import traceback
import aiohttp
import json
import requests
import discord
import config

from discord import app_commands
from discord.ext import commands


def get_quote():
    res = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(res.text)
    return json_data


def dad_joke():
    res = requests.get("https://icanhazdadjoke.com/",
                       headers={"Accept": "application/json", "User-Agent": "Adriftus"})
    joke_data = json.loads(res.text)
    joke = f"{joke_data['joke']}\n"
    return joke


class Fun(commands.Cog, name="fun"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

# LMGTFY (Let Me Google That For You)
    @app_commands.command(
        name="lmgtfy",
        description="Return a Google web page")
    async def lmgtfy(
            self,
            itx: discord.Interaction,
            search: str) -> None:
        """
        Will return a web page with Google Searches for your convenience.
        """
        url = ''
        for a in search.split():
            url = url + f"{a}+"
        combined_url = f"https://duckduckgo.com/?q={url}"
        await itx.response.send_message(f"{combined_url[:len(combined_url)-1]}")

    # Inspire Command
    @app_commands.command(
        name="inspire",
        description="Be Inspired! Random quotes provided by ZenQuotes.")
    async def _inspire(
            self,
            itx: discord.Interaction):
        """
        Be inspired. random quotes provided by ZenQuotes.
        """
        json_data = get_quote()
        quote = f"{json_data[0]['q']}"
        author = f"{json_data[0]['a']}"
        embed = discord.Embed(
            title="Inspirational Message for " + itx.user.display_name, color=config.success)
        embed.add_field(name="Inspire Others", value=quote, inline=False)
        embed.set_footer(text=f" - {author}")
        embed.set_author(name=itx.user.display_name, icon_url=itx.user.avatar)

        try:
            await itx.response.send_message(embed=embed)
        except Exception as err:
            traceback.format_exc()
            await itx.response.send_message(f'An error has occured: {err}')

    # Vote command
    @app_commands.command(
        name="vote",
        description="Full, updated vote sites for your convenience!")
    async def vote(
            self,
            itx: discord.Interaction):
        """
        Vote sites for the Adritftus Minecraft server
        """
        embed = discord.Embed(
            title="Vote sites for **play.adriftus.net**", color=config.success)
        for s in config.vote_sites:
            embed.add_field(name=f"Vote:", value=f"{s}\n", inline=False)
        embed.set_footer(text=f" - Adriftus server team")
        embed.set_author(name=itx.user.display_name, icon_url=itx.user.avatar)

        try:
            await itx.response.send_message(embed=embed)
        except Exception as err:
            traceback.format_exc()
            await itx.response.send_message(f'An error has occured: {err}')

    @app_commands.command(
        name="bitcoin",
        description="Returns the spot price of bitcoin")
    async def bitcoin(self, itx: discord.Interaction):
        """
        Get the current price of bitcoin.
        """
        url = "https://api.coindesk.com/v1/bpi/currentprice/BTC.json"
        # Async HTTP request
        async with aiohttp.ClientSession() as session:
            raw_response = await session.get(url)
            response = await raw_response.text()
            response = json.loads(response)
            embed = discord.Embed(
                title=":information_source: Info",
                description=f"Bitcoin price is: ${response['bpi']['USD']['rate']}",
                color=config.success
            )
            await itx.response.send_message(embed=embed)

    # Dad Joke Command
    @app_commands.command(
        name="joke",
        description="Not a dad? Can't think of something this funny? Don't worry, we've got you covered!")
    async def _joke(
            self,
            itx: discord.Interaction):
        """
        Not a dad? Can't think of something this funny? Don't worry, we've got you covered!
        """
        joke = dad_joke()
        embed = discord.Embed(title=f"Dad Jokes", color=config.success)
        embed.add_field(name="Fine Joke Incoming!", value=joke, inline=False)
        embed.set_footer(
            text=f"Only the best Dad Jokes for {itx.user.display_name}")
        embed.set_author(name=itx.user.display_name, icon_url=itx.user.avatar)

        try:
            await itx.response.send_message(embed=embed)
        except Exception as err:
            traceback.format_exc()
            await itx.response.send_message(f'An error has occurred: {err}')

        # Map command
        @app_commands.command(
            name="map",
            description="View the world of HeroCraft!")
        async def map(
                self,
                itx: discord.Interaction):
            embed = discord.Embed(
                title="Map **play.adriftus.net**", color=config.success)

            embed.add_field(
                name=f"Site:", value=f"http://maps.adriftus.net\n", inline=False)
            embed.set_footer(text=f" - Adriftus server team")
            embed.set_author(name=itx.user.display_name,
                             icon_url=itx.user.avatar)

            try:
                await itx.response.send_message(embed=embed)
            except Exception as err:
                traceback.format_exc()
                await itx.response.send_message(f'An error has occured: {err}')


async def setup(bot: commands.Bot):
    await bot.add_cog(
        Fun(bot),
        guilds=[
            discord.Object(id=626078288556851230),
            discord.Object(id=601677205445279744)
        ]
    )
