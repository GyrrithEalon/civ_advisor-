import os
from discord.ext import commands
from dotenv import load_dotenv
from bot import CommandsHandler
from webserver import Webserver
from gamedb import GameDB
from playerdb import PlayerDB

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
