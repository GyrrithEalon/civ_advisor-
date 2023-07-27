# -*- coding: utf-8 -*-
"""
Created on Wed Jul 26 16:54:47 2023

@author: timsargent
"""

from datetime import datetime, timedelta
from sqlhandler import SqlConnection
from dotenv import load_dotenv
import os

class func():
    def __init__(self):
        load_dotenv()
        CIV_GAME_DB = os.getenv('CIV_GAME_DB')
        self.sql = SqlConnection(CIV_GAME_DB)
        return
    
    def game_match(self, game_name, civ_name=None, game_turn=None):    
        #preform the fuzzy match for game based on the three values civ gives us
        #If the name is unuque or does not exsist, it's a quick match
        game_id = self.sql.get_games_by_name(game_name)
        if len(game_id) == 1:
            return game_id[0][0]
        elif len(game_id) == 0:
            return None
        else:
            return False
        
    def age_formater(self, time):   
        day_unit = timedelta(days=1)
        hour_unit = timedelta(hours=1)
        minute_unit = timedelta(seconds=60)
        now = datetime.now()
        
        if isinstance(time, str):
            date_format = '%Y-%m-%d %H:%M:%S.%f'
            time = datetime.strptime(time, date_format)
            
        delta = now - time
        if delta < minute_unit:
            #under a min
            return "<1m"
        elif delta < hour_unit:
            #under an hour, show min
            return str(divmod(delta.seconds, 60)[0]) + "m"
        elif delta < day_unit:
            #under a day, show hour
            return str(divmod(delta.seconds, 3600)[0]) + "h"
        else:
            #Show Days
            return str(delta.days) + "d"
        
    def ping_gen(self, game_name, civ_name, game_turn, game_note = None):        
    # Generate ping
        discord_id = self.sql.get_discord_id(civ_name)
        if discord_id == None:
            message = "**{}** Update! Turn {} for {}".format(game_name, 
                                                                str(game_turn), 
                                                                str(civ_name))
        else:
            message = "<@{}>, Turn {} for {}".format(str(discord_id[0]), 
                                                                str(game_turn), 
                                                                str(game_name))
        if game_note is not None:
            message = "{}\nGame Note: {}".format(message,game_note[0])
            
        return message