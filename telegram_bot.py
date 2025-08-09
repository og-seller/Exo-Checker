import os
import json
import aiohttp
import asyncio
import random
import threading
import telebot
from io import BytesIO
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, InputMediaPhoto
from PIL import Image, ImageDraw, ImageFont
from epic_auth import EpicUser, EpicGenerator, EpicEndpoints
from user import ExoUser
from cosmetic import FortniteCosmetic
from commands import (command_start, command_help, command_login, command_style, command_badges, command_stats, 
                     command_menu, command_code, command_locker, command_custom, command_clear,
                     command_user, command_logo, command_design, command_title, command_locate, command_livechat,
                     command_activate_code, command_delete_accounts, send_style_message, send_badges_message, 
                     available_styles, avaliable_badges)
from commands_shop import (command_shop, handle_shop_navigation, command_news, 
                          handle_news_navigation, command_cosmetics)

import epic_auth
import cosmetic
import commands
import utils
import xbox_api
import fortnite_api_wrapper

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# your telegram bot's api token
TELEGRAM_API_TOKEN = os.getenv('TELEGRAM_API_TOKEN', "")

# locker categories we render in the checker
telegram_bot = telebot.TeleBot(TELEGRAM_API_TOKEN)

telegram_bot.set_my_commands([
    telebot.types.BotCommand("/start", "🚀 Setup your user to start skinchecking."),
    telebot.types.BotCommand("/help", "❓ Display Basic Info and the commands."),
    telebot.types.BotCommand("/login", "🔐 Skincheck your Epic Games account."),
    telebot.types.BotCommand("/menu", "📋 Access settings menu."),
    telebot.types.BotCommand("/code", "🔑 Code login or alternative login method."),
    telebot.types.BotCommand("/locker", "🎒 View Player Locker."),

    telebot.types.BotCommand("/style", "🎨 Customize your checker's style."),
    telebot.types.BotCommand("/custom", "⚙️ Personalization menu."),
    telebot.types.BotCommand("/clear", "🧹 Clear your account's friend list."),
    telebot.types.BotCommand("/user", "👤 Enable/disable showing submission info."),
    telebot.types.BotCommand("/logo", "🖼️ Change logo."),
    telebot.types.BotCommand("/design", "🎭 Design choice."),
    telebot.types.BotCommand("/title", "📝 Title settings."),
    telebot.types.BotCommand("/locate", "📍 Location by xbox nick."),
    telebot.types.BotCommand("/livechat", "💬 Live chat status."),
    telebot.types.BotCommand("/badges", "🏆 Toggle your owned badges."),
    telebot.types.BotCommand("/stats", "📊 View your stats."),
    
    # New Fortnite API commands
    telebot.types.BotCommand("/shop", "🛍️ View current Fortnite item shop."),
    telebot.types.BotCommand("/news", "📰 View latest Fortnite news."),
    telebot.types.BotCommand("/cosmetics", "🔍 Search for Fortnite cosmetics.")
])

auth_code = None
@telegram_bot.message_handler(commands=['start'])
def handle_start(message):
    command_start(telegram_bot, message)

@telegram_bot.message_handler(commands=['help'])
def handle_help(message):
    command_help(telegram_bot, message)

@telegram_bot.message_handler(commands=['login'])
def handle_login(message):
    asyncio.run(command_login(telegram_bot, message))

@telegram_bot.message_handler(commands=['style'])
def handle_style(message):
    asyncio.run(command_style(telegram_bot, message))

@telegram_bot.message_handler(commands=['badges'])
def handle_badges(message):
    asyncio.run(command_badges(telegram_bot, message))
    
@telegram_bot.message_handler(commands=['stats'])
def handle_stats(message):
    asyncio.run(command_stats(telegram_bot, message))

@telegram_bot.message_handler(commands=['menu'])
def handle_menu(message):
    asyncio.run(command_menu(telegram_bot, message))

@telegram_bot.message_handler(commands=['code'])
def handle_code(message):
    asyncio.run(command_code(telegram_bot, message))

@telegram_bot.message_handler(commands=['locker'])
def handle_locker(message):
    asyncio.run(command_locker(telegram_bot, message))


