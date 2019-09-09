from discord.ext import commands
import asyncio
import discord

class utils(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reactemoji = '\N{THUMBS UP SIGN}'
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
        '''[ID] [Message] DM a user with a specific message'''
        await user_id.send(message)
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

    @commands.command()
    async def game(self, ctx, *, string):
        '''[Message] - Change the bots "currently playing" message'''
        await self.bot.change_presence(activity=discord.Game(name=string))
        await ctx.message.add_reaction(self.reactemoji)


    #@commands.command()
    #async def test(self, ctx, channel_id: discord.TextChannel, *, message):
    #    await channel_id.send(message)

    #@commands.command()
    #async def test2(self, ctx, channel_id, *, message):
    #    channel = self.bot.get_channel(int(channel_id))
    #    await channel.send(message)


def setup(bot):
    bot.add_cog(utils(bot))