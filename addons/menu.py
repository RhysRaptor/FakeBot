import discord
import asyncio
from discord.ext import menus

class MenuList(menus.ListPageSource):
    def __init__(self, name, data, embedcolor, per_page):
        super().__init__(data, per_page=per_page)
        self.name = name
        self.embedcolor = embedcolor

    async def format_page(self, menu, entries):
        offset = menu.current_page * self.per_page
        embed = discord.Embed(title=self.name, description='\n'.join(f"{i + 1}: {v}" for i,v in enumerate(entries, start=offset)), color=self.embedcolor)
        embed.set_footer(text=f"page {menu.current_page + 1} / {self.get_max_pages()}")
        return embed

def MakeMenu(name, data, embedcolor, perPage):
    return menus.MenuPages(source=MenuList(name, data, embedcolor, perPage), clear_reactions_after=True)