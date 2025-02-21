# -*- coding: utf-8 -*-
"""
Created on Mon Apr 10 14:10:43 2023

@author: timsargent
"""

import os
from discord.ext import commands
from discord.commands import Option
from dotenv import load_dotenv
import random
from table2ascii import table2ascii as t2a, PresetStyle
from gamedb import GameDB
from playerdb import PlayerDB

# =============================================================================
# Load Env
# =============================================================================
load_dotenv()
GUILD = os.getenv('DISCORD_GUILD')
GUILD_ID = os.getenv('DISCORD_GUILD_ID')
EALON_ID = os.getenv('EALON_ID')

# =============================================================================
# Make a shell bot class
# =============================================================================

class CommandsHandler(commands.Cog):
    
    def __init__(self, bot, Games:GameDB, Players:PlayerDB):
        self.bot = bot
        self.games = Games
        self.players = Players

       
    @commands.Cog.listener()
    async def on_ready(self):
        #for multi Server access, will need to sort through connecte servers
        self.guild = self.bot.guilds[0]
        print(
            f'{self.bot.user.name} is connected to the following guild:\n'
            f'{self.guild.name}(id: {self.guild.id})'
        )
        

# =============================================================================
# simple text reply
# =============================================================================
    @commands.slash_command(name='build_order', guild_ids=[GUILD_ID])
    async def build_order(self, ctx):
        """Need Early Game Help?"""
        great_people = ['Alexander the Great', 
                        'Genghis Khan',
                        'Napoleon Bonaparte',
                        'Sun Tzu']
        response = '\"scout, scout, slinger, settler\", ' + random.choice(great_people)
        await ctx.respond(response)
        
    @commands.slash_command(name='current_games', guild_ids=[GUILD_ID])
    async def current_games(self, ctx):
        """Get current_games"""
        text = self.games.make_table(column_widths=[17, 12, 6, 5])
        await ctx.respond(f"```\n{text}\n```")
            
    @commands.slash_command(name='era_score', guild_ids=[GUILD_ID])
    async def era_score(self, ctx):
        """Link to era score table"""
        await ctx.respond("[Ways to get era Score](https://docs.google.com/spreadsheets/d/1bcghYw_lk2vbBHdQV4T73C-gUWV5bq_McQjMGeoWN38/edit#gid=1645377719)")
        
        
    @commands.slash_command(name='fresh_water', guild_ids=[GUILD_ID])
    async def fresh_water(self, ctx):
        """It's Over rated"""
        await ctx.respond("Access to water is overrated")    

    @commands.slash_command(name='game_note', guild_ids=[GUILD_ID])
    async def set_game_note(self, ctx, game_name: str , game_note: str , 
                            overwrite_flag: Option(
                                str, 
                                description="Enter Yes to allow overwrite",
                                required=False,
                                default=""),
                            delete_note: Option(
                                str, 
                                description="Enter Yes to remove note",
                                required=False,
                                default="")):
        """Update the notes info for an active game"""
        
        #find the game ID
        game_to_update = self.games.get_game(game_name)
        
        if game_to_update is None:
            table = []
            names = self.games.games.keys()
            for name in names:
                table.append([name])
            text =  t2a(header=["Game Names"], body=table)
            message = f"I could not find that name from my list, pick one of these names.\n```\n{text}\n```"
            
        else:
            if len(game_to_update.game_note) == 0 or overwrite_flag == "Yes":
                self.games.update_game(game_to_update.name, game_note=game_note)
                message = f"I have added your note to **{game_name}**"
                
            elif delete_note == "Yes" and overwrite_flag == "Yes":
                self.games.update_game(game_to_update.name, game_note="")
                message = f"I have removed the note from **{game_name}**"
                
            else:
                message = "If you want to make changes, I need you to enter **Yes** overwrite_flag field"
                
        await ctx.respond(message) 

    @commands.slash_command(name='get_game_notes', guild_ids=[GUILD_ID])
    async def get_game_notes(self, ctx):
        """Update the notes info for an active game. """
        #find the game ID
        games_display = self.games.get_games_with_notes()
        cleaned_table = []
        for game in games_display:
            cleaned_table.append([game.name, game.game_note])
        text =  t2a(header=["Game Names","Note"],
                    body=cleaned_table)
        message = f"```\n{text}\n```"        
        await ctx.respond(message) 
                
                    
  
# =============================================================================
# Name Regestry Commands
# =============================================================================
        
    @commands.slash_command(name='reg-name', guild_ids=[GUILD_ID])
    async def reg_name(self, ctx, civ_name: str):
        """Add or Update User to Player Registry"""
        discord_id = ctx.author.id
        if self.players.get_name_by_discord_id(discord_id) is None:
            self.players.add_player(discord_id, civ_name)
            await ctx.respond("I have added <@" + str(discord_id) + "> as " +
                              civ_name)
        else:
            self.players.update_player(discord_id, civ_name)
            await ctx.respond("I've updated <@" + str(discord_id) + "> as " + 
                          civ_name)
            
    @commands.slash_command(name='remove-me', guild_ids=[GUILD_ID])
    async def remove_name(self, ctx):
        """Remove User to Player Registry"""
        discord_id = ctx.author.id
        if discord_id in self.players:
            self.players.remove_player(discord_id)
            await ctx.respond("I've removed <@" + str(discord_id) + "> from the database")
        else:
            await ctx.respond("You are not in the player database.")
    