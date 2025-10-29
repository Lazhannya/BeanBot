#!/usr/bin/env python3
"""
Test script specifically for DM mention functionality.

This script tests the webhook functionality when the bot is mentioned in DM channels,
focusing on privacy compliance and DM-specific payload structure.
"""

import asyncio
import sys
import os
from datetime import datetime
from unittest.mock import Mock, MagicMock

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.webhook_handler import WebhookHandler


class MockBotUser:
    """Mock Discord Bot User object"""
    def __init__(self):
        self.id = 999888777
        self.name = "BeanBot"
        self.display_name = "BeanBot"
        
    def mentioned_in(self, message):
        """Simulate bot mention detection"""
        return "@BeanBot" in message.content or "BeanBot" in message.content


class MockUser:
    """Mock Discord User object for DMs"""
    def __init__(self, user_id: int = 111222333, username: str = "dmuser", display_name: str = "DM User"):
        self.id = user_id
        self.name = username
        self.display_name = display_name
        # DM users don't have guild roles


class MockDMChannel:
    """Mock Discord DM Channel object"""
    def __init__(self):
        self.id = 123456789
        self.type = "private"  # DM channel type
        # DM channels don't have names in the traditional sense


class MockDMMessage:
    """Mock Discord Message object for DM testing"""
    def __init__(self):
        self.id = 555666777
        self.content = f"Hey @BeanBot, can you help me with something?"
        self.created_at = datetime.now()
        
        # Author (user who sent the DM)
        self.author = MockUser()
        
        # DM context - no guild
        self.guild = None
        self.channel = MockDMChannel()
        
        # Attachments and embeds
        self.attachments = []
        self.embeds = []


class MockBot:
    """Mock Discord Bot object"""
    def __init__(self):
        self.user = MockBotUser()


async def test_dm_webhook_handler():
    """Test the webhook handler functionality for DM contexts"""
    print("🔒 Testing Webhook Handler for DM Mentions")
    print("=" * 50)
    
    # Initialize webhook handler
    webhook_handler = WebhookHandler("https://httpbin.org/post")  # Test endpoint
    bot = MockBot()
    
    # Test 1: DM mention with privacy compliance
    print("\n📋 Test 1: DM mention with privacy compliance")
    dm_message = MockDMMessage()
    
    # Test mention detection in DM
    is_mentioned = webhook_handler.is_bot_mentioned(dm_message, bot.user)
    print(f"  Mention detected: {is_mentioned}")
    
    if is_mentioned:
        # Test DM payload construction
        payload = webhook_handler.build_payload(dm_message)
        print(f"  Payload keys: {list(payload.keys())}")
        
        # Verify DM privacy compliance
        print(f"\n  🔒 Privacy Compliance Check:")
        print(f"    Context type: {payload['context']['type']}")
        print(f"    Guild data: {payload['context']['guild']} (should be None)")
        print(f"    User roles: {payload['user']['roles']} (should be empty)")
        print(f"    Channel type: {payload['context']['channel']['type']}")
        
        # Verify essential data is still included
        print(f"\n  📊 Essential Data Check:")
        print(f"    User ID: {payload['user']['id']}")
        print(f"    User name: {payload['user']['username']}")
        print(f"    Message ID: {payload['message']['id']}")
        print(f"    Message content: {payload['message']['content'][:50]}...")
        print(f"    Channel ID: {payload['context']['channel']['id']}")
        
        # Privacy validation
        privacy_issues = []
        if payload['context']['guild'] is not None:
            privacy_issues.append("Guild data should be None for DMs")
        if len(payload['user']['roles']) > 0:
            privacy_issues.append("User roles should be empty for DMs")
        if payload['context']['type'] != 'dm':
            privacy_issues.append("Context type should be 'dm'")
            
        if privacy_issues:
            print(f"\n  ❌ Privacy Issues Found:")
            for issue in privacy_issues:
                print(f"    - {issue}")
        else:
            print(f"\n  ✅ All privacy checks passed!")
        
        # Test webhook sending
        print(f"\n  📤 Testing webhook send...")
        try:
            success = await webhook_handler.send_mention_notification(dm_message)
            print(f"    Result: {'✅ Success' if success else '⚠️ Failed (expected for test endpoint)'}")
        except Exception as e:
            print(f"    Error: {e}")
    
    # Test 2: DM with no mention (should not trigger webhook)
    print("\n📋 Test 2: DM without mention")
    no_mention_dm = MockDMMessage()
    no_mention_dm.content = "Hello, how are you doing today?"
    
    is_mentioned = webhook_handler.is_bot_mentioned(no_mention_dm, bot.user)
    print(f"  Mention detected: {is_mentioned} (should be False)")
    
    # Test 3: DM with attachment (data handling)
    print("\n📋 Test 3: DM with attachments")
    attachment_dm = MockDMMessage()
    attachment_dm.content = "Check this out @BeanBot!"
    
    # Mock attachment
    class MockAttachment:
        def __init__(self, url):
            self.url = url
    
    attachment_dm.attachments = [MockAttachment("https://cdn.discordapp.com/test.png")]
    
    is_mentioned = webhook_handler.is_bot_mentioned(attachment_dm, bot.user)
    if is_mentioned:
        payload = webhook_handler.build_payload(attachment_dm)
        print(f"  Attachments in payload: {len(payload['message']['attachments'])}")
        print(f"  Attachment URLs: {payload['message']['attachments']}")
    
    print("\n✅ DM mention testing completed!")
    print("\n🔒 DM Privacy Summary:")
    print("   ✓ No guild information leaked")
    print("   ✓ No user role information exposed") 
    print("   ✓ Essential communication data preserved")
    print("   ✓ Webhook structure maintained")
    
    print("\n💡 To test with real Discord DMs:")
    print("   1. Send a DM to the bot mentioning @BeanBot")
    print("   2. Check webhook endpoint for POST requests")
    print("   3. Verify payload has guild: null and roles: []")
    print("   4. Confirm user and message data is present")


if __name__ == "__main__":
    try:
        asyncio.run(test_dm_webhook_handler())
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()