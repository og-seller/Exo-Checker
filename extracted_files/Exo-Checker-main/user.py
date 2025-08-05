import json
import os
import telebot
from telebot import types

# the version of the json data we save to our telegram users's stats
# when something new gets added, we increase the version by 1
TELEGRAM_USER_DATA_VERSION = 0

class ExoUser:
    def __init__(self, userID: int, username: str):
        self.userID: int = userID
        self.username: str = username
        self.user_data: json = {}

    def register(self) -> dict:
        user_path = f"users/{self.userID}.json"  
        if os.path.exists(user_path):
            # user is already registered
            return {}
        
        os.makedirs(os.path.dirname(user_path), exist_ok=True)
        self.user_data = {
            'ID': self.userID,
            'username': self.username,
            'version': TELEGRAM_USER_DATA_VERSION,
            'accounts_checked': 0,
            'style': 0,
            'gradient_type': 0,
            'alpha_tester_1_badge': False,
            'alpha_tester_2_badge': False,
            'alpha_tester_3_badge': False,
            'newbie_badge': False,
            'advanced_badge': False,
            'epic_badge': False,
            'alpha_tester_1_badge_active': False,
            'alpha_tester_2_badge_active': False,
            'alpha_tester_3_badge_active': False,
            'newbie_badge_active': False,
            'advanced_badge_active': False,
            'epic_badge_active': False,
            'show_submission': True,
            'live_chat_enabled': False,
            'design_choice': 'modern',
            'custom_title': 'Exo Checker User',
            'redeemed_codes': [],
            'saved_accounts': []
        }
    
        with open(user_path, 'w') as user_data_file:
            json.dump(self.user_data, user_data_file, indent=4)
        
        return self.user_data

    def load_data(self) -> dict:
        # loading the telegram user profile's stats
        user_path = f"users/{self.userID}.json"
        if not os.path.exists(user_path):
            # profile not found
            return {}
        
        if os.path.getsize(user_path) > 0:
            # loading the user profile's stats
            with open(user_path, 'r') as user_data_file:
                self.user_data = json.load(user_data_file)

        # versioning, making sure there is no missing info to not mess the user data

        # returning the user data
        self.user_data['version'] = TELEGRAM_USER_DATA_VERSION
        return self.user_data
    
    def update_data(self):
        # updating the telegram user profile's stats
        user_path = f"users/{self.userID}.json"
        if not os.path.exists(user_path):
            # user path doesn't exists, so we cannot update it
            return
        
        with open(user_path, 'w') as user_data_file:
            json.dump(self.user_data, user_data_file, indent=4)
    
    def add_saved_account(self, account_data: dict):
        """Add a saved account to the user's profile"""
        if 'saved_accounts' not in self.user_data:
            self.user_data['saved_accounts'] = []
        
        # Check if account already exists (by account ID)
        account_id = account_data.get('account_id')
        for i, existing_account in enumerate(self.user_data['saved_accounts']):
            if existing_account.get('account_id') == account_id:
                # Update existing account
                self.user_data['saved_accounts'][i] = account_data
                self.update_data()
                return
        
        # Add new account
        self.user_data['saved_accounts'].append(account_data)
        self.update_data()
    
    def get_saved_accounts(self) -> list:
        """Get all saved accounts for the user"""
        return self.user_data.get('saved_accounts', [])
    
    def remove_saved_account(self, account_id: str):
        """Remove a saved account by account ID"""
        if 'saved_accounts' not in self.user_data:
            return False
        
        for i, account in enumerate(self.user_data['saved_accounts']):
            if account.get('account_id') == account_id:
                del self.user_data['saved_accounts'][i]
                self.update_data()
                return True
        return False
    
    def get_saved_account(self, account_id: str) -> dict:
        """Get a specific saved account by account ID"""
        for account in self.user_data.get('saved_accounts', []):
            if account.get('account_id') == account_id:
                return account
        return None