"""
How is module for BeanBot.
This module provides functionality to send randomly generated dad jokes to users.
"""

import discord
from discord.ext import commands
import random
import aiohttp
import json

class HowIsJoke:
    def __init__(self, bot):
        self.bot = bot
        self.dad_jokes = [
            "How is a moon like a dollar? They both have four quarters.",
            "How is a dog like a tree? They both lose their bark when they die.",
            "How is a baseball player like a detective? They both go for runs.",
            "How is a lawyer like a banana? They both appear in slips.",
            "How is a book like a king? They both have pages.",
            "How is a tennis match like a math problem? They both involve solving sets.",
            "How is a piano like a fish? You can tune-a piano but you can't tuna fish!",
            "How is a computer like an elephant? They both have memory.",
            "How is a bad joke like a pencil? They both have no point.",
            "How is a calendar like a politician? They both have many dates.",
        ]
        # We'll keep this list as a fallback, but we'll also try to fetch jokes from an API

    async def get_joke_from_api(self):
        """Fetch a dad joke from icanhazdadjoke API"""
        try:
            headers = {
                "Accept": "application/json",
                "User-Agent": "BeanBot Dad Jokes Module (Discord Bot)"
            }
            async with aiohttp.ClientSession() as session:
                async with session.get("https://icanhazdadjoke.com/", headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("joke", None)
        except Exception as e:
            print(f"Failed to fetch joke from API: {e}")
        
        return None

    async def send_dad_joke(self, user_id):
        """Send a dad joke to a specific user"""
        try:
            user = await self.bot.fetch_user(user_id)
            
            # Try to get a joke from the API first
            joke = await self.get_joke_from_api()
            
            # If API fails, use our backup list
            if not joke:
                joke = random.choice(self.dad_jokes)
                
            # Create a nice embed for the joke
            embed = discord.Embed(
                title="Dad Joke Time!",
                description="Hey there, it seems like you didn't read Lazzy's bio. We don't ask 'how are you'-questions in this house. Here's a dad joke instead:\n\n" + joke,
                color=0x00FF00
            )
            embed.set_footer(text="Sent with ❤️ by BeanBot")
            
            # Send the joke
            await user.send(embed=embed)
            print(f"Sent dad joke to user {user.name}")
            return True
            
        except Exception as e:
            print(f"Failed to send dad joke: {e}")
            return False

def setup(bot):
    """Create and register the dad joke commands"""
    how_is_joke = HowIsJoke(bot)
    
    @bot.command(name="sendjoke")
    async def send_joke(ctx, user_id: int = None):
        """Send a dad joke to a specified user or to the command invoker if no user specified"""
        if not user_id:
            user_id = ctx.author.id
            
        success = await how_is_joke.send_dad_joke(user_id)
        
        if success:
            await ctx.send(f"Dad joke sent successfully! 😄")
        else:
            await ctx.send(f"Failed to send dad joke. Check logs for details.")
    
    # Set up a message listener instead of a command
    @bot.event
    async def on_message(message):
        # Don't respond to bot messages (prevents potential loops)
        if message.author.bot:
            return
        
        # Process commands if this is a command message
        await bot.process_commands(message)
        
        # Check if the message contains any of the target phrases
        msg_content = message.content.lower()
        target_phrases = ["how are you", "how is", "hows it going", "how's it going"]
        
        if any(phrase in msg_content for phrase in target_phrases):
            # Try to get a joke from the API first
            joke = await how_is_joke.get_joke_from_api()
            
            # If API fails, use our backup list
            if not joke:
                joke = random.choice(how_is_joke.dad_jokes)
            
            # Send the response with the preface
            response = "We don't ask those questions here. Here's a dad joke instead:\n\n" + joke
            await message.channel.send(response)
    
    return how_is_joke
