"""
Webhook Handler Module for BeanBot

This module handles webhook notifications when the bot is mentioned in Discord.
It sends POST requests to a configured n8n endpoint with message context data.
"""

import logging
import os
import asyncio
import json
from typing import Optional, Dict, Any
import discord
import aiohttp


class WebhookHandler:
    """
    Handles webhook notifications for bot mentions.
    
    This class is responsible for detecting when the bot is mentioned,
    constructing appropriate payloads, and sending webhook notifications
    to external services like n8n.
    """
    
    def __init__(self, webhook_url: Optional[str] = None):
        """
        Initialize the webhook handler.
        
        Args:
            webhook_url (Optional[str]): The webhook URL to send notifications to.
                                       If None, will attempt to load from environment.
        """
        self.logger = logging.getLogger(__name__)
        
        # Load webhook URL from environment if not provided
        if webhook_url is None:
            webhook_url = os.getenv('WEBHOOK_URL')
        
        self.webhook_url = webhook_url
        
        # Validate webhook URL configuration
        if self.webhook_url:
            if not self._is_valid_webhook_url(self.webhook_url):
                self.logger.error(f"Invalid webhook URL format: {self.webhook_url}")
                self.webhook_url = None
            else:
                self.logger.info(f"WebhookHandler initialized with URL: {self._mask_url(self.webhook_url)}")
        else:
            self.logger.warning("No WEBHOOK_URL configured - webhook notifications will be disabled")
            
    def _is_valid_webhook_url(self, url: str) -> bool:
        """
        Validate webhook URL format.
        
        Args:
            url (str): URL to validate
            
        Returns:
            bool: True if URL format is valid, False otherwise
        """
        return url.startswith(('http://', 'https://')) and len(url.strip()) > 10
    
    def _mask_url(self, url: str) -> str:
        """
        Mask sensitive parts of URL for logging.
        
        Args:
            url (str): URL to mask
            
        Returns:
            str: Masked URL for safe logging
        """
        try:
            parts = url.split('/')
            if len(parts) >= 3:
                return f"{parts[0]}//{parts[2]}/***"
            return "***"
        except Exception:
            return "***"
        
    async def send_mention_notification(self, message: discord.Message) -> bool:
        """
        Send a webhook notification for a bot mention.
        
        Args:
            message (discord.Message): The Discord message containing the mention
            
        Returns:
            bool: True if notification was sent successfully, False otherwise
        """
        self.logger.info(f"Processing mention notification for message {message.id}")
        
        try:
            payload = self.build_payload(message)
            return await self.send_webhook_with_retry(payload)
        except Exception as e:
            self.logger.error(f"Failed to send mention notification: {e}", exc_info=True)
            # Return False but don't raise - graceful degradation
            return False
    
    def build_payload(self, message: discord.Message) -> Dict[str, Any]:
        """
        Build the JSON payload for webhook notification.
        
        Args:
            message (discord.Message): The Discord message to build payload from
            
        Returns:
            Dict[str, Any]: JSON-serializable payload dictionary
        """
        try:
            self.logger.debug(f"Building payload for message {message.id}")
            
            # Determine if this is a DM or guild message with error handling
            try:
                # Primary check: isinstance for DMChannel
                is_dm = isinstance(message.channel, discord.DMChannel)
                
                # Secondary check: guild is None (more reliable fallback)
                if not is_dm:
                    is_dm = message.guild is None
                    
                # Tertiary check: channel type string contains 'private'
                if not is_dm and hasattr(message.channel, 'type'):
                    is_dm = 'private' in str(message.channel.type).lower()
                    
            except Exception:
                # Ultimate fallback: check if guild is None
                is_dm = message.guild is None
                
            self.logger.debug(f"DM detection result: {is_dm} (guild: {message.guild is None if hasattr(message, 'guild') else 'unknown'})")
            
            # Build user data
            user_data = {
                "id": str(message.author.id),
                "username": message.author.name,
                "display_name": message.author.display_name
            }
        
            # Add roles only for guild messages (privacy for DMs)
            if not is_dm:
                try:
                    if hasattr(message.author, 'roles') and message.author.roles:
                        user_data["roles"] = [
                            role.name for role in message.author.roles 
                            if role.name != "@everyone" and hasattr(role, 'name')
                        ]
                    else:
                        self.logger.warning(f"No roles available for user {message.author.id} in guild")
                        user_data["roles"] = []
                except Exception as e:
                    self.logger.error(f"Failed to fetch user roles for {message.author.id}: {e}")
                    user_data["roles"] = []
            else:
                user_data["roles"] = []
            
            # Build message data
            message_data = {
                "content": message.content,
                "id": str(message.id),
                "timestamp": message.created_at.isoformat(),
                "attachments": [attachment.url for attachment in message.attachments],
                "embeds": [embed.to_dict() for embed in message.embeds]
            }
            
            # Build context data
            context_data = {
                "type": "dm" if is_dm else "guild"
            }
        
            # Guild context (null for DMs for privacy)
            if is_dm:
                context_data["guild"] = None
            else:
                try:
                    if message.guild and hasattr(message.guild, 'id') and hasattr(message.guild, 'name'):
                        context_data["guild"] = {
                            "id": str(message.guild.id),
                            "name": str(message.guild.name)
                        }
                    else:
                        self.logger.warning("Guild object missing or incomplete for guild message")
                        context_data["guild"] = {
                            "id": "unknown_guild",
                            "name": "Unknown Guild"
                        }
                except Exception as e:
                    self.logger.error(f"Failed to extract guild information: {e}")
                    context_data["guild"] = {
                        "id": "error_guild",
                        "name": "Guild Error"
                    }
        
            # Channel context with error handling
            try:
                context_data["channel"] = {
                    "id": str(message.channel.id) if hasattr(message.channel, 'id') else "unknown_channel",
                    "name": getattr(message.channel, 'name', 'dm' if is_dm else 'unknown'),
                    "type": str(getattr(message.channel, 'type', 'unknown'))
                }
            except Exception as e:
                self.logger.error(f"Failed to extract channel information: {e}")
                context_data["channel"] = {
                    "id": "error_channel",
                    "name": "dm" if is_dm else "error",
                    "type": "unknown"
                }
            
            # Bot metadata - get bot ID from guild context or fallback
            try:
                if not is_dm and hasattr(message.guild, 'me') and message.guild.me:
                    bot_id = str(message.guild.me.id)
                elif not is_dm and hasattr(message.guild, 'get_member'):
                    # Alternative: try to get bot member if direct access fails
                    bot_id = "guild_bot_member"  # Placeholder for now
                else:
                    bot_id = "bot_id_placeholder"  # DM or fallback case
            except Exception:
                bot_id = "bot_id_fallback"
                
            bot_data = {
                "id": bot_id,
                "mention_detected": True  # This method only called when mention detected
            }
            
            # Construct complete payload
            payload = {
                "user": user_data,
                "message": message_data,
                "context": context_data,
                "bot": bot_data
            }
            
            self.logger.debug(f"Built payload for {context_data['type']} message with {len(user_data.get('roles', []))} user roles")
        
            # Validate payload before returning
            validation_result = self._validate_payload(payload)
            if not validation_result["valid"]:
                self.logger.warning(f"Payload validation issues: {validation_result['issues']}")
            
            return payload
            
        except Exception as e:
            # If payload construction fails completely, return a minimal error payload
            from datetime import datetime
            self.logger.error(f"Critical error building payload for message {getattr(message, 'id', 'unknown')}: {e}")
            return {
                "error": "payload_construction_failed",
                "message_id": str(getattr(message, 'id', 'unknown')),
                "timestamp": datetime.now().isoformat(),
                "user": {
                    "id": str(getattr(message.author, 'id', 'unknown')),
                    "username": getattr(message.author, 'name', 'unknown'),
                    "display_name": getattr(message.author, 'display_name', 'unknown'),
                    "roles": []
                },
                "message": {
                    "content": str(getattr(message, 'content', '')),
                    "id": str(getattr(message, 'id', 'unknown')),
                    "timestamp": getattr(message, 'created_at', datetime.now()).isoformat(),
                    "attachments": [],
                    "embeds": []
                },
                "context": {
                    "type": "error",
                    "guild": None,
                    "channel": {
                        "id": "error",
                        "name": "error", 
                        "type": "error"
                    }
                },
                "bot": {
                    "id": "error",
                    "mention_detected": True
                }
            }
    
    def _validate_payload(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate webhook payload structure and completeness.
        
        Args:
            payload (Dict[str, Any]): The payload to validate
            
        Returns:
            Dict[str, Any]: Validation result with 'valid' bool and 'issues' list
        """
        issues = []
        
        # Check required top-level keys
        required_keys = ["user", "message", "context", "bot"]
        for key in required_keys:
            if key not in payload:
                issues.append(f"Missing required key: {key}")
        
        # Validate user data
        if "user" in payload:
            user_data = payload["user"]
            user_required = ["id", "username", "display_name"]
            for key in user_required:
                if key not in user_data or not user_data[key]:
                    issues.append(f"Missing or empty user.{key}")
            
            # Check roles array exists
            if "roles" not in user_data:
                issues.append("Missing user.roles array")
        
        # Validate message data
        if "message" in payload:
            message_data = payload["message"]
            message_required = ["id", "content", "timestamp"]
            for key in message_required:
                if key not in message_data:
                    issues.append(f"Missing message.{key}")
        
        # Validate context data
        if "context" in payload:
            context_data = payload["context"]
            
            if "type" not in context_data:
                issues.append("Missing context.type")
            
            # Guild-specific validation
            if context_data.get("type") == "guild":
                if context_data.get("guild") is None:
                    issues.append("Guild context missing for guild message")
                else:
                    guild_data = context_data["guild"]
                    if "id" not in guild_data or "name" not in guild_data:
                        issues.append("Incomplete guild data (missing id or name)")
                
                # Channel validation for guild messages
                if "channel" in context_data:
                    channel_data = context_data["channel"]
                    if "id" not in channel_data or "name" not in channel_data:
                        issues.append("Incomplete channel data for guild message")
            
            # DM-specific validation
            elif context_data.get("type") == "dm":
                if context_data.get("guild") is not None:
                    issues.append("Guild data should be null for DM messages")
        
        # Validate bot data
        if "bot" in payload:
            bot_data = payload["bot"]
            if "id" not in bot_data or "mention_detected" not in bot_data:
                issues.append("Incomplete bot data")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues
        }
    
    async def send_webhook(self, payload: Dict[str, Any]) -> bool:
        """
        Send the webhook HTTP POST request.
        
        Args:
            payload (Dict[str, Any]): The JSON payload to send
            
        Returns:
            bool: True if webhook was sent successfully, False otherwise
        """
        self.logger.debug(f"Sending webhook with payload keys: {list(payload.keys())}")
        
        if not self.webhook_url:
            self.logger.warning("No webhook URL configured, skipping webhook send")
            return False
        
        try:
            # Prepare headers for JSON content
            headers = {
                "Content-Type": "application/json",
                "User-Agent": "BeanBot Webhook Handler (Discord Bot)"
            }
            
            # Create timeout configuration (5 seconds as specified)
            timeout = aiohttp.ClientTimeout(total=5.0)
            
            # Send the webhook POST request
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    self.webhook_url, 
                    json=payload, 
                    headers=headers
                ) as response:
                    
                    if response.status == 200:
                        self.logger.info(f"Webhook sent successfully to {self.webhook_url}")
                        return True
                    else:
                        self.logger.error(
                            f"Webhook failed with status {response.status}: "
                            f"{await response.text()}"
                        )
                        return False
                        
        except asyncio.TimeoutError:
            self.logger.error(f"Webhook request timed out after 5 seconds")
            return False
        except aiohttp.ClientError as e:
            self.logger.error(f"HTTP client error during webhook send: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error during webhook send: {e}")
            return False
    
    def is_bot_mentioned(self, message: discord.Message, bot_user: discord.User) -> bool:
        """
        Check if the bot is mentioned in the given message.
        
        Args:
            message (discord.Message): The message to check for mentions
            bot_user (discord.User): The bot's user object
            
        Returns:
            bool: True if bot is mentioned, False otherwise
        """
        self.logger.debug(f"Checking mention in message {message.id} from {message.author.name}")
        
        # Exclude self-mentions (bot mentioning itself)
        if message.author.id == bot_user.id:
            self.logger.debug("Ignoring self-mention from bot")
            return False
        
        # Use Discord.py's built-in mention detection
        # This handles both direct @mentions and reply mentions
        is_mentioned = bot_user.mentioned_in(message)
        
        if is_mentioned:
            self.logger.info(f"Bot mentioned in message {message.id} by {message.author.name}")
        else:
            self.logger.debug(f"No mention detected in message {message.id}")
            
        return is_mentioned
    
    async def send_webhook_with_retry(self, payload: Dict[str, Any], max_retries: int = 3) -> bool:
        """
        Send webhook with retry logic and exponential backoff.
        
        Args:
            payload (Dict[str, Any]): The JSON payload to send
            max_retries (int): Maximum number of retry attempts (default: 3)
            
        Returns:
            bool: True if webhook was sent successfully, False otherwise
        """
        for attempt in range(max_retries + 1):  # +1 for initial attempt
            try:
                success = await self.send_webhook(payload)
                if success:
                    if attempt > 0:
                        self.logger.info(f"Webhook sent successfully on attempt {attempt + 1}")
                    return True
                    
                # If not successful and not the last attempt, wait before retry
                if attempt < max_retries:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    self.logger.warning(f"Webhook attempt {attempt + 1} failed, retrying in {wait_time}s")
                    await asyncio.sleep(wait_time)
                    
            except (asyncio.TimeoutError, aiohttp.ClientError) as e:
                if attempt < max_retries:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    self.logger.warning(
                        f"Network error on attempt {attempt + 1}: {e}, retrying in {wait_time}s"
                    )
                    await asyncio.sleep(wait_time)
                else:
                    self.logger.error(f"All {max_retries + 1} webhook attempts failed: {e}")
                    
            except Exception as e:
                # For non-network errors, don't retry
                self.logger.error(f"Non-retryable error during webhook send: {e}")
                return False
        
        self.logger.error(f"Failed to send webhook after {max_retries + 1} attempts")
        return False
    
    def _check_dm_permissions(self, message: discord.Message, bot) -> bool:
        """
        Check if DM webhook notifications are allowed for this user.
        
        Args:
            message (discord.Message): The message to check
            bot: The bot instance
            
        Returns:
            bool: True if webhook notification is allowed, False otherwise
        """
        try:
            # For guild messages, always allow
            if message.guild is not None:
                return True
            
            # For DM messages, only allow from bot owner
            if hasattr(bot, 'owner_id') and bot.owner_id:
                is_owner = message.author.id == bot.owner_id
                
                if not is_owner:
                    self.logger.warning(
                        f"DM webhook blocked: user {message.author.id} ({message.author.name}) "
                        f"is not bot owner (owner: {bot.owner_id})"
                    )
                
                return is_owner
            else:
                self.logger.error("Bot owner_id not available for DM permission check")
                return False
                
        except Exception as e:
            self.logger.error(f"Error checking DM permissions: {e}")
            return False