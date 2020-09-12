from discord.ext import commands, tasks, menus
from discord.utils import get
import discord
import json
import asyncio
from datetime import datetime
import random
import yaml
from addons.jsonReader import JsonInteractor
from addons.menu import MakeMenu
from addons.utils import randomhex, isAdminCheck

def tryIntParse(string: str):
    try:
        ret = int(string)
        return ret
    except:
        return None

def getter(iterables, id: int):
    data = get(iterables, id=id)
    return data

class toggle(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reactemoji = '\N{THUMBS UP SIGN}'
        self.roles = JsonInteractor("toggle")
        if not self.roles:
            self.roles["roles"] = {}

    async def displayRole(self, ctx, role, name):
        embed = discord.Embed(title=name, color=randomhex())
        embed.add_field(name="Role:", value=f"<@&{role['id']}>", inline=False)
        embed.add_field(name="Description:", value=role["desc"], inline=False)
        
        roleObj = getter(ctx.guild.roles, int(role['id']))

        if (len(roleObj.members) > 0):
            users = [x.mention for x in roleObj.members]
            embed.add_field(name="Members:", value=" ".join(users), inline=False)

        if (roleObj is not None):
            embed.set_footer(text=f"Amount of people who have this role: {len(roleObj.members)}")

        await ctx.send(embed=embed)

    async def parseSearch(self, ctx, search):
        if (str(ctx.guild.id) not in self.roles["roles"]):
            await ctx.send("This server has no toggleable roles")
            return None

        roleDict = self.roles["roles"][str(ctx.guild.id)]
        roleList = list(roleDict.keys())

        name = None

        if (tryIntParse(search) is not None):
            searchInt = tryIntParse(search)
            if (0 < searchInt <= len(roleDict)):
                name = roleList[searchInt - 1]
            else:
                await ctx.send("Index out of range")
                return None
        else:
            searchLower = search.lower()
            for x in roleList:
                if (searchLower == x.lower()):
                    name = x

            if (name is None):
                await ctx.send("No toggleable roles found with that name")
                return None

        return name
    
    async def parseSearchToRoleDict(self, ctx, search):
        name = await self.parseSearch(ctx, search)
        if (name is not None):
            return self.roles["roles"][str(ctx.guild.id)][name]
        return None

    @commands.command(aliases=["toggleableroles", "toggleshow", "togglerole", "roleinfo", "info"])
    async def toggleroles(self, ctx, *, search = None):
        if (str(ctx.guild.id) not in self.roles["roles"]):
            await ctx.send("This server has no toggleable roles")
            return

        roleDict = self.roles["roles"][str(ctx.guild.id)]
        roleList = list(roleDict.keys())

        if (search is None):
            menu = MakeMenu(f"Toggleable roles for {ctx.guild.name}", roleList, randomhex(), 20)
            await menu.start(ctx)
        else:
            name = await self.parseSearch(ctx, search)
            if (name is not None):
                role = self.roles["roles"][str(ctx.guild.id)][name]
                await self.displayRole(ctx, role, name)


    @commands.command(aliases=["join", "leave", "toggleleave"])
    async def togglejoin(self, ctx, *, search):
        name = await self.parseSearch(ctx, search)
        if (name is None):
            return

        role = self.roles["roles"][str(ctx.guild.id)][name]
        roleObj = getter(ctx.author.roles, int(role['id']))

        if (roleObj is not None):
            await ctx.author.remove_roles(roleObj)
            await ctx.send(f"Successfully removed {name} from {ctx.author.display_name}")
        else:
            roleObj = getter(ctx.guild.roles, int(role['id']))
            await ctx.author.add_roles(roleObj)
            await ctx.send(f"Successfully added {name} to {ctx.author.display_name}")


    @commands.command(aliases=["mention"])
    async def mentionrole(self, ctx, *, search):
        role = await self.parseSearchToRoleDict(ctx, search)
        if (role is None):
            return

        await ctx.send(f"<@&{role['id']}>")


    @commands.command(aliases=["addrole"])
    @isAdminCheck()
    async def togglecreate(self, ctx, name, *, description):
        role = await ctx.guild.create_role(name=name)

        if (str(ctx.guild.id) not in self.roles["roles"]):
            self.roles["roles"][str(ctx.guild.id)] = {}

        self.roles["roles"][str(ctx.guild.id)][name] = {"id": str(role.id), "desc": description}
        self.roles.save()

        await ctx.message.add_reaction(self.reactemoji)


    @commands.command(aliases=["delrole", "deleterole"])
    @isAdminCheck()
    async def toggledelete(self, ctx, *, search):
        name = await self.parseSearch(ctx, search)
        if (name is None):
            return

        role = self.roles["roles"][str(ctx.guild.id)][name]

        roleObj = getter(ctx.guild.roles, int(role['id']))
        if (roleObj is not None):
            await roleObj.delete()

        del self.roles["roles"][str(ctx.guild.id)][name]
        self.roles.save()

        await ctx.message.add_reaction(self.reactemoji)

    @commands.command(aliases=["editrole"])
    @isAdminCheck()
    async def toggleedit(self, ctx, search, key, value):
        name = await self.parseSearch(ctx, search)
        if (name is None):
            return

        role = self.roles["roles"][str(ctx.guild.id)][name]
        
        if key not in role.keys():
            await ctx.send(f"This is not a valid key. Valid keys are: {', '.join(role.keys())}")
            return
        
        self.roles["roles"][str(ctx.guild.id)][name][key] = value
        self.roles.save()

        await ctx.message.add_reaction(self.reactemoji)

    

def setup(bot):
    bot.add_cog(toggle(bot))