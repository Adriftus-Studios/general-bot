import os
import sys
import asyncio

import pymongo
import secrets
import requests
import discord
import config
from discord import app_commands
from discord.ext import commands, tasks
from discord.app_commands import Choice
from pymongo import MongoClient

db_client = secrets.MONGO_CLIENT
db = db_client["PetsDB"]


# Main cog class
class Pet(commands.Cog, app_commands.Group, name="pets"):
    """
    Adriftus Pets --> Add more info here"
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        super().__init__()

    # @app_commands.checks.has_any_role(715674936395694091, 601677268477149184)
    @app_commands.command(
        name="list",
        description="Pokemon")
    async def pet_list(self, ctx: discord.Interaction):
        try:
            embed = discord.Embed(title="Testing DBs", description=f"DB List:", color=config.info)
            for c in db.Users.find():
                embed.add_field(name=f"Pass", value=f"{c}\n", inline=True)

            await ctx.response.send_message(embed=embed)
        except Exception as err:
            await ctx.response.send_message(f"An error has occurred: {err}")

    @app_commands.command(name="create")
    async def pet_create(self, ctx: discord.Interaction):
        """ test """

        user_info = {
            "_id": f"{ctx.user.id}",
            "user_name": f"{ctx.user.name}",
            "experience": 0,
            "level": 0,
            "money": 0,
            "active_poke": "None",
            "poke_info": [{
                "poke_name": "No_Name",
                "poke_experience": 0,
                "poke_level": 1,
                "poke_hunger": 100,
                "poke_happiness": 100,
                "poke_thirst": 100,
                "poke_cleanliness": 100
            }],
            "inventory": ["Stick", "Rock", "Bait", "Food"]
        }

        try:
            x = db.Users.insert_one(user_info)
            embed = discord.Embed(
                title="Created DB",
                description=f"DB Created: \n{db}",
                color=config.info
            )
            for c in db.Users.find():
                embed.add_field(name=f"█", value=f"{c}\n", inline=True)
            embed.set_author(name=x, icon_url=ctx.user.avatar)

            await ctx.response.send_message(embed=embed)
        except pymongo.errors.DuplicateKeyError:
            await ctx.response.send_message("You already have an account")

    @app_commands.command(name="remove")
    async def pet_remove(self, ctx: discord.Interaction, user: discord.Member):
        """ test """

        try:
            remove_user = {"_id": f"{user.id}"}
            db.Users.delete_one(remove_user)
            await ctx.response.send_message(f"Deleted user file for {user.name}")
        except Exception as err:
            await ctx.response.send_message(f"An error has occurred: {err}")

    @app_commands.command(name="feed")
    async def pet_feed(self, ctx: discord.Interaction):
        """ Feed your Pokemon! They faint if you don't feed em """
        try:
            await ctx.response.send_message(f"<t:{ctx.user.created_at.strftime('%s')}:R>")

        except Exception as err:
            await ctx.response.send_message(f"{err}")

    # @tasks.loop(seconds=12.0)
    # async def stat_deplete(self):
    #     db.Users.update_many({
    #         "poke_info.poke_hunger":
    #             {
    #                 "$gt": 0
    #             }
    #     }, {
    #         "$inc": {"poke_info.$[].poke_hunger": -1}
    #     }
    #     )


async def setup(bot: commands.Bot):
    await bot.add_cog(
        Pet(bot),
        guilds=[
            discord.Object(id=626078288556851230)
        ]
    )
