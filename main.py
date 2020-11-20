# Bot cog template - Dynamic cog loading template.
# Copyright (C) 2018 - Valentijn "noirscape" V.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License, version 2 as published by
# the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

import yaml
from discord.ext import commands
import discord
import os
from traceback import format_exception, format_exc
import addons.jsonReader as jsonReader

'''Bot framework that can dynamically load and unload cogs.'''

jsonReader.GlobalJsonStorage = jsonReader.JsonStorage("./data.json")

config = yaml.safe_load(open('config.yml'))
secure = yaml.safe_load(open('secure.yml'))
admin = jsonReader.JsonInteractor("admin")
bot = commands.Bot(command_prefix=commands.when_mentioned_or(
    config['prefix']),
    description='',
    intents = discord.Intents().all())

bot.loaded_cogs = []
bot.unloaded_cogs = []

def check_if_dirs_exist():
    '''Function that creates the "cogs" directory if it doesn't exist already'''
    os.makedirs('cogs', exist_ok=True)

def load_autoload_cogs():
    '''
    Loads all .py files in the cogs subdirectory that are in the config file as "autoload_cogs" as cogs into the bot. 
    If your cogs need to reside in subfolders (ie. for config files) create a wrapper file in the cogs 
    directory to load the cog.
    '''
    bot.load_extension("jishaku")
    print("Loaded jishaku")
    for entry in os.listdir('cogs'):
        if entry.endswith('.py') and os.path.isfile('cogs/{}'.format(entry)) and entry[:-3] in config['autoload_cogs']:
            try:
                bot.load_extension("cogs.{}".format(entry[:-3]))
                bot.loaded_cogs.append(entry[:-3])
            except Exception as e:
                print(e)
            else:
                print('Succesfully loaded cog {}'.format(entry))

def get_names_of_unloaded_cogs():
    '''
    Creates an easy loadable list of cogs.
    If your cogs need to reside in subfolders (ie. for config files) create a wrapper file in the auto_cogs
    directory to load the cog.
    '''
    for entry in os.listdir('cogs'):
        if entry.endswith('.py') and os.path.isfile('cogs/{}'.format(entry)) and entry[:-3] not in bot.loaded_cogs:
            bot.unloaded_cogs.append(entry[:-3])

check_if_dirs_exist()
load_autoload_cogs()
get_names_of_unloaded_cogs()

@bot.command()
@commands.is_owner()
async def list_cogs(ctx):
    '''Lists all cogs and their status of loading.'''
    cog_list = commands.Paginator(prefix='', suffix='')
    cog_list.add_line('**✅ Succesfully loaded:**')
    for cog in bot.loaded_cogs:
        cog_list.add_line('- ' + cog)
    cog_list.add_line('**❌ Not loaded:**')
    for cog in bot.unloaded_cogs:
        cog_list.add_line('- ' + cog)
    
    for page in cog_list.pages:
        await ctx.send(page)

@bot.command()
@commands.is_owner()
async def load(ctx, cog):
    '''Try and load the selected cog.'''
    if cog not in bot.unloaded_cogs:
        await ctx.send('⚠ WARNING: Cog appears not to be found in the available cogs list. Will try loading anyway.')
    if cog in bot.loaded_cogs:
        return await ctx.send('Cog already loaded.')
    try:
        bot.load_extension('cogs.{}'.format(cog))
    except Exception as e:
        await ctx.send('**💢 Could not load cog: An exception was raised. For your convenience, the exception will be printed below:**')
        await ctx.send('```{}\n{}```'.format(type(e).__name__, e))
    else:
        bot.loaded_cogs.append(cog)
        bot.unloaded_cogs.remove(cog)
        await ctx.send('✅ Cog succesfully loaded.')

@bot.command()
@commands.is_owner()
async def reload(ctx, cog):
    """Reloads the selected cog."""
    ctx.bot.reload_extension('cogs.{}'.format(cog))
    await ctx.send('✅ Cog succesfully reloaded.')

@bot.command()
@commands.is_owner()
async def unload(ctx, cog):
    if cog not in bot.loaded_cogs:
        return await ctx.send('💢 Cog not loaded.')
    bot.unload_extension('cogs.{}'.format((cog)))
    bot.loaded_cogs.remove(cog)
    bot.unloaded_cogs.append(cog)
    await ctx.send('✅ Cog succesfully unloaded.')

@bot.event
async def on_ready():
    storage = [f'----------\nLogged in as:\n{bot.user.name}\n{bot.user.id}\n----------\nCurrently joined servers:\n']
    async for guild in bot.fetch_guilds(limit=150):
        storage.append(f"{guild.name} {guild.id}\n")
    output = "".join(storage)
    await message_in_logs(output)

async def message_in_logs(message):
    channel = bot.get_channel(int(admin['logchannel']))
    print(message)
    for chunk in [message[i:i + 1800] for i in range(0, len(message), 1800)]:
        await channel.send(f'```\n{chunk}\n```')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.MissingRequiredArgument):
        await ctx.send("Command has missing arguments!")
    elif isinstance(error, discord.ext.commands.errors.CheckFailure):
        await ctx.send("Command checks failed. Check your permissions")
    elif isinstance(error, discord.ext.commands.CommandNotFound):
        # await ctx.send("this command doesn't exist, and neither do you")
        await ctx.invoke(bot.get_command('runcommanderrquote'), name=ctx.message.content[1:].split(' ')[0])
    elif isinstance(error, discord.ext.commands.CommandOnCooldown):
        await ctx.send("Command is on cooldown. Try again in %.2f seconds" % error.retry_after)
    else:
        await ctx.send("An error occured!")
        await message_in_logs(f"An error occured in a command:\n{str(error)}")

@bot.event
async def on_error(event, *args, **kwargs):
    error = format_exc()
    await message_in_logs(f"Error in {event}:\n\n{error}")

bot.allowed_mentions = discord.AllowedMentions(everyone=False)
bot.run(secure["token"])
