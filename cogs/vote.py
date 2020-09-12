from discord.ext import commands, tasks
import json
import asyncio
import time
import datetime
import yaml
import discord
from addons.jsonReader import JsonInteractor
from addons.utils import isAdminCheck

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

class vote(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.timer = load_json("vote.json")
        self.reactemoji = '\N{THUMBS UP SIGN}'
        self.erremoji = '\N{Octagonal Sign}'

    def is_vote_inactive():
        async def predicate(ctx):
            return ("Current vote" in load_json("vote.json")) == 0
        return commands.check(predicate)

    def is_vote_active():
        async def predicate(ctx):
            return "Current vote" in load_json("vote.json")
        return commands.check(predicate)
    
    @commands.command()
    @isAdminCheck()
    @is_vote_inactive()
    async def startvote(self, ctx, name, maxnum: int, maxpp: int):
        self.timer = {}
        self.timer["Current vote"] = name
        self.timer["Max vote num"] = str(maxnum)
        self.timer["Max per person"] = str(maxpp)
        self.timer["Votes"] = {}
        self.timer["Enum"] = {}
        write_json("vote.json", self.timer)
        await ctx.message.add_reaction(self.reactemoji)

    @commands.command(aliases=["vote_status"])
    @is_vote_active()
    async def tally(self, ctx):
        embed = discord.Embed(title=f"Vote progress for {self.timer['Current vote']}", color=0x00ff00) # for {self.timer["Current vote"]}
        votes = {}
        votes_combined = []

        if not self.timer["Votes"]:
            await ctx.send("Nobody has voted!")
            return

        for x in self.timer["Votes"]:
            for y in self.timer["Votes"][x]:
                if y not in votes:
                    votes[y] = 1
                else:
                    votes[y] = int(votes[y]) + 1
        

        for x in sorted(votes):
            if (str(x) in self.timer["Enum"]):   
                votes_combined.append(f"[{x}] {self.timer['Enum'][str(x)]}: {votes[x]} vote(s)")
            else:
                votes_combined.append(f"{x}: {votes[x]} vote(s)")

        votes_str = "\n".join(votes_combined)

        embed.add_field(name="Recorded votes", value=votes_str)
        embed.set_footer(text=f"Amount of users who voted: {len(self.timer['Votes'])}")
        await ctx.send(embed=embed)

    @commands.command(aliases=["vote_status_me"])
    @is_vote_active()
    async def tally_me(self, ctx):
        embed = discord.Embed(title=f"Vote progress for {self.timer['Current vote']}", color=0x00ff00) # for {self.timer["Current vote"]}

        if (str(ctx.author.id) in self.timer["Votes"]):
            votes_str = str(sorted(self.timer["Votes"][str(ctx.author.id)]))[1:-1]
        else:
            await ctx.send(f"No votes found for {ctx.author.display_name}")
            return

        embed.add_field(name=f"Recorded votes for {ctx.author.display_name}", value=votes_str)
        embed.set_footer(text=f"Amount of users who voted: {len(self.timer['Votes'])}")
        await ctx.send(embed=embed)


    @commands.command(aliases=["vote"])
    @is_vote_active()
    async def vote_on(self, ctx, number: int):
        if (str(ctx.author.id) in self.timer["Votes"]):
            if len(self.timer["Votes"][str(ctx.author.id)]) >= int(self.timer["Max per person"]):
                await ctx.send(f"You already have {int(self.timer['Max per person'])} vote(s) set!")
                return
        else:
            self.timer["Votes"][str(ctx.author.id)] = []

        if (number > int(self.timer["Max vote num"]) or number < 1):
            await ctx.send("Invalid voting number!")
            return

        if (number in self.timer["Votes"][str(ctx.author.id)]):
            await ctx.send("You already voted on this!")
            return

        self.timer["Votes"][str(ctx.author.id)].append(number)
        write_json("vote.json", self.timer)
        await ctx.message.delete()
        await ctx.send(f"Vote registered for {ctx.author.display_name}")

    @commands.command(aliases=["clearvote"])
    @is_vote_active()
    async def vote_clear(self, ctx):
        if (str(ctx.author.id) in self.timer["Votes"]):
            self.timer["Votes"].pop(str(ctx.author.id))
        else:
            await ctx.send(f"No votes found for {ctx.author.display_name}")
            return

        write_json("vote.json", self.timer)
        await ctx.message.add_reaction(self.reactemoji)
        
    @commands.command()
    @is_vote_active()
    @isAdminCheck()
    async def wipeactivevote(self, ctx):
        self.timer = {}
        write_json("vote.json", self.timer)
        await ctx.message.add_reaction(self.reactemoji)

    @commands.command()
    @is_vote_active()
    @isAdminCheck()
    async def voteAddEnum(self, ctx, number: int, *, enum):
        if (number > int(self.timer["Max vote num"]) or number <= 0):
            await ctx.send("Number out of range")
            return

        self.timer["Enum"][str(number)] = enum
        write_json("vote.json", self.timer)
        await ctx.message.add_reaction(self.reactemoji)

    @commands.command(aliases=["showvotable", "votable"])
    @is_vote_active()
    async def showVotable(self, ctx):
        embed = discord.Embed(title=f"Registered entries for {self.timer['Current vote']}", color=0x0000ff)

        for x in self.timer["Enum"]:
            embed.add_field(name=f"Vote on {x} for", value=f"{self.timer['Enum'][x]}", inline=False)

        embed.set_footer(text=f"Amount of users who voted: {len(self.timer['Votes'])}")
        await ctx.send(embed=embed)
    


def setup(bot):
    bot.add_cog(vote(bot))