@telegram_bot.message_handler(commands=['custom'])
def handle_custom(message):
    asyncio.run(command_custom(telegram_bot, message))

@telegram_bot.message_handler(commands=['clear'])
def handle_clear(message):
    asyncio.run(command_clear(telegram_bot, message))

@telegram_bot.message_handler(commands=['user'])
def handle_user(message):
    asyncio.run(command_user(telegram_bot, message))

@telegram_bot.message_handler(commands=['logo'])
def handle_logo(message):
    asyncio.run(command_logo(telegram_bot, message))

@telegram_bot.message_handler(commands=['design'])
def handle_design(message):
    asyncio.run(command_design(telegram_bot, message))

@telegram_bot.message_handler(commands=['title'])
def handle_title(message):
    asyncio.run(command_title(telegram_bot, message))

@telegram_bot.message_handler(commands=['locate'])
def handle_locate(message):
    asyncio.run(command_locate(telegram_bot, message))

@telegram_bot.message_handler(commands=['livechat'])
def handle_livechat(message):
    asyncio.run(command_livechat(telegram_bot, message))

@telegram_bot.message_handler(commands=['activate_code'])
def handle_activate_code(message):
    asyncio.run(command_activate_code(telegram_bot, message))

@telegram_bot.message_handler(commands=['delete_accounts'])
def handle_delete_accounts(message):
    asyncio.run(command_delete_accounts(telegram_bot, message))

# New Fortnite API command handlers
@telegram_bot.message_handler(commands=['shop'])
def handle_shop(message):
    asyncio.run(command_shop(telegram_bot, message))

@telegram_bot.message_handler(commands=['news'])
def handle_news(message):
    asyncio.run(command_news(telegram_bot, message))

@telegram_bot.message_handler(commands=['cosmetics'])
def handle_cosmetics(message):
    asyncio.run(command_cosmetics(telegram_bot, message))

@telegram_bot.callback_query_handler(func=lambda call: call.data.startswith("style_") or call.data.startswith("select_"))
def handle_style_navigation(call):
    data = call.data
    user = ExoUser(call.from_user.id, call.from_user.username)
    user_data = user.load_data()

    if not user_data:
        telegram_bot.reply_to(call.message, "🚫 You haven't setup your user yet, please use /start before using styles!", parse_mode="Markdown")
        return
    
    if data.startswith("style_"):
        new_index = int(data.split("_")[1])
        telegram_bot.delete_message(call.message.chat.id, call.message.message_id)
        send_style_message(telegram_bot, call.message.chat.id, new_index)

    elif data.startswith("select_"):
        selected_index = int(data.split("_")[1])
        selected_style = available_styles[selected_index]
        user_data['style'] = selected_style['ID']
        user.update_data()
        telegram_bot.send_message(call.message.chat.id, f"🎨 **Style Updated**\n\n✅ {selected_style['name']} style selected successfully!", parse_mode="Markdown")

@telegram_bot.callback_query_handler(func=lambda call: call.data.startswith("badge_") or call.data.startswith("toggle_"))
def handle_badge_navigation(call):
    data = call.data
    user = ExoUser(call.from_user.id, call.from_user.username)
    user_data = user.load_data()

    if not user_data:
        telegram_bot.reply_to(call.message, "🚫 You haven't setup your user yet, please use /start before using badges!", parse_mode="Markdown")
        return
    
    if data.startswith("badge_"):
        new_index = int(data.split("_")[1])
        telegram_bot.delete_message(call.message.chat.id, call.message.message_id)
        send_badges_message(telegram_bot, call.message.chat.id, new_index, user_data)

    elif data.startswith("toggle_"):
        badge_index = int(data.split("_")[1])
        badge = avaliable_badges[badge_index]
        current_status = user_data.get(badge['data2'], False)
        user_data[badge['data2']] = not current_status

        user.update_data()
        telegram_bot.answer_callback_query(call.id, f"🏆 {badge['name']} is now {'✅ Enabled' if not current_status else '❌ Disabled'}!")
        telegram_bot.delete_message(call.message.chat.id, call.message.message_id)
        send_badges_message(telegram_bot, call.message.chat.id, badge_index, user_data)

