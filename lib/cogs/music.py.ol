import os
import sys
import DiscordUtils
import discord
import youtube_dl
import urllib
import simplejson
from ffmpeg import FFmpeg

from discord_components import DiscordComponents, ComponentsBot, Button  # For buttons later
from discord.ext import commands

if not os.path.isfile("config.py"):
    sys.exit("'config.py' not found! Please add it and try again.")
else:
    import config
discord_error = discord.ext.commands.errors

music = DiscordUtils.Music()


class Music(commands.Cog, name="music"):
    def __init__(self, bot):
        self.bot = bot

    # Join Command
    @commands.command(name="join")
    async def join(self, ctx):
        """
        Makes the Bot join the VC that the sender is in.
        """
        author_connected = ctx.author.voice
        bot_connected = ctx.guild.me.voice

        try:
            if author_connected and not bot_connected:
                await ctx.author.voice.channel.connect()
                await ctx.send(f'Bot is connected for music in: {ctx.guild.me.voice.channel}')
                print(f'Bot joined {ctx.author.voice.channel} (ID: {ctx.author.voice.channel.id})')
            else:
                await ctx.send("You're not in a voice channel")
        except Exception as err:
            print(f'Error with joining channel {ctx.author.voice.channel}: {err}')
            await ctx.send(f'Error with joining channel {ctx.author.voice.channel}: {err}')

    # Leave Command
    @commands.command(name="leave")
    async def leave(self, ctx):
        """
        Forces the Bot to leave the VC.
        """
        author_connected = ctx.author.voice
        bot_connected = ctx.guild.me.voice

        if author_connected and bot_connected:
            await ctx.send(f'Bot disconnected music for: {ctx.guild.me.voice.channel}')
            print(f'Bot left {ctx.author.voice.channel} (ID: {ctx.author.voice.channel.id})')
            await ctx.voice_client.disconnect()
        elif author_connected and not bot_connected:
            await ctx.send("I'm not in a voice channel.")
        elif bot_connected and not author_connected:
            await ctx.send("We're not in the same voice channel.")

    # Player handler
    @commands.command(name="play")
    async def play(self, ctx, *, url):
        """
        Plays a song from URL. Adds to queue if a song is already playing.
        """

        ctx.voice_client.stop()
        FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        YDL_OPTIONS = {'format': 'bestaudio',
                       "noplaylist": True,
                       'audioformat': 'mp3',
                       'quiet': True,
                       'no_warnings': True,
                       'default_search': 'auto'}
        vc = ctx.voice_client

        author_connected = ctx.author.voice
        bot_connected = ctx.guild.me.voice

        if author_connected and bot_connected:
            if bot_connected.channel.id == author_connected.channel.id:
                try:
                    with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
                        info = ydl.extract_info(url, download=False)
                        url2 = info['formats'][0]['url']
                        videoID = url.split("watch?v=")[1].split("&")[0]
                        thumbnail = f"https://img.youtube.com/vi/{videoID}/0.jpg"
                        source = await discord.FFmpegOpusAudio.from_probe(url2, **FFMPEG_OPTIONS)
                        vc.play(source)

                    await ctx.message.delete()

                    embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)
                    embed.set_image(url=thumbnail)
                    await ctx.send(embed=embed)
                    print(f'Bot playing music in {ctx.author.voice.channel} (ID: {ctx.author.voice.channel.id})')

                except DownloadError as err:
                    print(f'There was an error playing song: {err}')
                    await ctx.send(f'You cannot play this song right now, please try again later.')
                except exception:
                    await ctx.send('An error has occurred with your requested song. Please try a different link.')

            else:
                await ctx.send("We need to be in the same channel to give me commands.")

        elif author_connected and not bot_connected:
            await ctx.send("Please invite me to your channel with !join")

        elif bot_connected and not author_connected:
            await ctx.send("We're not in the same voice channel.")

    # Queue Command
    @commands.command(name="queue")
    async def queue(self, ctx):
        """
        Prints the queue to chat.
        """
        player = self.music.get_player(guild_id=ctx.guild.id)
        try:
            await ctx.send(f"Current Queue: {', '.join([song.name for song in player.current_queue()][1::2])}")
        except AttributeError as err:
            print(f"The queue is empty: {err}")
            await ctx.send(f'The queue is empty! Try adding a song with `{config.BOT_PREFIX}play [url]`')

    # Pause Command
    @commands.command(name="pause")
    async def pause(self, ctx):
        """
        Will pause the player, and wait for resume.
        """
        try:
            await ctx.voice_client.pause()
            await ctx.send('Paused')
        except AttributeError as err:
            print(f'There is no song playing: {err}')
            await ctx.send(f'There is no song playing. Try adding a song with `{config.BOT_PREFIX}play [url]`')

    # Resume Command
    @commands.command(name="resume")
    async def resume(self, ctx):
        """
        Will resume the player if paused.
        """
        try:
            await ctx.voice_client.resume()
            await ctx.send(f'Resumed')
        except AttributeError as err:
            print(f'There is no song paused: {err}')
            await ctx.send(f'There is no song paused. You can pause the song with `{config.BOT_PREFIX}pause`')


def setup(bot):
    bot.add_cog(Music(bot))
