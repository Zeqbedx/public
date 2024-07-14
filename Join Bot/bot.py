import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
import io
import os
from dotenv import load_dotenv
import requests
from io import BytesIO

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

load_dotenv()
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_ID = int(os.getenv('CHANNEL_ID'))
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.event
async def on_member_join(member):
    background = Image.open('./Join Bot/welcome_background.png')
    
    avatar_url = str(member.avatar.url if member.avatar else member.default_avatar.url)
    avatar_response = requests.get(avatar_url)
    avatar_image = Image.open(BytesIO(avatar_response.content)).convert('RGBA')
    
    size = 150
    border_width = 5
    total_size = size + 2 * border_width
    mask = Image.new('L', (size, size), 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.ellipse((0, 0, size, size), fill=255)

    avatar_with_border = Image.new('RGBA', (total_size, total_size), (255, 255, 255, 255))
    
    avatar_image = avatar_image.resize((size, size), Image.LANCZOS)
    avatar_with_border.paste(avatar_image, (border_width, border_width), mask)
    
    total_mask = Image.new('L', (total_size, total_size), 0)
    draw_total_mask = ImageDraw.Draw(total_mask)
    draw_total_mask.ellipse((0, 0, total_size, total_size), fill=255)
    
    avatar_with_border.putalpha(total_mask)
    
    total_height = total_size + 100
    start_y = (background.height - total_height) // 2
    
    avatar_position = ((background.width - total_size) // 2, start_y)
    background.paste(avatar_with_border, avatar_position, avatar_with_border)

    draw = ImageDraw.Draw(background)
    
    large_font = ImageFont.truetype('arialbd.ttf', 48)  # Bigger font for welcome text
    small_font = ImageFont.truetype('arialbd.ttf', 32)  # Smaller font for member count
    
    welcome_text = f"Welcome, {member.name}!"
    text_bbox = draw.textbbox((0, 0), welcome_text, font=large_font)
    text_position = ((background.width - text_bbox[2]) // 2, start_y + total_size + 20)
    draw.text(text_position, welcome_text, font=large_font, fill=(255, 255, 255))
    
    member_count = len(member.guild.members)
    suffix = 'th' if 11 <= member_count % 100 <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(member_count % 10, 'th')
    count_text = f"You are the {member_count}{suffix} member!"
    count_bbox = draw.textbbox((0, 0), count_text, font=small_font)
    count_position = ((background.width - count_bbox[2]) // 2, text_position[1] + text_bbox[3] - text_bbox[1] + 20)
    draw.text(count_position, count_text, font=small_font, fill=(230, 230, 230))  # Light grey color
    
    buffer = io.BytesIO()
    background.save(buffer, format='PNG')
    buffer.seek(0)
    
    channel = bot.get_channel(CHANNEL_ID)
    await channel.send(file=discord.File(buffer, 'welcome.png'))


bot.run(DISCORD_TOKEN)