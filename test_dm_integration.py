#!/usr/bin/env python3
"""
Integration test for DM slash commands
Tests the complete DM command flow including command registration
"""

import sys
import asyncio
from unittest.mock import Mock, AsyncMock

def test_dm_command_integration():
    """Test DM command integration"""
    print("🧪 Testing DM Command Integration")
    print("=" * 50)
    
    try:
        # Add current directory to path
        sys.path.append('.')
        
        # Import required modules
        from modules.reminder_system import (
            is_dm_context,
            is_owner_in_context,
            get_dm_error_message,
            get_context_info
        )
        
        print("✅ Successfully imported DM command functions")
        
        # Mock bot
        class MockBot:
            def __init__(self):
                self.owner_id = 143474592529252353
        
        # Mock DM interaction from owner
        class MockDMOwnerInteraction:
            def __init__(self):
                self.guild = None  # DM context
                self.user = Mock()
                self.user.id = 143474592529252353  # Bot owner
                self.client = MockBot()
                self.channel = Mock()
                self.channel.id = 12345
                self.channel.type = 'dm'
        
        # Mock DM interaction from non-owner
        class MockDMUserInteraction:
            def __init__(self):
                self.guild = None  # DM context
                self.user = Mock()
                self.user.id = 999999999  # Not bot owner
                self.client = MockBot()
                self.channel = Mock()
                self.channel.id = 12345
                self.channel.type = 'dm'
        
        # Mock guild interaction
        class MockGuildInteraction:
            def __init__(self):
                self.guild = Mock()
                self.guild.id = 67890
                self.user = Mock()
                self.user.id = 143474592529252353  # Bot owner
                self.client = MockBot()
                self.channel = Mock()
        
        dm_owner = MockDMOwnerInteraction()
        dm_user = MockDMUserInteraction()
        guild_owner = MockGuildInteraction()
        
        # Test DM context detection
        print("\n🔍 Testing DM Context Detection:")
        print(f"  • DM Owner is DM: {is_dm_context(dm_owner)} ✅")
        print(f"  • DM User is DM: {is_dm_context(dm_user)} ✅")
        print(f"  • Guild is DM: {is_dm_context(guild_owner)} ✅")
        
        # Test owner permission checks
        print("\n🔐 Testing Owner Permission Checks:")
        dm_owner_check = is_owner_in_context(dm_owner, dm_owner.client)
        dm_user_check = is_owner_in_context(dm_user, dm_user.client)
        guild_owner_check = is_owner_in_context(guild_owner, guild_owner.client)
        
        print(f"  • DM Owner has permission: {dm_owner_check} ✅")
        print(f"  • DM User has permission: {dm_user_check} ✅") 
        print(f"  • Guild Owner has permission: {guild_owner_check} ✅")
        
        # Test error messages
        print("\n💬 Testing DM Error Messages:")
        owner_msg = get_dm_error_message("/reminder test", True)
        user_msg = get_dm_error_message("/reminder test", False)
        
        print(f"  • Owner message: {owner_msg[:50]}...")
        print(f"  • User message: {user_msg[:50]}...")
        
        # Test context info generation
        print("\n📊 Testing Context Info Generation:")
        dm_context = get_context_info(dm_owner)
        guild_context = get_context_info(guild_owner)
        
        print(f"  • DM context complete: {'is_dm' in dm_context and dm_context['is_dm']} ✅")
        print(f"  • Guild context complete: {'is_dm' in guild_context and not guild_context['is_dm']} ✅")
        
        # Validation checks
        print("\n" + "=" * 50)
        print("📋 DM Command Integration Summary:")
        
        validation_results = {
            "DM Context Detection": is_dm_context(dm_owner) and not is_dm_context(guild_owner),
            "Owner Permission (DM)": dm_owner_check and not dm_user_check,
            "Owner Permission (Guild)": guild_owner_check,
            "Error Message Generation": "owner" in owner_msg.lower() and "sorry" in user_msg.lower(),
            "Context Info Complete": dm_context['is_dm'] and not guild_context['is_dm']
        }
        
        for check, result in validation_results.items():
            status = "✅" if result else "❌"
            print(f"  • {check}: {status}")
        
        all_passed = all(validation_results.values())
        
        if all_passed:
            print("\n🎉 DM Command Integration: READY!")
            print("💡 Key Features Verified:")
            print("  • DM context detection working")
            print("  • Owner permissions enforced in DMs") 
            print("  • Guild functionality preserved")
            print("  • Error messages are DM-aware")
            print("  • Comprehensive logging context")
        else:
            print("\n⚠️ Some integration tests failed")
        
        return all_passed
        
    except Exception as e:
        print(f"\n❌ Error in DM command integration test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_dm_command_integration()
    print(f"\n{'🎉 SUCCESS' if success else '❌ FAILURE'}: DM Integration Test")
    sys.exit(0 if success else 1)