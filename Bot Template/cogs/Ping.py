import discord
from discord.ext import commands
from discord import app_commands

class PingCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Returns the bot's latency")
    async def ping(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Pong!",
            description=f"Latency: **{round(self.bot.latency * 1000)}ms**",
            color=0x5f6d45
        )
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(PingCommand(bot))