"""
Dog reminder module for BeanBot.
This module provides functionality to send reminders for feeding and walking the dog.
"""

import discord
from discord.ext import commands, tasks
import datetime
import asyncio

class DogReminder:
    def __init__(self, bot):
        self.bot = bot
        self.dog_reminder_user_id = 343513966049492999  # Default user ID
        self.dog_owner_id = 143474592529252353  # Owner to notify if dog isn't taken care of
        self.morning_time = datetime.time(hour=8, minute=0)  # 08:00
        self.noon_time = datetime.time(hour=13, minute=0)  # 13:00
        self.evening_time = datetime.time(hour=20, minute=0)  # 20:00
        self.timeout = 60 * 60  # 1 hour timeout in seconds
        self.pending_reminders = {}
        self._task = None
        
    async def start(self):
        """Start the dog reminder task - MUST be called from an async context"""
        # Define the task check function in on_ready
        self._task = self.bot.loop.create_task(self._reminder_loop())
        
    def cog_unload(self):
        """Clean up when the cog is unloaded"""
        if self._task:
            self._task.cancel()
            
    async def _reminder_loop(self):
        """The main reminder loop that replaces the tasks decorator"""
        await self.bot.wait_until_ready()
        print("Dog reminder loop started!")
        
        while not self.bot.is_closed():
            # Check current time
            now = datetime.datetime.now().time()
            current_hour, current_minute = now.hour, now.minute
            
            # Check for morning reminder
            if current_hour == self.morning_time.hour and current_minute == self.morning_time.minute:
                await self.send_dog_reminder("morning")
            
            # Check for noon reminder
            if current_hour == self.noon_time.hour and current_minute == self.noon_time.minute:
                await self.send_dog_reminder("noon")
            
            # Check for evening reminder
            if current_hour == self.evening_time.hour and current_minute == self.evening_time.minute:
                await self.send_dog_reminder("evening")
                
            # Wait for a minute before checking again
            await asyncio.sleep(60)
        
    # Removed tasks decorator and replaced with _reminder_loop above
    
    async def send_dog_reminder(self, time_of_day):
        """Send a dog reminder to the configured user"""
        try:
            user = await self.bot.fetch_user(self.dog_reminder_user_id)
            
            # Create yes/no buttons
            view = self.DogReminderView(time_of_day, self)
            
            # Send appropriate message with buttons
            if time_of_day == "morning":
                message = await user.send("Good morning! Have you fed and walked the dog yet?", view=view)
            elif time_of_day == "noon":
                message = await user.send("It's noon! Has the dog been fed and walked for lunch?", view=view)
            else:
                message = await user.send("Good evening! Have you fed and walked the dog yet?", view=view)
                
            # Store the reminder in pending reminders
            reminder_id = f"{time_of_day}_{datetime.datetime.now().strftime('%Y%m%d')}"
            self.pending_reminders[reminder_id] = {
                "message_id": message.id,
                "user_id": user.id,
                "time_of_day": time_of_day,
                "timestamp": datetime.datetime.now(),
                "view": view
            }
            
            # Start timeout check task
            self.bot.loop.create_task(self.check_reminder_timeout(reminder_id))
                
            print(f"Sent {time_of_day} dog reminder to user {user.name}")
        except Exception as e:
            print(f"Failed to send dog reminder: {e}")
    
    async def check_reminder_timeout(self, reminder_id):
        """Check if a reminder has timed out after the configured timeout period"""
        await asyncio.sleep(self.timeout)
        
        # Check if the reminder is still pending
        if reminder_id in self.pending_reminders:
            try:
                # Reminder timed out, notify the owner
                owner = await self.bot.fetch_user(self.dog_owner_id)
                time_of_day = self.pending_reminders[reminder_id]["time_of_day"]
                await owner.send(f"⚠️ OVERDUE ALERT: The dog is overdue for the {time_of_day} walk and feeding! No response received within an hour.")
                
                # Disable buttons on the original message if possible
                try:
                    user = await self.bot.fetch_user(self.pending_reminders[reminder_id]["user_id"])
                    message = await user.fetch_message(self.pending_reminders[reminder_id]["message_id"])
                    
                    view = self.pending_reminders[reminder_id]["view"]
                    for item in view.children:
                        item.disabled = True
                    
                    await message.edit(view=view)
                except:
                    pass  # Message might be deleted or inaccessible
                    
                # Remove from pending reminders
                del self.pending_reminders[reminder_id]
                
            except Exception as e:
                print(f"Failed to process reminder timeout: {e}")
    
    # Button view for dog reminders
    class DogReminderView(discord.ui.View):
        def __init__(self, time_of_day, reminder_instance):
            super().__init__(timeout=None)  # No timeout on the view itself
            self.time_of_day = time_of_day
            self.reminder = reminder_instance
            self.response = None
            
        @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
        async def yes_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.send_message("Great! Thanks for taking care of the dog! 🐕", ephemeral=True)
            self.response = "yes"
            self.stop()
            
            # Find and resolve the reminder
            for reminder_id, reminder in list(self.reminder.pending_reminders.items()):
                if reminder["message_id"] == interaction.message.id:
                    del self.reminder.pending_reminders[reminder_id]
                    break
                    
            # Disable the buttons
            for item in self.children:
                item.disabled = True
                
            await interaction.message.edit(view=self)
            
        @discord.ui.button(label="No", style=discord.ButtonStyle.red)
        async def no_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.response.send_message("Please take care of the dog as soon as possible! 🐕", ephemeral=True)
            self.response = "no"
            self.stop()
            
            # Find the reminder
            reminder_id = None
            for rid, reminder in self.reminder.pending_reminders.items():
                if reminder["message_id"] == interaction.message.id:
                    reminder_id = rid
                    break
                    
            if reminder_id:
                # Send notification to owner
                try:
                    owner = await self.reminder.bot.fetch_user(self.reminder.dog_owner_id)
                    await owner.send(f"⚠️ Alert: The dog hasn't been taken care of for the {self.reminder.pending_reminders[reminder_id]['time_of_day']} session!")
                    del self.reminder.pending_reminders[reminder_id]
                except Exception as e:
                    print(f"Failed to notify owner: {e}")
                    
            # Disable the buttons
            for item in self.children:
                item.disabled = True
                
            await interaction.message.edit(view=self)

