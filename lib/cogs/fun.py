import asyncio
import aiohttp
import json
import os
import time
import random
import requests
import discord
import config

from discord import app_commands
from discord.ext import commands
from twitchAPI.twitch import Twitch

from googleapiclient import discovery


def get_quote():
    res = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(res.text)
    quote = f"{json_data[0]['q']}\n "
    return quote


def dad_joke():
    res = requests.get("https://icanhazdadjoke.com/", headers={"Accept": "application/json", "User-Agent": "Adriftus"})
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
        description="Be Inspired!")
    async def _inspire(
            self,
            itx: discord.Interaction):
        """
        Be inspired. random quotes provided by ZenQuotes.
        """
        quote = get_quote()
        author = json_data[0]['a']
        embed = discord.Embed(title="Inspirational Message for " + itx.user.display_name, color=config.success)
        embed.add_field(name="Inspire Others", value=quote, inline=False)
        embed.set_footer(text=f" - {author}")
        embed.set_author(name=itx.user.display_name, icon_url=itx.user.avatar)

        try:
            await itx.response.send_message(embed=embed)
        except Exception as err:
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
        embed = discord.Embed(title="Vote sites for **play.adriftus.net**", color=config.success)
        for s in config.vote_sites:
            embed.add_field(name=f"Vote:", value=f"{s}\n", inline=False)
        embed.set_footer(text=f" - Adriftus server team")
        embed.set_author(name=itx.user.display_name, icon_url=itx.user.avatar)

        try:
            await itx.response.send_message(embed=embed)
        except Exception as err:
            await itx.response.send_message(f'An error has occured: {err}')

    # Vote command
    @app_commands.command(
        name="role",
        description="Add role for testing")
    @app_commands.checks.has_any_role(601677268477149184, 938604804501037078)
    async def role(
            self,
            itx: discord.Interaction,
            role: discord.Role):
        """
        Assign a role
        """
        try:
            await itx.user.remove_roles(role)
            await itx.response.send_message(f"Role {role.name} removed successfully!", ephemeral=True)
        except Exception as err:
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
        description="The worlds FINEST Dad Jokes!")
    async def _joke(
            self,
            itx: discord.Interaction):
        """
        Not a dad? Can't think of something this funny? Don't worry, we've got you covered!
        """
        joke = dad_joke()
        embed = discord.Embed(title=f"Dad Jokes", color=config.success)
        embed.add_field(name="Fine Joke Incoming!", value=joke, inline=False)
        embed.set_footer(text=f"Only the best Dad Jokes for {itx.user.display_name}")
        embed.set_author(name=itx.user.display_name, icon_url=itx.user.avatar)

        try:
            await itx.response.send_message(embed=embed)
        except Exception as err:
            await itx.response.send_message(f'An error has occurred: {err}')

    @app_commands.command(
        name="xlist",
        description="It really never ends Xeane")
    async def _xlist(
            self,
            itx: discord.Interaction,
            *,
            note: str):
        """
        One day, we'll make our own game, and this madness might end.
        """
        embed = discord.Embed(title="Your Note:", color=config.success)
        embed.add_field(name=": ", value=note, inline=True)
        embed.set_footer(text=f"{itx.user.display_name} - {time.ctime(time.time())}")

        try:
            channel = itx.client.get_guild(626078288556851230).get_channel(626906799269871666)

            await itx.response.send_message(f"Your life is over....")
            await channel.send(embed=embed)
        except Exception as err:
            await itx.response.send_message(f'An error has occurred: {err}')

    @app_commands.command(
        name="dlist",
        description="It really never ends Devin")
    async def _dlist(
            self,
            itx: discord.Interaction,
            *,
            note: str):
        """
        One day, we'll make our own game, and this madness might end.
        """
        embed = discord.Embed(title="Your Note:", color=config.success)
        embed.add_field(name=": ", value=note, inline=True)
        embed.set_footer(text=f"{itx.user.display_name} - {time.ctime(time.time())}")

        try:
            channel = itx.client.get_guild(626078288556851230).get_channel(969401285445050388)

            await itx.response.send_message(f"Lore is being saved....")
            await channel.send(embed=embed)
        except Exception as err:
            await itx.response.send_message(f'An error has occurred: {err}')


async def setup(bot: commands.Bot):
    await bot.add_cog(
        Fun(bot),
        guilds=[
            discord.Object(id=626078288556851230),
            discord.Object(id=601677205445279744)
        ]
    )