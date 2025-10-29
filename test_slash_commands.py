#!/usr/bin/env python3
"""
Test script for slash command implementation validation
Tests slash command registration, autocomplete functions, and permissions
"""

import sys
import asyncio
import importlib
from unittest.mock import Mock, AsyncMock

def test_imports():
    """Test that all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        import discord
        from discord.ext import commands
        from discord import app_commands
        print("✅ Discord.py imports successful")
        
        import reminder_config
        print("✅ Reminder config import successful")
        
        from modules.reminder_system import (
            ReminderSystem, 
            reminder_name_autocomplete, 
            schedule_label_autocomplete,
            timezone_autocomplete
        )
        print("✅ Reminder system imports successful")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_autocomplete_functions():
    """Test autocomplete functions work correctly"""
    print("\n🧪 Testing autocomplete functions...")
    
    try:
        from modules.reminder_system import (
            reminder_name_autocomplete,
            timezone_autocomplete
        )
        
        # Mock interaction object
        mock_interaction = Mock()
        
        async def run_tests():
            # Test reminder name autocomplete
            choices = await reminder_name_autocomplete(mock_interaction, "")
            print(f"✅ Reminder autocomplete returned {len(choices)} choices")
            
            # Test timezone autocomplete
            choices = await timezone_autocomplete(mock_interaction, "America")
            print(f"✅ Timezone autocomplete returned {len(choices)} choices")
            
            # Test empty input
            choices = await timezone_autocomplete(mock_interaction, "")
            print(f"✅ Timezone autocomplete (empty) returned {len(choices)} choices")
        
        asyncio.run(run_tests())
        return True
        
    except Exception as e:
        print(f"❌ Autocomplete test error: {e}")
        return False

def test_command_structure():
    """Test the structure of slash command implementation"""
    print("\n🧪 Testing command structure...")
    
    try:
        with open('modules/reminder_system.py', 'r') as f:
            content = f.read()
        
        # Check for required elements
        tests = {
            "ReminderGroup class": "class ReminderGroup(app_commands.Group)" in content,
            "DogGroup class": "class DogGroup(app_commands.Group)" in content,
            "Help commands": content.count("def help(self") >= 2,
            "Permission checks": "owner_id" in content,
            "Comprehensive logging": content.count("SLASH_COMMAND:") >= 10,
            "Autocomplete decorators": "@" and ".autocomplete(" in content,
        }
        
        all_passed = True
        for test_name, passed in tests.items():
            if passed:
                print(f"✅ {test_name}")
            else:
                print(f"❌ {test_name}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Structure test error: {e}")
        return False

def test_configuration_compatibility():
    """Test that configuration is compatible with slash commands"""
    print("\n🧪 Testing configuration compatibility...")
    
    try:
        import reminder_config
        
        # Check required attributes
        required_attrs = ['REMINDERS', 'TIMEZONE']
        
        for attr in required_attrs:
            if hasattr(reminder_config, attr):
                print(f"✅ Configuration has {attr}")
            else:
                print(f"❌ Configuration missing {attr}")
                return False
        
        # Check reminders structure
        if isinstance(reminder_config.REMINDERS, list) and len(reminder_config.REMINDERS) > 0:
            reminder = reminder_config.REMINDERS[0]
            required_keys = ['name', 'schedules', 'target_user_id']
            
            for key in required_keys:
                if key in reminder:
                    print(f"✅ Reminder has {key}")
                else:
                    print(f"❌ Reminder missing {key}")
                    return False
        
        print("✅ Configuration structure compatible")
        return True
        
    except Exception as e:
        print(f"❌ Configuration test error: {e}")
        return False

def test_documentation():
    """Test that documentation is updated with slash commands"""
    print("\n🧪 Testing documentation...")
    
    try:
        with open('README.md', 'r') as f:
            readme = f.read()
        
        tests = {
            "Slash commands documented": "/reminder" in readme and "/dog" in readme,
            "Autocomplete guide": "autocomplete" in readme.lower(),
            "Migration guide": "migration" in readme.lower(),
            "Help commands documented": "/reminder help" in readme,
            "Examples provided": "Example Usage" in readme or "example" in readme.lower(),
        }
        
        all_passed = True
        for test_name, passed in tests.items():
            if passed:
                print(f"✅ {test_name}")
            else:
                print(f"❌ {test_name}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ Documentation test error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Slash Command Implementation Validation")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Autocomplete Functions", test_autocomplete_functions),
        ("Command Structure", test_command_structure),
        ("Configuration Compatibility", test_configuration_compatibility),
        ("Documentation", test_documentation),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("🏁 FINAL RESULTS:")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n📊 Summary: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Slash command implementation ready!")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())