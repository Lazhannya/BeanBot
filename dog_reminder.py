"""
Dog reminder module for BeanBot.
This module provides functionality to send reminders for feeding and walking the dog.
"""

import discord
from discord.ext import commands, tasks
import datetime
import asyncio
import logging
import pytz

# Set up logging
logger = logging.getLogger('dog_reminder')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('dog_reminder.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class DogReminder:
    def __init__(self, bot):
        self.bot = bot
        self.dog_reminder_user_id = 343513966049492999  # Default user ID
        self.dog_owner_id = 143474592529252353  # Owner to notify if dog isn't taken care of
        self.timezone = pytz.timezone('Europe/Paris')  # GMT+1 timezone (Paris)
        self.morning_time = datetime.time(hour=8, minute=0)  # 08:00
        self.noon_time = datetime.time(hour=13, minute=0)  # 13:00
        self.evening_time = datetime.time(hour=20, minute=0)  # 20:00
        self.timeout = 60 * 60  # 1 hour timeout in seconds
        self.pending_reminders = {}
        self._task = None
        logger.info("DogReminder initialized")
        
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
        logger.info("Dog reminder loop started!")
        print("Dog reminder loop started!")
        
        while not self.bot.is_closed():
            try:
                # Get current time in the specified timezone
                now = datetime.datetime.now(self.timezone)
                current_hour, current_minute = now.hour, now.minute
                
                logger.debug(f"Current time check: {now.strftime('%Y-%m-%d %H:%M:%S')} ({self.timezone})")
                logger.debug(f"Morning time: {self.morning_time.hour}:{self.morning_time.minute}")
                logger.debug(f"Noon time: {self.noon_time.hour}:{self.noon_time.minute}")
                logger.debug(f"Evening time: {self.evening_time.hour}:{self.evening_time.minute}")
                
                # Check for morning reminder
                if current_hour == self.morning_time.hour and current_minute == self.morning_time.minute:
                    logger.info(f"Triggering morning reminder at {now.strftime('%H:%M')}")
                    await self.send_dog_reminder("morning")
                
                # Check for noon reminder
                if current_hour == self.noon_time.hour and current_minute == self.noon_time.minute:
                    logger.info(f"Triggering noon reminder at {now.strftime('%H:%M')}")
                    await self.send_dog_reminder("noon")
                
                # Check for evening reminder
                if current_hour == self.evening_time.hour and current_minute == self.evening_time.minute:
                    logger.info(f"Triggering evening reminder at {now.strftime('%H:%M')}")
                    await self.send_dog_reminder("evening")
            
            except Exception as e:
                logger.error(f"Error in reminder loop: {e}", exc_info=True)
                
            # Wait for a minute before checking again
            await asyncio.sleep(60)
        
    # Removed tasks decorator and replaced with _reminder_loop above
    
    async def send_dog_reminder(self, time_of_day):
        """Send a dog reminder to the configured user"""
        logger.info(f"Attempting to send {time_of_day} dog reminder")
        try:
            # Fetch the user
            try:
                user = await self.bot.fetch_user(self.dog_reminder_user_id)
                logger.debug(f"Successfully fetched user {user.name} (ID: {user.id})")
            except Exception as user_error:
                logger.error(f"Failed to fetch user with ID {self.dog_reminder_user_id}: {user_error}")
                # Try to notify owner about this failure
                try:
                    owner = await self.bot.fetch_user(self.dog_owner_id)
                    await owner.send(f"❌ Error: Failed to send dog reminder because user with ID {self.dog_reminder_user_id} could not be found.")
                except Exception as owner_error:
                    logger.error(f"Also failed to notify owner: {owner_error}")
                return
            
            # Create yes/no buttons
            view = self.DogReminderView(time_of_day, self)
            
            # Send appropriate message with buttons
            try:
                if time_of_day == "morning":
                    message = await user.send("Good morning! Have you fed and walked the dog yet?", view=view)
                elif time_of_day == "noon":
                    message = await user.send("It's noon! Has the dog been fed and walked for lunch?", view=view)
                else:
                    message = await user.send("Good evening! Have you fed and walked the dog yet?", view=view)
                
                logger.info(f"Successfully sent {time_of_day} reminder message (ID: {message.id}) to {user.name}")
            except Exception as message_error:
                logger.error(f"Failed to send message to user: {message_error}", exc_info=True)
                # Try to notify owner about this failure
                try:
                    owner = await self.bot.fetch_user(self.dog_owner_id)
                    await owner.send(f"❌ Error: Failed to send dog reminder to {user.name} due to: {str(message_error)}")
                except:
                    logger.error("Also failed to notify owner about message sending failure")
                return
                
            # Store the reminder in pending reminders
            now = datetime.datetime.now(self.timezone)
            reminder_id = f"{time_of_day}_{now.strftime('%Y%m%d')}"
            self.pending_reminders[reminder_id] = {
                "message_id": message.id,
                "user_id": user.id,
                "time_of_day": time_of_day,
                "timestamp": now,
                "view": view
            }
            logger.debug(f"Created reminder with ID: {reminder_id}")
            
            # Start timeout check task
            self.bot.loop.create_task(self.check_reminder_timeout(reminder_id))
            logger.debug(f"Started timeout check task for reminder {reminder_id}")
                
            print(f"Sent {time_of_day} dog reminder to user {user.name}")
        except Exception as e:
            logger.error(f"Unexpected error in send_dog_reminder: {e}", exc_info=True)
            print(f"Failed to send dog reminder: {e}")
    
    async def check_reminder_timeout(self, reminder_id):
        """Check if a reminder has timed out after the configured timeout period"""
        logger.debug(f"Starting timeout check for reminder {reminder_id}, will wait {self.timeout} seconds")
        await asyncio.sleep(self.timeout)
        
        # Check if the reminder is still pending
        if reminder_id in self.pending_reminders:
            logger.info(f"Reminder {reminder_id} has timed out and is still pending")
            try:
                # Reminder timed out, notify the owner
                try:
                    owner = await self.bot.fetch_user(self.dog_owner_id)
                    time_of_day = self.pending_reminders[reminder_id]["time_of_day"]
                    await owner.send(f"⚠️ OVERDUE ALERT: The dog is overdue for the {time_of_day} walk and feeding! No response received within {self.timeout//60} minutes.")
                    logger.info(f"Successfully notified owner about overdue {time_of_day} reminder")
                except Exception as owner_error:
                    logger.error(f"Failed to notify owner about timeout: {owner_error}")
                
                # Disable buttons on the original message if possible
                try:
                    user = await self.bot.fetch_user(self.pending_reminders[reminder_id]["user_id"])
                    message = await user.fetch_message(self.pending_reminders[reminder_id]["message_id"])
                    
                    view = self.pending_reminders[reminder_id]["view"]
                    for item in view.children:
                        item.disabled = True
                    
                    await message.edit(view=view)
                    logger.debug(f"Successfully disabled buttons on reminder {reminder_id}")
                except Exception as message_error:
                    logger.error(f"Failed to disable buttons on original message: {message_error}")
                    # We continue execution despite this error
                    
                # Remove from pending reminders
                del self.pending_reminders[reminder_id]
                logger.debug(f"Removed reminder {reminder_id} from pending reminders")
                
            except Exception as e:
                logger.error(f"Failed to process reminder timeout: {e}", exc_info=True)
                print(f"Failed to process reminder timeout: {e}")
        else:
            logger.debug(f"Reminder {reminder_id} was already handled or removed")
    
    # Button view for dog reminders
    class DogReminderView(discord.ui.View):
        def __init__(self, time_of_day, reminder_instance):
            super().__init__(timeout=None)  # No timeout on the view itself
            self.time_of_day = time_of_day
            self.reminder = reminder_instance
            self.response = None
            
        @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
        async def yes_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            try:
                # Try to respond to interaction
                try:
                    await interaction.response.send_message("Great! Thanks for taking care of the dog! 🐕", ephemeral=True)
                    logger.info(f"User confirmed taking care of dog via 'Yes' button (user: {interaction.user.name})")
                except Exception as resp_error:
                    logger.error(f"Failed to respond to interaction: {resp_error}")
                    # If responding to interaction fails, we'll still try to process the button click
            
                self.response = "yes"
                self.stop()
                
                # Find and resolve the reminder
                reminder_removed = False
                for reminder_id, reminder in list(self.reminder.pending_reminders.items()):
                    if reminder["message_id"] == interaction.message.id:
                        del self.reminder.pending_reminders[reminder_id]
                        reminder_removed = True
                        logger.debug(f"Removed reminder {reminder_id} after 'Yes' response")
                        break
                
                if not reminder_removed:
                    logger.warning(f"Could not find matching reminder for message ID {interaction.message.id}")
                        
                # Disable the buttons
                for item in self.children:
                    item.disabled = True
                
                try:
                    await interaction.message.edit(view=self)
                    logger.debug("Successfully disabled buttons after 'Yes' response")
                except Exception as edit_error:
                    logger.error(f"Failed to edit message to disable buttons: {edit_error}")
            except Exception as e:
                logger.error(f"Unexpected error in yes_button: {e}", exc_info=True)
            
        @discord.ui.button(label="No", style=discord.ButtonStyle.red)
        async def no_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            try:
                # Try to respond to interaction
                try:
                    await interaction.response.send_message("Please take care of the dog as soon as possible! 🐕", ephemeral=True)
                    logger.info(f"User indicated dog not taken care of via 'No' button (user: {interaction.user.name})")
                except Exception as resp_error:
                    logger.error(f"Failed to respond to interaction: {resp_error}")
                    # If responding to interaction fails, we'll still try to process the button click
                
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
                        time_of_day = self.reminder.pending_reminders[reminder_id]['time_of_day']
                        await owner.send(f"⚠️ Alert: The dog hasn't been taken care of for the {time_of_day} session!")
                        logger.info(f"Successfully notified owner about unattended {time_of_day} dog session")
                        del self.reminder.pending_reminders[reminder_id]
                        logger.debug(f"Removed reminder {reminder_id} after 'No' response")
                    except Exception as owner_error:
                        logger.error(f"Failed to notify owner: {owner_error}")
                else:
                    logger.warning(f"Could not find matching reminder for message ID {interaction.message.id}")
                        
                # Disable the buttons
                for item in self.children:
                    item.disabled = True
                    
                try:
                    await interaction.message.edit(view=self)
                    logger.debug("Successfully disabled buttons after 'No' response")
                except Exception as edit_error:
                    logger.error(f"Failed to edit message to disable buttons: {edit_error}")
            except Exception as e:
                logger.error(f"Unexpected error in no_button: {e}", exc_info=True)

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
        logger.info("Dog reminder started from on_ready event")
        print("Dog reminder loop started from on_ready")
    
    @bot.command(name="dogtimezone")
    @commands.is_owner()  # Only the bot owner can use this command
    async def dog_timezone(ctx, timezone_name: str = None):
        """Set or check the timezone for dog reminders"""
        if timezone_name:
            try:
                new_tz = pytz.timezone(timezone_name)
                dog_reminder.timezone = new_tz
                await ctx.send(f"Timezone set to {timezone_name}")
                logger.info(f"Changed timezone to {timezone_name}")
            except Exception as e:
                await ctx.send(f"Error setting timezone: {e}")
                logger.error(f"Error setting timezone: {e}")
        else:
            current_time = datetime.datetime.now(dog_reminder.timezone)
            await ctx.send(f"Current timezone: {dog_reminder.timezone}\n"
                          f"Current time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                          f"Morning reminder: {dog_reminder.morning_time.hour}:{dog_reminder.morning_time.minute:02d}\n"
                          f"Noon reminder: {dog_reminder.noon_time.hour}:{dog_reminder.noon_time.minute:02d}\n"
                          f"Evening reminder: {dog_reminder.evening_time.hour}:{dog_reminder.evening_time.minute:02d}")
            logger.info(f"Displayed current timezone settings: {dog_reminder.timezone}")
    
    @bot.command(name="dogstatus")
    @commands.is_owner()  # Only the bot owner can use this command
    async def dog_status(ctx):
        """Check the current status of dog reminders"""
        current_time = datetime.datetime.now(dog_reminder.timezone)
        pending_count = len(dog_reminder.pending_reminders)
        status_message = (
            f"🐕 Dog Reminder Status 🐕\n"
            f"Current time: {current_time.strftime('%Y-%m-%d %H:%M:%S')} ({dog_reminder.timezone})\n"
            f"Active reminders: {pending_count}\n"
            f"Reminder recipient: <@{dog_reminder.dog_reminder_user_id}>\n"
            f"Alert recipient: <@{dog_reminder.dog_owner_id}>\n"
            f"Timeout: {dog_reminder.timeout//60} minutes"
        )
        
        # Add details of pending reminders if any
        if pending_count > 0:
            status_message += "\n\nPending reminders:"
            for reminder_id, reminder in dog_reminder.pending_reminders.items():
                time_since = (current_time - reminder["timestamp"]).total_seconds() // 60
                status_message += f"\n- {reminder_id}: {reminder['time_of_day']} ({time_since} minutes ago)"
                
        await ctx.send(status_message)
        logger.info("Displayed dog reminder status")
    
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