from discord.ext import commands
import discord
import youtube_dl
import yaml
import functools
import asyncio
import os

dl_settings = {
"outtmpl": "music/output.mp3",
"format": "bestaudio/best"
}

class music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.vc = None
        self.config = yaml.safe_load(open('config.yml'))
        self.reactemoji = '\N{THUMBS UP SIGN}'
        self.volumefloat = 0.4

    @commands.command(aliases=["summon"])
    async def join(self, ctx):
        '''Let the bot join the voice channel you're currently in'''
        if self.vc is not None:
            await ctx.send("Im already in a voice channel!")
            return
        try:
            channel = ctx.message.author.voice.channel
            await channel.connect()
            self.vc = ctx.voice_client
        except AttributeError:
            await ctx.send("You are not in a voice channel")
    
    @commands.command(aliases=["fuckoff"])
    async def leave(self, ctx):
        voice_user = ctx.message.author.voice
        '''Let the bot leave a voice channel'''
        if self.vc.is_playing() is True or self.vc.is_paused() is True:
            self.vc.stop()
        if self.vc is None:
            await ctx.send("The bot hasn't joined a voice channel")
        elif voice_user is None:
            await ctx.send("You are not in a voice channel")
        elif voice_user.channel.id is self.vc.channel.id:
            await self.vc.disconnect()
            self.vc = None
        elif voice_user.channel.id is not self.vc.channel.id:
            await ctx.send("You arent in the same voice channel as me!")
            
    @commands.command()
    async def volume(self, ctx, vol=50):
        '''[Vol 1-100] - Set the volume of the bot, default 40%'''
        if vol > 100 or vol < 1:
            await ctx.send("Volume needs to be between 1 and 100")
            return
        if self.vc is not None:
            if self.vc.is_playing() is True or self.vc.is_paused() is True:
                self.vc.source.volume = (vol/100)
            self.volumefloat = (vol/100)
            await ctx.message.add_reaction(self.reactemoji)
        else:
            await ctx.send("Bot isn't playing any music")

    @commands.command(aliases=["continue"])
    async def pause(self, ctx):
        '''Pause or continue playing the music on the bot'''
        print(f"{self.vc.is_playing()} {self.vc.is_paused()}")
        if self.vc.is_playing() is True:
            self.vc.pause()
        else:
            self.vc.resume()
        await ctx.message.add_reaction(self.reactemoji)

    @commands.command()
    async def play_mp3(self, ctx, path):
        '''Lets you play a hardcoded mp3 file - Only meme should use this'''
        if self.vc is None:
            await ctx.send("Bot is not in a voice channel")
        else:
            self.vc.play(discord.FFmpegPCMAudio(path))
            self.vc.source = discord.PCMVolumeTransformer(self.vc.source)
            self.vc.source.volume = self.volumefloat
            try:
                await ctx.message.add_reaction(self.reactemoji)
            except:
                pass


    @commands.command()
    async def play(self, ctx, url):
        '''Plays a song from a yt link'''
        if os.path.isfile("music/output.mp3") is True:
            os.remove("music/output.mp3")
        if self.vc is None:
            await ctx.send("Bot is not in a voice channel, attempting to join")
            await ctx.invoke(self.bot.get_command('join'))
            await asyncio.sleep(1)
            if self.vc is None:
                await ctx.send("failed to join channel")
                return
        if self.vc.is_playing() is True or self.vc.is_paused() is True:
            self.vc.stop()
        with youtube_dl.YoutubeDL(dl_settings) as ydl:
            loop = asyncio.get_event_loop()
            dictMeta = ydl.extract_info(url, download=False)
            if int(dictMeta['duration']) > 600:
                await ctx.send("Song is too long! (Needs to be less than 600 seconds)")
                return
            meth = functools.partial(ydl.download, [url])
            await loop.run_in_executor(None, meth)
        print(f"[Playing]: {url}")
        await ctx.invoke(self.bot.get_command('play_mp3'), "music/output.mp3")

def setup(bot):
    bot.add_cog(music(bot))