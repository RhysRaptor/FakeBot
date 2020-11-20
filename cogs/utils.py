from discord.ext import commands
import asyncio
import discord
import random
import json
from addons.utils import isAdmin, isAdminCheck, isGlobalAdmin, isGlobalAdminCheck
import typing

class utils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reactemoji = '\N{THUMBS UP SIGN}'
        self.erremoji = '\N{Octagonal Sign}'
        self.angryemoji = '\N{Angry Face}'
        self.toomuchinputemoji = '\N{Input Symbol for Symbols}'
        self.isspamactive = False

    @commands.command()
    async def ping(self, ctx):
        '''Responds with Pong!'''
        await ctx.send("Pong!")

    @commands.command()
    async def source(self, ctx):
        '''Responds with a link to the source code of this bot'''
        await ctx.send("https://github.com/suchmememanyskill/FakeBot")

    @commands.command()
    async def message(self, ctx, *, message):
        '''[Message] Sends a message on the bots behalf'''
        await ctx.send(message)
    
    @commands.command()
    async def message_delete(self, ctx, *, message):
        '''[Message] ^ and also deletes the invoking message'''
        await ctx.send(message)
        await ctx.message.delete()

    @commands.command()
    async def embed(self, ctx, title, *, description):
        '''Send and embed via the bot'''
        embed = discord.Embed(title=title, description=description, color=0x00ff00)
        await ctx.message.channel.send(embed=embed)
    
    @commands.command()
    async def dm(self, ctx, user_id: discord.User, *, message):
        '''[Ping] [Message] DM a user with a specific message'''
        await user_id.send(message)
        await ctx.message.add_reaction(self.reactemoji)
    
    @commands.command()
    @isAdminCheck()
    async def dmuser(self, ctx, user_id: typing.Union[discord.User, int]=None, *, message):
        if isinstance(user_id, int):
            user = await self.bot.fetch_user(user_id)
        elif isinstance(user_id, discord.User):
            user = user_id
        else:
            user = ctx.author

        await user.send(message)
        await ctx.message.add_reaction(self.reactemoji)

    @commands.command()
    async def spam(self, ctx, amount_string, *, message):
        '''[Amount] [Message] Spam a message'''
        if self.isspamactive is None:
            self.isspamactive = False
        amount = int(amount_string)
        if amount > 5 or self.isspamactive is True:
            await ctx.send("Fuck you")
        else:
            self.isspamactive = True
            for i in range(amount):
               await ctx.send(message)
            self.isspamactive = False

    @commands.command(aliases=["playing"])
    async def game(self, ctx, *, string):
        '''[Message] - Change the bots "currently playing" message'''
        await self.bot.change_presence(activity=discord.Game(name=string))
        await ctx.message.add_reaction(self.reactemoji)

    @commands.command()
    async def nick(self, ctx, *, name : str):
        if (len(name) > 32):
            await ctx.send("Provided name is too long")
        
        await ctx.guild.me.edit(nick=name)
        await ctx.message.add_reaction(self.reactemoji)

    @commands.command(aliases=["coin"])
    async def coinflip(self, ctx):
        '''Flip a coin'''
        if random.randint(0, 1) == 0:
            await ctx.send("Heads!")
        else:
            await ctx.send("Tails!")

    @commands.command(aliases=["rolldice"])
    async def dice(self, ctx, amount: int = 1, eyes: int = 6):
        '''[amount] [eyes] - yeet a dice'''
        if eyes < 1 or amount < 1 or amount > 999 or eyes > (40**40):
            await ctx.message.add_reaction(self.erremoji)
        else:
            rolls = []
            for _ in range(0, amount):
                rolls.append(random.randint(1, eyes))
            outputstring = str(rolls)[1:-1]
            if len(outputstring) > 1900:
                await ctx.message.add_reaction(self.toomuchinputemoji)
            else:
                await ctx.send(f"{eyes}-sided dice roll (x{amount}) [sum: {sum(rolls)}]: {outputstring}")

def setup(bot):
    bot.add_cog(utils(bot))