from discord.ext import commands
import yaml
import discord
import asyncio

class admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = yaml.safe_load(open('config.yml'))
    
    @commands.command(aliases=["shutdown"])
    async def stop(self, ctx):
        '''Stops the bot'''
        if ctx.message.author.id in self.config["admins"]:
            await ctx.send("Cya!")
            await asyncio.sleep(1)
            await self.bot.logout()
        else:
            await ctx.send("This user isn't an admin")

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
            await channel.send(f"[Delete] <{message.author.name}> {message.content}")

def setup(bot):
    bot.add_cog(admin(bot))