@telegram_bot.callback_query_handler(func=lambda call: call.data.startswith("menu_") or call.data.startswith("custom_") or call.data.startswith("design_") or call.data.startswith("clear_") or call.data.startswith("delete_"))
def handle_menu_navigation(call):
    data = call.data
    user = ExoUser(call.from_user.id, call.from_user.username)
    user_data = user.load_data()

    if not user_data:
        telegram_bot.answer_callback_query(call.id, "🚫 You haven't setup your user yet!")
        return
    
    if data.startswith("menu_"):
        menu_type = data.split("_")[1]
        if menu_type == "style":
            asyncio.run(command_style(telegram_bot, call.message))
        elif menu_type == "badges":
            asyncio.run(command_badges(telegram_bot, call.message))
        elif menu_type == "logo":
            asyncio.run(command_logo(telegram_bot, call.message))
        elif menu_type == "design":
            asyncio.run(command_design(telegram_bot, call.message))
        elif menu_type == "title":
            asyncio.run(command_title(telegram_bot, call.message))
        elif menu_type == "user":
            asyncio.run(command_user(telegram_bot, call.message))
        elif menu_type == "stats":
            asyncio.run(command_stats(telegram_bot, call.message))
    
    elif data.startswith("custom_"):
        custom_type = data.split("_")[1]
        if custom_type == "gradient":
            # Cycle through gradient types
            current_gradient = user_data.get('gradient_type', 0)
            new_gradient = (current_gradient + 1) % 4  # 0-3 gradient types
            user_data['gradient_type'] = new_gradient
            user.update_data()
            gradient_names = ["Normal", "Rainbow", "Golden", "Silver"]
            telegram_bot.answer_callback_query(call.id, f"🌈 Gradient changed to: {gradient_names[new_gradient]}")
        elif custom_type == "background":
            telegram_bot.answer_callback_query(call.id, "🖼️ Send an image to set as background!")
        elif custom_type == "logo":
            asyncio.run(command_logo(telegram_bot, call.message))
        elif custom_type == "colors":
            telegram_bot.answer_callback_query(call.id, "🎨 Color scheme feature coming soon!")
        elif custom_type == "title":
            asyncio.run(command_title(telegram_bot, call.message))
    
    elif data.startswith("design_"):
        design_type = data.split("_")[1]
        user_data['design_choice'] = design_type
        user.update_data()
        telegram_bot.answer_callback_query(call.id, f"🎨 Design changed to: {design_type.title()}")
        telegram_bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"🖼️ **Design Choice**\n\nCurrent design: **{design_type.title()}**\n\n✅ Design updated successfully!",
            parse_mode="Markdown"
        )
    
    elif data.startswith("clear_friends_"):
        action = data.split("_")[2]
        if action == "confirm":
            telegram_bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="🔔 **Friend List Cleared**\n\n⚠️ This feature requires Epic Games API integration and is currently under development.",
                parse_mode="Markdown"
            )
        elif action == "cancel":
            telegram_bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="❌ **Operation Cancelled**\n\nYour friend list was not modified.",
                parse_mode="Markdown"
            )
    
    elif data.startswith("delete_all_"):
        action = data.split("_")[2]
        if action == "confirm":
            # Clear user's cached data
            import os
            import shutil
            try:
                # Remove user's account cache if it exists
                accounts_dir = f"accounts"
                if os.path.exists(accounts_dir):
                    for account_folder in os.listdir(accounts_dir):
                        account_path = os.path.join(accounts_dir, account_folder)
                        if os.path.isdir(account_path):
                            shutil.rmtree(account_path)
                
                # Reset user stats
                user_data['accounts_checked'] = 0
                user.update_data()
                
                telegram_bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text="✅ **All Account Data Deleted**\n\nAll cached account data and statistics have been permanently removed.",
                    parse_mode="Markdown"
                )
            except Exception as e:
                telegram_bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=f"❌ **Error**\n\nFailed to delete account data: {str(e)}",
                    parse_mode="Markdown"
                )
        elif action == "cancel":
            telegram_bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="❌ **Operation Cancelled**\n\nNo data was deleted.",
                parse_mode="Markdown"
            )

