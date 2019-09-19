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

class music2(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.vc = None
        self.guild_id = None
        self.config = yaml.safe_load(open('config.yml'))
        self.reactemoji = '\N{THUMBS UP SIGN}'
        self.clock = '\N{STOPWATCH}'
        self.volumefloat = 0.4
        self.queue = []
        self.nowplaying = None
    
    def isinvoice():
        async def predicate(ctx):
            if ctx.voice_client is None:
                return False
            else:
                return True
        return commands.check(predicate)        

    async def autojoinvoice(self, ctx):
        if ctx.voice_client is None:
            channel = ctx.message.author.voice.channel
            if channel is not None:
                await channel.connect()
                return True
            return False
        else:
            return True

    def userinsamevoice():
        async def predicate(ctx):
            if ctx.message.author.voice is None or ctx.voice_client is None:
                return False
            else:
                return ctx.message.author.voice.channel.id == ctx.voice_client.channel.id
        return commands.check(predicate) 

    async def ret_list(self, input_list, pageamount):
        length = len(input_list)
        storage = []
        rightbound = pageamount

        if length < rightbound:
            rightbound = length

        for i in range(rightbound):
            getytstring = await self.getyoutubestat(input_list[i], 'title')
            storage.append(f"{i + 1}: {getytstring}\n")

        return "".join(storage)

    async def getyoutubestat(self, url, stat):
        with youtube_dl.YoutubeDL(dl_settings) as ydl:
            loop = asyncio.get_event_loop()
            meth = functools.partial(ydl.extract_info, url, download=False)
            dictMeta = await loop.run_in_executor(None, meth)
            return dictMeta[stat]
    
    async def downloadandplay(self, url):
        path = f"music/{self.guild_id}.mp3"
        if os.path.isfile(path) is True:
            os.remove(path)
        dl_settings["outtmpl"] = path
        with youtube_dl.YoutubeDL(dl_settings) as ydl:
            loop = asyncio.get_event_loop()
            meth = functools.partial(ydl.download, [url])
            await loop.run_in_executor(None, meth)
        self.nowplaying = url
        print(f"[Playing]: {self.nowplaying}")
        await self.playmp3_internal(path)

    def queuefunc(self, error):
        self.nowplaying = None
        if self.queue == []:
            self.bot.loop.create_task(self.vc.disconnect())
        else:
            self.bot.loop.create_task(self.downloadandplay(self.queue[0]))
            self.queue.pop(0)  

    async def playmp3_internal(self, path):
        self.vc.play(discord.FFmpegPCMAudio(path), after=self.queuefunc)
        self.vc.source = discord.PCMVolumeTransformer(self.vc.source)
        self.vc.source.volume = self.volumefloat

    @commands.command()
    async def play_mp3(self, ctx, path):
        '''todo: add desc'''
        invoice = await self.autojoinvoice(ctx)
        if invoice is True:
            self.vc = ctx.voice_client
            await self.playmp3_internal(path)
            await ctx.message.add_reaction(self.reactemoji)
    
    @commands.command(aliases=["continue"])
    @userinsamevoice()
    @isinvoice()
    async def pause(self, ctx):
        '''Pause or continue playing the music on the bot'''
        if self.vc is None:
            return
        if self.vc.is_playing() is True:
            self.vc.pause()
        else:
            self.vc.resume()
        await ctx.message.add_reaction(self.reactemoji)
    
    @commands.command(aliases=["fuckoff"])
    @isinvoice()
    @userinsamevoice()
    async def stop(self, ctx):
        if self.vc is None:
            return
        if (self.vc.is_playing() is True or self.vc.is_paused() is True):
            self.queue = []
            self.vc.stop()
        await ctx.message.add_reaction(self.reactemoji)
    
    @commands.command()
    @isinvoice()
    @userinsamevoice()
    async def skip(self, ctx):
        if self.vc is None:
            return
        if (self.vc.is_playing() is True or self.vc.is_paused() is True):
            self.vc.stop()
        await ctx.message.add_reaction(self.reactemoji)

    @commands.command()
    @userinsamevoice()
    async def volume(self, ctx, vol=50):
        if 101 < vol < 1:
            await ctx.send("Volume needs to be between 1 and 100")
            return
        if self.vc is not None:
            if self.vc.is_playing() is True or self.vc.is_paused() is True:
                self.vc.source.volume = (vol/100)
                self.volumefloat = (vol/100)
                await ctx.message.add_reaction(self.reactemoji)
        else:
            await ctx.send("Bot isn't playing any music")

    @commands.command()
    async def play(self, ctx, url):
        invoice = await self.autojoinvoice(ctx)
        if invoice is True:
            self.guild_id = ctx.message.guild.id
            self.vc = ctx.voice_client
            lengthstring = await self.getyoutubestat(url, 'duration')
            if int(lengthstring) > 600:
                await ctx.send("Song is too long!")
                return
            if self.vc.is_playing() is True or self.vc.is_paused() is True:
                self.queue.append(url)
                await ctx.message.add_reaction(self.clock)
                return
            await ctx.send("Downloading song, please wait...")
            await self.downloadandplay(url)
            await ctx.message.add_reaction(self.reactemoji)

    @commands.command(aliases=["nowplaying"])
    async def queue(self, ctx):
        if self.queue == []:
            if self.nowplaying is None:
                await ctx.send("Queue is empty!")
            else:
                await ctx.send(f"Bot is currently playing:\n{self.nowplaying}")

        else:
            await ctx.send("Getting song names, please wait....")
            queuestring = await self.ret_list(self.queue, 6)
            getytstring = await self.getyoutubestat(self.nowplaying, 'title')
            await ctx.send(f"List Queue, total {len(self.queue)}\nNow playing: {getytstring}\n-----\n{queuestring}")

    @commands.command(aliases=["del"])
    async def queue_del(self, ctx, pos=1):
        if self.queue == []:
            await ctx.send("Queue is empty!")
        elif pos < 1:
            await ctx.send("Invalid queue position (position should be bigger or equal to 1)")
        elif pos > len(self.queue):
            await ctx.send("Invalid queue position (position should not be bigger than the queue itself)")
        else:
            self.queue.pop(pos - 1)
            await ctx.message.add_reaction(self.reactemoji)

    @play_mp3.error
    async def play_mp3_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("I'm not in voice and i can't join voice for some reason")

    #notes
    #get length of song before adding it to the queue
    #is a good idea
        

def setup(bot):
    bot.add_cog(music2(bot))