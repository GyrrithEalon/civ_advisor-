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
from sqlhandler import SqlConnection
from table2ascii import table2ascii as t2a, PresetStyle

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
    
    def __init__(self, bot, CIV_GAME_DB):
       self.bot = bot
       self.sql = SqlConnection(CIV_GAME_DB)

       
    @commands.Cog.listener()
    async def on_ready(self):
        #for multi Server access, will need to sort through connecte servers
        self.guild = self.bot.guilds[0]
        print(
            f'{self.bot.user.name} is connected to the following guild:\n'
            f'{self.guild.name}(id: {self.guild.id})'
        )
    
    def game_match(self, game_name):    
        #preform the fuzzy match for game based on the three values civ gives us
        #If the name is unuque or does not exsist, it's a quick match
        game_id = self.sql.get_games_by_name(game_name)
        if len(game_id) == 1:
            return game_id[0][0]
        elif len(game_id) == 0:
            return None
        else:
            return False
        

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
        
    # @commands.slash_command(name='whoami', guild_ids=[GUILD_ID])
    # async def whoami(self, ctx):
    #     """Ping tester"""
    #     discord_id = ctx.author.id
    #     print(ctx.channel.id)
    #     await ctx.respond("Why, you are <@" + str(discord_id) + "> of course.")
        
    @commands.slash_command(name='current_games', guild_ids=[GUILD_ID])
    async def current_games(self, ctx):
        """Get current_games"""
        table = self.sql.remove_column(self.sql.get_all_games(), 0)
        table = self.sql.char_limit(table, 0, 15)
        table = self.sql.char_limit(table, 1, 10)
        text =  t2a(header=["Name", "Player", "Turn"],
                    body=table,
                    column_widths=[17, 12, 6])
        await ctx.respond(f"```\n{text}\n```")
        
    @commands.slash_command(name='purge_games_db', guild_ids=[GUILD_ID])
    async def purge_table(self, ctx):
        """Purge the games table"""
        discord_id = ctx.author.id
        if str(discord_id) != str(EALON_ID):
            await ctx.respond("Only <@" + str(EALON_ID) + "> can run that commnand.")
        else:
            self.sql.truncate_table("games")
            await ctx.respond("Games Table Truncated")
            
    @commands.slash_command(name='era_score', guild_ids=[GUILD_ID])
    async def era_score(self, ctx):
        """Link to ear score table"""
        await ctx.respond("[Ways to get era Score](https://docs.google.com/spreadsheets/d/1bcghYw_lk2vbBHdQV4T73C-gUWV5bq_McQjMGeoWN38/edit#gid=1645377719)")
        
        
    @commands.slash_command(name='fresh_water', guild_ids=[GUILD_ID])
    async def fresh_water(self, ctx):
        """Fresh water, AM I RIGHT"""
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
        game_id = self.game_match(game_name)
        
        if game_id is None:
            table = self.sql.get_all_games()
            table = self.sql.remove_column(table, 3)
            table = self.sql.remove_column(table, 2)
            table = self.sql.remove_column(table, 0)
            text =  t2a(header=["Game Names"],
                        body=table)
            message = f"I could not find that game name, pick one of these names\n\n```\n{text}\n```"
            
        else:
            old_note = self.sql.get_game_note(game_id)
            if old_note is None:
                self.sql.insert_game_note(game_id, game_note)
                message = f"I added your note to {game_name}"
                
                
            elif delete_note == "Yes" and overwrite_flag == "Yes":
                self.sql.remove_game_note(game_id)
                message = f"I removed the note from {game_name}"
                
            elif overwrite_flag == "Yes":
                old_note = self.sql.get_game_note(game_id)
                old_note = old_note[0]
                self.sql.update_game_note(game_id, game_note)
                message = f"The old note ({old_note}) has been replaced with ({game_note})"
            else:
                message = "If you want to make changes, try again and enter Yes in the overwrite_flag field"
                
        await ctx.respond(message) 

    @commands.slash_command(name='get_game_notes', guild_ids=[GUILD_ID])
    async def get_game_notes(self, ctx):
        """Update the notes info for an active game. """
        
        #find the game ID
        notes_table = self.sql.get_all_game_notes()
        cleaned_table = []
        for row in notes_table:
            game_record = self.sql.get_game(row[0])
            name = list(game_record).pop(1)
            cleaned_table.append([name,row[1]])
        
    
        text =  t2a(header=["Game Names", "Note"],
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
        if self.sql.get_civ_name(discord_id) is None:
            self.sql.insert_player(discord_id, civ_name)
            await ctx.respond("I have added <@" + str(discord_id) + "> as " +
                              civ_name)
        else:
            self.sql.update_player(discord_id, civ_name)
            await ctx.respond("I've updated <@" + str(discord_id) + "> as " + 
                          civ_name)
            
    @commands.slash_command(name='remove-me', guild_ids=[GUILD_ID])
    async def remove_name(self, ctx):
        """Remove User to Player Registry"""
        discord_id = ctx.author.id
        if self.sql.get_civ_name(discord_id) is None:
            await ctx.respond("You are not in the player database.")
        else:
            if self.sql.remove_player(discord_id):
                await ctx.respond("I've removed <@" + str(discord_id) + "> from the database")
            else:
                await ctx.respond("Error removing player.")
            
    # @commands.slash_command(name='get-players', guild_ids=[GUILD_ID])
    # async def get_players(self, ctx):
    #     result = self.sql.get_all_players()
    #     await ctx.respond("here is the player table: " + str(result))
    
    
        

    