@telegram_bot.callback_query_handler(func=lambda call: call.data.startswith("shop_") and not call.data == "shop_back")
def handle_shop_callbacks(call):
    """Handle shop-related callbacks"""
    asyncio.run(handle_shop_navigation(telegram_bot, call))

@telegram_bot.callback_query_handler(func=lambda call: call.data.startswith("news_") and not call.data == "news_back")
def handle_news_callbacks(call):
    """Handle news-related callbacks"""
    asyncio.run(handle_news_navigation(telegram_bot, call))

@telegram_bot.callback_query_handler(func=lambda call: call.data == "shop_back")
def handle_shop_back(call):
    """Handle back button from shop details"""
    asyncio.run(command_shop(telegram_bot, call.message))

@telegram_bot.callback_query_handler(func=lambda call: call.data == "news_back")
def handle_news_back(call):
    """Handle back button from news details"""
    asyncio.run(command_news(telegram_bot, call.message))

@telegram_bot.callback_query_handler(func=lambda call: call.data.startswith("welcome_"))
def handle_welcome_navigation(call):
    data = call.data
    
    # Ensure user is registered before handling any welcome navigation
    user = ExoUser(call.from_user.id, call.from_user.username)
    user_data = user.load_data()
    
    # Auto-register user if not registered
    if not user_data:
        print(f"Auto-registering user: {call.from_user.id}")
        user.register()
    
    if data == "welcome_connect":
        # Redirect to login command
        asyncio.run(command_login(telegram_bot, call.message))
    elif data == "welcome_saved":
        # Show saved accounts (previously checked accounts)
        show_saved_accounts(call)
    elif data == "welcome_shop":
        # Show items shop using the new Fortnite API integration
        asyncio.run(command_shop(telegram_bot, call.message))
    elif data == "welcome_settings":
        # Show settings menu
        markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("Checker Style 🎨", callback_data="settings_style"),
                InlineKeyboardButton("Badges 🏆", callback_data="settings_badges")
            ],
            [
                InlineKeyboardButton("Custom Design 🖌️", callback_data="settings_design"),
                InlineKeyboardButton("User Info 👤", callback_data="settings_user")
            ],
            [
                InlineKeyboardButton("Delete Accounts 🗑️", callback_data="settings_delete"),
                InlineKeyboardButton("Clear Friends 🧹", callback_data="settings_clear")
            ],
            [
                InlineKeyboardButton("Back to Menu 🔙", callback_data="back_to_menu")
            ]
        ])
        
        telegram_bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="⚙️ **Settings Menu**\n\nCustomize your Exo-Checker experience with the options below:",
            reply_markup=markup,
            parse_mode="Markdown"
        )

def show_saved_accounts(call):
    """Show saved accounts with credentials for the specific user"""
    from user import ExoUser
    
    user_id = call.from_user.id
    username = call.from_user.username or call.from_user.first_name or "User"
    
    # Load user data and auto-register if needed
    user_obj = ExoUser(user_id, username)
    user_data = user_obj.load_data()
    
    if not user_data:
        # Auto-register the user
        user_obj.register()
        user_data = user_obj.load_data()
    
    # Get saved accounts from user data
    saved_accounts = user_obj.get_saved_accounts()
    
    if not saved_accounts:
        # Instead of using answer_callback_query, edit the message
        telegram_bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="📁 **Saved Accounts**\n\nYou don't have any saved accounts yet. Use the Connect Account button to add one.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_welcome")]]),
            parse_mode="Markdown"
        )
        return
    
    # Sort by last used date (newest first)
    saved_accounts.sort(key=lambda x: x.get('last_used', ''), reverse=True)
    
    # Create buttons for saved accounts
    markup = InlineKeyboardMarkup()
    for i, account_info in enumerate(saved_accounts[:10]):  # Limit to 10 accounts
        account_id = account_info['account_id']
        display_name = account_info['display_name']
        email = account_info.get('email', '')
        
        # Create display text with name and masked email
        button_text = f"👤 {display_name}"
        if len(button_text) > 25:  # Telegram button text limit
            button_text = f"👤 {display_name[:20]}..."
            
        markup.add(InlineKeyboardButton(button_text, callback_data=f"saved_account_{account_id}"))
    
    # Add management buttons
    markup.add(InlineKeyboardButton("🗑️ Manage Accounts", callback_data="manage_saved_accounts"))
    markup.add(InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_welcome"))
    
    telegram_bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"📁 **Your Saved Accounts** ({len(saved_accounts)} found)\n\n🔐 These accounts are saved with credentials for quick access.\n👤 Select an account to use:",
        reply_markup=markup,
        parse_mode="Markdown"
    )

