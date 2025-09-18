"""
Test script to verify Discord message reception
"""

import discord
from discord.ext import commands
import logging
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging to console and file
logging.basicConfig(level=logging.DEBUG, 
                   format='[%(asctime)s] [%(levelname)-8s] %(name)-15s: %(message)s',
                   handlers=[
                       logging.FileHandler("debug_messages.log", encoding='utf-8', mode='w'),
                       logging.StreamHandler()
                   ])

# Set up intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

# Create bot instance
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')
    print(f'Bot is in {len(bot.guilds)} guilds')
    for guild in bot.guilds:
        print(f" - {guild.name} (id: {guild.id})")
        # Get list of text channels
        text_channels = [channel for channel in guild.channels if isinstance(channel, discord.TextChannel)]
        print(f"   Text channels: {len(text_channels)}")
        for channel in text_channels[:5]:  # Print first 5 channels only
            print(f"     - #{channel.name} (id: {channel.id})")
            # Check permissions
            perms = channel.permissions_for(guild.me)
            print(f"       Can read messages: {perms.read_messages}")
            print(f"       Can send messages: {perms.send_messages}")
            print(f"       Can read history: {perms.read_message_history}")

@bot.event
async def on_message(message):
    print(f'MESSAGE RECEIVED: {message.author} in #{message.channel}: "{message.content}"')
    logging.info(f'MESSAGE RECEIVED: {message.author} in #{message.channel}: "{message.content}"')
    
    # This is needed to process commands
    await bot.process_commands(message)

@bot.command(name="ping")
async def ping(ctx):
    await ctx.send(f"Pong! Latency: {round(bot.latency * 1000)}ms")
    print(f"Ping command executed by {ctx.author}")

# Get the token from .env file
token = os.getenv('DISCORD_TOKEN')

# Run the bot
try:
    bot.run(token, log_level=logging.DEBUG)
except Exception as e:
    print(f"Error running bot: {e}")