### Start Variables ###
import os
import discord
from discord import app_commands
import aiohttp
from discord.ext import tasks
import logging
from dotenv import load_dotenv
import json
import traceback

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
SERVER_ID = os.getenv('BATTLEMETRICS_SERVER_ID')
SERVER_NAME = os.getenv('SERVER_NAME')
UPDATE_TIME = int(os.getenv('UPDATE_TIME', 5))

intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)
### End Variables ###


### Start API ###
async def get_server_info():
    url = f'https://api.battlemetrics.com/servers/{SERVER_ID}'
    
    logging.info(f"Attempting to fetch server info from: {url}")
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                logging.info(f"Received response with status code: {response.status}")
                
                response_text = await response.text()
                logging.debug(f"Raw response: {response_text}")

                try:
                    response_json = json.loads(response_text)
                    logging.debug(f"Parsed JSON response: {json.dumps(response_json, indent=2)}")
                except json.JSONDecodeError:
                    logging.error(f"Failed to parse response as JSON. Raw text: {response_text}")
                
                if response.status == 200:
                    data = response_json
                    server_status = data['data']['attributes']['status']
                    
                    logging.info(f"Server status: {server_status}")
                    
                    if server_status == 'online':
                        result = {
                            'status': 'online',
                            'players': data['data']['attributes']['players'],
                            'maxPlayers': data['data']['attributes']['maxPlayers'],
                            'name': data['data']['attributes']['name']
                        }
                    elif server_status in ['offline', 'dead']:
                        result = {
                            'status': 'offline',
                            'name': data['data']['attributes']['name']
                        }
                    else:
                        logging.warning(f"Unknown server status: {server_status}")
                        result = {'status': 'unknown'}
                    
                    logging.info(f"Returning result: {result}")
                    return result

                elif response.status == 404:
                    logging.warning(f"Received 404 error: {response_json}")
                    error_title = response_json['errors'][0]['title']
                    if error_title == "Unknown Server":
                        logging.info("Server not found")
                        return {'status': 'not_found'}
                    else:
                        logging.error(f"Unexpected 404 error: {error_title}")
                        return {'status': 'error'}
                else:
                    logging.error(f"Unexpected response status: {response.status}. Response text: {response_text}")
                    return {'status': 'error'}
        except aiohttp.ClientError as e:
            logging.error(f"Aiohttp ClientError occurred: {str(e)}")
            logging.debug(f"ClientError traceback: {traceback.format_exc()}")
            return {'status': 'error'}
        except Exception as e:
            logging.error(f"Unexpected error occurred: {str(e)}")
            logging.debug(f"Exception traceback: {traceback.format_exc()}")
            return {'status': 'error'}
    
    logging.error("Reached end of function without returning - this should not happen")
    return {'status': 'error'}
### End API ###

### Start Update ###
@tasks.loop(minutes=UPDATE_TIME)
async def update_status():
    server_info = await get_server_info()
    logging.info(f"Received server info: {server_info}")
    status = server_info['status']

    if status == 'online':
        players = server_info['players']
        max_players = server_info['maxPlayers']
        server_name = server_info['name']
        await client.change_presence(
            status=discord.Status.online,
            activity=discord.Activity(
                type=discord.ActivityType.watching, 
                name=f"{server_name} {players}/{max_players}!"
            )
        )
    elif status == 'offline':
        server_name = server_info.get('name', 'Unknown Server')
        await client.change_presence(
            status=discord.Status.do_not_disturb,
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name=f"{server_name} - Offline"
            )
        )
    elif status == 'not_found':
        await client.change_presence(
            status=discord.Status.idle,
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="Server Not Found"
            )
        )
    elif status == 'error':
        await client.change_presence(
            status=discord.Status.idle,
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="Error Fetching Server Status"
            )
        )
    else:
        await client.change_presence(
            status=discord.Status.idle,
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="Unknown Server Status"
            )
        )
    print(f"Current status: {status}")
### End Update ###

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    await tree.sync()
    update_status.start()

client.run(DISCORD_TOKEN)