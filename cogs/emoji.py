from discord.ext import commands
import asyncio
import discord
import random

class emoji(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emojilist = None

    @commands.command(aliases=["emote"])
    async def emoji(self, ctx, emojiname):
        if self.emojilist == None:
            print("building emote db")
            self.emojilist = []
            for emote in self.bot.emojis:
                print(f"emote: {emote.name}")
                self.emojilist.append(emote)

        for emote in self.emojilist:
            if emojiname == emote.name:
                await ctx.send(str(emote))
                return

        await ctx.send("Emoji not found!")

    @commands.command()
    async def refresh_emoji(self, ctx):
        print("building emote db")
        self.emojilist = []
        for emote in self.bot.emojis:
            print(f"emote: {emote.name}")
            self.emojilist.append(emote)
        await ctx.send(f"This bot has access to {len(self.emojilist)} emotes")

    @commands.command()
    async def emoji_count(self, ctx):
        await ctx.send(f"This bot has access to {len(self.emojilist)} emotes")


def setup(bot):
    bot.add_cog(emoji(bot))