import discord
import random
from discord.ext import commands
from addons.jsonReader import JsonInteractor

def randomhex(): 
    return discord.Colour.from_rgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

def isAdmin(authorId : int, guildOwnerId : int):
    admin = JsonInteractor("admin")
    if str(authorId) in admin["globalAdmins"] or guildOwnerId == authorId:
        return True
    
    if str(ctx.guild.id) in admin["admins"]:
        if (str(authorId) in admin["admins"][str(ctx.guild.id)]):
            return True

    return False

def isGlobalAdmin(authorId : int):
    admin = JsonInteractor("admin")
    return str(authorId) in admin["globalAdmins"]

def isAdminCheck():
    async def predicate(ctx):
        admin = JsonInteractor("admin")
        if str(ctx.author.id) in admin["globalAdmins"] or ctx.guild.owner.id == ctx.author.id:
            return True
    
        if str(ctx.guild.id) in admin["admins"]:
            if (str(ctx.author.id) in admin["admins"][str(ctx.guild.id)]):
                return True

        return False
    return commands.check(predicate)

def isGlobalAdminCheck():
    async def predicate(ctx):
        admin = JsonInteractor("admin")
        return str(ctx.author.id) in admin["globalAdmins"]
    return commands.check(predicate)

def isOwnServerCheck():
    async def predicate(ctx):
        return ctx.guild.id == 381588351653904385
    return commands.check(predicate)