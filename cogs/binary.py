from discord.ext import commands
import codecs
import binascii
from discord.utils import get
from discord import Colour


def tryIntParse(string: str):
    try:
        ret = int(string, 16)
        return ret
    except:
        return None

def getter(iterables, name):
    data = get(iterables, name=name)
    return data

class binary(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.reactemoji = '\N{THUMBS UP SIGN}'
	
	@commands.command()
	async def decode_hex(self, ctx, *, hex):
		'''[Hex] Decodes hex to text'''
		hexnospace = hex.replace(" ", "")
		try:
			output = str(codecs.decode(hexnospace, "hex"))[2:-1]
		except:
			await ctx.send("Something went wrong, check your input")
			return

		await ctx.send(f"```\nText: {output}\n```")

	@commands.command()
	async def encode_hex(self, ctx, *, text):
		'''[Text] Encodes Hex to Text'''
		try:
			output = ''.join(hex(ord(c))[2:] for c in text)
		except:
			await ctx.send("Something went wrong, check your input")
			return
		
		await ctx.send(f"```\nHex: {output}\n```")
		await ctx.message.delete()


	@commands.command(aliases=["setcolour", "fuckyouraptor"])
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def setcolor(self, ctx, color):

		if (color.lower().startswith('0x')):
			color = color[2:]

		if (len(color) != 6):
			await ctx.send("A hex color code consists of 6 characters")
			return

		if (color == "000000"):
			await ctx.send("Note this is discord's default color")

		r = tryIntParse(color[0:2])
		g = tryIntParse(color[2:4])
		b = tryIntParse(color[4:6])

		if (r is None or g is None or b is None):
			await ctx.send("Invalid color provided")
			return

		colour = Colour.from_rgb(r, g, b)

		posRole = getter(ctx.guild.roles, "-- Colors --")
		if (posRole is None):
			await ctx.send("I need a '-- Colors --' role to figure out where to place the roles")
			return

		userRole = getter(ctx.guild.roles, str(ctx.author.id))
		if (userRole is None):
			userRole = await ctx.guild.create_role(name=str(ctx.author.id), colour=colour)
		elif (userRole.colour == colour):
			await ctx.send("You already have this color!")
			return

		posRole = getter(ctx.guild.roles, "-- Colors --")

		onUserRole = getter(ctx.author.roles, str(ctx.author.id))
		if (onUserRole is None):
			await ctx.author.add_roles(userRole)

		await userRole.edit(colour=colour, position=posRole.position - 1)
		await ctx.message.add_reaction(self.reactemoji)


def setup(bot):
	bot.add_cog(binary(bot))