def show_items_shop(call):
    """Show Fortnite items shop information using the new Fortnite API integration"""
    # Use the new command_shop function instead
    asyncio.run(command_shop(telegram_bot, call.message))

@telegram_bot.callback_query_handler(func=lambda call: call.data.startswith("saved_account_"))
def handle_saved_account_selection(call):
    """Handle saved account selection for quick login"""
    from user import ExoUser
    from epic_auth import EpicUser
    import datetime
    
    user_id = call.from_user.id
    username = call.from_user.username or call.from_user.first_name or "User"
    account_id = call.data.replace("saved_account_", "")
    
    # Load user data
    user_obj = ExoUser(user_id, username)
    user_data = user_obj.load_data()
    
    if not user_data:
        telegram_bot.answer_callback_query(call.id, "🚫 Please register first using /start!")
        return
    
    # Get the specific saved account
    saved_account = user_obj.get_saved_account(account_id)
    
    if not saved_account:
        telegram_bot.answer_callback_query(call.id, "🚫 Account not found!")
        return
    
    # Check if tokens are still valid (basic check)
    try:
        expires_at = saved_account.get('expires_at', '')
        if expires_at:
            from datetime import datetime
            expiry_time = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
            if datetime.now() > expiry_time:
                telegram_bot.answer_callback_query(call.id, "🔄 Token expired, please re-login this account")
                return
    except:
        pass
    
    # Update last used time
    saved_account['last_used'] = datetime.datetime.now().isoformat()
    user_obj.add_saved_account(saved_account)  # This will update the existing account
    
    # Create action buttons for this account
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("🌐 Web Login", callback_data=f"web_login_{account_id}")],
        [InlineKeyboardButton("🔄 Recheck Account", callback_data=f"quick_check_{account_id}")],
        [InlineKeyboardButton("🗑️ Remove Account", callback_data=f"remove_account_{account_id}")],
        [InlineKeyboardButton("🔙 Back to Accounts", callback_data="welcome_saved")]
    ])
    
    display_name = saved_account['display_name']
    email = saved_account.get('email', 'Unknown')
    saved_at = saved_account.get('saved_at', 'Unknown')
    
    # Format saved date
    if saved_at != 'Unknown':
        try:
            dt = datetime.datetime.fromisoformat(saved_at.replace('Z', '+00:00'))
            saved_at = dt.strftime('%Y-%m-%d %H:%M')
        except:
            pass
    
    telegram_bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"👤 **{display_name}**\n\n📧 Email: {email}\n📅 Saved: {saved_at}\n\n🚀 What would you like to do with this account?",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@telegram_bot.callback_query_handler(func=lambda call: call.data.startswith("web_login_"))
def handle_web_login(call):
    """Handle web login for saved account"""
    from user import ExoUser
    
    user_id = call.from_user.id
    username = call.from_user.username or call.from_user.first_name or "User"
    account_id = call.data.replace("web_login_", "")
    
    # Load user data
    user_obj = ExoUser(user_id, username)
    saved_account = user_obj.get_saved_account(account_id)
    
    if not saved_account:
        telegram_bot.answer_callback_query(call.id, "🚫 Account not found!")
        return
    
    # Get account details
    display_name = saved_account['display_name']
    
    # Send web login instructions
    telegram_bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"🌐 **Web Login for {display_name}**\n\n"
             f"To login to this account on the Epic Games website:\n\n"
             f"1. Go to https://www.epicgames.com/id/login\n"
             f"2. Use the saved credentials for this account\n\n"
             f"⚠️ For security reasons, we don't store or display your password.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Back to Account", callback_data=f"saved_account_{account_id}")]
        ]),
        parse_mode="Markdown"
    )

