import discord
from discord.ext import commands
import logging
import os
import datetime
import sys
import random
from dotenv import load_dotenv

# Local modules
import dog_reminder
import how_is

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
    print("Bot is ready and listening for messages!")

# Funny message reactions
@bot.event
async def on_message(message):
    print(f'RECEIVED MESSAGE: {message.author} in #{message.channel}: "{message.content}"')
    
    if message.author == bot.user:
        print("Message is from the bot itself, ignoring")
        return

    msg_content = message.content.lower()
    how_are_phrases = ["how are you", "how is", "hows it going", "how's it going", "how are"]

    # Log some information about the message context
    print(f"Message is in guild: {message.guild}, channel: {message.channel}")
    if message.guild:
        print(f"Bot permissions in this channel: {message.channel.permissions_for(message.guild.me)}")

    # Check if specific phrases are contained anywhere in the message
    
    if "what am i" in msg_content:
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
    
    if "love you" in msg_content:
        await message.channel.send(f'I love you too, {message.author.mention}! <3')

    if "fuck you" in msg_content or "i hate you" in msg_content:
        await message.channel.send(f'Fuck you too, {message.author.mention}!')

 # Check if the message contains any of the target phrases
        
    if any(phrase in msg_content for phrase in how_are_phrases):
        # Try to get a joke from the API first
        joke = await how_is_joke.get_joke_from_api()
        
        # If API fails, use our backup list
        if not joke:
            joke = random.choice(how_is_joke.dad_jokes)
        
        # Send the response with the preface
        response = "We don't ask those questions here. Here's a dad joke instead:\n\n" + joke
        await message.channel.send(response)

    # This is needed to process commands
    await bot.process_commands(message)


# Get the token from .env file
token = os.getenv('DISCORD_TOKEN')

# Initialize modules
dog_reminder_instance = dog_reminder.setup(bot)
how_is_instance = how_is.setup(bot)

# Create an instance of HowIsJoke for use in message handler
from how_is import HowIsJoke
how_is_joke = HowIsJoke(bot)

# Add some simple commands to test responsiveness
@bot.command(name="ping")
async def ping(ctx):
    await ctx.send(f"Pong! Bot latency: {round(bot.latency * 1000)}ms")
    print(f"Ping command executed by {ctx.author}")

@bot.command(name="test")
async def test(ctx):
    await ctx.send("I can see your messages! This is a test response.")
    print(f"Test command executed by {ctx.author}")
    
@bot.event
async def on_message_delete(message):
    print(f"Message deleted: {message.content} by {message.author}")
    
@bot.event
async def on_typing(channel, user, when):
    print(f"User {user} is typing in {channel}")
    
# Add a direct channel message test
@bot.command(name="testchannel")
async def testchannel(ctx, channel_id: int = None):
    if not channel_id:
        channel_id = ctx.channel.id
    
    try:
        channel = bot.get_channel(channel_id)
        if channel:
            await channel.send(f"Test message in {channel.name}")
            await ctx.send(f"Test message sent to {channel.name}")
        else:
            await ctx.send(f"Could not find channel with ID: {channel_id}")
    except Exception as e:
        await ctx.send(f"Error: {e}")

# Run the bot
try:
    print("Starting bot with token:", token[:5] + "..." if token else "None")
    bot.run(token, log_level=logging.DEBUG)
except Exception as e:
    print(f"Error running bot: {e}")
    # Log the error to a file for debugging on the server
    with open("error_log.txt", "a") as f:
        import traceback
        f.write(f"Error occurred at {datetime.datetime.now()}: {str(e)}\n")
        f.write(traceback.format_exc())
        f.write("\n---\n")