#!/usr/bin/env python3
"""
Test script for guild mention notifications.

This script tests the webhook functionality when the bot is mentioned in guild channels.
It creates mock Discord objects to simulate guild mention scenarios.
"""

import asyncio
import sys
import os
from datetime import datetime
from unittest.mock import Mock, MagicMock

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.webhook_handler import WebhookHandler


class MockRole:
    """Mock Discord Role object"""
    def __init__(self, name: str):
        self.name = name


class MockGuild:
    """Mock Discord Guild object"""
    def __init__(self, guild_id: int = 123456789, name: str = "Test Guild"):
        self.id = guild_id
        self.name = name


class MockChannel:
    """Mock Discord Channel object"""
    def __init__(self, channel_id: int = 987654321, name: str = "general", channel_type="text"):
        self.id = channel_id
        self.name = name
        self.type = channel_type


class MockUser:
    """Mock Discord User object"""
    def __init__(self, user_id: int = 111222333, username: str = "testuser", display_name: str = "Test User"):
        self.id = user_id
        self.name = username
        self.display_name = display_name
        self.roles = [
            MockRole("@everyone"),
            MockRole("Member"),
            MockRole("Tester")
        ]


class MockAttachment:
    """Mock Discord Attachment object"""
    def __init__(self, url: str = "https://cdn.discordapp.com/test.png"):
        self.url = url


class MockEmbed:
    """Mock Discord Embed object"""
    def __init__(self, title: str = "Test Embed"):
        self.title = title
    
    def to_dict(self):
        return {"title": self.title, "type": "rich"}


class MockMessage:
    """Mock Discord Message object for testing"""
    def __init__(self, guild_context: bool = True):
        self.id = 555666777
        self.content = f"Hey @BeanBot, how are you doing?"
        self.created_at = datetime.now()
        
        # Author (user who sent the message)
        self.author = MockUser()
        
        # Guild context (None for DMs)
        if guild_context:
            self.guild = MockGuild()
            self.channel = MockChannel()
        else:
            self.guild = None
            self.channel = MockChannel(channel_type="private")
        
        # Attachments and embeds
        self.attachments = [MockAttachment()]
        self.embeds = [MockEmbed()]


class MockBotUser:
    """Mock Discord Bot User object"""
    def __init__(self):
        self.id = 999888777
        self.name = "BeanBot"
        self.display_name = "BeanBot"
        
    def mentioned_in(self, message):
        """Simulate bot mention detection"""
        return "@BeanBot" in message.content or "BeanBot" in message.content


class MockBot:
    """Mock Discord Bot object"""
    def __init__(self):
        self.user = MockBotUser()


async def test_webhook_handler():
    """Test the webhook handler functionality"""
    print("🧪 Testing Webhook Handler for Guild Mentions")
    print("=" * 50)
    
    # Initialize webhook handler
    webhook_handler = WebhookHandler("https://httpbin.org/post")  # Test endpoint
    bot = MockBot()
    
    # Test 1: Guild mention with @bot
    print("\n📋 Test 1: Guild mention with @bot")
    guild_message = MockMessage(guild_context=True)
    
    # Test mention detection
    is_mentioned = webhook_handler.is_bot_mentioned(guild_message, bot.user)
    print(f"  Mention detected: {is_mentioned}")
    
    if is_mentioned:
        # Test payload construction
        payload = webhook_handler.build_payload(guild_message)
        print(f"  Payload keys: {list(payload.keys())}")
        
        # Verify guild context
        print(f"  Context type: {payload['context']['type']}")
        print(f"  Guild ID: {payload['context']['guild']['id']}")
        print(f"  Guild name: {payload['context']['guild']['name']}")
        print(f"  Channel ID: {payload['context']['channel']['id']}")
        print(f"  Channel name: {payload['context']['channel']['name']}")
        print(f"  User roles: {payload['user']['roles']}")
        
        # Test webhook sending (will fail gracefully with test endpoint)
        print("  Testing webhook send...")
        try:
            success = await webhook_handler.send_mention_notification(guild_message)
            print(f"  ✅ Webhook send result: {success}")
        except Exception as e:
            print(f"  ⚠️ Webhook send error (expected): {e}")
    
    # Test 2: DM mention 
    print("\n📋 Test 2: DM mention")
    dm_message = MockMessage(guild_context=False)
    
    is_mentioned = webhook_handler.is_bot_mentioned(dm_message, bot.user)
    print(f"  Mention detected: {is_mentioned}")
    
    if is_mentioned:
        payload = webhook_handler.build_payload(dm_message)
        print(f"  Context type: {payload['context']['type']}")
        print(f"  Guild data: {payload['context']['guild']}")
        print(f"  User roles: {payload['user']['roles']}")
    
    # Test 3: Message without mention
    print("\n📋 Test 3: Message without mention")
    no_mention_message = MockMessage()
    no_mention_message.content = "Hello everyone, how is the weather?"
    
    is_mentioned = webhook_handler.is_bot_mentioned(no_mention_message, bot.user)
    print(f"  Mention detected: {is_mentioned}")
    
    # Test 4: Bot self-mention (should be ignored)
    print("\n📋 Test 4: Bot self-mention (should be ignored)")
    self_mention_message = MockMessage()
    self_mention_message.author = bot.user  # Bot is the author
    self_mention_message.content = "I am BeanBot and I'm testing myself"
    
    is_mentioned = webhook_handler.is_bot_mentioned(self_mention_message, bot.user)
    print(f"  Mention detected: {is_mentioned} (should be False)")
    
    print("\n✅ Guild mention testing completed!")
    print("\n💡 To test with real Discord:")
    print("   1. Run the bot with proper WEBHOOK_URL in .env")
    print("   2. Mention @BeanBot in a guild channel")
    print("   3. Check webhook endpoint for POST requests")
    print("   4. Verify payload structure matches specification")


if __name__ == "__main__":
    try:
        asyncio.run(test_webhook_handler())
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()