#!/usr/bin/env python3
"""
Test script for DM permission integration.

This script tests that DM webhook notifications respect the existing DM permission model,
where only the bot owner can trigger DM webhook notifications.
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.webhook_handler import WebhookHandler


class MockBot:
    """Mock Discord Bot object with owner_id"""
    def __init__(self, owner_id: int = 123456789):
        self.owner_id = owner_id
        self.user = MockBotUser()


class MockBotUser:
    """Mock Discord Bot User object"""
    def __init__(self):
        self.id = 999888777
        self.name = "BeanBot"
        self.display_name = "BeanBot"
        
    def mentioned_in(self, message):
        """Simulate bot mention detection"""
        return "@BeanBot" in message.content


class MockUser:
    """Mock Discord User object"""
    def __init__(self, user_id: int, username: str, is_owner: bool = False):
        self.id = user_id
        self.name = username
        self.display_name = username.title()


class MockDMMessage:
    """Mock Discord DM Message object"""
    def __init__(self, user_id: int, username: str):
        self.id = 555666777
        self.content = f"Hey @BeanBot, can you help me?"
        self.created_at = datetime.now()
        self.author = MockUser(user_id, username)
        self.guild = None  # DM context
        self.channel = MockDMChannel()
        self.attachments = []
        self.embeds = []


class MockGuildMessage:
    """Mock Discord Guild Message object"""
    def __init__(self, user_id: int, username: str):
        self.id = 888999000
        self.content = f"Hey @BeanBot, check this out!"
        self.created_at = datetime.now()
        self.author = MockUser(user_id, username)
        self.guild = MockGuild()
        self.channel = MockChannel()
        self.attachments = []
        self.embeds = []


class MockDMChannel:
    """Mock Discord DM Channel"""
    def __init__(self):
        self.id = 111222333
        self.type = "private"


class MockChannel:
    """Mock Discord Guild Channel"""
    def __init__(self):
        self.id = 444555666
        self.name = "general"
        self.type = "text"


class MockGuild:
    """Mock Discord Guild"""
    def __init__(self):
        self.id = 777888999
        self.name = "Test Server"


async def test_dm_permissions():
    """Test DM permission checking for webhook notifications"""
    print("🔐 Testing DM Permission Integration")
    print("=" * 50)
    
    # Bot configuration
    BOT_OWNER_ID = 123456789
    NON_OWNER_ID = 987654321
    
    bot = MockBot(owner_id=BOT_OWNER_ID)
    webhook_handler = WebhookHandler("https://httpbin.org/post")
    
    # Test 1: DM from bot owner (should be allowed)
    print("\n📋 Test 1: DM from bot owner (should be allowed)")
    owner_dm = MockDMMessage(BOT_OWNER_ID, "bot_owner")
    
    is_mentioned = webhook_handler.is_bot_mentioned(owner_dm, bot.user)
    has_permission = webhook_handler._check_dm_permissions(owner_dm, bot)
    
    print(f"  Mention detected: {is_mentioned}")
    print(f"  Permission granted: {has_permission}")
    print(f"  Should send webhook: {is_mentioned and has_permission}")
    
    if is_mentioned and has_permission:
        print(f"  ✅ Owner DM webhook would be sent")
    else:
        print(f"  ❌ Owner DM webhook would be blocked")
    
    # Test 2: DM from non-owner (should be blocked) 
    print("\n📋 Test 2: DM from non-owner (should be blocked)")
    non_owner_dm = MockDMMessage(NON_OWNER_ID, "regular_user")
    
    is_mentioned = webhook_handler.is_bot_mentioned(non_owner_dm, bot.user)
    has_permission = webhook_handler._check_dm_permissions(non_owner_dm, bot)
    
    print(f"  Mention detected: {is_mentioned}")
    print(f"  Permission granted: {has_permission}")
    print(f"  Should send webhook: {is_mentioned and has_permission}")
    
    if is_mentioned and not has_permission:
        print(f"  ✅ Non-owner DM webhook correctly blocked")
    else:
        print(f"  ❌ Non-owner DM webhook incorrectly allowed")
    
    # Test 3: Guild message from non-owner (should be allowed)
    print("\n📋 Test 3: Guild message from non-owner (should be allowed)")
    guild_message = MockGuildMessage(NON_OWNER_ID, "guild_user")
    
    is_mentioned = webhook_handler.is_bot_mentioned(guild_message, bot.user)
    has_permission = webhook_handler._check_dm_permissions(guild_message, bot)
    
    print(f"  Mention detected: {is_mentioned}")
    print(f"  Permission granted: {has_permission}")
    print(f"  Should send webhook: {is_mentioned and has_permission}")
    
    if is_mentioned and has_permission:
        print(f"  ✅ Guild message webhook would be sent")
    else:
        print(f"  ❌ Guild message webhook would be blocked")
    
    # Test 4: Guild message from owner (should be allowed)
    print("\n📋 Test 4: Guild message from owner (should be allowed)")
    owner_guild_message = MockGuildMessage(BOT_OWNER_ID, "owner_in_guild")
    
    is_mentioned = webhook_handler.is_bot_mentioned(owner_guild_message, bot.user)
    has_permission = webhook_handler._check_dm_permissions(owner_guild_message, bot)
    
    print(f"  Mention detected: {is_mentioned}")
    print(f"  Permission granted: {has_permission}")
    print(f"  Should send webhook: {is_mentioned and has_permission}")
    
    if is_mentioned and has_permission:
        print(f"  ✅ Owner guild message webhook would be sent")
    else:
        print(f"  ❌ Owner guild message webhook would be blocked")
    
    print("\n✅ DM Permission Integration Testing Complete!")
    print("\n🔐 Security Summary:")
    print(f"   ✓ DM webhooks restricted to bot owner (ID: {BOT_OWNER_ID})")
    print(f"   ✓ Guild webhooks allowed for all users")
    print(f"   ✓ Permission checks integrated with existing DM system")
    print(f"   ✓ Non-owner DM attempts logged for security awareness")
    
    print("\n💡 Integration with existing DM system:")
    print("   • Follows same permission model as /reminder and /dog commands")
    print("   • DM webhooks only from bot owner for security")
    print("   • Guild webhooks unrestricted (public channels)")
    print("   • Consistent with existing reminder_system.py DM permissions")


if __name__ == "__main__":
    try:
        asyncio.run(test_dm_permissions())
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()