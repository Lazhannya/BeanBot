"""
Reminder system module for BeanBot.
This module provides functionality to send scheduled reminders with acknowledgment,
denial, and timeout escalation features.
"""

import discord
from discord.ext import commands, tasks
from discord import app_commands
import datetime
import asyncio
import logging
import pytz
import importlib
import time

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

# === VALIDATION FUNCTIONS ===

def validate_reminder_and_schedule(reminder_name: str, schedule_label: str = None) -> tuple[bool, str, dict, dict]:
    """
    Enhanced validation for reminder and schedule combinations
    Returns: (is_valid, error_message, reminder_obj, schedule_obj)
    """
    try:
        # Find reminder
        reminder = next((r for r in reminder_config.REMINDERS if r['name'] == reminder_name), None)
        if not reminder:
            available = ", ".join([r['name'] for r in reminder_config.REMINDERS])
            return False, f"Reminder '{reminder_name}' not found. Available: {available}", None, None
        
        # If no schedule specified, use first one
        if schedule_label is None:
            if not reminder.get('schedules'):
                return False, f"Reminder '{reminder_name}' has no schedules configured.", reminder, None
            schedule = reminder['schedules'][0]
            return True, "", reminder, schedule
        
        # Find specific schedule
        schedule = next((s for s in reminder.get('schedules', []) if s['label'] == schedule_label), None)
        if not schedule:
            available = ", ".join([s['label'] for s in reminder.get('schedules', [])])
            return False, f"Schedule '{schedule_label}' not found for '{reminder_name}'. Available: {available}", reminder, None
        
        return True, "", reminder, schedule
        
    except Exception as e:
        logger.error(f"Error in validate_reminder_and_schedule: {e}")
        return False, f"Validation error: {str(e)}", None, None

# === DM CONTEXT UTILITIES ===

def is_dm_context(interaction: discord.Interaction) -> bool:
    """Check if interaction is happening in a DM context"""
    return interaction.guild is None

def get_context_info(interaction: discord.Interaction) -> dict:
    """Get context information for logging and debugging"""
    return {
        'is_dm': is_dm_context(interaction),
        'guild_id': interaction.guild.id if interaction.guild else None,
        'guild_name': interaction.guild.name if interaction.guild else 'DM',
        'channel_id': interaction.channel.id if interaction.channel else None,
        'channel_type': str(interaction.channel.type) if interaction.channel else 'unknown',
        'user_id': interaction.user.id,
        'user_name': str(interaction.user)
    }

def is_owner_in_context(interaction: discord.Interaction, bot) -> bool:
    """Check if user is bot owner, works in both guild and DM context"""
    try:
        # DM context: check against bot.owner_id directly
        if is_dm_context(interaction):
            return interaction.user.id == bot.owner_id
        
        # Guild context: check against interaction.client.owner_id (existing logic)
        return interaction.user.id == interaction.client.owner_id
        
    except Exception as e:
        logger.error(f"Error checking owner status: {e}")
        return False

def get_dm_error_message(command_name: str, is_owner: bool) -> str:
    """Generate appropriate error message for DM context"""
    if is_owner:
        return f"✅ You can use `{command_name}` in DMs as the bot owner."
    else:
        return (
            f"❌ Sorry, `{command_name}` is restricted to the bot owner in DMs for security.\n"
            f"💡 Try using this command in a server where the bot is present instead."
        )

def handle_autocomplete_error(interaction: discord.Interaction, error: Exception, function_name: str) -> list[app_commands.Choice[str]]:
    """Centralized error handling for autocomplete functions in DM context"""
    context_info = get_context_info(interaction)
    logger.error(f"Error in {function_name} - Context: {context_info}, Error: {error}")
    
    if is_dm_context(interaction):
        return [
            app_commands.Choice(name="❌ Error in DM autocomplete", value="dm_error"),
            app_commands.Choice(name="💡 Try again or use guild", value="retry")
        ]
    else:
        return [app_commands.Choice(name="❌ Autocomplete error", value="error")]

def get_fallback_choices(interaction: discord.Interaction, choice_type: str) -> list[app_commands.Choice[str]]:
    """Provide fallback autocomplete choices when configuration is unavailable"""
    if choice_type == "reminder":
        if is_dm_context(interaction):
            return [
                app_commands.Choice(name="🔄 Config loading... (DM)", value="loading"),
                app_commands.Choice(name="💡 Try: dog_walking", value="dog_walking")
            ]
        else:
            return [app_commands.Choice(name="🔄 Config loading...", value="loading")]
    
    elif choice_type == "timezone":
        return [
            app_commands.Choice(name="🌍 UTC (fallback)", value="UTC"),
            app_commands.Choice(name="🌍 Europe/Paris", value="Europe/Paris"),
            app_commands.Choice(name="🌍 America/New_York", value="America/New_York")
        ]
    
    return [app_commands.Choice(name="❌ No options available", value="none")]

# === AUTOCOMPLETE FUNCTIONS ===

