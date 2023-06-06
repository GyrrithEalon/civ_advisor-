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
from flask import Flask

# =============================================================================
# Load Env
# =============================================================================
load_dotenv()
GUILD = os.getenv('DISCORD_GUILD')
GUILD_ID = os.getenv('DISCORD_GUILD_ID')

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
        
    @commands.slash_command(name='whoami', guild_ids=[GUILD_ID])
    async def whoami(self, ctx):
        """Ping tester"""
        discord_id = ctx.author.id
        print(ctx.channel.id)
        await ctx.respond("Why, you are <@" + str(discord_id) + "> of course, ID: " + str(discord_id))
        
    @commands.slash_command(name='reg-name', guild_ids=[GUILD_ID])
    async def reg_name(self, ctx, civ_name: str):
        """Add User to Player Registry"""
        discord_id = ctx.author.id
        if self.sql.get_civ_name(discord_id) is None:
            self.sql.insert_player(discord_id, civ_name)
            await ctx.respond("I have added <@" + str(discord_id) + "> as " +
                              civ_name)
        else:
            self.sql.insert_player(discord_id, civ_name)
            await ctx.respond("I've updated <@" + str(discord_id) + "> as " + 
                          civ_name)
            
    
    
# =============================================================================
# example of input typing convertion
# =============================================================================
    @commands.slash_command(name="roll", guild_ids=[GUILD_ID])    
    async def roll(self, ctx, dice_number: int, dice_sides: int):
        dice = [
            str(random.choice(range(1, dice_sides + 1)))
            for _ in range(dice_number)
            ]
        await ctx.respond(', '.join(dice))
        

    
