### Start Variables ###
import os
import discord
from discord import app_commands
import aiohttp
from discord.ext import tasks
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
SERVER_ID = os.getenv('BATTLEMETRICS_SERVER_ID')
SERVER_NAME = os.getenv('SERVER_NAME')

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
### End Variables ###

### Start API ###
async def get_server_info():
    url = f'https://api.battlemetrics.com/servers/{SERVER_ID}'
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return {
                    'status': 'online',
                    'players': data['data']['attributes']['players'],
                    'maxPlayers': data['data']['attributes']['maxPlayers']
                }
            elif response.status == 404:
                return {'status': 'not_found'}
    return {'status': 'offline'}
### End API ###

### Start Update ###
@tasks.loop(minutes=1)
async def update_status():
    server_info = await get_server_info()
    status = server_info['status']

    if status == 'online': # Server Online
        players = server_info['players']
        max_players = server_info['maxPlayers']
        await client.change_presence(
            status=discord.Status.online,
            activity=discord.Activity(
                type=discord.ActivityType.watching, 
                name=f"Players: ({players}/{max_players})!"
            )
        )
    elif status == 'not_found': # Error/Not Found
        await client.change_presence(
            status=discord.Status.idle,
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"Status - Server Not Found"
            )
        )
    else:  # Server Offline
        await client.change_presence(
            status=discord.Status.do_not_disturb,
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"Status - Offline"
            )
        )
### End Update ###

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    await tree.sync()
    update_status.start()

client.run(DISCORD_TOKEN)