import asyncio

from parser_vilado_site_items.parser import ViladoParser
v = ViladoParser()
asyncio.run(v.get_items_from_Vilado())