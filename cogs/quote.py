from discord.ext import commands, tasks
import json
import asyncio
from datetime import datetime
import random
import yaml
from addons.jsonReader import JsonInteractor

class quote(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.lock = asyncio.Lock(loop=bot.loop)
        # self.quotes = load_json("quote.json")
        self.quotes = JsonInteractor("quotes")
        self.quotestartloop.start()

    @commands.command()
    async def addquote(self, ctx, *, quote):
        if (str(ctx.author.id) in self.quotes["quoters"]):
            self.quotes["quotes"].append(quote)
            # write_json("quote.json", self.quotes)
            self.quotes.save()
            await ctx.send(f"Added `{quote}`")
        else:
            await ctx.send("You are not allowed to add quotes") 

    @commands.command()
    async def quotecount(self, ctx):
        await ctx.send(f"The bot has currently {len(self.quotes['quotes'])} quotes")

    @commands.command()
    async def forcequote(self, ctx, number=-1):
        if int(number) < 0:
            getquote = self.quotes["quotes"][random.randint(0, len(self.quotes["quotes"]) - 1)]
            await ctx.send(f"{getquote}")
        else:
            if int(number) > len(self.quotes["quotes"]):
                getquote = self.quotes["quotes"][len(self.quotes["quotes"]) - 1]
            else:
                getquote = self.quotes["quotes"][number - 1]
            await ctx.send(f"{number}: {getquote}")

    @tasks.loop(seconds=300)
    async def quotestartloop(self):
        async with self.lock:
            await self.quotemainloop()

    @quotestartloop.before_loop
    async def before_mainloop(self):
        await self.bot.wait_until_ready()

    async def quotemainloop(self):
        channel = self.bot.get_channel(int(self.quotes["channel"]))
        if channel is None:
            print("Can't retrieve info, skipping for this round")
            return

        messages = await channel.history(limit=1).flatten()
        yeet = messages[0].created_at.timestamp() + self.quotes["time"] - datetime.utcnow().timestamp()
        print(f"running check {yeet}")
        if messages[0].created_at.timestamp() + self.quotes["time"] < datetime.utcnow().timestamp() and messages[0].author.bot is False:
            getquote = self.quotes["quotes"][random.randint(0, len(self.quotes["quotes"]) - 1)]
            await channel.send(f"{getquote}")

    def cog_unload(self):
        self.quotestartloop.cancel()

def setup(bot):
    bot.add_cog(quote(bot))