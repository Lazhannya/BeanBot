#!/usr/bin/env python3
"""
BeanBot Reminder System - Automated Verification Script

This script performs basic verification of the reminder system implementation
to ensure all components are properly configured and ready for manual testing.
"""

import os
import sys
import importlib.util

def check_file_exists(filepath, description):
    """Check if a required file exists"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} - MISSING")
        return False

def check_module_structure():
    """Verify the module structure and imports"""
    print("\n📁 Checking Project Structure...")
    
    checks = [
        ("/home/vitruvia/workspace/BeanBot/modules/", "Modules directory"),
        ("/home/vitruvia/workspace/BeanBot/modules/reminder_system.py", "Reminder system module"),
        ("/home/vitruvia/workspace/BeanBot/modules/how_is.py", "How is module"),
        ("/home/vitruvia/workspace/BeanBot/reminder_config.py", "Reminder configuration"),
        ("/home/vitruvia/workspace/BeanBot/main.py", "Main bot file"),
        ("/home/vitruvia/workspace/BeanBot/MANUAL_TESTING_GUIDE.md", "Testing documentation")
    ]
    
    results = []
    for filepath, description in checks:
        results.append(check_file_exists(filepath, description))
    
    return all(results)

def check_reminder_config():
    """Verify reminder configuration is valid"""
    print("\n⚙️  Checking Reminder Configuration...")
    
    try:
        # Add the project directory to Python path
        sys.path.insert(0, '/home/vitruvia/workspace/BeanBot')
        
        # Import reminder config
        import reminder_config
        
        # Check required attributes
        if hasattr(reminder_config, 'REMINDERS'):
            print(f"✅ REMINDERS list found: {len(reminder_config.REMINDERS)} reminders")
            
            for i, reminder in enumerate(reminder_config.REMINDERS):
                name = reminder.get('name', f'reminder_{i}')
                schedules = len(reminder.get('schedules', []))
                print(f"   • {name}: {schedules} schedules")
        else:
            print("❌ REMINDERS list not found in config")
            return False
            
        if hasattr(reminder_config, 'TIMEZONE'):
            print(f"✅ TIMEZONE found: {reminder_config.TIMEZONE}")
        else:
            print("❌ TIMEZONE not found in config")
            return False
            
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import reminder_config: {e}")
        return False
    except Exception as e:
        print(f"❌ Error checking reminder config: {e}")
        return False

def check_reminder_system_module():
    """Verify reminder system module has required functions"""
    print("\n🔧 Checking Reminder System Module...")
    
    try:
        # Add the project directory to Python path
        sys.path.insert(0, '/home/vitruvia/workspace/BeanBot')
        
        # Load the module file directly
        spec = importlib.util.spec_from_file_location(
            "reminder_system", 
            "/home/vitruvia/workspace/BeanBot/modules/reminder_system.py"
        )
        reminder_system = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(reminder_system)
        
        # Check for key classes and functions
        if hasattr(reminder_system, 'ReminderSystem'):
            print("✅ ReminderSystem class found")
        else:
            print("❌ ReminderSystem class not found")
            return False
            
        if hasattr(reminder_system, 'ReminderView'):
            print("✅ ReminderView class found")
        else:
            print("❌ ReminderView class not found")
            return False
            
        # Check if setup function would be created (when bot is passed)
        print("✅ Module structure appears correct")
        return True
        
    except Exception as e:
        print(f"❌ Error checking reminder system module: {e}")
        return False

def check_test_commands():
    """Check if test commands are implemented in the module"""
    print("\n🧪 Checking Test Commands Implementation...")
    
    try:
        with open('/home/vitruvia/workspace/BeanBot/modules/reminder_system.py', 'r') as f:
            content = f.read()
        
        test_commands = [
            ('testreminder', '!testreminder command'),
            ('settimeout', '!settimeout command'),
            ('reloadreminders', '!reloadreminders command'),
            ('reminderstatus', '!reminderstatus command'),
            ('listreminders', '!listreminders command')
        ]
        
        all_found = True
        for cmd_name, description in test_commands:
            if f'name="{cmd_name}"' in content:
                print(f"✅ {description} implemented")
            else:
                print(f"❌ {description} not found")
                all_found = False
                
        return all_found
        
    except Exception as e:
        print(f"❌ Error checking test commands: {e}")
        return False

def main():
    """Run all verification checks"""
    print("🤖 BeanBot Reminder System - Verification Script")
    print("=" * 50)
    
    all_checks = []
    
    # Run all checks
    all_checks.append(check_module_structure())
    all_checks.append(check_reminder_config())
    all_checks.append(check_reminder_system_module())
    all_checks.append(check_test_commands())
    
    # Final result
    print("\n" + "=" * 50)
    if all(all_checks):
        print("🎉 ALL CHECKS PASSED - System Ready for Manual Testing!")
        print("\nNext steps:")
        print("1. Start the bot: python main.py")
        print("2. Follow MANUAL_TESTING_GUIDE.md for comprehensive testing")
        print("3. Key test commands:")
        print("   • !testreminder dog_walking morning")
        print("   • !reminderstatus")
        print("   • !listreminders")
        return 0
    else:
        print("❌ Some checks failed - Please review errors above")
        return 1

if __name__ == "__main__":
    sys.exit(main())