#!/usr/bin/env python3
"""
Test script to verify that all new commands are properly implemented
"""

import sys
import importlib.util

def test_imports():
    """Test that all modules can be imported without errors"""
    try:
        import commands
        import user
        import epic_auth
        print("✅ Core modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_command_functions():
    """Test that all command functions exist"""
    import commands
    
    required_commands = [
        'command_start', 'command_help', 'command_login', 'command_style', 
        'command_badges', 'command_stats', 'command_menu', 'command_code',
        'command_locker', 'command_rocket', 'command_custom', 'command_clear',
        'command_user', 'command_logo', 'command_design', 'command_title',
        'command_locate', 'command_livechat', 'command_activate_code', 
        'command_delete_accounts'
    ]
    
    missing_commands = []
    for cmd in required_commands:
        if not hasattr(commands, cmd):
            missing_commands.append(cmd)
    
    if missing_commands:
        print(f"❌ Missing commands: {missing_commands}")
        return False
    else:
        print("✅ All command functions exist")
        return True

def test_user_data_structure():
    """Test that user data structure includes new fields"""
    from user import ExoUser
    import os
    
    # Create a test user with random ID to avoid conflicts
    import random
    test_id = random.randint(100000, 999999)
    test_user = ExoUser(test_id, "testuser")
    user_data = test_user.register()
    
    required_fields = [
        'show_submission', 'live_chat_enabled', 'design_choice', 
        'custom_title', 'redeemed_codes'
    ]
    
    missing_fields = []
    for field in required_fields:
        if field not in user_data:
            missing_fields.append(field)
    
    # Clean up test user file
    test_file = f"users/{test_id}.json"
    if os.path.exists(test_file):
        os.remove(test_file)
    
    if missing_fields:
        print(f"❌ Missing user data fields: {missing_fields}")
        return False
    else:
        print("✅ User data structure is complete")
        return True

def main():
    """Run all tests"""
    print("🧪 Testing Exo-Checker implementation...")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_command_functions,
        test_user_data_structure
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Implementation is ready.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())