async def reminder_name_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    """Enhanced autocomplete function for reminder names with DM support and validation"""
    start_time = time.time()
    try:
        # Log context for debugging DM functionality
        context_info = get_context_info(interaction)
        logger.debug(f"Reminder name autocomplete called - Context: {context_info}")
        
        # Enhanced error handling for config unavailable with DM support
        if not hasattr(reminder_config, 'REMINDERS') or not reminder_config.REMINDERS:
            logger.warning(f"REMINDERS configuration not available for autocomplete - DM context: {is_dm_context(interaction)}")
            return get_fallback_choices(interaction, "reminder")
        
        choices = []
        for reminder in reminder_config.REMINDERS:
            reminder_name = reminder.get('name', 'unknown')
            if current.lower() in reminder_name.lower():
                # Enhanced: Show additional context in autocomplete
                schedule_count = len(reminder.get('schedules', []))
                display_name = f"{reminder_name} ({schedule_count} schedules)"
                choices.append(app_commands.Choice(name=display_name, value=reminder_name))
        
        # Enhanced: If no matches found, provide helpful message
        if not choices and current.strip():
            choices.append(app_commands.Choice(name=f"No reminders match '{current}'", value="none"))
        
        # DM context: Add helpful hint if in DM
        if is_dm_context(interaction) and choices and len(choices) < 25:
            choices.append(app_commands.Choice(name="💡 Using DM - all features available", value="dm_hint"))
        
        # Limit to Discord's maximum of 25 choices
        # Performance monitoring
        end_time = time.time()
        response_time = end_time - start_time
        logger.debug(f"Returning {len(choices[:25])} reminder autocomplete choices for DM context: {is_dm_context(interaction)}, Response time: {response_time:.3f}s")
        
        # Warn if response is slow (Discord has 3-second limit)
        if response_time > 2.0:
            logger.warning(f"Slow autocomplete response in reminder_name_autocomplete: {response_time:.3f}s (DM: {is_dm_context(interaction)})")
        
        return choices[:25]
    except Exception as e:
        return handle_autocomplete_error(interaction, e, "reminder_name_autocomplete")

async def schedule_label_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    """Enhanced autocomplete function for schedule labels with DM support"""
    start_time = time.time()
    try:
        # Log context for debugging DM functionality
        context_info = get_context_info(interaction)
        logger.debug(f"Schedule label autocomplete called - Context: {context_info}")
        
        choices = []
        
        # Try to get the reminder name from the interaction (enhanced context awareness)
        reminder_name = None
        if hasattr(interaction, 'namespace') and interaction.namespace:
            reminder_name = getattr(interaction.namespace, 'reminder', None)
        
        # Enhanced: Also try to get from command data if namespace isn't available
        if not reminder_name and hasattr(interaction, 'data') and interaction.data:
            options = interaction.data.get('options', [])
            for option in options:
                if option.get('name') == 'reminder':
                    reminder_name = option.get('value')
                    break
        
        if reminder_name:
            # Find the specific reminder (dynamic filtering)
            reminder = next((r for r in reminder_config.REMINDERS if r['name'] == reminder_name), None)
            if reminder:
                for schedule in reminder['schedules']:
                    label = schedule['label']
                    if current.lower() in label.lower():
                        # Enhanced: Include time in display name for clarity
                        display_name = f"{label} ({schedule['hour']:02d}:{schedule['minute']:02d})"
                        choices.append(app_commands.Choice(name=display_name, value=label))
        else:
            # If no reminder selected, show all possible schedule labels with context
            seen_labels = set()
            for reminder in reminder_config.REMINDERS:
                for schedule in reminder['schedules']:
                    label = schedule['label']
                    if current.lower() in label.lower() and label not in seen_labels:
                        # Enhanced: Show which reminder this label belongs to
                        display_name = f"{label} (from {reminder['name']})"
                        choices.append(app_commands.Choice(name=display_name, value=label))
                        seen_labels.add(label)
        
        # DM context: Add performance info if in DM and choices exist
        if is_dm_context(interaction) and choices and len(choices) < 25:
            choices.append(app_commands.Choice(name="🚀 DM autocomplete active", value="dm_active"))
        
        # Performance monitoring
        end_time = time.time()
        response_time = end_time - start_time
        logger.debug(f"Returning {len(choices[:25])} schedule autocomplete choices for DM context: {is_dm_context(interaction)}, Response time: {response_time:.3f}s")
        
        if response_time > 2.0:
            logger.warning(f"Slow autocomplete response in schedule_label_autocomplete: {response_time:.3f}s (DM: {is_dm_context(interaction)})")
        
        return choices[:25]
    except Exception as e:
        return handle_autocomplete_error(interaction, e, "schedule_label_autocomplete")

