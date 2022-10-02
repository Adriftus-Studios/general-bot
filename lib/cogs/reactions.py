
import discord
from discord import app_commands, ui
from discord.ui import Select, View
from discord.ext import commands
from datetime import datetime, timedelta


import config


class RoleView(View):
    @discord.ui.select(
            min_values=1,
            placeholder="Select a Server Role! Collapse the dropdown to confirm selection.",
            options=[])
    async def select_callback(self, ctx: discord.Interaction, select: discord.ui.Select):
        select.disabled = True

        roles_id = select.values[0]

        role_object = ctx.guild.get_role(int(roles_id))
        try:
            if role_object not in ctx.user.roles:
                await ctx.user.add_roles(role_object, reason="Self assigned Role", atomic=True)
                await ctx.response.send_message(f"Added role(s) {role_object}", ephemeral=True)
            else:
                await ctx.user.remove_roles(role_object, reason="Self removed Role", atomic=True)
                await ctx.response.send_message(f"Removed role(s) {role_object}", ephemeral=True)
        except Exception as err:
            await ctx.response.send_message(f"Role ID: {roles_id}\nRole Object: {role_object}\nError: {err}", ephemeral=True)


class Roles(commands.Cog, name="roles"):
    def __init__(self, bot):
        self.bot = bot

    """
    Roles
    """

    @app_commands.checks.cooldown(1, 10.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.command(
        name="roles",
        description="Assign a Role")
    async def roles(
            self,
            ctx: discord.Interaction):
        """
        Roles
        """
        view = RoleView()
        try:
            # Add new roles here  <--
            role_info = [{
                "role_id": 998003246171967589,
                "role_emoji": "📣"
            }, {
                "role_id": 998004575053291540,
                "role_emoji": "👀"
            }, {
                "role_id": 998004676534476840,
                "role_emoji": "📕"
            }, {
                "role_id": 997995099189432340,
                "role_emoji": "📊"
            }, {
                "role_id": 997991924038389780,
                "role_emoji": "🎉"
            }, {
                "role_id": 998005359669170267,
                "role_emoji": "💎"
            }
            ]
            if len(view.children[0].options) == 0:
                for r in role_info:
                    role_object = ctx.guild.get_role(r["role_id"])
                    print(f'Role Found: {role_object.name}')

                    view.children[0].options.append(discord.SelectOption(
                        label=f'Add/Remove role: {role_object.name}',
                        value=f'{r["role_id"]}',
                        emoji=f'{r["role_emoji"]}',
                        description=f'{len(role_object.members)} members have this role!'))
            view.children[0].max_values = len(view.children[0].options)
            await ctx.response.send_message(
                "Select your roles! You will be able to remove the role by selecting the role again.",
                ephemeral=True, view=view)
        except Exception as err:
            await ctx.response.send_message(f'An error has occurred: {err}')

    @app_commands.checks.cooldown(1, 10.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.checks.has_any_role(992669093545136189)
    @app_commands.command(
        name="role_setup",
        description="Set up the role menu")
    async def role_setup(
            self,
            ctx: discord.Interaction):
        index = {
            'Announcements': 0,
            'Spoilers': 1,
            'Changelog': 2,
            'Polls': 3,
            'Events': 4,
            'Highlights': 5}
        role_info = [{
            "role_id": 998003246171967589,
            "role_emoji": "📣"
        }, {
            "role_id": 998004575053291540,
            "role_emoji": "👀"
        }, {
            "role_id": 998004676534476840,
            "role_emoji": "📕"
        }, {
            "role_id": 997995099189432340,
            "role_emoji": "📊"
        }, {
            "role_id": 997991924038389780,
            "role_emoji": "🎉"
        }, {
            "role_id": 998005359669170267,
            "role_emoji": "💎"
        }
        ]
        role_channel = 998931403225972746
        try:
            embed = discord.Embed(
                title=f"*Adriftus Reaction Roles!*",
                description=f"Stay up to date with **Adriftus** related content!\n"
                            f"Get your __**Notification Roles**__ Now!"
                            f"*For more information check #rules-and-info*",
                color=config.success)
            embed.add_field(
                name=f"", value=f"", inline=False)
            embed.set_footer(
                text=f"Adriftus Staff")
            embed.set_image(url=
                            'https://cdn.discordapp.com/attachments/642764810001448980/734880181008728094/logoHalf.png')

        except Exception as err:
            print(err)


async def setup(bot: commands.Bot):
    await bot.add_cog(
        Roles(bot),
        guilds=[
            discord.Object(id=601677205445279744)
        ]
    )
