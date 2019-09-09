from discord.ext import commands
import json
import asyncio
import yaml
import random
import discord

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
    
def randomhex(): 
    return discord.Colour.from_rgb(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

class memes(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.reactemoji = '\N{THUMBS UP SIGN}'
        self.config = yaml.safe_load(open('config.yml'))
    
    @commands.command()
    async def readjson(self, ctx, path):
        '''[Path] - Reads and prints a json'''
        parsed_json = load_json(path)
        if parsed_json is None:
            await ctx.send("This file doesn't exist")
        elif parsed_json is -1:
            await ctx.send("This file is not a valid json")
        else:
            string = str(parsed_json)
            await ctx.send(f"```json\n{string[0:1950]}\n```")

    @commands.command()
    async def runjson(self, ctx, path):
        '''[Path] - Runs a json'''
        parsed_json = load_json(path)
        if parsed_json is None:
            await ctx.send("This file doesn't exist")
        elif parsed_json is -1:
            await ctx.send("This file is not a valid json")
        else:
            loop = parsed_json["repeat"]
            delay = parsed_json["delay"]
            while loop != 0:
                loop -= 1
                channels = parsed_json["channels"]
                for channel_id in channels:
                    messages = channels[channel_id]
                    channel = self.bot.get_channel(int(channel_id))
                    for message_text in messages:
                        await channel.send(message_text)
                        await asyncio.sleep(delay)

    @commands.command()
    async def addmeme(self, ctx, title, link):
        '''[title] [link] - Add a meme to the meme database'''
        parsed_json = load_json("meme.json")
        if title in parsed_json:
            await ctx.send("This meme already exists!")
        else:
            if len(title) > 25:
                await ctx.send(f"The title is too long! max 25 characters (currently {len(title)})")
            elif len(link) > 150:
                await ctx.send(f"The url is too long! max 150 characters (currently {len(link)})")
            else:
                parsed_json[title] = {"owner": ctx.message.author.id, "link": link}
                write_json("meme.json", parsed_json)
                await ctx.message.add_reaction(self.reactemoji)
        
    @commands.command()
    async def delmeme(self, ctx, *, title):
        '''[title] - Deletes a meme'''
        parsed_json = load_json("meme.json")
        if title not in parsed_json:
            await ctx.send("This meme doesn't exist!")
        else:
            meme = parsed_json[title]
            if meme["owner"] == ctx.message.author.id or ctx.message.author.id in self.config["admins"]:
                del parsed_json[title]
                write_json("meme.json", parsed_json)
                await ctx.message.add_reaction(self.reactemoji)
            else:
                await ctx.send("You are not an admin or not the owner of the meme")

    @commands.command()
    async def listmemes(self, ctx, page=1): #shit code, needs better code
        '''Lists all memes'''
        leftbound = 15 * (page - 1)
        rightbound = leftbound + 15
        parsed_json = load_json("meme.json")
        storage = []
        
        for meme in parsed_json:
            storage.append(meme)

        toprint = [f"ListMemes, page {page}/{int((len(storage) + 14) / 15)}, total {len(storage)} memes\n-----\n"]

        if len(storage) < leftbound:
            await ctx.send("input is out of range")
            return

        if len(storage) < rightbound:
            rightbound = len(storage)

        for i in range(rightbound - leftbound):
            toprint.append(f"{storage[i + leftbound]}\n")

        output = "".join(toprint)
        await ctx.send(output)

    @commands.command()
    async def meme(self, ctx, *, title):
        '''[title] - Displays a saved meme'''
        parsed_json = load_json("meme.json")
        if title not in parsed_json:
            await ctx.send("This meme doesn't exist!")
        else:
            meme = parsed_json[title]
            embed = discord.Embed(title=title, color=randomhex())
            embed.set_image(url=meme["link"])
            await ctx.send(embed=embed)

    @commands.command()
    async def dm_meme(self, ctx, user_id: discord.User, *, title):
        '''[ID] [title] - Dms a user a meme'''
        parsed_json = load_json("meme.json")
        if title not in parsed_json:
            await ctx.send("This meme doesn't exist!")
        else:
            meme = parsed_json[title]
            embed = discord.Embed(title=title, color=randomhex())
            embed.set_image(url=meme["link"])
            await user_id.send(embed=embed)
            await ctx.message.add_reaction(self.reactemoji)

    @commands.command(aliases=["yt"])
    async def youtube(self, ctx, number=0):
        '''Return a random youtube song in a pre-defined list'''
        number_local = number
        parsed_json = load_json("yt.json")
        yt = parsed_json["yt"]
        if number_local < 1:
            random_numb = random.randint(0, len(yt) - 1)
            await ctx.send(f"Random number: {random_numb + 1} / {len(yt)}\n{yt[random_numb]}")
        else:
            if number_local > len(yt):
                number_local = len(yt)
            await ctx.send(f"Video: {number_local} / {len(yt)}\n{yt[number_local-1]}")

def setup(bot):
    bot.add_cog(memes(bot))
