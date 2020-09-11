import discord
import random

def randomhex(): 
    return discord.Colour.from_rgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))