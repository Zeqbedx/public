Hello! Thanks for downloading and using my bot, if you would like to stay up to date or purchase any of my 
services please join my discord at: https://discord.gg/Zd4G2a42Mu

Thanks, Zeqbed!

# Discord Bot Template

This is a template for a Discord bot using discord.py. It includes a basic structure with cog support and slash command integration.

## Features

- Utilizes discord.py library
- Implements cog system for modular command organization
- Supports slash commands
- Uses environment variables for secure token storage

## Setup

1. Clone this repository or download the source code.
2. Install the required dependencies:
pip install discord.py python-dotenv
3. Create a `.env` file in the root directory and add your Discord bot token:
DISCORD_TOKEN=your_bot_token_here
4. Customize the bot by adding your own cogs and commands in the `cogs` directory.

## Structure

- `bot.py`: The main bot file containing the core setup and initialization code.
- `cogs/`: Directory to store cog files for modular command organization.
- `.env`: File to securely store your Discord bot token.


## Usage

Add your cogs to the cogs directory.

Run the bot using:
python bot.py

### Adding Commands
To add new commands, create new cog files in the cogs directory or modify existing ones.
Use the @commands.command() decorator for traditional commands or @app_commands.command() 
for slash commands.