@telegram_bot.callback_query_handler(func=lambda call: call.data == "manage_saved_accounts")
def handle_manage_saved_accounts(call):
    """Handle saved accounts management"""
    from user import ExoUser
    
    user_id = call.from_user.id
    username = call.from_user.username or call.from_user.first_name or "User"
    
    # Load user data
    user_obj = ExoUser(user_id, username)
    saved_accounts = user_obj.get_saved_accounts()
    
    if not saved_accounts:
        telegram_bot.answer_callback_query(call.id, "📁 No saved accounts to manage!")
        return
    
    # Create buttons for account management
    markup = InlineKeyboardMarkup()
    for account_info in saved_accounts[:10]:  # Limit to 10 accounts
        account_id = account_info['account_id']
        display_name = account_info['display_name']
        
        button_text = f"🗑️ {display_name}"
        if len(button_text) > 25:
            button_text = f"🗑️ {display_name[:20]}..."
            
        markup.add(InlineKeyboardButton(button_text, callback_data=f"remove_account_{account_id}"))
    
    markup.add(InlineKeyboardButton("🗑️ Remove All Accounts", callback_data="remove_all_accounts"))
    markup.add(InlineKeyboardButton("🔙 Back to Accounts", callback_data="welcome_saved"))
    
    telegram_bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"🗑️ **Manage Saved Accounts**\n\n⚠️ Select accounts to remove:\n\n*Note: This will permanently delete the saved credentials.*",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@telegram_bot.callback_query_handler(func=lambda call: call.data.startswith("remove_account_"))
def handle_remove_account(call):
    """Handle removing a specific saved account"""
    from user import ExoUser
    
    user_id = call.from_user.id
    username = call.from_user.username or call.from_user.first_name or "User"
    account_id = call.data.replace("remove_account_", "")
    
    # Load user data
    user_obj = ExoUser(user_id, username)
    saved_account = user_obj.get_saved_account(account_id)
    
    if not saved_account:
        telegram_bot.answer_callback_query(call.id, "🚫 Account not found!")
        return
    
    # Remove the account
    success = user_obj.remove_saved_account(account_id)
    
    if success:
        display_name = saved_account['display_name']
        telegram_bot.answer_callback_query(call.id, f"🗑️ Removed {display_name}")
        
        # Go back to saved accounts list
        show_saved_accounts(call)
    else:
        telegram_bot.answer_callback_query(call.id, "🚫 Failed to remove account!")

@telegram_bot.callback_query_handler(func=lambda call: call.data == "remove_all_accounts")
def handle_remove_all_accounts(call):
    """Handle removing all saved accounts"""
    from user import ExoUser
    
    user_id = call.from_user.id
    username = call.from_user.username or call.from_user.first_name or "User"
    
    # Load user data
    user_obj = ExoUser(user_id, username)
    user_obj.user_data['saved_accounts'] = []
    user_obj.update_data()
    
    telegram_bot.answer_callback_query(call.id, "🗑️ All accounts removed!")
    
    # Go back to welcome menu
    handle_back_to_welcome(call)

@telegram_bot.callback_query_handler(func=lambda call: call.data.startswith("quick_check_"))
def handle_quick_check(call):
    """Handle quick account check using saved credentials"""
    from user import ExoUser
    from epic_auth import EpicUser
    import asyncio
    
    user_id = call.from_user.id
    username = call.from_user.username or call.from_user.first_name or "User"
    account_id = call.data.replace("quick_check_", "")
    
    # Load user data
    user_obj = ExoUser(user_id, username)
    saved_account = user_obj.get_saved_account(account_id)
    
    if not saved_account:
        telegram_bot.answer_callback_query(call.id, "🚫 Account not found!")
        return
    
    telegram_bot.answer_callback_query(call.id, "🔍 Checking account...")
    
    # Create a message object for the command
    class MockMessage:
        def __init__(self, chat_id, from_user):
            self.chat = type('obj', (object,), {'id': chat_id})
            self.from_user = from_user
    
    mock_message = MockMessage(call.message.chat.id, call.from_user)
    
    # Create EpicUser from saved credentials
    epic_user_data = {
        'access_token': saved_account['access_token'],
        'refresh_token': saved_account['refresh_token'],
        'expires_at': saved_account['expires_at'],
        'refresh_expires_at': saved_account['refresh_expires_at'],
        'account_id': saved_account['account_id'],
        'displayName': saved_account['display_name']
    }
    
    # Run the code command with saved credentials
    from commands import run_code_command_with_saved_account
    asyncio.run(run_code_command_with_saved_account(telegram_bot, mock_message, epic_user_data, user_obj))

