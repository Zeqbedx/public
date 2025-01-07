import discord
from discord.ext import commands
import asyncio
from datetime import datetime, timezone
import typing

class ModMailTimer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.plugin_db.get_partition(self)
        self.ticket_timers = {}
        self.checking = asyncio.Lock()
        self.bot.loop.create_task(self.check_timers())

    async def check_timers(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed():
            async with self.checking:
                try:
                    current_time = datetime.now(timezone.utc)
                    for channel_id, timer_data in list(self.ticket_timers.items()):
                        channel = self.bot.get_channel(channel_id)
                        if not channel:
                            del self.ticket_timers[channel_id]
                            continue

                        elapsed_minutes = (current_time - timer_data['last_user_message']).total_seconds() / 60
                        new_emoji = self.get_status_emoji(elapsed_minutes)
                        
                        if new_emoji != timer_data['current_emoji']:
                            try:
                                thread = await self.bot.threads.find(channel=channel)
                                if thread and thread.channel:
                                    await thread.channel.edit(name=f"{new_emoji}︱{thread.channel.name.split('︱')[1]}")
                                    self.ticket_timers[channel_id]['current_emoji'] = new_emoji
                            except Exception as e:
                                print(f"Error updating channel name: {e}")
                except Exception as e:
                    print(f"Error in timer check: {e}")
            
            await asyncio.sleep(60)

    def get_status_emoji(self, minutes: float) -> str:
        if minutes <= 15:
            return "🟢"
        elif minutes <= 30:
            return "🟡"
        elif minutes <= 45:
            return "🟠"
        elif minutes <= 60:
            return "🔴"
        elif minutes <= 120:
            return "💀"
        else:
            return "☠️"

    @commands.Cog.listener()
    async def on_thread_reply(self, thread, message, creator, channel, is_anonymous=False):
        if not is_anonymous:
            is_mod = message.author.id == creator.id
            if is_mod:
                if channel.id in self.ticket_timers:
                    del self.ticket_timers[channel.id]
                    await channel.edit(name=f"🟢︱{channel.name.split('︱')[1]}")
            else:
                self.ticket_timers[channel.id] = {
                    'last_user_message': datetime.now(timezone.utc),
                    'current_emoji': "🟢"
                }

async def setup(bot):
    await bot.add_cog(ModMailTimer(bot))
