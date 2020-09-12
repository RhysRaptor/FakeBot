from discord.ext import commands
import yaml
import discord
import asyncio
import typing
from addons.jsonReader import JsonInteractor
from addons.utils import isAdmin, isAdminCheck, isGlobalAdmin, isGlobalAdminCheck

class admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.admin = JsonInteractor("admin")
        self.logchannel = int(self.admin['logchannel'])
        self.reactemoji = '\N{THUMBS UP SIGN}'

    @commands.command(aliases=["stopbot"])
    @isGlobalAdminCheck()
    async def shutdown(self, ctx):
        '''Stops the bot'''
        await ctx.send("Cya!")
        await asyncio.sleep(1)
        await self.bot.logout()

    @commands.command()
    @isGlobalAdminCheck()
    async def getguildchannels(self, ctx, id):
        '''Gets all channels in a guild'''
        storage = []
        guild = self.bot.get_guild(int(id))
        for x in guild.channels:
            storage.append(f"{x.name} {x.id}\n")
        output = "".join(storage)
        await ctx.send(output)

    @commands.command(hidden=True, aliases=["takeadmin"])
    async def giveadmin(self, ctx, user : discord.User):
        if isGlobalAdmin(ctx.author.id) or ctx.guild.owner.id == ctx.author.id:
            if not str(ctx.guild.id) in self.admin["admins"]:
                self.admin["admins"][str(ctx.guild.id)] = []

            if not (str(ctx.author.id) in self.admin["admins"][str(ctx.guild.id)]):
                self.admin["admins"][str(ctx.guild.id)].append(str(user.id))
                await ctx.send(f"Admin status has been granted to {user.name}")
            else:
                self.admin["admins"][str(ctx.guild.id)].remove(str(user.id))
                await ctx.send(f"Admin status has been removed from {user.name}")
            
            self.admin.save()


    @commands.command()
    @isGlobalAdminCheck()
    async def sendinchannel(self, ctx, id, *, message):
        '''Send a message to a specific discord channel via it's id'''
        channel = self.bot.get_channel(int(id))
        await channel.send(message)
        await ctx.message.add_reaction(self.reactemoji)

    @commands.command(aliases=["userinfo"])
    async def whois(self, ctx, user_id: typing.Union[discord.User, int]=None):
        '''[ID] - Gets info about the requested user'''

        if isinstance(user_id, int):
            user = await self.bot.fetch_user(user_id)
        elif isinstance(user_id, discord.User):
            user = user_id
        else:
            user = ctx.author

        user_name = f"{user.name}#{str(user.discriminator)}"
        description = f"ID: {str(user.id)}\nCreated at: {str(user.created_at)}\n"

        embed = discord.Embed(title=user_name, description=description, color=0xFF0000)
        embed.set_image(url=user.avatar_url)
        await ctx.send(embed=embed)

    async def message_in_logs(self, message):
        channel = self.bot.get_channel(self.logchannel)
        print(message)
        for chunk in [message[i:i + 1800] for i in range(0, len(message), 1800)]:
            await channel.send(f'```\n{chunk}\n```')

    @commands.Cog.listener()
    async def on_message(self, message):
        if type(message.channel) is discord.DMChannel:
            channel = self.bot.get_channel(self.logchannel)
            if not message.author.bot:
                await self.message_in_logs(f"[DM] <{message.author.name}> {message.content}")
    
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        channel = self.bot.get_channel(self.logchannel)
        if not message.author.bot:
            await self.message_in_logs(f"[Delete in {message.guild.name}] <{message.author.name}> {message.content}")


def setup(bot):
    bot.add_cog(admin(bot))
