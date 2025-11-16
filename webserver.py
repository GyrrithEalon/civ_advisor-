from aiohttp import web
import asyncio
from discord.ext import commands, tasks
import os
from gamedb import GameDB
from playerdb import PlayerDB




class ValidationError(Exception):
    pass

def validate_game_update(data): 
    if not isinstance(data, dict):
        raise ValidationError("Request body must be a JSON object")
    if 'value1' not in data:
        raise ValidationError("value1 is required")
    if 'value2' not in data:
        raise ValidationError("value2 is required")
    if 'value3' not in data:
        raise ValidationError("value3 is required")
    if not isinstance(data['value1'], str):
        raise ValidationError("value1 must be a string")
    if not isinstance(data['value2'], str):
        raise ValidationError("value2 must be a string")
    if not isinstance(data['value3'], int):
        if isinstance(data['value3'], str):
            try:
                data['value3'] = int(data['value3'])
            except ValueError:
                raise ValidationError("value3 must be an integer")
        else:
            raise ValidationError("value3 must be an integer")
    if len(data['value1']) > 100 or len(data['value1']) < 1:
        raise ValidationError("value1 must be less than 100 characters")
    if len(data['value2']) > 100 or len(data['value2']) < 1:
        raise ValidationError("value2 must be less than 100 characters")
    if data['value3'] > 10000 or data['value3'] < 0:
        raise ValidationError("value3 must be positive and less than 10000")
    return data

app = web.Application(client_max_size=1024*1024)
routes = web.RouteTableDef()
class Webserver(commands.Cog):
    def __init__(self, bot, Games:GameDB, Players:PlayerDB):
        self.bot = bot       
        self.games = Games
        self.players = Players
        self.expression_lock = asyncio.Lock()
        self.webserver_port = os.environ.get('PORT', 5000)
        self.webserver_address = os.environ.get('IP_ADDRESS', '127.0.0.1')

        # =============================================================================
        # Web server Processing
        # =============================================================================
        # #Browser site the shows the games and players datafiles, disabled for now
        # @routes.get('/')
        # async def welcome(request):
        #     webtext = str(self.games) + "\n\n" + str(self.players)
        #     try:
        #         return web.Response(text=webtext)
        #     except Exception as error:
        #         # handle the exception
        #         print("An exception occurred:", type(error).__name__)
        #         return web.Response(text="An exception occurred:" + type(error).__name__)

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
                    return web.Response(status=400, text="Bad Request")
                
                try:
                    validate_game_update(data)
                except ValidationError as e:
                    return web.Response(status=400, text=str(e))

                #only allow printable characters
                incoming_game_name = ''.join(char for char in data['value1'] if char.isprintable())
                incoming_player_name = ''.join(char for char in data['value2'] if char.isprintable())
                incoming_game_turn = int(data['value3'])

                if incoming_game_name == "GENERATEPING":
                    games_to_ping = self.games.get_stale_games()

                    if len(games_to_ping) == 0:
                        return web.Response(status=200)
                    
                    async with self.expression_lock:
                        message = ""
                        try:
                            with open("expression.txt", "r") as file:
                                lines = file.readlines()

                            # Read the first line and increment it
                            line_number = int(lines[0].strip()) + 1

                            # Read the line at the new index
                            if line_number >= len(lines):
                                line_number = 1

                            # Update the first line
                            lines[0] = str(line_number) + "\n"
                            # Write the new number back to the file
                            with open("expression.txt", "w") as file:
                                file.writelines(lines)

                            message = lines[line_number] + "\n\n"
                        except:
                            pass

                    for game in games_to_ping:
                        message = message + self.games.ping_gen(game.name,self.players) + "\n"
                    await self.channel.send(message)
                    return web.Response(status=200)

                # Check for new game
                check_game = self.games.get_game(incoming_game_name)
                if check_game is None:
                    self.games.add_game(incoming_game_name, incoming_player_name, incoming_game_turn)
                    message = self.games.ping_gen(incoming_game_name, self.players)
                    await self.channel.send(message)
                    return web.Response(status=200)
                if check_game.active_player == incoming_player_name and int(check_game.turn_number) == incoming_game_turn:
                    return web.Response(status=200)
                else:
                    self.games.update_game(incoming_game_name, incoming_player_name, incoming_game_turn)
                    message = self.games.ping_gen(incoming_game_name, self.players)
                    await self.channel.send(message)
                    return web.Response(status=200)


        # =============================================================================
        # Web Server Funcion
        # =============================================================================
        app.add_routes(routes)
        self.web_server.start()



    @commands.Cog.listener()
    async def on_ready(self):
        #for multi Server access, will need to sort through connecte servers
        self.channel = self.bot.get_channel(int(os.getenv('DISCORD_CHANNEL')))
        print(
            f'{self.channel.name}(id: {self.channel.id})'
        )

    @tasks.loop()
    async def web_server(self):
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host=self.webserver_address, port=int(self.webserver_port))
        await site.start()

    @web_server.before_loop
    async def web_server_before_loop(self):
        await self.bot.wait_until_ready()
        
