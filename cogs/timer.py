from discord.ext import commands, tasks
import json
import asyncio
import time
import datetime

def load_json(path):
    try:
        with open(path) as json_file:
            parsed_json = json.load(json_file)
            return parsed_json
    except FileNotFoundError:
        return None
    except json.decoder.JSONDecodeError:
        return -1

def write_json(path, todump):
    with open(path, 'w') as fp:
        json.dump(todump, fp)

class timer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.timer = load_json("timer.json")
        self.reactemoji = '\N{THUMBS UP SIGN}'
        self.erremoji = '\N{Octagonal Sign}'
        self.lock = asyncio.Lock(loop=bot.loop)
        self.mainloop.start()
    
    @commands.command()
    async def remindme(self, ctx, number: int, numbertype, *, message):
        finaltime = int(time.time())
        addtime = number
        if number < 1:
            addtime = 1
        elif number > 500:
            addtime = 500
        else:
            addtime = number

        if (numbertype.lower() == "h"):
            addtime *= 3600
        elif (numbertype.lower() == "m"):
            addtime *= 60
        elif (numbertype.lower() == "s"):
            pass
        else:
            await ctx.message.add_reaction(self.erremoji)
            return
        
        finaltime += addtime
        self.timer[str(finaltime)] = [ctx.author.mention, ctx.message.channel.id, message]
        write_json("timer.json", self.timer)
        await ctx.message.add_reaction(self.reactemoji)

    @commands.command()
    async def remind_date(self, ctx, hour: int, minute: int, day: int, month: int, year: int, *, message):
        timestamp = int(datetime.datetime(year, month, day, hour, minute).timestamp())
        if str(timestamp) not in self.timer:
            self.timer[str(timestamp)] = [ctx.author.mention, ctx.message.channel.id, message]
            write_json("timer.json", self.timer)
            await ctx.message.add_reaction(self.reactemoji)

    @tasks.loop(seconds=5)
    async def mainloop(self):
        async with self.lock:
            await self.sideloop()


    async def sideloop(self):
        currenttime = int(time.time())
        todelete = []
        yeet = False
        for timerstr in self.timer:
            timer = int(timerstr)
            if (timer < currenttime):
                timerobj = self.timer[timerstr]
                channel = self.bot.get_channel(int(timerobj[1]))
                await channel.send(f"Time is up {timerobj[0]}! {timerobj[2]}")
                todelete.append(timerstr)

        if len(todelete) > 0:
            yeet = True
            for x in todelete:
                del self.timer[x]

        if yeet:
            write_json("timer.json", self.timer)

    def cog_unload(self):
        self.mainloop.cancel()

    @mainloop.before_loop
    async def before_mainloop(self):
        print("waiting til ready...")
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(timer(bot))