@telegram_bot.callback_query_handler(func=lambda call: call.data.startswith("quick_stats_"))
def handle_quick_stats(call):
    """Handle quick stats view using saved credentials"""
    telegram_bot.answer_callback_query(call.id, "📊 This feature will be implemented soon!")

@telegram_bot.callback_query_handler(func=lambda call: call.data.startswith("quick_image_"))
def handle_quick_image(call):
    """Handle quick image generation using saved credentials"""
    telegram_bot.answer_callback_query(call.id, "🎨 This feature will be implemented soon!")

@telegram_bot.callback_query_handler(func=lambda call: call.data.startswith("view_account_"))
def handle_view_account(call):
    """Handle viewing saved account images for the specific user"""
    user_id = call.from_user.id
    account_id = call.data.replace("view_account_", "")
    account_path = os.path.join("accounts", f"user_{user_id}", account_id)
    
    if not os.path.exists(account_path):
        telegram_bot.answer_callback_query(call.id, "🚫 Account data not found!")
        return
    
    # Get all images for this account
    images = [f for f in os.listdir(account_path) if f.endswith(('.png', '.jpg', '.jpeg'))]
    
    if not images:
        telegram_bot.answer_callback_query(call.id, "🚫 No images found for this account!")
        return
    
    # Load account metadata
    metadata_path = os.path.join(account_path, "metadata.json")
    display_name = "Unknown"
    last_checked = "Unknown"
    
    if os.path.exists(metadata_path):
        try:
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            display_name = metadata.get('display_name', 'Unknown')
            last_checked = metadata.get('last_checked', 'Unknown')
            # Format the date nicely
            if last_checked != 'Unknown':
                try:
                    from datetime import datetime
                    dt = datetime.fromisoformat(last_checked.replace('Z', '+00:00'))
                    last_checked = dt.strftime('%Y-%m-%d %H:%M')
                except:
                    pass
        except:
            pass
    
    # Create buttons for each image category
    markup = InlineKeyboardMarkup()
    for image in images:
        # Extract category from filename (e.g., "Outfits.png" -> "Outfits")
        category = image.replace('.png', '').replace('.jpg', '').replace('.jpeg', '')
        markup.add(InlineKeyboardButton(f"🖼️ {category}", callback_data=f"show_image_{account_id}_{image}"))
    
    markup.add(InlineKeyboardButton("🔙 Back to Accounts", callback_data="welcome_saved"))
    
    telegram_bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=f"📁 **Account: {display_name}**\n\n📅 Last checked: {last_checked}\n🖼️ Available images ({len(images)} found):\nSelect a category to view:",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@telegram_bot.callback_query_handler(func=lambda call: call.data.startswith("show_image_"))
