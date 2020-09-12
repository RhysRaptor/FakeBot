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
from addons.utils import isAdmin

class custom(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reactemoji = '\N{THUMBS UP SIGN}'
        self.commands = JsonInteractor("customCommands")
        if not self.commands:
            self.commands["commands"] = {}
        
    @commands.command()
    async def addcommand(self, ctx, name, *, message):
        if str(ctx.guild.id) not in self.commands["commands"]:
            self.commands["commands"][str(ctx.guild.id)] = {}

        if name not in self.commands["commands"][str(ctx.guild.id)]:
            self.commands["commands"][str(ctx.guild.id)][name] = {"message": message, "owner": str(ctx.author.id)}
            self.commands.save()
            await ctx.message.add_reaction(self.reactemoji)
        else:
            await ctx.send("This command already exists")

    @commands.command(aliases=["delcommand"])
    async def removecommand(self, ctx, name):
        if str(ctx.guild.id) in self.commands["commands"] and name in self.commands["commands"][str(ctx.guild.id)]:
            if int(self.commands["commands"][str(ctx.guild.id)][name]["owner"]) == ctx.author.id or isAdmin(ctx.author.id, ctx.guild.owner.id):
                del self.commands["commands"][str(ctx.guild.id)][name]
                self.commands.save()
                await ctx.message.add_reaction(self.reactemoji)
            else:
                await ctx.send("You cannot delete this command")
        else:
            await ctx.send("Custom command not found")

    @commands.command(aliases=["listmemes"])
    async def listcommands(self, ctx):
        if str(ctx.guild.id) in self.commands["commands"] and len(self.commands["commands"][str(ctx.guild.id)]) > 0:
            menu = MakeMenu("Custom Commands", list(self.commands["commands"][str(ctx.guild.id)].keys()), randomhex(), 15)
            await menu.start(ctx)
        else:
            await ctx.send("No custom commands were found for this server")

    @commands.command()
    async def runcommand(self, ctx, name):
        if str(ctx.guild.id) in self.commands["commands"] and name in self.commands["commands"][str(ctx.guild.id)]:
            await ctx.send(self.commands["commands"][str(ctx.guild.id)][name]["message"])
        else:
            await ctx.send("Custom command not found")

    @commands.command(hidden=True)
    async def runcommanderrquote(self, ctx, name):
        if str(ctx.guild.id) in self.commands["commands"] and name in self.commands["commands"][str(ctx.guild.id)]:
            await ctx.send(self.commands["commands"][str(ctx.guild.id)][name]["message"])
        else:
            temp = self.bot.get_command('forcequote')
            if temp and ctx.guild.id == 381588351653904385:
                try:
                    await ctx.invoke(temp)
                except:
                    pass
                

def setup(bot):
    bot.add_cog(custom(bot))