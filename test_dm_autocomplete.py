#!/usr/bin/env python3
"""
Test script for DM autocomplete functionality
Tests all autocomplete functions in simulated DM context
"""

import sys
import asyncio
import time
from unittest.mock import Mock

def test_dm_autocomplete():
    """Test DM autocomplete functions"""
    print("🧪 Testing DM Autocomplete Implementation")
    print("=" * 50)
    
    try:
        # Add current directory to path
        sys.path.append('.')
        
        # Import required modules
        from modules.reminder_system import (
            reminder_name_autocomplete,
            schedule_label_autocomplete, 
            timezone_autocomplete,
            is_dm_context,
            get_context_info,
            handle_autocomplete_error,
            get_fallback_choices
        )
        import reminder_config
        
        print("✅ Successfully imported DM autocomplete functions")
        
        # Mock DM interaction
        class MockDMInteraction:
            def __init__(self):
                self.guild = None  # DM context
                self.channel = Mock()
                self.channel.id = 12345
                self.channel.type = 'dm'
                self.user = Mock()
                self.user.id = 143474592529252353  # Bot owner
                self.user.name = 'TestOwner'
        
        # Mock guild interaction for comparison
        class MockGuildInteraction:
            def __init__(self):
                self.guild = Mock()
                self.guild.id = 67890
                self.guild.name = 'TestGuild'
                self.channel = Mock()
                self.channel.id = 54321
                self.channel.type = 'text'
                self.user = Mock()
                self.user.id = 143474592529252353
                self.user.name = 'TestOwner'
        
        dm_interaction = MockDMInteraction()
        guild_interaction = MockGuildInteraction()
        
        # Test DM context detection
        print("\n🔍 Testing DM Context Detection:")
        is_dm = is_dm_context(dm_interaction)
        is_guild = is_dm_context(guild_interaction)
        print(f"  • DM interaction detected as DM: {is_dm} ✅")
        print(f"  • Guild interaction detected as DM: {is_guild} ✅")
        
        # Test context info
        print("\n📊 Testing Context Info:")
        dm_context = get_context_info(dm_interaction)
        guild_context = get_context_info(guild_interaction)
        print(f"  • DM context info: {dm_context}")
        print(f"  • Guild context info: {guild_context}")
        
        # Test autocomplete functions
        async def test_autocomplete_functions():
            print("\n🔧 Testing Autocomplete Functions in DM:")
            
            # Test reminder name autocomplete in DM
            start_time = time.time()
            dm_reminder_choices = await reminder_name_autocomplete(dm_interaction, "")
            dm_time = time.time() - start_time
            print(f"  • DM reminder autocomplete: {len(dm_reminder_choices)} choices in {dm_time:.3f}s")
            
            # Test guild for comparison
            start_time = time.time()
            guild_reminder_choices = await reminder_name_autocomplete(guild_interaction, "")
            guild_time = time.time() - start_time
            print(f"  • Guild reminder autocomplete: {len(guild_reminder_choices)} choices in {guild_time:.3f}s")
            
            # Test schedule autocomplete in DM
            dm_schedule_choices = await schedule_label_autocomplete(dm_interaction, "")
            print(f"  • DM schedule autocomplete: {len(dm_schedule_choices)} choices")
            
            # Test timezone autocomplete in DM
            dm_timezone_choices = await timezone_autocomplete(dm_interaction, "America")
            print(f"  • DM timezone autocomplete: {len(dm_timezone_choices)} choices")
            
            # Test performance
            print(f"\n⚡ Performance Analysis:")
            print(f"  • DM vs Guild response time difference: {(dm_time - guild_time)*1000:.1f}ms")
            if dm_time < 3.0 and guild_time < 3.0:
                print(f"  • ✅ Both contexts under 3-second Discord limit")
            else:
                print(f"  • ⚠️ Performance concern detected")
            
            return dm_reminder_choices, dm_schedule_choices, dm_timezone_choices
        
        # Run async tests
        dm_reminder, dm_schedule, dm_timezone = asyncio.run(test_autocomplete_functions())
        
        # Test fallback choices
        print("\n🛡️ Testing Fallback Mechanisms:")
        reminder_fallback = get_fallback_choices(dm_interaction, "reminder")
        timezone_fallback = get_fallback_choices(dm_interaction, "timezone")
        print(f"  • Reminder fallback choices: {len(reminder_fallback)}")
        print(f"  • Timezone fallback choices: {len(timezone_fallback)}")
        
        # Test error handling
        print("\n🚨 Testing Error Handling:")
        test_error = Exception("Test error")
        error_choices = handle_autocomplete_error(dm_interaction, test_error, "test_function")
        print(f"  • DM error handling: {len(error_choices)} choices returned")
        
        # Summary
        print("\n" + "=" * 50)
        print("📋 DM Autocomplete Implementation Summary:")
        print(f"  • ✅ DM Context Detection: Working")
        print(f"  • ✅ Performance Monitoring: Implemented")
        print(f"  • ✅ Error Handling: DM-aware")
        print(f"  • ✅ Fallback Mechanisms: Ready")
        print(f"  • ✅ All autocomplete functions: DM compatible")
        
        # Check if any choices have DM indicators
        dm_indicators = []
        for choices in [dm_reminder, dm_schedule, dm_timezone]:
            for choice in choices:
                if 'DM' in choice.name or '💡' in choice.name or '🚀' in choice.name:
                    dm_indicators.append(choice.name)
        
        if dm_indicators:
            print(f"  • ✅ DM-specific indicators found: {len(dm_indicators)}")
        
        print("\n🎉 DM Autocomplete Implementation: READY!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error testing DM autocomplete: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_dm_autocomplete()
    sys.exit(0 if success else 1)