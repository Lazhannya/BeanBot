#!/usr/bin/env python3
"""
Test script for User Story 1: Basic DM Slash Commands
Tests that all core reminder slash commands work in DM context with proper permissions.
"""

import asyncio
import sys
from unittest.mock import Mock, AsyncMock, MagicMock
import discord
from discord import app_commands

# Add project root to path
sys.path.insert(0, '/home/vitruvia/workspace/BeanBot')

# Import the reminder system
from modules.reminder_system import is_dm_context, is_owner_in_context, get_context_info, get_dm_error_message

def create_mock_dm_interaction(user_id: int, is_owner: bool = False) -> Mock:
    """Create a mock Discord interaction for DM context"""
    interaction = Mock(spec=discord.Interaction)
    
    # Mock user
    interaction.user = Mock()
    interaction.user.id = user_id
    interaction.user.name = f"TestUser{user_id}"
    
    # Mock DM channel (no guild)
    interaction.guild = None
    interaction.channel = Mock()
    interaction.channel.type = discord.ChannelType.private
    
    # Mock client/bot
    interaction.client = Mock()
    interaction.client.owner_id = 143474592529252353 if is_owner else 999999999
    
    # Mock response methods
    interaction.response = Mock()
    interaction.response.defer = AsyncMock()
    interaction.response.send_message = AsyncMock()
    interaction.followup = Mock()
    interaction.followup.send = AsyncMock()
    
    return interaction

def create_mock_guild_interaction(user_id: int, is_owner: bool = False) -> Mock:
    """Create a mock Discord interaction for guild context"""
    interaction = Mock(spec=discord.Interaction)
    
    # Mock user
    interaction.user = Mock()
    interaction.user.id = user_id
    interaction.user.name = f"TestUser{user_id}"
    
    # Mock guild
    interaction.guild = Mock()
    interaction.guild.id = 67890
    interaction.guild.name = "TestGuild"
    interaction.channel = Mock()
    interaction.channel.type = discord.ChannelType.text
    interaction.channel.id = 54321
    
    # Mock client/bot
    interaction.client = Mock()
    interaction.client.owner_id = 143474592529252353 if is_owner else 999999999
    
    # Mock response methods
    interaction.response = Mock()
    interaction.response.defer = AsyncMock()
    interaction.response.send_message = AsyncMock()
    interaction.followup = Mock()
    interaction.followup.send = AsyncMock()
    
    return interaction

async def test_dm_context_detection():
    """Test DM context detection utility function"""
    print("🔍 Testing DM context detection...")
    
    # Test DM context
    dm_interaction = create_mock_dm_interaction(12345)
    assert is_dm_context(dm_interaction) == True, "Should detect DM context"
    
    # Test guild context
    guild_interaction = create_mock_guild_interaction(12345)
    assert is_dm_context(guild_interaction) == False, "Should detect guild context"
    
    print("  ✅ DM context detection working correctly")

async def test_owner_permission_checking():
    """Test owner permission checking in DM vs guild context"""
    print("🔒 Testing owner permission checking...")
    
    owner_id = 143474592529252353
    non_owner_id = 987654321
    
    # Test DM context - owner
    dm_owner = create_mock_dm_interaction(owner_id, is_owner=True)
    assert is_owner_in_context(dm_owner, dm_owner.client) == True, "Owner should have access in DM"
    
    # Test DM context - non-owner
    dm_non_owner = create_mock_dm_interaction(non_owner_id, is_owner=False)
    assert is_owner_in_context(dm_non_owner, dm_non_owner.client) == False, "Non-owner should not have access in DM"
    
    # Test guild context - owner
    guild_owner = create_mock_guild_interaction(owner_id, is_owner=True)
    assert is_owner_in_context(guild_owner, guild_owner.client) == True, "Owner should have access in guild"
    
    print("  ✅ Owner permission checking working correctly")

async def test_error_messages():
    """Test DM error message generation"""
    print("💬 Testing DM error messages...")
    
    # Test owner message
    owner_msg = get_dm_error_message("/reminder test", True)
    assert "✅" in owner_msg, "Owner message should be positive"
    assert "can use" in owner_msg, "Owner message should indicate permission"
    
    # Test non-owner message
    non_owner_msg = get_dm_error_message("/reminder test", False)
    assert "❌" in non_owner_msg, "Non-owner message should be negative"
    assert "restricted" in non_owner_msg, "Non-owner message should explain restriction"
    assert "security" in non_owner_msg, "Non-owner message should mention security"
    
    print("  ✅ DM error messages working correctly")

async def test_context_info_generation():
    """Test context info generation for logging"""
    print("📊 Testing context info generation...")
    
    # Test DM context
    dm_interaction = create_mock_dm_interaction(12345)
    dm_info = get_context_info(dm_interaction)
    
    assert dm_info['is_dm'] == True, "Should identify DM context"
    assert dm_info['guild_id'] is None, "DM should have no guild ID"
    assert dm_info['guild_name'] == "DM", "DM should show as 'DM'"
    print(f"    DM channel type: {dm_info['channel_type']}")
    assert dm_info['channel_type'] in ["dm", "private"], "Should identify DM channel type"
    
    # Test guild context
    guild_interaction = create_mock_guild_interaction(12345)
    guild_info = get_context_info(guild_interaction)
    
    assert guild_info['is_dm'] == False, "Should identify guild context"
    assert guild_info['guild_id'] == 67890, "Should have guild ID"
    assert guild_info['guild_name'] == "TestGuild", "Should have guild name"
    assert guild_info['channel_type'] == "text", "Should identify channel type"
    
    print("  ✅ Context info generation working correctly")

async def main():
    """Run all User Story 1 DM basic command tests"""
    print("🎯 USER STORY 1: BASIC DM SLASH COMMANDS - TEST SUITE")
    print("=" * 60)
    
    try:
        await test_dm_context_detection()
        await test_owner_permission_checking()
        await test_error_messages()
        await test_context_info_generation()
        
        print("\n" + "=" * 60)
        print("🎉 SUCCESS: All User Story 1 tests passed!")
        print("\n💡 Key Features Verified:")
        print("  • DM context detection ✅")
        print("  • Owner-only permission enforcement ✅")
        print("  • Clear error messages for non-owners ✅")
        print("  • Enhanced logging with DM context ✅")
        print("\n🚀 Ready for testing with actual Discord bot!")
        print("\n📋 Commands to test in Discord DMs:")
        print("  • /reminder test <reminder_name>")
        print("  • /reminder status")
        print("  • /reminder list")
        print("  • /dog test <time>")
        print("  • /dog status")
        print("\n⚠️  Note: Only bot owner can use these commands in DMs")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)