def handle_show_image(call):
    """Handle showing saved account images for the specific user"""
    user_id = call.from_user.id
    parts = call.data.replace("show_image_", "").split("_", 1)
    if len(parts) != 2:
        telegram_bot.answer_callback_query(call.id, "🚫 Invalid image request!")
        return
    
    account_id, image_name = parts
    image_path = os.path.join("accounts", f"user_{user_id}", account_id, image_name)
    
    if not os.path.exists(image_path):
        telegram_bot.answer_callback_query(call.id, "🚫 Image not found!")
        return
    
    # Load account metadata for display name
    metadata_path = os.path.join("accounts", f"user_{user_id}", account_id, "metadata.json")
    display_name = "Unknown"
    
    if os.path.exists(metadata_path):
        try:
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            display_name = metadata.get('display_name', 'Unknown')
        except:
            pass
    
    try:
        with open(image_path, 'rb') as image_file:
            category = image_name.replace('.png', '').replace('.jpg', '').replace('.jpeg', '')
            
            telegram_bot.send_photo(
                chat_id=call.message.chat.id,
                photo=image_file,
                caption=f"🖼️ **{category}** - {display_name}\n\n📅 Cached image from previous check",
                parse_mode="Markdown"
            )
            telegram_bot.answer_callback_query(call.id, f"🖼️ Showing {category} image")
    except Exception as e:
        telegram_bot.answer_callback_query(call.id, "🚫 Error loading image!")

@telegram_bot.callback_query_handler(func=lambda call: call.data.startswith("shop_"))
def handle_shop_navigation(call):
    """Handle items shop navigation"""
    shop_type = call.data.replace("shop_", "")
    
    if shop_type == "today":
        text = "🛍️ **Today's Shop**\n\n🎮 Current items available in Fortnite Battle Royale!\n\n⚠️ *This feature is under development. Shop data will be integrated soon.*"
    elif shop_type == "featured":
        text = "⭐ **Featured Items**\n\n🌟 Special featured items and bundles!\n\n⚠️ *This feature is under development. Featured items data will be integrated soon.*"
    elif shop_type == "daily":
        text = "🔄 **Daily Items**\n\n📅 Daily rotating items in the shop!\n\n⚠️ *This feature is under development. Daily items data will be integrated soon.*"
    elif shop_type == "special":
        text = "🎁 **Special Offers**\n\n💎 Limited time offers and exclusive deals!\n\n⚠️ *This feature is under development. Special offers data will be integrated soon.*"
    else:
        telegram_bot.answer_callback_query(call.id, "🚫 Unknown shop section!")
        return
    
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔙 Back to Shop", callback_data="welcome_shop")]
    ])
    
    telegram_bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text=text,
        reply_markup=markup,
        parse_mode="Markdown"
    )

@telegram_bot.callback_query_handler(func=lambda call: call.data.startswith("settings_"))
def handle_settings_menu(call):
    """Handle settings menu callbacks"""
    data = call.data
    
    if data == "settings_style":
        # Show style settings
        asyncio.run(send_style_message(telegram_bot, call.message))
    elif data == "settings_badges":
        # Show badges settings
        asyncio.run(send_badges_message(telegram_bot, call.message))
    elif data == "settings_design":
        # Show design settings
        asyncio.run(command_design(telegram_bot, call.message))
    elif data == "settings_user":
        # Show user info
        asyncio.run(command_user(telegram_bot, call.message))
    elif data == "settings_delete":
        # Show delete accounts menu
        asyncio.run(command_delete_accounts(telegram_bot, call.message))
    elif data == "settings_clear":
        # Show clear friends menu
        asyncio.run(command_clear(telegram_bot, call.message))

@telegram_bot.callback_query_handler(func=lambda call: call.data == "back_to_welcome" or call.data == "back_to_menu")
def handle_back_to_welcome(call):
    """Handle back to welcome menu"""
    # Recreate the welcome menu
    markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Connect Account ⚡", callback_data="welcome_connect"),
            InlineKeyboardButton("Saved Accounts 📁", callback_data="welcome_saved")
        ],
        [
            InlineKeyboardButton("Items Shop 🛍️", callback_data="welcome_shop"),
            InlineKeyboardButton("Settings ⚙️", callback_data="welcome_settings")
        ],
        [InlineKeyboardButton("📞 Contact Developer", url="https://t.me/ogsellz")]
    ])
    
    telegram_bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="👋 **Welcome to the Exo-Checker Bot!**\n\n📰 **Our News channel** - t.me/ExoChecker\n\nBy using the bot, you automatically agree to the user agreement.",
        reply_markup=markup,
        parse_mode="Markdown"
    )

print("🚀 Starting Exo-Checker...")          
if __name__ == '__main__':
    telegram_bot.infinity_polling()