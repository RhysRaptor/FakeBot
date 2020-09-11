from discord.ext import commands, tasks, menus
import discord
import json
import asyncio
from datetime import datetime
import random
import yaml
from addons.jsonReader import JsonInteractor
from addons.menu import MakeMenu
from addons.utils import randomhex

class custom(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reactemoji = '\N{THUMBS UP SIGN}'
        self.commands = JsonInteractor("customCommands")
        self.admin = JsonInteractor("admin")
        if not self.commands:
            self.commands["commands"] = {}
        
    @commands.command()
    async def addcommand(self, ctx, name, *, message):
        if name not in self.commands["commands"]:
            self.commands["commands"][name] = {"message": message, "owner": str(ctx.author.id)}
            self.commands.save()
            await ctx.message.add_reaction(self.reactemoji)
        else:
            await ctx.send("This command already exists")

    @commands.command(aliases=["delcommand"])
    async def removecommand(self, ctx, name):
        if name in self.commands["commands"]:
            if int(self.commands["commands"][name]["owner"]) == ctx.author.id or str(ctx.author.id) in self.admin["admins"]:
                del self.commands["commands"][name]
                self.commands.save()
                await ctx.message.add_reaction(self.reactemoji)
            else:
                await ctx.send("You cannot delete this command")
        else:
            await ctx.send("Custom command not found")

    @commands.command(aliases=["listmemes"])
    async def listcommands(self, ctx):
        menu = MakeMenu("Custom Commands", list(self.commands["commands"].keys()), randomhex(), 15)
        await menu.start(ctx)

    @commands.command()
    async def runcommand(self, ctx, name):
        if name in self.commands["commands"]:
            await ctx.send(self.commands["commands"][name]["message"])
        else:
            await ctx.send("Custom command not found")

    @commands.command(hidden=True)
    async def runcommanderrquote(self, ctx, name):
        if name in self.commands["commands"]:
            await ctx.send(self.commands["commands"][name]["message"])
        else:
            temp = self.bot.get_command('forcequote')
            if temp:
                await ctx.invoke(temp)

def setup(bot):
    bot.add_cog(custom(bot))