# -*- coding: utf-8 -*-
"""
Created on Sun Jun  4 21:20:56 2023

@author: timsargent
"""
from aiohttp import web
from discord.ext import commands, tasks
import os
from datetime import datetime
from sqlhandler import SqlConnection
from table2ascii import table2ascii as t2a, PresetStyle

app = web.Application()
routes = web.RouteTableDef()




class Webserver(commands.Cog):
    def __init__(self, bot, CIV_GAME_DB):
        self.bot = bot       
        self.sql = SqlConnection(CIV_GAME_DB)
        self.web_server.start()

    @commands.Cog.listener()
    async def on_ready(self):
        #for multi Server access, will need to sort through connecte servers
        self.channel = self.bot.get_channel(int(os.getenv('DISCORD_CHANNEL')))
        print(
            f'{self.channel.name}(id: {self.channel.id})'
        )
# =============================================================================
#         Game Matching processing
# =============================================================================

        
        def game_match(self, game_name, civ_name, turn_number):    
            #preform the fuzzy match for game based on the three values civ gives us
            #If the name is unuque or does not exsist, it's a quick match
            game_id = self.sql.get_games_by_name(game_name)
            if len(game_id) == 1:
                return game_id[0][0]
            elif len(game_id) == 0:
                return None
            else:
                return False
            
        def ping_gen(self, game_name, civ_name, game_turn):        
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
            return message

            
                
        # def make_game_table(self, game_ids):
        #     for i in range(0,len(game_id)):
        #         game_values.append(self.sql.get_game(game_id[i][0]))

# =============================================================================
# Web server Processing
# =============================================================================
        #Browser site        
        @routes.get('/')
        async def welcome(request):
            table = self.sql.remove_column(self.sql.get_all_games(), 0)
            table = self.sql.char_limit(table, 0, 15)
            table = self.sql.char_limit(table, 1, 10)
            return web.Response(text=t2a(
                                header=["Name", "Player", "Turn"],
                                body=table,
                                column_widths=[17, 12, 6]
                                ))



# =============================================================================
# Endpoint Process
# =============================================================================

        #API Endpoint
        @routes.post(os.getenv('END_POINT_URL'))
        async def civ_update(request):
            data = await request.json()
            game_name = data['value1']
            civ_name = data['value2']
            game_turn = data['value3']

            #log json for testing
            now = datetime.now()
            with open("data/" + now.strftime("%Y-%m-%d_%H-%M-%S") + '.json', 'w') as file:
                file.write(str(data))
                
            # Check for redundant
            checked_id = game_match(self, game_name, civ_name, game_turn)
            if checked_id == None:
                self.sql.insert_game(game_name, civ_name, game_turn)
                message = ping_gen(self, game_name, civ_name, game_turn)
                await self.channel.send(message)
            elif checked_id == False:
                return 200
            else:
                #Check for redundace ping
                game_data = self.sql.get_game(checked_id)
                if game_data == (checked_id ,game_name, civ_name, int(game_turn)):
                    return 200
                else:
                    self.sql.update_game(checked_id, game_name, civ_name, game_turn)
                    message = ping_gen(self, game_name, civ_name, game_turn)
                    await self.channel.send(message)
                    return 200





# =============================================================================
# Web Server Funcion
# =============================================================================
        self.webserver_port = os.environ.get('PORT', 5000)
        self.webserver_address = os.environ.get('IP_ADDRESS', '127.0.0.1')
        app.add_routes(routes)

    @tasks.loop()
    async def web_server(self):
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host=self.webserver_address, port=self.webserver_port)
        await site.start()

    @web_server.before_loop
    async def web_server_before_loop(self):
        await self.bot.wait_until_ready()
        
        
        
        
