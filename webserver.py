# -*- coding: utf-8 -*-
"""
Created on Sun Jun  4 21:20:56 2023

@author: timsargent
"""
from aiohttp import web
from discord.ext import commands, tasks
import discord
import os
from datetime import datetime

app = web.Application()
routes = web.RouteTableDef()


class Webserver(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.web_server.start()

        @routes.get('/')
        async def welcome(request):
            return web.Response(text="Hello, world")

        @routes.post(os.getenv('END_POINT_URL'))
        async def testwebhook(request):
            data = await request.json()
            #user = self.bot.get_user(data['user']) or await self.bot.fetch_user(data['user'])
            DIS_CHANNEL = os.getenv('DISCORD_CHANNEL')
            channel = self.bot.get_channel(int(DIS_CHANNEL))
            #discord_id = user.id
            
            
            now = datetime.now()            
            message = "Data From Civ At: " + now.strftime("%Y-%m-%d %H:%M:%S")
            
            with open("data/" + now.strftime("%Y-%m-%d_%H-%M-%S") + '.json', 'w') as file:
                file.write(str(data))
            
            await channel.send(message)
            return 200

        self.webserver_port = os.environ.get('PORT', 5000)
        app.add_routes(routes)

    @tasks.loop()
    async def web_server(self):
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host='0.0.0.0', port=self.webserver_port)
        await site.start()

    @web_server.before_loop
    async def web_server_before_loop(self):
        await self.bot.wait_until_ready()
        
        
        
        
