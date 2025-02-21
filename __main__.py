# -*- coding: utf-8 -*-
"""
Created on Tue Apr 11 15:12:48 2023

@author: Ealon
"""
#For Spyder
import nest_asyncio
nest_asyncio.apply()


#Start Code
import os
from discord.ext import commands
from dotenv import load_dotenv
from bot import CommandsHandler
from webserver import Webserver
from gamedb import GameDB
from playerdb import PlayerDB



#insalls for miniconda env
#PYTHON 3.10

#pip install py-cord
#pip install nest_asyncio
#pip install python-dotenv
#pip install table2ascii



# =============================================================================
# Load Env
# =============================================================================
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CIV_GAME_JSON = os.getenv('CIV_GAME_JSON')
CIV_PLAYER_JSON = os.getenv('CIV_PLAYER_JSON')

# =============================================================================
# Start Bot
# =============================================================================
games = GameDB(CIV_GAME_JSON)
players = PlayerDB(CIV_PLAYER_JSON)
bot = commands.Bot()
bot.add_cog(CommandsHandler(bot, games, players))
bot.add_cog(Webserver(bot, games, players))

bot.run(TOKEN)
