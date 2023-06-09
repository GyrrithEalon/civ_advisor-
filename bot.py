# -*- coding: utf-8 -*-
"""
Created on Mon Apr 10 14:10:43 2023

@author: timsargent
"""

import os
from discord.ext import commands
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
    async def getgames(self, ctx):
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
    
    
        

    