async def timezone_autocomplete(interaction: discord.Interaction, current: str) -> list[app_commands.Choice[str]]:
    """Enhanced autocomplete function for timezone names with DM support"""
    try:
        # Log context for debugging DM functionality
        context_info = get_context_info(interaction)
        logger.debug(f"Timezone autocomplete called - Context: {context_info}")
        
        # Enhanced: More comprehensive timezone list with regions
        popular_timezones = [
            'UTC', 'Europe/London', 'Europe/Paris', 'Europe/Berlin', 'Europe/Rome', 'Europe/Madrid',
            'America/New_York', 'America/Chicago', 'America/Denver', 'America/Los_Angeles',
            'Asia/Tokyo', 'Asia/Shanghai', 'Asia/Kolkata', 'Asia/Dubai', 'Asia/Seoul',
            'Australia/Sydney', 'Australia/Melbourne', 'Pacific/Auckland'
        ]
        
        choices = []
        
        # Enhanced: Prioritize exact matches first
        exact_matches = []
        partial_matches = []
        
        for tz in popular_timezones:
            if current.lower() == tz.lower():
                exact_matches.append(app_commands.Choice(name=f"⭐ {tz}", value=tz))
            elif current.lower() in tz.lower():
                partial_matches.append(app_commands.Choice(name=tz, value=tz))
        
        # Enhanced: Show current timezone if available
        try:
            current_tz = str(reminder_config.TIMEZONE)
            if current.lower() in current_tz.lower() and current_tz not in [choice.value for choice in exact_matches + partial_matches]:
                choices.append(app_commands.Choice(name=f"🌍 {current_tz} (current)", value=current_tz))
        except:
            pass
        
        # Combine results: exact matches first, then partial matches
        choices.extend(exact_matches)
        choices.extend(partial_matches)
        
        # Enhanced: If no matches, show a helpful message
        if not choices and current.strip():
            choices.append(app_commands.Choice(name=f"No timezone matches '{current}'", value="UTC"))
        
        # DM context: Add helpful timezone info if in DM
        if is_dm_context(interaction) and len(choices) < 24:  # Leave room for DM hint
            choices.append(app_commands.Choice(name="🌍 DM timezone selection", value="dm_tz"))
        
        logger.debug(f"Returning {len(choices[:25])} timezone autocomplete choices for DM context: {is_dm_context(interaction)}")
        return choices[:25]
    except Exception as e:
        fallback = get_fallback_choices(interaction, "timezone")
        logger.error(f"Error in timezone_autocomplete - DM context: {is_dm_context(interaction)}, returning fallback: {fallback}")
        return fallback

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
    
    # === SLASH COMMAND GROUPS ===
    
    class ReminderGroup(app_commands.Group):
        """Reminder management slash commands"""
        
        def __init__(self, reminder_system):
            super().__init__(name="reminder", description="Reminder management commands")
            self.reminder_system = reminder_system
        
        @app_commands.command(name="test", description="Test a reminder delivery")
        @app_commands.describe(
            reminder="Name of the reminder to test",
            schedule="Schedule label to test (optional)"
        )
        async def test(self, interaction: discord.Interaction, reminder: str, schedule: str = None):
            """Test reminder delivery - slash command version of !testreminder"""
            try:
                # Check DM permissions first (before deferring)
                if is_dm_context(interaction) and not is_owner_in_context(interaction, interaction.client):
                    context_info = get_context_info(interaction)
                    error_msg = get_dm_error_message("/reminder test", False)
                    await interaction.response.send_message(error_msg, ephemeral=True)
                    logger.warning(f"Permission denied for /reminder test - User: {interaction.user.id}, Context: {context_info}")
                    return
                
                # Defer response since this might take time
                await interaction.response.defer()
                
                # Find the reminder
                reminder_config_obj = next((r for r in self.reminder_system.reminders if r['name'] == reminder), None)
                if not reminder_config_obj:
                    await interaction.followup.send(f"❌ Reminder '{reminder}' not found in configuration.")
                    return
                
                # If no schedule label specified, use the first one
                if schedule is None:
                    if len(reminder_config_obj['schedules']) == 0:
                        await interaction.followup.send(f"❌ Reminder '{reminder}' has no schedules configured.")
                        return
                    schedule_obj = reminder_config_obj['schedules'][0]
                    schedule = schedule_obj['label']
                else:
                    # Find the schedule
                    schedule_obj = next((s for s in reminder_config_obj['schedules'] if s['label'] == schedule), None)
                    if not schedule_obj:
                        available = ", ".join([s['label'] for s in reminder_config_obj['schedules']])
                        await interaction.followup.send(f"❌ Schedule '{schedule}' not found for reminder '{reminder}'.\nAvailable schedules: {available}")
                        return
                
                # Send the reminder
                await self.reminder_system.send_reminder(reminder_config_obj, schedule_obj)
                await interaction.followup.send(f"✅ Test reminder sent: **{reminder}** - *{schedule}*!")
                
                # Enhanced logging with DM context information
                context_info = get_context_info(interaction)
                logger.info(f"SLASH_COMMAND: /reminder test executed by {interaction.user} ({interaction.user.id}) - reminder: {reminder}, schedule: {schedule}, Context: {context_info}")
                
            except Exception as e:
                logger.error(f"Error in /reminder test: {e}", exc_info=True)
                await interaction.followup.send(f"❌ Error testing reminder: {str(e)}")
        
        @test.autocomplete('reminder')
        async def test_reminder_autocomplete(self, interaction: discord.Interaction, current: str):
            return await reminder_name_autocomplete(interaction, current)
        
        @test.autocomplete('schedule')
        async def test_schedule_autocomplete(self, interaction: discord.Interaction, current: str):
            return await schedule_label_autocomplete(interaction, current)
        
        @app_commands.command(name="status", description="Check reminder system status")
        async def status(self, interaction: discord.Interaction):
            """Show reminder system status - slash command version of !reminderstatus"""
            try:
                # Check DM permissions (status is read-only, but still enforce owner-only in DMs)
                if is_dm_context(interaction) and not is_owner_in_context(interaction, interaction.client):
                    context_info = get_context_info(interaction)
                    error_msg = get_dm_error_message("/reminder status", False)
                    await interaction.response.send_message(error_msg, ephemeral=True)
                    logger.warning(f"Permission denied for /reminder status - User: {interaction.user.id}, Context: {context_info}")
                    return
                
                current_time = datetime.datetime.now(self.reminder_system.timezone)
                pending_count = len(self.reminder_system.pending_reminders)
                
                status_message = (
                    f"📋 **Reminder System Status**\n"
                    f"🕐 Current time: {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}\n"
                    f"⏰ Pending reminders: {pending_count}\n"
                    f"📍 Timezone: {self.reminder_system.timezone}\n"
                    f"🔧 Active reminders: {len(self.reminder_system.reminders)}\n\n"
                )
                
                if pending_count > 0:
                    status_message += "**Pending Reminders:**\n"
                    for reminder_id, reminder_info in self.reminder_system.pending_reminders.items():
                        reminder_name = reminder_info.get('reminder_name', 'unknown')
                        timestamp = reminder_info.get('timestamp')
                        if timestamp:
                            time_since = (current_time - timestamp).total_seconds() / 60
                            schedule_label = reminder_info.get('schedule_label', 'unknown')
                            status_message += f"• {reminder_name} - {schedule_label} ({int(time_since)} minutes ago)\n"
                
                await interaction.response.send_message(status_message)
                
                # Enhanced logging with DM context information
                context_info = get_context_info(interaction)
                logger.info(f"SLASH_COMMAND: /reminder status executed by {interaction.user} ({interaction.user.id}), Context: {context_info}")
                
            except Exception as e:
                logger.error(f"Error in /reminder status: {e}", exc_info=True)
                await interaction.response.send_message(f"❌ Error getting status: {str(e)}")
        
        @app_commands.command(name="list", description="List all configured reminders")
        async def list_reminders(self, interaction: discord.Interaction):
            """List all configured reminders - slash command version of !listreminders"""
            try:
                # Check DM permissions (list is read-only, but still enforce owner-only in DMs)
                if is_dm_context(interaction) and not is_owner_in_context(interaction, interaction.client):
                    context_info = get_context_info(interaction)
                    error_msg = get_dm_error_message("/reminder list", False)
                    await interaction.response.send_message(error_msg, ephemeral=True)
                    logger.warning(f"Permission denied for /reminder list - User: {interaction.user.id}, Context: {context_info}")
                    return
                
                if len(self.reminder_system.reminders) == 0:
                    await interaction.response.send_message("📋 No reminders configured.")
                    return
                
                message = f"📋 **Configured Reminders** ({len(self.reminder_system.reminders)} total):\n\n"
                
                for reminder in self.reminder_system.reminders:
                    message += f"**{reminder['name']}**\n"
                    message += f"  📅 Schedules:\n"
                    for schedule in reminder['schedules']:
                        message += f"    • {schedule['label']}: {schedule['hour']:02d}:{schedule['minute']:02d}\n"
                    message += f"  👤 Target: <@{reminder['target_user_id']}>\n"
                    message += f"  🚨 Escalation: <@{reminder['escalation_user_id']}>\n"
                    message += f"  ⏱️ Timeout: {reminder['timeout_minutes']} minutes\n\n"
                
                await interaction.response.send_message(message)
                
                # Enhanced logging with DM context information
                context_info = get_context_info(interaction)
                logger.info(f"SLASH_COMMAND: /reminder list executed by {interaction.user} ({interaction.user.id}), Context: {context_info}")
                
            except Exception as e:
                logger.error(f"Error in /reminder list: {e}", exc_info=True)
                await interaction.response.send_message(f"❌ Error listing reminders: {str(e)}")
        
        @app_commands.command(name="reload", description="Reload reminder configuration")
        async def reload(self, interaction: discord.Interaction):
            """Reload reminder configuration - slash command version of !reloadreminders"""
            try:
                # Check if user is bot owner (DM-aware)
                if not is_owner_in_context(interaction, interaction.client):
                    context_info = get_context_info(interaction)
                    error_msg = get_dm_error_message("/reminder reload", False)
                    await interaction.response.send_message(error_msg, ephemeral=True)
                    logger.warning(f"Permission denied for /reminder reload - User: {interaction.user.id}, Context: {context_info}")
                    return
                
                success, message = self.reminder_system.reload_config()
                await interaction.response.send_message(message)
                logger.info(f"SLASH_COMMAND: /reminder reload executed by {interaction.user} ({interaction.user.id})")
                
            except Exception as e:
                logger.error(f"Error in /reminder reload: {e}", exc_info=True)
                await interaction.response.send_message(f"❌ Error reloading configuration: {str(e)}")
        
        @app_commands.command(name="timeout", description="Set timeout for a reminder")
        @app_commands.describe(
            reminder="Name of the reminder to modify",
            minutes="Timeout in minutes (must be at least 1)"
        )
        async def timeout(self, interaction: discord.Interaction, reminder: str, minutes: int):
            """Set reminder timeout - slash command version of !settimeout"""
            try:
                # Check if user is bot owner (DM-aware)
                if not is_owner_in_context(interaction, interaction.client):
                    context_info = get_context_info(interaction)
                    error_msg = get_dm_error_message("/reminder timeout", False)
                    await interaction.response.send_message(error_msg, ephemeral=True)
                    logger.warning(f"Permission denied for /reminder timeout - User: {interaction.user.id}, Context: {context_info}")
                    return
                
                # Validate minutes
                if minutes < 1:
                    await interaction.response.send_message("❌ Timeout must be at least 1 minute.")
                    return
                
                # Find the reminder
                reminder_obj = next((r for r in self.reminder_system.reminders if r['name'] == reminder), None)
                if not reminder_obj:
                    await interaction.response.send_message(f"❌ Reminder '{reminder}' not found in configuration.")
                    return
                
                # Update timeout (in memory only)
                reminder_obj['timeout_minutes'] = minutes
                await interaction.response.send_message(
                    f"✅ Timeout for **{reminder}** set to {minutes} minutes.\n"
                    f"⚠️ *Note: This change is in-memory only. Edit `reminder_config.py` to persist changes.*"
                )
                logger.info(f"SLASH_COMMAND: /reminder timeout executed by {interaction.user} ({interaction.user.id}) - reminder: {reminder}, timeout: {minutes} minutes")
                
            except Exception as e:
                logger.error(f"Error in /reminder timeout: {e}", exc_info=True)
                await interaction.response.send_message(f"❌ Error setting timeout: {str(e)}")
        
        @timeout.autocomplete('reminder')
        async def timeout_reminder_autocomplete(self, interaction: discord.Interaction, current: str):
            return await reminder_name_autocomplete(interaction, current)
        
        @app_commands.command(name="help", description="Show help for reminder commands")
        async def help(self, interaction: discord.Interaction):
            """Show help for all reminder slash commands"""
            try:
                # Check DM permissions (help is informational, but still enforce owner-only in DMs for consistency)
                if is_dm_context(interaction) and not is_owner_in_context(interaction, interaction.client):
                    context_info = get_context_info(interaction)
                    error_msg = get_dm_error_message("/reminder help", False)
                    await interaction.response.send_message(error_msg, ephemeral=True)
                    logger.warning(f"Permission denied for /reminder help - User: {interaction.user.id}, Context: {context_info}")
                    return
                
                help_message = (
                    "📋 **Reminder System Commands**\n\n"
                    
                    "**🧪 Testing & Status**\n"
                    "`/reminder test` - Test a reminder delivery\n"
                    "`/reminder status` - Check reminder system status\n"
                    "`/reminder list` - List all configured reminders\n\n"
                    
                    "**⚙️ Configuration**\n"
                    "`/reminder reload` - Reload reminder configuration\n"
                    "`/reminder timeout` - Set timeout for a reminder\n\n"
                    
                    "**💡 Tips**\n"
                    "• All commands support autocomplete - start typing to see suggestions\n"
                    "• Use `/dog help` for dog-specific reminder commands\n"
                    "• Configuration changes are in-memory only - edit `reminder_config.py` to persist\n\n"
                    
                    "**📚 Legacy Commands**\n"
                    "Old `!` commands still work but slash commands are recommended for better UX"
                )
                
                await interaction.response.send_message(help_message, ephemeral=True)
                
                # Enhanced logging with DM context information
                context_info = get_context_info(interaction)
                logger.info(f"SLASH_COMMAND: /reminder help executed by {interaction.user} ({interaction.user.id}), Context: {context_info}")
                
            except Exception as e:
                logger.error(f"Error in /reminder help: {e}", exc_info=True)
                await interaction.response.send_message(f"❌ Error showing help: {str(e)}")
        
    
    class DogGroup(app_commands.Group):
        """Legacy dog reminder slash commands"""
        
        def __init__(self, reminder_system):
            super().__init__(name="dog", description="Dog reminder commands (legacy compatibility)")
            self.reminder_system = reminder_system
        
        @app_commands.command(name="test", description="Test dog reminder")
        @app_commands.describe(time="Time of day (morning, noon, evening)")
        async def test(self, interaction: discord.Interaction, time: str = "morning"):
            """Test dog reminder - slash command version of !testreminderdog"""
            try:
                # Check DM permissions first (before deferring)
                if is_dm_context(interaction) and not is_owner_in_context(interaction, interaction.client):
                    context_info = get_context_info(interaction)
                    error_msg = get_dm_error_message("/dog test", False)
                    await interaction.response.send_message(error_msg, ephemeral=True)
                    logger.warning(f"Permission denied for /dog test - User: {interaction.user.id}, Context: {context_info}")
                    return
                
                await interaction.response.defer()
                
                # Find dog_walking reminder
                dog_reminder = next((r for r in self.reminder_system.reminders if r['name'] == 'dog_walking'), None)
                if not dog_reminder:
                    await interaction.followup.send("❌ Dog walking reminder not found in configuration.")
                    return
                
                # Find the schedule
                schedule = next((s for s in dog_reminder['schedules'] if s['label'] == time), None)
                if not schedule:
                    available = ", ".join([s['label'] for s in dog_reminder['schedules']])
                    await interaction.followup.send(f"❌ Time '{time}' not found. Available times: {available}")
                    return
                
                await self.reminder_system.send_reminder(dog_reminder, schedule)
                await interaction.followup.send(f"✅ Test {time} dog reminder sent!")
                
                # Enhanced logging with DM context information
                context_info = get_context_info(interaction)
                logger.info(f"SLASH_COMMAND: /dog test executed by {interaction.user} ({interaction.user.id}) - time: {time}, Context: {context_info}")
                
            except Exception as e:
                logger.error(f"Error in /dog test: {e}", exc_info=True)
                await interaction.followup.send(f"❌ Error testing dog reminder: {str(e)}")
        
        @test.autocomplete('time')
        async def test_time_autocomplete(self, interaction: discord.Interaction, current: str):
            try:
                # Log context for debugging DM functionality
                context_info = get_context_info(interaction)
                logger.debug(f"Dog test autocomplete called - Context: {context_info}")
                
                dog_reminder = next((r for r in reminder_config.REMINDERS if r['name'] == 'dog_walking'), None)
                if not dog_reminder:
                    return []
                
                choices = []
                for schedule in dog_reminder['schedules']:
                    label = schedule['label']
                    if current.lower() in label.lower():
                        # Enhanced: Include time in display for clarity in DMs
                        display_name = f"{label} ({schedule['hour']:02d}:{schedule['minute']:02d})"
                        choices.append(app_commands.Choice(name=display_name, value=label))
                
                # DM context: Add DM indicator
                if is_dm_context(interaction) and choices and len(choices) < 25:
                    choices.append(app_commands.Choice(name="🐕 DM dog commands ready", value="dm_dog"))
                
                logger.debug(f"Returning {len(choices[:25])} dog schedule autocomplete choices for DM context: {is_dm_context(interaction)}")
                return choices[:25]
            except Exception as e:
                return handle_autocomplete_error(interaction, e, "dog_test_autocomplete")
        
        @app_commands.command(name="status", description="Check dog reminder status")
        async def status(self, interaction: discord.Interaction):
            """Show dog reminder status - slash command version of !dogstatus"""
            try:
                # Check DM permissions (status is read-only, but still enforce owner-only in DMs)
                if is_dm_context(interaction) and not is_owner_in_context(interaction, interaction.client):
                    context_info = get_context_info(interaction)
                    error_msg = get_dm_error_message("/dog status", False)
                    await interaction.response.send_message(error_msg, ephemeral=True)
                    logger.warning(f"Permission denied for /dog status - User: {interaction.user.id}, Context: {context_info}")
                    return
                
                dog_reminder = next((r for r in self.reminder_system.reminders if r['name'] == 'dog_walking'), None)
                if not dog_reminder:
                    await interaction.response.send_message("❌ Dog walking reminder not found in configuration.")
                    return
                
                current_time = datetime.datetime.now(self.reminder_system.timezone)
                status_message = f"🐕 **Dog Reminder Status**\n"
                status_message += f"🕐 Current time: {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')}\n"
                status_message += f"📍 Timezone: {self.reminder_system.timezone}\n\n"
                
                status_message += f"📅 **Scheduled Times:**\n"
                for schedule in dog_reminder['schedules']:
                    status_message += f"• {schedule['label']}: {schedule['hour']:02d}:{schedule['minute']:02d}\n"
                
                status_message += f"\n👤 Target user: <@{dog_reminder['target_user_id']}>\n"
                status_message += f"🚨 Escalation user: <@{dog_reminder['escalation_user_id']}>\n"
                status_message += f"⏱️ Timeout: {dog_reminder['timeout_minutes']} minutes\n"
                
                # Check for pending dog reminders
                dog_pending = {k: v for k, v in self.reminder_system.pending_reminders.items() 
                              if v.get('reminder_name') == 'dog_walking'}
                if dog_pending:
                    status_message += f"\n⏰ **Pending:** {len(dog_pending)} reminder(s)\n"
                    for reminder_id, reminder_info in dog_pending.items():
                        timestamp = reminder_info.get('timestamp')
                        if timestamp:
                            time_since = (current_time - timestamp).total_seconds() / 60
                            schedule_label = reminder_info.get('schedule_label', 'unknown')
                            status_message += f"• {schedule_label} ({int(time_since)} minutes ago)\n"
                
                await interaction.response.send_message(status_message)
                
                # Enhanced logging with DM context information
                context_info = get_context_info(interaction)
                logger.info(f"SLASH_COMMAND: /dog status executed by {interaction.user} ({interaction.user.id}), Context: {context_info}")
                
            except Exception as e:
                logger.error(f"Error in /dog status: {e}", exc_info=True)
                await interaction.response.send_message(f"❌ Error getting dog status: {str(e)}")
        
        @app_commands.command(name="timezone", description="View or set timezone")
        @app_commands.describe(zone="Timezone name (e.g., Europe/Paris, America/New_York)")
        async def timezone(self, interaction: discord.Interaction, zone: str = None):
            """View or set timezone - slash command version of !dogtimezone"""
            try:
                if zone is None:
                    # Just show current timezone
                    await interaction.response.send_message(f"🌍 Current timezone: **{self.reminder_system.timezone}**")
                    return
                
                # Check if user is bot owner for setting timezone (DM-aware)
                if not is_owner_in_context(interaction, interaction.client):
                    context_info = get_context_info(interaction)
                    error_msg = get_dm_error_message("/dog timezone", False)
                    await interaction.response.send_message(error_msg, ephemeral=True)
                    logger.warning(f"Permission denied for /dog timezone - User: {interaction.user.id}, Context: {context_info}")
                    return
                
                # Try to set the timezone
                try:
                    new_timezone = pytz.timezone(zone)
                    self.reminder_system.timezone = new_timezone
                    
                    # Update in config (in memory only)
                    reminder_config.TIMEZONE = zone
                    
                    await interaction.response.send_message(
                        f"✅ Timezone set to: **{new_timezone}**\n"
                        f"⚠️ *Note: This change is in-memory only. Edit `reminder_config.py` to persist changes.*"
                    )
                    logger.info(f"SLASH_COMMAND: /dog timezone executed by {interaction.user} ({interaction.user.id}) - zone: {zone}")
                    
                except pytz.exceptions.UnknownTimeZoneError:
                    await interaction.response.send_message(f"❌ Unknown timezone: {zone}. Use a valid timezone like 'Europe/Paris' or 'America/New_York'.")
                
            except Exception as e:
                logger.error(f"Error in /dog timezone: {e}", exc_info=True)
                await interaction.response.send_message(f"❌ Error with timezone: {str(e)}")
        
        @timezone.autocomplete('zone')
        async def timezone_zone_autocomplete(self, interaction: discord.Interaction, current: str):
            return await timezone_autocomplete(interaction, current)
        
        @app_commands.command(name="set-reminder", description="Set dog reminder user")
        @app_commands.describe(user="User who should receive dog reminders")
        async def set_reminder(self, interaction: discord.Interaction, user: discord.Member):
            """Set dog reminder user - slash command version of !setdogreminder"""
            try:
                # Check if user is bot owner (DM-aware)
                if not is_owner_in_context(interaction, interaction.client):
                    context_info = get_context_info(interaction)
                    error_msg = get_dm_error_message("/dog set-reminder", False)
                    await interaction.response.send_message(error_msg, ephemeral=True)
                    logger.warning(f"Permission denied for /dog set-reminder - User: {interaction.user.id}, Context: {context_info}")
                    return
                
                # Find dog_walking reminder
                dog_reminder = next((r for r in self.reminder_system.reminders if r['name'] == 'dog_walking'), None)
                if not dog_reminder:
                    await interaction.response.send_message("❌ Dog walking reminder not found in configuration.")
                    return
                
                # Update target user (in memory only)
                dog_reminder['target_user_id'] = user.id
                await interaction.response.send_message(
                    f"✅ Dog reminder target set to: {user.mention}\n"
                    f"⚠️ *Note: This change is in-memory only. Edit `reminder_config.py` to persist changes.*"
                )
                logger.info(f"SLASH_COMMAND: /dog set-reminder executed by {interaction.user} ({interaction.user.id}) - user: {user.id}")
                
            except Exception as e:
                logger.error(f"Error in /dog set-reminder: {e}", exc_info=True)
                await interaction.response.send_message(f"❌ Error setting reminder user: {str(e)}")
        
        @app_commands.command(name="set-owner", description="Set dog owner (escalation user)")
        @app_commands.describe(user="User who should receive escalation notifications")
        async def set_owner(self, interaction: discord.Interaction, user: discord.Member):
            """Set dog owner - slash command version of !setdogowner"""
            try:
                # Check if user is bot owner (DM-aware)
                if not is_owner_in_context(interaction, interaction.client):
                    context_info = get_context_info(interaction)
                    error_msg = get_dm_error_message("/dog set-owner", False)
                    await interaction.response.send_message(error_msg, ephemeral=True)
                    logger.warning(f"Permission denied for /dog set-owner - User: {interaction.user.id}, Context: {context_info}")
                    return
                
                # Find dog_walking reminder
                dog_reminder = next((r for r in self.reminder_system.reminders if r['name'] == 'dog_walking'), None)
                if not dog_reminder:
                    await interaction.response.send_message("❌ Dog walking reminder not found in configuration.")
                    return
                
                # Update escalation user (in memory only)
                dog_reminder['escalation_user_id'] = user.id
                await interaction.response.send_message(
                    f"✅ Dog owner (escalation user) set to: {user.mention}\n"
                    f"⚠️ *Note: This change is in-memory only. Edit `reminder_config.py` to persist changes.*"
                )
                logger.info(f"SLASH_COMMAND: /dog set-owner executed by {interaction.user} ({interaction.user.id}) - user: {user.id}")
                
            except Exception as e:
                logger.error(f"Error in /dog set-owner: {e}", exc_info=True)
                await interaction.response.send_message(f"❌ Error setting owner: {str(e)}")
        
        @app_commands.command(name="set-time", description="Set reminder time")
        @app_commands.describe(
            type="Type of reminder time (morning, noon, evening)",
            hour="Hour (0-23)",
            minute="Minute (0-59, default: 0)"
        )
        async def set_time(self, interaction: discord.Interaction, type: str, hour: int, minute: int = 0):
            """Set reminder time - slash command version of !setremindertime"""
            try:
                # Check if user is bot owner (DM-aware)
                if not is_owner_in_context(interaction, interaction.client):
                    context_info = get_context_info(interaction)
                    error_msg = get_dm_error_message("/dog set-time", False)
                    await interaction.response.send_message(error_msg, ephemeral=True)
                    logger.warning(f"Permission denied for /dog set-time - User: {interaction.user.id}, Context: {context_info}")
                    return
                
                # Validate hour and minute
                if not (0 <= hour <= 23):
                    await interaction.response.send_message("❌ Hour must be between 0 and 23.")
                    return
                if not (0 <= minute <= 59):
                    await interaction.response.send_message("❌ Minute must be between 0 and 59.")
                    return
                
                # Find dog_walking reminder
                dog_reminder = next((r for r in self.reminder_system.reminders if r['name'] == 'dog_walking'), None)
                if not dog_reminder:
                    await interaction.response.send_message("❌ Dog walking reminder not found in configuration.")
                    return
                
                # Find and update the schedule
                schedule = next((s for s in dog_reminder['schedules'] if s['label'] == type), None)
                if not schedule:
                    available = ", ".join([s['label'] for s in dog_reminder['schedules']])
                    await interaction.response.send_message(f"❌ Reminder type '{type}' not found. Available types: {available}")
                    return
                
                # Update time (in memory only)
                schedule['hour'] = hour
                schedule['minute'] = minute
                await interaction.response.send_message(
                    f"✅ {type.capitalize()} dog reminder time set to: **{hour:02d}:{minute:02d}**\n"
                    f"⚠️ *Note: This change is in-memory only. Edit `reminder_config.py` to persist changes.*"
                )
                logger.info(f"SLASH_COMMAND: /dog set-time executed by {interaction.user} ({interaction.user.id}) - type: {type}, time: {hour:02d}:{minute:02d}")
                
            except Exception as e:
                logger.error(f"Error in /dog set-time: {e}", exc_info=True)
                await interaction.response.send_message(f"❌ Error setting time: {str(e)}")
        
        @set_time.autocomplete('type')
        async def set_time_type_autocomplete(self, interaction: discord.Interaction, current: str):
            try:
                dog_reminder = next((r for r in reminder_config.REMINDERS if r['name'] == 'dog_walking'), None)
                if not dog_reminder:
                    return []
                
                choices = []
                for schedule in dog_reminder['schedules']:
                    label = schedule['label']
                    if current.lower() in label.lower():
                        choices.append(app_commands.Choice(name=label, value=label))
                
                return choices[:25]
            except Exception as e:
                logger.error(f"Error in set-time type autocomplete: {e}")
                return []
        
        @app_commands.command(name="help", description="Show help for dog commands")
        async def help(self, interaction: discord.Interaction):
            """Show help for all dog slash commands"""
            try:
                # Check DM permissions (help is informational, but still enforce owner-only in DMs for consistency)
                if is_dm_context(interaction) and not is_owner_in_context(interaction, interaction.client):
                    context_info = get_context_info(interaction)
                    error_msg = get_dm_error_message("/dog help", False)
                    await interaction.response.send_message(error_msg, ephemeral=True)
                    logger.warning(f"Permission denied for /dog help - User: {interaction.user.id}, Context: {context_info}")
                    return
                
                help_message = (
                    "🐕 **Dog Reminder Commands**\n\n"
                    
                    "**🧪 Testing & Status**\n"
                    "`/dog test` - Test dog reminder at specific time\n"
                    "`/dog status` - Check dog reminder status\n"
                    "`/dog timezone` - View or set timezone\n\n"
                    
                    "**⚙️ Configuration (Owner Only)**\n"
                    "`/dog set-reminder` - Set user who receives dog reminders\n"
                    "`/dog set-owner` - Set dog owner (escalation user)\n"
                    "`/dog set-time` - Set reminder times (morning/noon/evening)\n\n"
                    
                    "**💡 Tips**\n"
                    "• All commands support autocomplete - start typing to see suggestions\n"
                    "• Use `/reminder help` for general reminder commands\n"
                    "• Configuration commands require bot owner permissions\n"
                    "• Configuration changes are in-memory only - edit `reminder_config.py` to persist\n\n"
                    
                    "**📚 Legacy Commands**\n"
                    "Old `!` commands still work but slash commands are recommended for better UX"
                )
                
                await interaction.response.send_message(help_message, ephemeral=True)
                
                # Enhanced logging with DM context information
                context_info = get_context_info(interaction)
                logger.info(f"SLASH_COMMAND: /dog help executed by {interaction.user} ({interaction.user.id}), Context: {context_info}")
                
            except Exception as e:
                logger.error(f"Error in /dog help: {e}", exc_info=True)
                await interaction.response.send_message(f"❌ Error showing help: {str(e)}")
        
    
    # Create command group instances
    reminder_group = ReminderGroup(reminder_system)
    dog_group = DogGroup(reminder_system)
    
    # Utility function to sync slash commands
    def sync_slash_commands():
        """Utility function to register slash commands with Discord"""
        try:
            bot.tree.add_command(reminder_group)
            bot.tree.add_command(dog_group)
            logger.info("Slash command groups added to command tree")
            return True
        except Exception as e:
            logger.error(f"Failed to add slash command groups: {e}")
            return False
    
    # Register slash commands
    if sync_slash_commands():
        logger.info("Slash command groups registered successfully")
    else:
        logger.error("Failed to register slash command groups")
    
    return reminder_system