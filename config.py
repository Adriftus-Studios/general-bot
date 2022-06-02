import discord

# General Config Options
BOT_PREFIX = "!"
# -- Token moved to secrets file
GAME_STATUS = "on play.adriftus.net"
OWNERS = [715674936395694091]
BLACKLIST = []
APPLICATION_ID = 604336080589684776

# Bot Colors
main_color = 0xD75BF4
error = 0xE02B2B
success = 0x42F56C
warning = 0xF59E42
info = 0x3682F5
level_up = 0x66DDAA
menu = 0x3D3D3D

# Vote Sites

vote_sites = [
    "https://servers-minecraft.net/server-adriftus-content.10752",
    "https://minecraftservers.org/server/628200"
]


# 8 ball responses
ball_responses = [
    "● It is certain.",
    "● It is decidedly so.",
    "● Without a doubt.",
    "● Yes – definitely.",
    "● You may rely on it.",
    "● As I see it, yes.",
    "● Most likely.",
    "● Outlook good.",
    "● Yes.",
    "● Signs point to yes.",
    "● Reply hazy, try again.",
    "● Ask again later.",
    "● Better not tell you now.",
    "● Cannot predict now.",
    "● Concentrate and ask again.",
    "● Don't count on it.",
    "● My reply is no.",
    "● My sources say no.",
    "● Outlook not so good.",
    "● Very doubtful."]

# Embeds ---------------------

permission_error = discord.Embed(
                title="Error!",
                description="You don't have the permission to use this command.",
                color=error
            )