def setup(bot):
    """Create and register the dog reminder commands"""
    dog_reminder = DogReminder(bot)
    
    # Add a modified on_ready handler to start the reminders
    original_on_ready = bot.event(bot.on_ready)
    
    @bot.event
    async def on_ready():
        # Call the original on_ready if it exists
        if original_on_ready:
            await original_on_ready()
        
        # Start the dog reminder task
        await dog_reminder.start()
        print("Dog reminder loop started from on_ready")
    
    @bot.command(name="setdogreminder")
    @commands.is_owner()  # Only the bot owner can use this command
    async def set_dog_reminder(ctx, user_id: int = None):
        """Set which user should receive dog reminders"""
        if user_id:
            try:
                user = await bot.fetch_user(user_id)
                dog_reminder.dog_reminder_user_id = user_id
                await ctx.send(f"Dog reminder recipient set to {user.name}")
            except:
                await ctx.send("Could not find a user with that ID.")
        else:
            user = await bot.fetch_user(dog_reminder.dog_reminder_user_id)
            await ctx.send(f"Current dog reminder recipient: {user.name}")
    
    @bot.command(name="setdogowner")
    @commands.is_owner()  # Only the bot owner can use this command
    async def set_dog_owner(ctx, user_id: int = None):
        """Set which user should be notified if the dog is not taken care of"""
        if user_id:
            try:
                user = await bot.fetch_user(user_id)
                dog_reminder.dog_owner_id = user_id
                await ctx.send(f"Dog owner alert recipient set to {user.name}")
            except:
                await ctx.send("Could not find a user with that ID.")
        else:
            user = await bot.fetch_user(dog_reminder.dog_owner_id)
            await ctx.send(f"Current dog owner alert recipient: {user.name}")
    
    @bot.command(name="setremindertime")
    @commands.is_owner()  # Only the bot owner can use this command
    async def set_reminder_time(ctx, reminder_type: str, hour: int, minute: int = 0):
        """Set reminder times. Type can be 'morning', 'noon', or 'evening'."""
        if reminder_type.lower() not in ["morning", "noon", "evening"]:
            await ctx.send("Type must be 'morning', 'noon', or 'evening'")
            return
        
        if not (0 <= hour < 24 and 0 <= minute < 60):
            await ctx.send("Invalid time. Hour must be 0-23, minute must be 0-59")
            return
        
        new_time = datetime.time(hour=hour, minute=minute)
        
        if reminder_type.lower() == "morning":
            dog_reminder.morning_time = new_time
            await ctx.send(f"Morning reminder time set to {hour:02d}:{minute:02d}")
        elif reminder_type.lower() == "noon":
            dog_reminder.noon_time = new_time
            await ctx.send(f"Noon reminder time set to {hour:02d}:{minute:02d}")
        else:
            dog_reminder.evening_time = new_time
            await ctx.send(f"Evening reminder time set to {hour:02d}:{minute:02d}")
    
    @bot.command(name="testreminderdog")
    @commands.is_owner()  # Only the bot owner can use this command
    async def test_dog_reminder(ctx, time_of_day: str = "morning"):
        """Manually trigger a dog reminder to test it"""
        if time_of_day.lower() not in ["morning", "noon", "evening"]:
            time_of_day = "morning"
            
        await dog_reminder.send_dog_reminder(time_of_day)
        await ctx.send(f"Test {time_of_day} reminder sent!")
    
    @bot.command(name="settimeout")
    @commands.is_owner()  # Only the bot owner can use this command
    async def set_timeout(ctx, minutes: int = 60):
        """Set how long to wait for a response before sending an alert (in minutes)"""
        if minutes < 1:
            await ctx.send("Timeout must be at least 1 minute.")
            return
            
        dog_reminder.timeout = minutes * 60  # Convert minutes to seconds
        await ctx.send(f"Reminder timeout set to {minutes} minutes.")
    
    return dog_reminder