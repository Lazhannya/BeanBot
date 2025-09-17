import discord
from discord.ext import commands
import logging
import os
from dotenv import load_dotenv

# Local modules
import dog_reminder

# Load environment variables from .env file
load_dotenv()

# Set up logging
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

# Set up intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

# Create bot instance
bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')

# Funny message reactions
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if "what am i?" in message.content.lower():
        if message.author.id == 143474592529252353:
            await message.channel.send(f'You are the dumbest of all nerds, {message.author.mention}!')
        elif message.author.id == 343513966049492999:
            await message.channel.send(f'Youre a bottom cow, {message.author.mention}!')
        elif message.author.id == 287897806751006720:
            await message.channel.send(f'Youre a bimbdeer pretending to be a smart doctor.. who is also actually a smart doctor, {message.author.mention}!')
        elif message.author.id == 690988264697364532:
            await message.channel.send(f'Youre a lil piss baby, {message.author.mention}!')
        else:
            await message.channel.send(f'You are a bottom, {message.author.mention}!')
    
    if "i love you" in message.content.lower():
        await message.channel.send(f'I love you too, {message.author.mention}! <3')

    if "fuck you" in message.content.lower() or "i hate you" in message.content.lower():
        await message.channel.send(f'Fuck you too, {message.author.mention}!')

    # This is needed to process commands
    await bot.process_commands(message)


# Get the token from .env file
token = os.getenv('DISCORD_TOKEN')

# Initialize the dog reminder module
dog_reminder_instance = dog_reminder.setup(bot)

# Run the bot
bot.run(token, log_handler=handler, log_level=logging.DEBUG)