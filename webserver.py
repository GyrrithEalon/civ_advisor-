# -*- coding: utf-8 -*-
"""
Created on Sun Jun  4 21:20:56 2023

@author: timsargent
"""
from aiohttp import web
from discord.ext import commands, tasks
import os
from sqlhandler import SqlConnection
import json
from table2ascii import table2ascii as t2a, PresetStyle
import datetime
from fuc import func



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
            for row in table:
                row[3] = func.age_formater(self, row[3])
                
            
            players = self.sql.remove_column(self.sql.get_all_players(), 0)
            
            webtext = t2a(header=["Name", "Player", "Turn", "Age"], body=table) + \
                        "\n\n" + t2a(header=["Civ_Name"], body=players)
            
            
            try:
                return web.Response(text=webtext)
            except Exception as error:
                # handle the exception
                print("An exception occurred:", type(error).__name__)
                return web.Response(text="An exception occurred:" + type(error).__name__)



# =============================================================================
# Endpoint Process
# =============================================================================

        #API Endpoint
        @routes.post(os.getenv('END_POINT_URL'))
        async def civ_update(request):
            try:
                data = await request.json()
            except Exception as error:
                # handle the exception
                print("An exception occurred:", type(error).__name__)
                # Write the request data to an error file
                with open('error.log', 'a') as error_file:
                    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    error_file.write(f"[{timestamp}] An exception occurred: {type(error).__name__}\n")
                    error_file.write(f"[{timestamp}] Request data: {await request.text()}\n")
                    return web.Response(status=400, text="Bad Request")
            

            now = datetime.datetime.now()
            game_name = data['value1']
            civ_name = data['value2']
            game_turn = data['value3']
    
            if game_name == "GENERATEPING":
                games = self.sql.get_all_games()
                games_to_ping = []
                for game in games:
                    if func.is_game_stale(self, game[4]):
                        games_to_ping.append(game)

                if len(games_to_ping) == 0:
                    return 200
                
                # Open the file in read mode
                with open("expression.txt", "r") as file:
                    lines = file.readlines()

                # Read the first line and increment it
                line_number = int(lines[0].strip()) + 1

                # Read the line at the new index
                if line_number > len(lines):
                    line_number = 1

                # Update the first line
                lines[0] = str(line_number) + "\n"
                # Write the new number back to the file
                with open("expression.txt", "w") as file:
                    file.writelines(lines)

                message = lines[line_number] + "\n\n"

                for game in games_to_ping:
                    message = message + func.ping_gen(self, game[1], game[2], game[3]) + "\n"
                await self.channel.send(message)
                return 200



                
            # Check for redundant
            checked_id = func.game_match(self, game_name, civ_name, game_turn)
            if checked_id == None:
                self.sql.insert_game(game_name, civ_name, game_turn, now)
                message = func.ping_gen(self, game_name, civ_name, game_turn)
                await self.channel.send(message)
            elif checked_id == False:
                return 200
            else:
                #Check for redundace ping
                game_data = self.sql.get_game(checked_id)
                game_data = list(game_data)
                game_data[4] = None
                game_note = self.sql.get_game_note(checked_id)
                if game_data == [checked_id, game_name, civ_name, int(game_turn), None]:
                    return 200
                else:
                    self.sql.update_game(checked_id, game_name, civ_name, game_turn, now)
                    message = func.ping_gen(self, game_name, civ_name, game_turn, game_note)
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
        
        
        
        
