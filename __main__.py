# -*- coding: utf-8 -*-
"""
Created on Tue Apr 11 15:12:48 2023

@author: timsargent
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

#from flask import Flask, request



# =============================================================================
# The Next Set:
# =============================================================================


# Add Flask to script to recieve http posts

#https://flask.palletsprojects.com/en/2.2.x/quickstart/#a-minimal-application

# Configure apache reverse proxy




# =============================================================================
# Load Env
# =============================================================================
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CIV_GAME_DB = os.getenv('CIV_GAME_DB')

bot = commands.Bot()
bot.add_cog(CommandsHandler(bot, CIV_GAME_DB))
bot.add_cog(Webserver(bot))

bot.run(TOKEN)
