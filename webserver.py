# -*- coding: utf-8 -*-
"""
Created on Sun Jun  4 21:20:56 2023

@author: timsargent
"""
from aiohttp import web
from discord.ext import commands, tasks
import os
from table2ascii import table2ascii as t2a
import datetime
from gamedb import GameDB
from playerdb import PlayerDB


app = web.Application()
routes = web.RouteTableDef()


class Webserver(commands.Cog):
    def __init__(self, bot, Games:GameDB, Players:PlayerDB):
        self.bot = bot       
        self.games = Games
        self.players = Players
        self.web_server.start()

    @commands.Cog.listener()
    async def on_ready(self):
        #for multi Server access, will need to sort through connecte servers
        self.channel = self.bot.get_channel(int(os.getenv('DISCORD_CHANNEL')))
        print(
            f'{self.channel.name}(id: {self.channel.id})'
        )
        

# =============================================================================
# Web server Processing
# =============================================================================
        #Browser site        
        @routes.get('/')
        async def welcome(request):
            webtext = str(self.games) + "\n\n" + str(self.players)
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
            

            incoming_game_name = data['value1']
            incoming_player_name = data['value2']
            incoming_game_turn = data['value3']
    
            if incoming_game_name == "GENERATEPING":
                games_to_ping = self.games.get_stale_games()

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
                    message = message + self.games.ping_gen(game.name,self.players) + "\n"
                await self.channel.send(message)
                return 200

            # Check for new game
            check_game = self.games.get_game(incoming_game_name)
            if check_game is None:
                self.games.add_game(incoming_game_name, incoming_player_name, incoming_game_turn)
                message = self.games.ping_gen(incoming_game_name, self.players)
                await self.channel.send(message)
                return 200
            if check_game.active_player == incoming_player_name and check_game.turn_number == incoming_game_turn:
                return 200
            else:
                self.games.update_game(incoming_game_name, incoming_player_name, incoming_game_turn)
                message = self.games.ping_gen(incoming_game_name, self.players)
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
        
