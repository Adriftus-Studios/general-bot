
import discord
from discord import app_commands, ui
from discord.ui import Select, View
from discord.ext import commands


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
                "role_id": 732771947338793030,
                "role_emoji": "<a:MineDragon:866449238271852544>"
            }, {
                "role_id": 732777026842263582,
                "role_emoji": "<a:MineDiamond:866448782001438720>"
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

    @roles.error
    async def sync_error_handler(self, itx: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            time_remaining = str(datetime.timedelta(seconds=int(error.retry_after)))
            await itx.response.send_message(
                f"Please wait `{time_remaining}` to execute this command again.",
                ephemeral=True)
        if isinstance(error, app_commands.MissingRole):
            await itx.response.send_message("You do not have permission to run this command!", ephemeral=True)

        else:
            await itx.response.send_message(f"An internal error has occurred: {error}")


async def setup(bot: commands.Bot):
    await bot.add_cog(
        Roles(bot),
        guilds=[
            discord.Object(id=601677205445279744)
        ]
    )
