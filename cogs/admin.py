from discord.ext import commands
import yaml
import discord
import asyncio

class admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = yaml.safe_load(open('config.yml'))

    def is_admin():
        async def predicate(ctx):
            yeet = yaml.safe_load(open('config.yml'))
            return ctx.author.id in yeet["admins"]
        return commands.check(predicate)
        

    @commands.command(aliases=["stopbot"])
    @is_admin()
    async def shutdown(self, ctx):
        '''Stops the bot'''
        await ctx.send("Cya!")
        await asyncio.sleep(1)
        await self.bot.logout()

    @shutdown.error
    async def shutdown_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("You can't shut down the server")

    @commands.command(aliases=["userinfo"])
    async def whois(self, ctx, user_id: discord.User=None):
        '''[ID] - Gets info about the requested user'''
        if not user_id:
            user_id = ctx.author
        user = f"{user_id.name}#{str(user_id.discriminator)}"
        description = f"ID: {str(user_id.id)}\nCreated at: {str(user_id.created_at)}\n"
        embed = discord.Embed(title=user, description=description, color=0xFF0000)
        embed.set_image(url=user_id.avatar_url)
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if type(message.channel) is discord.DMChannel:
            channel = self.bot.get_channel(self.config["log_channel"])
            if message.author.id != 620216042651910165:
                await channel.send(f"[DM] <{message.author.name}> {message.content}")
    
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        channel = self.bot.get_channel(self.config["log_channel"])
        if message.author.id != 620216042651910165:
            await channel.send(f"[Delete in {message.guild.name}] <{message.author.name}> {message.content}")

def setup(bot):
    bot.add_cog(admin(bot))
