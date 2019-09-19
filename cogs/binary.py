from discord.ext import commands
import codecs
import binascii

class binary(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
	
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

def setup(bot):
	bot.add_cog(binary(bot))
