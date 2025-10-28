"""
Reminder system module for BeanBot.
This module provides functionality to send scheduled reminders with acknowledgment,
denial, and timeout escalation features.
"""

import discord
from discord.ext import commands, tasks
import datetime
import asyncio
import logging
import pytz
import importlib

# Import reminder configuration
import reminder_config

# Set up logging
logger = logging.getLogger('reminder_system')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('reminder_system.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class ReminderSystem:
    def __init__(self, bot):
        self.bot = bot
        self.timezone = pytz.timezone(reminder_config.TIMEZONE)
        self.reminders = reminder_config.REMINDERS
        self.pending_reminders = {}
        self._task = None
        logger.info(f"ReminderSystem initialized with {len(self.reminders)} reminders")
        logger.info(f"Timezone: {self.timezone}")
    
    def reload_config(self):
        """Reload reminder configuration from reminder_config.py
        
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # Reload the configuration module
            importlib.reload(reminder_config)
            
            # Update instance variables
            self.timezone = pytz.timezone(reminder_config.TIMEZONE)
            self.reminders = reminder_config.REMINDERS
            
            logger.info(f"Configuration reloaded successfully: {len(self.reminders)} reminders, timezone: {self.timezone}")
            return (True, f"✅ Configuration reloaded: {len(self.reminders)} reminders, timezone: {self.timezone}")
        except Exception as e:
            error_msg = f"Failed to reload configuration: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return (False, f"❌ {error_msg}")
        
    async def start(self):
        """Start the reminder system task - MUST be called from an async context"""
        # Define the task check function in on_ready
        self._task = self.bot.loop.create_task(self._reminder_loop())
        
    def cog_unload(self):
        """Clean up when the cog is unloaded"""
        if self._task:
            self._task.cancel()
            
    async def _reminder_loop(self):
        """The main reminder loop that checks all configured reminders"""
        await self.bot.wait_until_ready()
        logger.info("Reminder system loop started!")
        print("Reminder system loop started!")
        
        while not self.bot.is_closed():
            try:
                # Get current time in the specified timezone
                now = datetime.datetime.now(self.timezone)
                current_hour, current_minute = now.hour, now.minute
                
                logger.debug(f"Current time check: {now.strftime('%Y-%m-%d %H:%M:%S')} ({self.timezone})")
                
                # Check all reminders
                for reminder in self.reminders:
                    reminder_name = reminder['name']
                    for schedule in reminder['schedules']:
                        schedule_hour = schedule['hour']
                        schedule_minute = schedule['minute']
                        schedule_label = schedule['label']
                        
                        # Check if it's time for this reminder
                        if current_hour == schedule_hour and current_minute == schedule_minute:
                            logger.info(f"Triggering {reminder_name} - {schedule_label} reminder at {now.strftime('%H:%M')}")
                            await self.send_reminder(reminder, schedule)
            
            except Exception as e:
                logger.error(f"Error in reminder loop: {e}", exc_info=True)
                
            # Wait for a minute before checking again
            await asyncio.sleep(60)
        
    # Removed tasks decorator and replaced with _reminder_loop above
    
    async def send_reminder(self, reminder_config, schedule):
        """Send a reminder to the configured user
        
        Args:
            reminder_config: Dict containing reminder configuration
            schedule: Dict containing schedule information (hour, minute, label)
        """
        reminder_name = reminder_config['name']
        schedule_label = schedule['label']
        target_user_id = reminder_config['target_user_id']
        escalation_user_id = reminder_config['escalation_user_id']
        timeout_minutes = reminder_config['timeout_minutes']
        
        logger.info(f"Attempting to send {reminder_name} - {schedule_label} reminder")
        try:
            # Fetch the target user
            try:
                user = await self.bot.fetch_user(target_user_id)
                logger.debug(f"Successfully fetched user {user.name} (ID: {user.id})")
            except Exception as user_error:
                logger.error(f"Failed to fetch user with ID {target_user_id}: {user_error}")
                # Try to notify escalation user about this failure
                try:
                    escalation_user = await self.bot.fetch_user(escalation_user_id)
                    await escalation_user.send(f"❌ Error: Failed to send {reminder_name} reminder because user with ID {target_user_id} could not be found.")
                except Exception as escalation_error:
                    logger.error(f"Also failed to notify escalation user: {escalation_error}")
                return
            
            # Create yes/no buttons
            view = self.ReminderView(reminder_config, schedule, self)
            
            # Get the message text from config
            message_text = reminder_config['messages'].get(schedule_label, f"Reminder: {reminder_name} - {schedule_label}")
            
            # Send message with buttons
            try:
                message = await user.send(message_text, view=view)
                logger.info(f"Successfully sent {reminder_name} - {schedule_label} reminder message (ID: {message.id}) to {user.name}")
            except Exception as message_error:
                logger.error(f"Failed to send message to user: {message_error}", exc_info=True)
                # Try to notify escalation user about this failure
                try:
                    escalation_user = await self.bot.fetch_user(escalation_user_id)
                    await escalation_user.send(f"❌ Error: Failed to send {reminder_name} reminder to {user.name} due to: {str(message_error)}")
                except:
                    logger.error("Also failed to notify escalation user about message sending failure")
                return
                
            # Store the reminder in pending reminders
            now = datetime.datetime.now(self.timezone)
            reminder_id = f"{reminder_name}_{schedule_label}_{now.strftime('%Y%m%d')}"
            self.pending_reminders[reminder_id] = {
                "message_id": message.id,
                "user_id": user.id,
                "reminder_name": reminder_name,
                "schedule_label": schedule_label,
                "reminder_config": reminder_config,
                "timestamp": now,
                "view": view
            }
            logger.debug(f"Created reminder with ID: {reminder_id}")
            
            # Start timeout check task
            timeout_seconds = timeout_minutes * 60
            self.bot.loop.create_task(self.check_reminder_timeout(reminder_id, timeout_seconds))
            logger.debug(f"Started timeout check task for reminder {reminder_id} ({timeout_minutes} minutes)")
                
            print(f"Sent {reminder_name} - {schedule_label} reminder to user {user.name}")
        except Exception as e:
            logger.error(f"Unexpected error in send_reminder: {e}", exc_info=True)
            print(f"Failed to send reminder: {e}")
    
    async def check_reminder_timeout(self, reminder_id, timeout_seconds):
        """Check if a reminder has timed out after the configured timeout period
        
        Args:
            reminder_id: Unique identifier for the reminder
            timeout_seconds: Timeout duration in seconds
        """
        logger.debug(f"Starting timeout check for reminder {reminder_id}, will wait {timeout_seconds} seconds")
        await asyncio.sleep(timeout_seconds)
        
        # Check if the reminder is still pending
        if reminder_id in self.pending_reminders:
            logger.info(f"Reminder {reminder_id} has timed out and is still pending")
            try:
                reminder_data = self.pending_reminders[reminder_id]
                reminder_config = reminder_data["reminder_config"]
                escalation_user_id = reminder_config["escalation_user_id"]
                schedule_label = reminder_data["schedule_label"]
                reminder_name = reminder_data["reminder_name"]
                timeout_minutes = timeout_seconds // 60
                
                # Get timeout message from config
                timeout_msg_template = reminder_config.get('timeout_message', 
                    f"⚠️ OVERDUE ALERT: Reminder {reminder_name} - {{label}} timed out! No response received within {{timeout}} minutes.")
                timeout_message = timeout_msg_template.format(label=schedule_label, timeout=timeout_minutes)
                
                # Notify the escalation user
                try:
                    escalation_user = await self.bot.fetch_user(escalation_user_id)
                    await escalation_user.send(timeout_message)
                    logger.info(f"Successfully notified escalation user about overdue {reminder_name} - {schedule_label} reminder")
                except Exception as escalation_error:
                    logger.error(f"Failed to notify escalation user about timeout: {escalation_error}")
                
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
    
    # Button view for reminders
    class ReminderView(discord.ui.View):
        def __init__(self, reminder_config, schedule, reminder_instance):
            super().__init__(timeout=None)  # No timeout on the view itself
            self.reminder_config = reminder_config
            self.schedule = schedule
            self.reminder = reminder_instance
            self.response = None
            
        @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
        async def yes_button(self, interaction: discord.Interaction, button: discord.ui.Button):
            try:
                reminder_name = self.reminder_config['name']
                schedule_label = self.schedule['label']
                
                # Try to respond to interaction
                try:
                    await interaction.response.send_message(f"Great! Thank you for confirming! ✓", ephemeral=True)
                    logger.info(f"User confirmed {reminder_name} - {schedule_label} via 'Yes' button (user: {interaction.user.name})")
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
                reminder_name = self.reminder_config['name']
                schedule_label = self.schedule['label']
                
                # Try to respond to interaction
                try:
                    await interaction.response.send_message(f"Noted. Please attend to this as soon as possible!", ephemeral=True)
                    logger.info(f"User denied {reminder_name} - {schedule_label} via 'No' button (user: {interaction.user.name})")
                except Exception as resp_error:
                    logger.error(f"Failed to respond to interaction: {resp_error}")
                    # If responding to interaction fails, we'll still try to process the button click
                
                self.response = "no"
                self.stop()
                
                # Find the reminder
                reminder_id = None
                reminder_data = None
                for rid, reminder in self.reminder.pending_reminders.items():
                    if reminder["message_id"] == interaction.message.id:
                        reminder_id = rid
                        reminder_data = reminder
                        break
                        
                if reminder_id and reminder_data:
                    # Get escalation info from config
                    reminder_config = reminder_data['reminder_config']
                    escalation_user_id = reminder_config['escalation_user_id']
                    
                    # Get denial message from config
                    denial_msg_template = reminder_config.get('denial_message',
                        f"⚠️ Alert: Reminder {reminder_name} - {{label}} was denied!")
                    denial_message = denial_msg_template.format(label=schedule_label)
                    
                    # Send notification to escalation user
                    try:
                        escalation_user = await self.reminder.bot.fetch_user(escalation_user_id)
                        await escalation_user.send(denial_message)
                        logger.info(f"Successfully notified escalation user about denied {reminder_name} - {schedule_label}")
                        del self.reminder.pending_reminders[reminder_id]
                        logger.debug(f"Removed reminder {reminder_id} after 'No' response")
                    except Exception as escalation_error:
                        logger.error(f"Failed to notify escalation user: {escalation_error}")
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
    """Create and register the reminder system"""
    reminder_system = ReminderSystem(bot)
    
    # Add a modified on_ready handler to start the reminders
    original_on_ready = bot.event(bot.on_ready)
    
    @bot.event
    async def on_ready():
        # Call the original on_ready if it exists
        if original_on_ready:
            await original_on_ready()
        
        # Start the reminder system task
        await reminder_system.start()
        logger.info("Reminder system started from on_ready event")
        print("Reminder system loop started from on_ready")
    
    @bot.command(name="dogtimezone")
    @commands.is_owner()  # Only the bot owner can use this command
    async def dog_timezone(ctx, timezone_name: str = None):
        """Set or check the timezone for reminders"""
        if timezone_name:
            try:
                new_tz = pytz.timezone(timezone_name)
                reminder_system.timezone = new_tz
                # Reload config to update timezone
                importlib.reload(reminder_config)
                await ctx.send(f"Timezone set to {timezone_name}")
                logger.info(f"Changed timezone to {timezone_name}")
            except Exception as e:
                await ctx.send(f"Error setting timezone: {e}")
                logger.error(f"Error setting timezone: {e}")
        else:
            current_time = datetime.datetime.now(reminder_system.timezone)
            status_msg = f"Current timezone: {reminder_system.timezone}\n"
            status_msg += f"Current time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            status_msg += f"Configured reminders: {len(reminder_system.reminders)}\n"
            for reminder in reminder_system.reminders:
                status_msg += f"\n{reminder['name']}:\n"
                for schedule in reminder['schedules']:
                    status_msg += f"  - {schedule['label']}: {schedule['hour']:02d}:{schedule['minute']:02d}\n"
            await ctx.send(status_msg)
            logger.info(f"Displayed current timezone settings: {reminder_system.timezone}")
    
    @bot.command(name="dogstatus")
    @commands.is_owner()  # Only the bot owner can use this command
    async def dog_status(ctx):
        """Check the current status of reminders"""
        current_time = datetime.datetime.now(reminder_system.timezone)
        pending_count = len(reminder_system.pending_reminders)
        
        # Find dog_walking reminder for backward compatibility
        dog_reminder = next((r for r in reminder_system.reminders if r['name'] == 'dog_walking'), None)
        if dog_reminder:
            status_message = (
                f"🐕 Dog Reminder Status 🐕\n"
                f"Current time: {current_time.strftime('%Y-%m-%d %H:%M:%S')} ({reminder_system.timezone})\n"
                f"Active reminders: {pending_count}\n"
                f"Reminder recipient: <@{dog_reminder['target_user_id']}>\n"
                f"Alert recipient: <@{dog_reminder['escalation_user_id']}>\n"
                f"Timeout: {dog_reminder['timeout_minutes']} minutes"
            )
        else:
            status_message = (
                f"📋 Reminder System Status\n"
                f"Current time: {current_time.strftime('%Y-%m-%d %H:%M:%S')} ({reminder_system.timezone})\n"
                f"Active reminders: {pending_count}\n"
                f"Configured reminders: {len(reminder_system.reminders)}"
            )
        
        # Add details of pending reminders if any
        if pending_count > 0:
            status_message += "\n\nPending reminders:"
            for reminder_id, reminder in reminder_system.pending_reminders.items():
                time_since = (current_time - reminder["timestamp"]).total_seconds() // 60
                reminder_name = reminder.get('reminder_name', 'unknown')
                schedule_label = reminder.get('schedule_label', 'unknown')
                status_message += f"\n- {reminder_id}: {reminder_name} - {schedule_label} ({int(time_since)} minutes ago)"
                
        await ctx.send(status_message)
        logger.info("Displayed reminder status")
    
    @bot.command(name="setdogreminder")
    @commands.is_owner()  # Only the bot owner can use this command
    async def set_dog_reminder(ctx, user_id: int = None):
        """Set which user should receive dog reminders (modifies config in memory)"""
        # Find dog_walking reminder
        dog_reminder = next((r for r in reminder_system.reminders if r['name'] == 'dog_walking'), None)
        if not dog_reminder:
            await ctx.send("Dog walking reminder not found in configuration.")
            return
            
        if user_id:
            try:
                user = await bot.fetch_user(user_id)
                dog_reminder['target_user_id'] = user_id
                await ctx.send(f"Dog reminder recipient set to {user.name} (in-memory only, edit reminder_config.py to persist)")
            except:
                await ctx.send("Could not find a user with that ID.")
        else:
            user = await bot.fetch_user(dog_reminder['target_user_id'])
            await ctx.send(f"Current dog reminder recipient: {user.name}")
    
    @bot.command(name="setdogowner")
    @commands.is_owner()  # Only the bot owner can use this command
    async def set_dog_owner(ctx, user_id: int = None):
        """Set which user should be notified if the dog is not taken care of (modifies config in memory)"""
        # Find dog_walking reminder
        dog_reminder = next((r for r in reminder_system.reminders if r['name'] == 'dog_walking'), None)
        if not dog_reminder:
            await ctx.send("Dog walking reminder not found in configuration.")
            return
            
        if user_id:
            try:
                user = await bot.fetch_user(user_id)
                dog_reminder['escalation_user_id'] = user_id
                await ctx.send(f"Dog owner alert recipient set to {user.name} (in-memory only, edit reminder_config.py to persist)")
            except:
                await ctx.send("Could not find a user with that ID.")
        else:
            user = await bot.fetch_user(dog_reminder['escalation_user_id'])
            await ctx.send(f"Current dog owner alert recipient: {user.name}")
    
    @bot.command(name="setremindertime")
    @commands.is_owner()  # Only the bot owner can use this command
    async def set_reminder_time(ctx, reminder_type: str, hour: int, minute: int = 0):
        """Set reminder times for dog walking (modifies config in memory)"""
        await ctx.send("⚠️ This command is deprecated. Please edit reminder_config.py and use !reloadreminders")
    
    @bot.command(name="testreminderdog")
    @commands.is_owner()  # Only the bot owner can use this command
    async def test_dog_reminder(ctx, time_of_day: str = "morning"):
        """Manually trigger a dog reminder to test it"""
        # Find dog_walking reminder
        dog_reminder = next((r for r in reminder_system.reminders if r['name'] == 'dog_walking'), None)
        if not dog_reminder:
            await ctx.send("Dog walking reminder not found in configuration.")
            return
            
        if time_of_day.lower() not in ["morning", "noon", "evening"]:
            time_of_day = "morning"
        
        # Find the schedule
        schedule = next((s for s in dog_reminder['schedules'] if s['label'] == time_of_day), None)
        if not schedule:
            await ctx.send(f"Schedule '{time_of_day}' not found for dog_walking reminder.")
            return
            
        await reminder_system.send_reminder(dog_reminder, schedule)
        await ctx.send(f"Test {time_of_day} reminder sent!")
    
    @bot.command(name="settimeout")
    @commands.is_owner()  # Only the bot owner can use this command
    async def set_timeout(ctx, minutes: int = 60):
        """Set how long to wait for a response before sending an alert (modifies config in memory)"""
        # Find dog_walking reminder
        dog_reminder = next((r for r in reminder_system.reminders if r['name'] == 'dog_walking'), None)
        if not dog_reminder:
            await ctx.send("Dog walking reminder not found in configuration.")
            return
            
        if minutes < 1:
            await ctx.send("Timeout must be at least 1 minute.")
            return
            
        dog_reminder['timeout_minutes'] = minutes
        await ctx.send(f"Reminder timeout set to {minutes} minutes (in-memory only, edit reminder_config.py to persist).")
    
    @bot.command(name="testreminder")
    @commands.is_owner()  # Only the bot owner can use this command
    async def test_reminder(ctx, reminder_name: str, schedule_label: str = None):
        """Manually trigger a reminder to test it
        
        Usage: !testreminder <reminder_name> [schedule_label]
        Example: !testreminder dog_walking morning
        """
        # Find the reminder
        reminder = next((r for r in reminder_system.reminders if r['name'] == reminder_name), None)
        if not reminder:
            await ctx.send(f"Reminder '{reminder_name}' not found in configuration.")
            return
        
        # If no schedule label specified, use the first one
        if schedule_label is None:
            if len(reminder['schedules']) == 0:
                await ctx.send(f"Reminder '{reminder_name}' has no schedules configured.")
                return
            schedule = reminder['schedules'][0]
            schedule_label = schedule['label']
        else:
            # Find the schedule
            schedule = next((s for s in reminder['schedules'] if s['label'] == schedule_label), None)
            if not schedule:
                await ctx.send(f"Schedule '{schedule_label}' not found for reminder '{reminder_name}'.")
                available = ", ".join([s['label'] for s in reminder['schedules']])
                await ctx.send(f"Available schedules: {available}")
                return
        
        await reminder_system.send_reminder(reminder, schedule)
        await ctx.send(f"Test reminder sent: {reminder_name} - {schedule_label}!")
    
    @bot.command(name="reloadreminders")
    @commands.is_owner()  # Only the bot owner can use this command
    async def reload_reminders(ctx):
        """Reload reminder configuration from reminder_config.py
        
        This allows you to add/edit/remove reminders without restarting the bot.
        """
        success, message = reminder_system.reload_config()
        await ctx.send(message)
    
    @bot.command(name="reminderstatus")
    @commands.is_owner()  # Only the bot owner can use this command
    async def reminder_status(ctx):
        """Check the current status of all reminders"""
        current_time = datetime.datetime.now(reminder_system.timezone)
        pending_count = len(reminder_system.pending_reminders)
        
        status_message = (
            f"📋 Reminder System Status\n"
            f"Current time: {current_time.strftime('%Y-%m-%d %H:%M:%S')} ({reminder_system.timezone})\n"
            f"Configured reminders: {len(reminder_system.reminders)}\n"
            f"Active/pending reminders: {pending_count}\n"
        )
        
        # List all configured reminders
        if len(reminder_system.reminders) > 0:
            status_message += "\n**Configured Reminders:**\n"
            for reminder in reminder_system.reminders:
                status_message += f"\n• **{reminder['name']}**\n"
                status_message += f"  Target: <@{reminder['target_user_id']}>\n"
                status_message += f"  Escalation: <@{reminder['escalation_user_id']}>\n"
                status_message += f"  Timeout: {reminder['timeout_minutes']} minutes\n"
                status_message += f"  Schedules: "
                schedules = [f"{s['label']} ({s['hour']:02d}:{s['minute']:02d})" for s in reminder['schedules']]
                status_message += ", ".join(schedules) + "\n"
        
        # Add details of pending reminders if any
        if pending_count > 0:
            status_message += "\n**Pending Reminders:**\n"
            for reminder_id, reminder in reminder_system.pending_reminders.items():
                time_since = (current_time - reminder["timestamp"]).total_seconds() // 60
                reminder_name = reminder.get('reminder_name', 'unknown')
                schedule_label = reminder.get('schedule_label', 'unknown')
                status_message += f"• {reminder_name} - {schedule_label} ({int(time_since)} minutes ago)\n"
        
        await ctx.send(status_message)
        logger.info("Displayed reminder system status")
    
    @bot.command(name="listreminders")
    @commands.is_owner()  # Only the bot owner can use this command
    async def list_reminders(ctx):
        """List all configured reminders with their schedules"""
        if len(reminder_system.reminders) == 0:
            await ctx.send("No reminders configured.")
            return
        
        message = f"📋 **Configured Reminders** ({len(reminder_system.reminders)} total):\n\n"
        
        for reminder in reminder_system.reminders:
            message += f"**{reminder['name']}**\n"
            message += f"  Schedules:\n"
            for schedule in reminder['schedules']:
                message += f"    • {schedule['label']}: {schedule['hour']:02d}:{schedule['minute']:02d}\n"
            message += f"  Target: <@{reminder['target_user_id']}>\n"
            message += f"  Escalation: <@{reminder['escalation_user_id']}>\n"
            message += f"  Timeout: {reminder['timeout_minutes']} minutes\n\n"
        
        await ctx.send(message)
        logger.info("Displayed configured reminders list")
    
    return reminder_system