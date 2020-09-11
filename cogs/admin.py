from discord.ext import commands
import yaml
import discord
import asyncio
import typing
from addons.jsonReader import JsonInteractor

class admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.admin = JsonInteractor("admin")
        self.logchannel = int(self.admin['logchannel'])
        self.reactemoji = '\N{THUMBS UP SIGN}'

    def is_admin():
        async def predicate(ctx):
            admin = JsonInteractor("admin")
            return str(ctx.author.id) in admin["admins"]
        return commands.check(predicate)

    @commands.command(aliases=["stopbot"])
    @is_admin()
    async def shutdown(self, ctx):
        '''Stops the bot'''
        await ctx.send("Cya!")
        await asyncio.sleep(1)
        await self.bot.logout()

    @commands.command()
    @is_admin()
    async def get_guild_channels(self, ctx, id):
        '''Gets all channels in a guild'''
        storage = []
        guild = self.bot.get_guild(int(id))
        for x in guild.channels:
            storage.append(f"{x.name} {x.id}\n")
        output = "".join(storage)
        await ctx.send(output)

    @commands.command()
    @is_admin()
    async def send_via_id(self, ctx, id, *, message):
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
