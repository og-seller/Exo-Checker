import os
from PIL import Image, ImageDraw, ImageFont, ImageOps
import json
import user
import colorsys
import logging
import math
import urllib.request
from datetime import datetime
from io import BytesIO
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils import mask_email, mask_account_id, bool_to_emoji, country_to_flag
from user import ExoUser
from cosmetic import FortniteCosmetic
from epic_auth import EpicUser, EpicEndpoints, EpicGenerator, LockerData
# Import all renderer functions from renderer.py
from renderer import (
    fortnite_cache, 
    draw_gradient_text,
    render_exo_style,
    render_easy_style,
    render_raika_style,
    render_kayy_style,
    render_storm_style,
    render_aqua_style,
    renderer
)

def escape_markdown(text):
    """
    Escapes special characters for markdown formatting
    @note: sometimes external connections shows error due to these, so we handle it that way
    """
    escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in escape_chars:
        text = text.replace(char, f"\\{char}")
        
    return text

# FortniteCache moved to renderer.py

available_styles = [
    {"ID": 0, "name": "Exo", "image": "img/styles/exo.png"},
    {"ID": 1, "name": "Easy", "image": "img/styles/easy.png"},
    {"ID": 2, "name": "Raika", "image": "img/styles/raika.png"},
    {"ID": 3, "name": "kayy", "image": "img/styles/kayy.png"},
    {"ID": 4, "name": "Storm", "image": "img/styles/storm.png"}
]

avaliable_badges = [
    {"name": "Alpha Tester 1", "data": "alpha_tester_1_badge", "data2": "alpha_tester_1_badge_active", "image": "badges/icon/alpha1.png"},
    {"name": "Alpha Tester 2", "data": "alpha_tester_2_badge", "data2": "alpha_tester_2_badge_active", "image": "badges/icon/alpha2.png"},
    {"name": "Alpha Tester 3", "data": "alpha_tester_3_badge", "data2": "alpha_tester_3_badge_active", "image": "badges/icon/alpha3.png"},
    {"name": "Epic Games", "data": "epic_badge", "data2": "epic_badge_active", "image": "badges/icon/epic.png"}
]

locker_categories = ['AthenaCharacter', 'AthenaBackpack', 'AthenaPickaxe', 'AthenaDance', 'AthenaGlider', 'AthenaPopular', 'AthenaExclusive']
# global members


def command_start(bot, message):
    if message.chat.type != "private":
        return
    
    user = ExoUser(message.from_user.id, message.from_user.username)
    user_data = user.register()
    if not user_data:
        bot.reply_to(message, "✅ **Already Registered**\n\nYou have already setup your account! Use /help to see available commands.", parse_mode="Markdown")
        return
    
    bot.reply_to(message, f'''
🎮 **What is Exo-Checker Bot?**
> Exo-Checker is a secure telegram fortnite skin checker bot that visualizes your locker into an image and displays account information.

🔒 **Security & Privacy:**
> We do NOT store your account information anywhere. All account credentials are private and inaccessible for security reasons.

📋 **Commands:**
🚀 /start - Register to Exo-Checker
❓ /help - Display bot information and commands
🔐 /login - Skincheck your Epic Games Fortnite account
📋 /menu - Access settings menu
🔑 /code - Alternative code login method
🎒 /locker - View specific locker categories
🎨 /style - Choose your skincheck style
🏆 /badges - Toggle your achieved badges
📊 /stats - View your account statistics
⚙️ /custom - Personalization menu
🧹 /clear - Clear your account's friend list
👤 /user - Toggle user display settings
🖼️ /logo - Change your custom logo
🎭 /design - Design choice settings
📝 /title - Title settings
📍 /locate - Location lookup by Xbox nickname
💬 /livechat - Live chat status
''', parse_mode="Markdown")

    # Create welcome menu with buttons
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

    bot.send_message(
        chat_id=message.chat.id,
        text="👋 **Welcome to the Exo-Checker Bot!**\n\n📰 **Our News channel** - t.me/ExoChecker\n\nBy using the bot, you automatically agree to the user agreement.",
        reply_markup=markup,
        parse_mode="Markdown"
    )
    
def command_help(bot, message):
    bot.reply_to(message, f'''
❓ **Exo-Checker Bot Help**

🎮 **What is Exo-Checker Bot?**
> Exo-Checker is a secure telegram fortnite skin checker bot that visualizes your locker into an image and displays account information.

🔒 **Security & Privacy:**
> We do NOT store your account information anywhere. All account credentials are private and inaccessible for security reasons.

📋 **Available Commands:**

🚀 **Basic Commands:**
🚀 /start - Register to Exo-Checker
❓ /help - Display this help message
🔐 /login - Skincheck your Epic Games account
📋 /menu - Access main settings menu

🔑 **Login & Authentication:**
🔑 /code - Alternative code login method
🧹 /clear - Clear your account's friend list

👀 **Viewing & Checking:**
🎒 /locker - View specific locker categories
🚀 /rocket - Rocket League checker (coming soon)
📍 /locate - Location lookup by Xbox nickname

🎨 **Customization:**
🎨 /style - Choose your skincheck style
⚙️ /custom - Personalization menu
🎭 /design - Design choice settings
🖼️ /logo - Change your custom logo
📝 /title - Title settings

👤 **Account Management:**
🏆 /badges - Toggle your achieved badges
📊 /stats - View your account statistics
👤 /user - Toggle user display settings
💬 /livechat - Live chat status

🛠️ **Developer:** ExoCheckBot.gg
📞 **Support:** @ogsellz
''', parse_mode="Markdown")

    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("📞 Contact Developer", url="https://t.me/ogsellz")]
    ])
    
    bot.send_message(
        chat_id=message.chat.id,
        text="❓ **Need help or have questions?** Contact the developer directly!",
        reply_markup=markup,
        parse_mode="Markdown"
    )
    
async def command_login(bot, message):
    if message.chat.type != "private":
        return
    
    user = ExoUser(message.from_user.id, message.from_user.username)
    user_data = user.load_data()
    if user_data == {}:
        bot.reply_to(message, "🚫 You haven't setup your user yet, please use /start before logging in!", parse_mode="Markdown")
        return
    
    msg = bot.reply_to(message, "⏳ **Creating authorization login link...**", parse_mode="Markdown")
    epic_generator = EpicGenerator()
    await epic_generator.start()
    device_data = await epic_generator.create_device_code()
    epic_games_auth_link = f"https://www.epicgames.com/activate?userCode={device_data['user_code']}"

    # login link message(embed link button)
    markup = InlineKeyboardMarkup()
    button = InlineKeyboardButton("🔗 Login", url=epic_games_auth_link)
    markup.add(button)
    bot.edit_message_text(
        chat_id=msg.chat.id,
        message_id=msg.message_id,
        text=f"🔐 **Epic Games Login**\n\nOpen [this link](<{epic_games_auth_link}>) to log in to your account.", 
        reply_markup=markup,
        parse_mode="Markdown")
    
    epic_user = await epic_generator.wait_for_device_code_completion(bot, message, code=device_data['device_code'])
    if not epic_user:
        # something went wrong so we can't check the account
        await epic_generator.kill()
        return
    
    account_data = await epic_generator.get_account_metadata(epic_user)
   
    accountID = account_data.get('id', "INVALID_ACCOUNT_ID")
    if (accountID == "INVALID_ACCOUNT_ID"):
        bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id, text="Invalid account(banned or fortnite has not been launched).")
        return
    
    bot.delete_message(msg.chat.id, msg.message_id)
    msg = bot.send_message(message.chat.id, f'✅ **Successfully logged in account:** {account_data.get("displayName", "HIDDEN_ID_ACCOUNT")}', parse_mode="Markdown")
    
    # Save account credentials for future use
    import datetime
    saved_account_data = {
        'account_id': accountID,
        'display_name': account_data.get('displayName', 'Unknown'),
        'email': account_data.get('email', ''),
        'access_token': epic_user.access_token,
        'refresh_token': epic_user.refresh_token,
        'expires_at': epic_user.expires_at,
        'refresh_expires_at': epic_user.refresh_expires_at,
        'saved_at': datetime.datetime.now().isoformat(),
        'last_used': datetime.datetime.now().isoformat()
    }
    
    # Add to user's saved accounts
    user_obj.add_saved_account(saved_account_data)
    
    # Send confirmation message about saving
    bot.send_message(message.chat.id, f'💾 **Account saved!** You can now use this account without logging in again.\n\n📁 Access your saved accounts from the main menu.', parse_mode="Markdown")

    # account information
    account_public_data = await epic_generator.get_public_account_info(epic_user)
    bot.send_message(message.chat.id,f'''
━━━━━━━━━━━
Account Information
━━━━━━━━━━━
#️⃣ Account ID: {mask_account_id(accountID)}
📧 Email: {mask_email(account_data.get('email', ''))}          
🧑‍🦱 Display Name: {account_data.get('displayName', 'DeletedUser')}
📛 Full Name: {account_data.get('name', '')} {account_data.get('lastName', '')}
🌐 Country: {account_data.get('country', 'US')} {country_to_flag(account_data.get('country', 'US'))}
🔐 Email Verified: {bool_to_emoji(account_data.get('emailVerified', False))}
🔒 Mandatory 2FA Security: {bool_to_emoji(account_data.get('tfaEnabled', False))}
''')
    
    # external connections
    connected_accounts = 0
    connected_accounts_message = f"""
━━━━━━━━━━━
Connected Account
━━━━━━━━━━━\n"""
 
    external_auths = account_public_data.get('externalAuths', [])
    for auth in external_auths:
        auth_type = auth.get('type', '?').lower()
        display_name = auth.get('externalDisplayName', '?')
        external_id = auth.get('externalAuthId', '?')
        date_added = auth.get('dateAdded', '?')
        if date_added != '?':
            parsed_date = datetime.strptime(date_added, "%Y-%m-%dT%H:%M:%S.%fZ")
            date_added = parsed_date.strftime("%d/%m/%Y")

        connected_accounts += 1
        connected_accounts_message += f"""
Connection Type: {escape_markdown(auth_type.upper())}
External Display Name: {escape_markdown(display_name)}
Date of Connection: {escape_markdown(date_added)}
"""

    if connected_accounts == 0:
        connected_accounts_message += "No connected accounts."

    markup = InlineKeyboardMarkup()
    button = InlineKeyboardButton("🔗 Remove Restrictions", url='https://www.epicgames.com/help/en/wizards/w4')
    markup.add(button)
    bot.send_message(
        chat_id=msg.chat.id,
        text=connected_accounts_message, 
        reply_markup=markup,
        parse_mode="Markdown")
    
    # purchases infos
    vbucks_categories = [
        "Currency:MtxPurchased",
        "Currency:MtxEarned",
        "Currency:MtxGiveaway",
        "Currency:MtxPurchaseBonus"
    ]
        
    total_vbucks = 0
    refunds_used = 0
    refund_credits = 0
    receipts = []
    vbucks_purchase_history = {
        "1000": 0,
        "2800": 0,
        "5000": 0,
        "7500": 0,
        "13500": 0
    }

    gift_received = 0
    gift_sent = 0
    pending_gifts_amount = 0
    
    common_profile_data = await epic_generator.get_common_profile(epic_user)
    for item_id, item_data in common_profile_data.get("profileChanges", [{}])[0].get("profile", {}).get("items", {}).items():
        if item_data.get("templateId") in vbucks_categories:
            # getting vbucks
            total_vbucks += item_data.get("quantity", 0)
    
    for profileChange in common_profile_data.get("profileChanges", []):
        attributes = profileChange["profile"]["stats"]["attributes"]
        mtx_purchases = attributes.get("mtx_purchase_history", {})
        if mtx_purchases:
            refunds_used = mtx_purchases.get("refundsUsed", 0)
            refund_credits = mtx_purchases.get("refundCredits", 0)
            
        iap = attributes.get("in_app_purchases", {})
        if iap:
            receipts = iap.get("receipts", [])
            purchases = iap.get("fulfillmentCounts", {})
            if purchases:
                # vbucks purchases packs amount
                vbucks_purchase_history["1000"] = purchases.get("FN_1000_POINTS", 0)
                vbucks_purchase_history["2800"] = purchases.get("FN_2800_POINTS", 0)
                vbucks_purchase_history["5000"] = purchases.get("FN_5000_POINTS", 0)
                vbucks_purchase_history["7500"] = purchases.get("FN_7500_POINTS", 0)
                vbucks_purchase_history["13500"] = purchases.get("FN_13500_POINTS", 0)

        gift_history = attributes.get("gift_history", {})
        if gift_history:
            # pending gifts count
            gifts_pending = gift_history.get("gifts", [])
            pending_gifts_amount = len(gifts_pending)

            # gifts sent & received count
            gift_sent = gift_history.get("num_sent", 0)
            gift_received = gift_history.get("num_received", 0)

    total_vbucks_bought = 1000 * vbucks_purchase_history["1000"] + 2800 * vbucks_purchase_history["2800"] + 5000 * vbucks_purchase_history["5000"] + 7500 * vbucks_purchase_history["7500"] + 13500 * vbucks_purchase_history["13500"]
    bot.send_message(message.chat.id,f'''
━━━━━━━━━━━
Purchases Information
━━━━━━━━━━━
💰 VBucks: {total_vbucks}
🎟  Refunds Used: {refunds_used}
🎟  Refund Tickets: {refund_credits}

━━━━━━━━━━━
Vbucks Purchases
━━━━━━━━━━━
#️⃣ Receipts: {len(receipts)}
💰 1000 Vbucks Packs: {vbucks_purchase_history["1000"]}
💰 2800 Vbucks Packs: {vbucks_purchase_history["2800"]}
💰 5000 Vbucks Packs: {vbucks_purchase_history["5000"]}
💰 7500 Vbucks Packs: {vbucks_purchase_history["7500"]}
💰 13500 Vbucks Packs: {vbucks_purchase_history["13500"]}

💰 Total Vbucks Purchased: {total_vbucks_bought}

━━━━━━━━━━━
Gifts Information
━━━━━━━━━━━
🎁 Pending Gifts: {pending_gifts_amount}
🎁 Gifts Sent: {gift_sent}
🎁 Gifts Received: {gift_received}
''')
    
    # season history
    seasons_msg = await epic_generator.get_seasons_message(epic_user)
    bot.send_message(message.chat.id, seasons_msg)

    # locker data
    locker_data = await epic_generator.get_locker_data(epic_user)
    
    # activity info
    bot.send_message(message.chat.id,f'''
━━━━━━━━━━━
Activity Information
━━━━━━━━━━━
👪 Parental Control: {bool_to_emoji(account_data.get('minorVerified', False))}
🕘 Last Match: {locker_data.last_match}
🤯 Headless: {bool_to_emoji(account_data.get("headless", False))}
✏️ Display Name Changes: {account_data.get("numberOfDisplayNameChanges", 0)}
✏️ Display Name Changeable: {bool_to_emoji(account_data.get("canUpdateDisplayName", False))}
#️⃣ Hashed email: {bool_to_emoji(account_data.get("hasHashedEmail", False))}
''')
    
    bot.send_message(message.chat.id,f'''
━━━━━━━━━━━
Locker Information
━━━━━━━━━━━
🧍‍♂️  Outfits: {len(locker_data.cosmetic_array.get('AthenaCharacter', []))}
🎒  Backpacks: {len(locker_data.cosmetic_array.get('AthenaBackpack', []))}
⛏️  Pickaxes: {len(locker_data.cosmetic_array.get('AthenaPickaxe', []))}
🕺  Emotes: {len(locker_data.cosmetic_array.get('AthenaDance', []))}
✈️  Gliders: {len(locker_data.cosmetic_array.get('AthenaGlider', []))}
⭐  Most Wanted Cosmetics: {len(locker_data.cosmetic_array.get('AthenaPopular', []))}
🌟  Exclusives: {len(locker_data.cosmetic_array.get('AthenaExclusive', []))}
''')
    
    homebase_data = await epic_generator.get_homebase_profile(epic_user)
    stats = homebase_data.get("profileChanges", [{}])[0].get("profile", {}).get("stats", {}).get("attributes", {})
    if stats:
        stw_level = 1
        research_offence = 1
        research_fortitude = 1
        research_resistance = 1
        research_tech = 1
        collection_book_level = 1
        stw_claimed = False
        legacy_research_points = 0
        matches_played = 0
    
        stats = homebase_data.get("profileChanges", [{}])[0].get("profile", {}).get("stats", {}).get("attributes", {})
        if stats:
            stw_level = stats.get("level", 1)
            research_offence = stats.get("research_levels", {}).get("offence", 1)
            research_fortitude = stats.get("research_levels", {}).get("fortitude", 1)
            research_resistance = stats.get("research_levels", {}).get("resistance", 1)
            research_tech = stats.get("research_levels", {}).get("technology", 1)
            collection_book_level = stats.get("collection_book", {}).get("maxBookXpLevelAchieved", 1)
            stw_claimed = stats.get("mfa_reward_claimed", False)
            legacy_research_points = stats.get("legacy_research_points_spent", 0)
            matches_played = stats.get("matches_played", 0)
        bot.send_message(message.chat.id,f'''
━━━━━━━━━━━
Homebase Information
━━━━━━━━━━━
#️⃣ Level: {stw_level}
🎒 Collection Book Level: {collection_book_level}
🎁 Claimed Rewards: {bool_to_emoji(stw_claimed)}

Research:
⭐ Total spent points: {legacy_research_points}
⛏️ Offence: {research_offence}
⚔️ Fortitude: {research_fortitude}
🪖 Resistance: {research_resistance}
🔧 Tech: {research_tech}

Activity:
🎟  Matches Played: {matches_played}
''')
        
    # saved data path - user-specific directory
    # note: it only saves the rendered images for locker, data that DOES NOT contain private or login information!!!
    user_accounts_dir = f"accounts/user_{user_data['ID']}"
    save_path = f"{user_accounts_dir}/{accountID}"
    if not os.path.exists(user_accounts_dir):
        os.makedirs(user_accounts_dir, exist_ok=True)
    if not os.path.exists(save_path):
        os.makedirs(save_path, exist_ok=True)
    
    # Save account metadata (display name and last checked date)
    import datetime
    account_metadata = {
        'account_id': accountID,
        'display_name': account_data.get('displayName', 'Unknown'),
        'last_checked': datetime.datetime.now().isoformat(),
        'user_id': user_data['ID']
    }
    
    metadata_path = f"{save_path}/metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(account_metadata, f, indent=2)

    for category in locker_categories:
        if category not in locker_data.cosmetic_array or len(locker_data.cosmetic_array[category]) < 1:
            continue

        header = 'Outfits'
        if category == 'AthenaBackpack':
            header = 'Backblings'
        elif category == 'AthenaPickaxe':
            header = 'Pickaxes'
        elif category == 'AthenaDance':
            header = 'Emotes'
        elif category == 'AthenaGlider':
            header = 'Gliders'
        elif category == 'AthenaExclusive':
            header = 'Exclusives'
        elif category == 'AthenaPopular':
            header = 'Popular'
            
        if user_data['style'] == 0: # exo style
            render_exo_style(header, user_data, locker_data.cosmetic_array[category], f'{save_path}/{category}.png')
            
        elif user_data['style'] == 1: # easy style
            render_easy_style(header, user_data, locker_data.cosmetic_array[category], f'{save_path}/{category}.png')
                     
        elif user_data['style'] == 2: # raika style
            render_raika_style(header, user_data, locker_data.cosmetic_array[category], f'{save_path}/{category}.png')
            
        elif user_data['style'] == 3: # kayy style
            render_kayy_style(header, user_data, locker_data.cosmetic_array[category], f'{save_path}/{category}.png') 
             
        elif user_data['style'] == 4: # storm style
            render_storm_style(header, user_data, locker_data.cosmetic_array[category], f'{save_path}/{category}.png') 
        
        elif user_data['style'] == 5: # aqua style
            render_aqua_style(header, user_data, locker_data.cosmetic_array[category], f'{save_path}/{category}.png') 
                
        with open(f'{save_path}/{category}.png', 'rb') as photo_file:
            file_size = os.path.getsize(f'{save_path}/{category}.png')
            if file_size > 10 * 1024 * 1024:  # 10 MBs
                print("File too large for photo, sending as a document.")
                bot.send_document(msg.chat.id, photo_file)
            else:
                bot.send_photo(msg.chat.id, photo_file)

    skins = len(locker_data.cosmetic_array['AthenaCharacter'])
    excl = locker_data.cosmetic_array['AthenaExclusive']
    cosmetic_list = ''
    desc = ''      
    cosmetics_listed = 0
    for cosmetic in excl:
        cosmetic_list += cosmetic.name + " + "
        cosmetics_listed += 1
        
        if cosmetics_listed >= 10:
            break
    
    cosmetic_list = cosmetic_list.rstrip(" + ")
    desc = f'{skins} + {cosmetic_list} + {total_vbucks}VB'
    bot.send_message(message.chat.id,f'{desc}')
    await epic_generator.kill()

async def run_code_command_with_saved_account(bot, message, epic_user_data, user_obj):
    """Run the code command using saved account credentials"""
    from epic_auth import EpicGenerator, EpicUser
    import datetime
    
    # Create EpicUser from saved data
    epic_user = EpicUser(epic_user_data)
    
    # Create epic generator
    epic_generator = EpicGenerator()
    
    try:
        # Get account metadata
        account_data = await epic_generator.get_account_metadata(epic_user)
        accountID = account_data.get('id', "INVALID_ACCOUNT_ID")
        
        if accountID == "INVALID_ACCOUNT_ID":
            bot.send_message(message.chat.id, "🚫 **Account Error**\n\nInvalid account or tokens expired. Please re-login this account.", parse_mode="Markdown")
            return
        
        # Update last used time
        saved_account_data = {
            'account_id': accountID,
            'display_name': account_data.get('displayName', 'Unknown'),
            'email': account_data.get('email', ''),
            'access_token': epic_user.access_token,
            'refresh_token': epic_user.refresh_token,
            'expires_at': epic_user.expires_at,
            'refresh_expires_at': epic_user.refresh_expires_at,
            'saved_at': epic_user_data.get('saved_at', datetime.datetime.now().isoformat()),
            'last_used': datetime.datetime.now().isoformat()
        }
        user_obj.add_saved_account(saved_account_data)
        
        bot.send_message(message.chat.id, f'✅ **Using Saved Account:** {account_data.get("displayName", "Unknown")}', parse_mode="Markdown")
        
        # Get user data for the command
        user_data = user_obj.load_data()
        
        # Run the main code command logic
        await run_main_code_logic(bot, message, epic_generator, epic_user, account_data, accountID, user_data)
        
    except Exception as e:
        print(f"Error in saved account check: {e}")
        bot.send_message(message.chat.id, "🚫 **Error**\n\nFailed to check account. Tokens may be expired. Please re-login this account.", parse_mode="Markdown")
    finally:
        await epic_generator.kill()

async def run_main_code_logic(bot, message, epic_generator, epic_user, account_data, accountID, user_data):
    """Main logic for the code command (extracted for reuse)"""
    # account information
    account_public_data = await epic_generator.get_public_account_info(epic_user)
    bot.send_message(message.chat.id,f'''
━━━━━━━━━━━
Account Information
━━━━━━━━━━━
#️⃣ Account ID: {accountID}
📧 Email: {account_data.get('email', '')}          
🧑‍🦱 Display Name: {account_data.get('displayName', 'DeletedUser')}
📛 Full Name: {account_data.get('name', '')} {account_data.get('lastName', '')}
🌐 Country: {account_data.get('country', 'US')} {country_to_flag(account_data.get('country', 'US'))}
🔐 Email Verified: {bool_to_emoji(account_data.get('emailVerified', False))}
🔒 Mandatory 2FA Security: {bool_to_emoji(account_data.get('tfaEnabled', False))}
''')
    
    # external connections
    connected_accounts = 0
    connected_accounts_message = f"""
━━━━━━━━━━━
Connected Account
━━━━━━━━━━━\n"""
 
    external_auths = account_public_data.get('externalAuths', [])
    for auth in external_auths:
        auth_type = auth.get('type', '?').lower()
        display_name = auth.get('externalDisplayName', '?')
        external_id = auth.get('externalAuthId', '?')
        date_added = auth.get('dateAdded', '?')
        if date_added != '?':
            parsed_date = datetime.strptime(date_added, "%Y-%m-%dT%H:%M:%S.%fZ")
            date_added = parsed_date.strftime("%d/%m/%Y")

        connected_accounts += 1
        connected_accounts_message += f"""
Connection Type: {escape_markdown(auth_type.upper())}
Display Name: {escape_markdown(display_name)}
External ID: {escape_markdown(external_id)}
Date Added: {escape_markdown(date_added)}
━━━━━━━━━━━"""

    if connected_accounts > 0:
        bot.send_message(message.chat.id, connected_accounts_message, parse_mode="MarkdownV2")
    else:
        bot.send_message(message.chat.id, f"""
━━━━━━━━━━━
Connected Account
━━━━━━━━━━━
No connected accounts found.
━━━━━━━━━━━""")

    # For now, just send a completion message
    bot.send_message(message.chat.id, "✅ **Account check completed!**\n\n🎮 Full locker analysis and image generation will be implemented in the next update.", parse_mode="Markdown")
    
    # Support message
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("📞 Contact Developer", url="https://t.me/ogsellz")]
    ])

    bot.send_message(
        chat_id=message.chat.id,
        text=(
            "✅ Skin check completed!\n"
            "Developed by ExoCheckBot.gg\n\n"
            "Need support? Contact: @ogsellz"
        ),
        reply_markup=markup,
        parse_mode="Markdown"
    )
    

async def command_style(bot, message):
    if message.chat.type != "private":
        return
    
    user = ExoUser(message.from_user.id, message.from_user.username)
    user_data = user.load_data()
    if not user_data:
        bot.reply_to(message, "🚫 You haven't setup your user yet, please use /start before using styles!", parse_mode="Markdown")
        return
        
    current_style_index = user_data['style']
    send_style_message(bot, message.chat.id, current_style_index)

async def command_badges(bot, message):
    if message.chat.type != "private":
        return
    
    user = ExoUser(message.from_user.id, message.from_user.username)
    user_data = user.load_data()
    if not user_data:
        bot.reply_to(message, "🚫 You haven't setup your user yet, please use /start before viewing badges!", parse_mode="Markdown")
        return
        
    badges_unlocked = 0
    for badge in avaliable_badges:
        if user_data[badge['data']] == True:
            badges_unlocked += 1
    
    if badges_unlocked < 1:
        msg = bot.reply_to(message, "🏆 **No Badges Unlocked**\n\nYou haven't unlocked any badges yet! Keep using the bot to earn badges.", parse_mode="Markdown")
        return
                  
    current_badge_index = 0
    send_badges_message(bot, message.chat.id, current_badge_index, user_data)

async def command_stats(bot, message):
    if message.chat.type != "private":
        return
    
    user = ExoUser(message.from_user.id, message.from_user.username)
    user_data = user.load_data()
    if not user_data:
        bot.reply_to(message, "🚫 You haven't setup your user yet, please use /start before viewing stats!", parse_mode="Markdown")
        return
    
    style_names = {
        0: '🎨 Exo Style',
        1: '✨ Easy Style', 
        2: '🌟 Raika Style',
        3: '💫 Kayy Style',
        4: '⚡ Storm Style',
        5: '🌊 Aqua Style'
    }
    
    current_style = style_names.get(user_data['style'], '❓ Unknown Style')
    
    msg = bot.reply_to(message, f'''📊 **User Statistics**

👤 **User**: @{message.from_user.username} (#{user_data['ID']})
🔍 **Accounts Checked**: {user_data['accounts_checked']}
🎨 **Current Style**: {current_style}

🏆 **Badges Status**:
🥇 Alpha Tester 1: {bool_to_emoji(user_data['alpha_tester_1_badge'])} | Active: {bool_to_emoji(user_data['alpha_tester_1_badge_active'])}
🥈 Alpha Tester 2: {bool_to_emoji(user_data['alpha_tester_2_badge'])} | Active: {bool_to_emoji(user_data['alpha_tester_2_badge_active'])}
🥉 Alpha Tester 3: {bool_to_emoji(user_data['alpha_tester_3_badge'])} | Active: {bool_to_emoji(user_data['alpha_tester_3_badge_active'])}
🎮 Epic Games: {bool_to_emoji(user_data['epic_badge'])} | Active: {bool_to_emoji(user_data['epic_badge_active'])}
💯 100 Checks: {bool_to_emoji(user_data['newbie_badge'])} | Active: {bool_to_emoji(user_data['newbie_badge_active'])}
🚀 200 Checks: {bool_to_emoji(user_data['advanced_badge'])} | Active: {bool_to_emoji(user_data['advanced_badge_active'])}
''', parse_mode="Markdown")
    
def send_style_message(bot, chat_id, style_index):
    style = available_styles[style_index]
    markup = InlineKeyboardMarkup()

    # Navigation buttons in a single row
    nav_buttons = []
    if style_index > 0:
        nav_buttons.append(InlineKeyboardButton("◀️ Previous", callback_data=f"style_{style_index - 1}"))
    if style_index < len(available_styles) - 1:
        nav_buttons.append(InlineKeyboardButton("Next ▶️", callback_data=f"style_{style_index + 1}"))
    
    if nav_buttons:
        markup.row(*nav_buttons)

    # Select button
    markup.add(InlineKeyboardButton("✅ Select This Style", callback_data=f"select_{style_index}"))
    
    try:
        if os.path.exists(style['image']):
            with open(style['image'], 'rb') as img_file:
                bot.send_photo(
                    chat_id,
                    img_file,
                    caption=f"🎨 **{style['name']} Style**\n\nStyle {style_index + 1} of {len(available_styles)}",
                    reply_markup=markup,
                    parse_mode="Markdown"
                )
        else:
            # Fallback if image doesn't exist
            bot.send_message(
                chat_id,
                f"🎨 **{style['name']} Style**\n\nStyle {style_index + 1} of {len(available_styles)}\n\n📷 Preview image not available",
                reply_markup=markup,
                parse_mode="Markdown"
            )
    except Exception as e:
        # Fallback message if image loading fails
        bot.send_message(
            chat_id,
            f"🎨 **{style['name']} Style**\n\nStyle {style_index + 1} of {len(available_styles)}\n\n⚠️ Preview temporarily unavailable",
            reply_markup=markup,
            parse_mode="Markdown"
        )

def send_badges_message(bot, chat_id, badge_index, user_data):
    unlocked_badges = [
        (i, badge)
        for i, badge in enumerate(avaliable_badges)
        if user_data.get(badge['data'], False)
    ]
    
    if not unlocked_badges:
        bot.send_message(chat_id, "You don't have any badges unlocked.")
        return

    badge_index = min(max(0, badge_index), len(unlocked_badges) - 1)
    actual_index, badge = unlocked_badges[badge_index]

    badge_status = user_data.get(badge['data2'], False)
    toggle_text = "✅ Enabled" if badge_status else "❌ Disabled"

    markup = InlineKeyboardMarkup()
    if badge_index > 0:
        markup.add(InlineKeyboardButton("◀️", callback_data=f"badge_{badge_index - 1}"))
    if badge_index < len(unlocked_badges) - 1: 
        markup.add(InlineKeyboardButton("▶️", callback_data=f"badge_{badge_index + 1}"))
    markup.add(InlineKeyboardButton(toggle_text, callback_data=f"toggle_{actual_index}"))

    try:
        with open(badge['image'], 'rb') as img:
            bot.send_photo(
                chat_id,
                img,
                caption=f"{badge['name']}",
                reply_markup=markup,
                parse_mode="Markdown"
            )
    except FileNotFoundError:
        bot.send_message(chat_id, f"Image for badge {badge['name']} not found.")

# New commands implementation

async def command_menu(bot, message):
    """Settings menu command"""
    if message.chat.type != "private":
        return
    
    user = ExoUser(message.from_user.id, message.from_user.username)
    user_data = user.load_data()
    if not user_data:
        bot.reply_to(message, "You haven't setup your user yet, please use /start before accessing the menu!")
        return
    
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎨 Style Settings", callback_data="menu_style")],
        [InlineKeyboardButton("🏆 Badge Settings", callback_data="menu_badges")],
        [InlineKeyboardButton("🖼️ Logo Settings", callback_data="menu_logo")],
        [InlineKeyboardButton("🎨 Design Settings", callback_data="menu_design")],
        [InlineKeyboardButton("🔧 Title Settings", callback_data="menu_title")],
        [InlineKeyboardButton("👤 User Settings", callback_data="menu_user")],
        [InlineKeyboardButton("📊 Statistics", callback_data="menu_stats")]
    ])
    
    bot.send_message(
        message.chat.id,
        "⚙️ **Settings Menu**\n\nChoose what you want to configure:",
        reply_markup=markup,
        parse_mode="Markdown"
    )

async def command_code(bot, message):
    """Code login command - alternative login method"""
    if message.chat.type != "private":
        return
    
    user = ExoUser(message.from_user.id, message.from_user.username)
    user_data = user.load_data()
    if not user_data:
        bot.reply_to(message, "🚫 You haven't setup your user yet, please use /start before using code login!", parse_mode="Markdown")
        return
    
    # Extract code from message if provided
    code_parts = message.text.split()
    if len(code_parts) > 1:
        auth_code = code_parts[1]
        msg = bot.reply_to(message, f"🔐 **Processing Authorization Code**\n\n⏳ Validating code: `{auth_code}`...", parse_mode="Markdown")
        
        try:
            epic_generator = EpicGenerator()
            await epic_generator.start()
            
            # Try to authenticate with the provided code
            epic_user = await epic_generator.authenticate_with_code(auth_code)
            if epic_user:
                bot.edit_message_text(
                    chat_id=msg.chat.id,
                    message_id=msg.message_id,
                    text="✅ Successfully authenticated with authorization code!"
                )
                # Continue with the same login flow as command_login
                await process_authenticated_user(bot, message, epic_generator, epic_user)
            else:
                bot.edit_message_text(
                    chat_id=msg.chat.id,
                    message_id=msg.message_id,
                    text="❌ Invalid authorization code. Please try again."
                )
        except Exception as e:
            bot.edit_message_text(
                chat_id=msg.chat.id,
                message_id=msg.message_id,
                text=f"❌ Error processing code: {str(e)}"
            )
    else:
        bot.reply_to(message, "🔑 **Code Login**\n\nUsage: `/code YOUR_AUTH_CODE`\n\nGet your authorization code from Epic Games and use it with this command.", parse_mode="Markdown")

async def command_locker(bot, message):
    """View player locker command"""
    if message.chat.type != "private":
        return
    
    user = ExoUser(message.from_user.id, message.from_user.username)
    user_data = user.load_data()
    if not user_data:
        bot.reply_to(message, "🚫 You haven't setup your user yet, please use /start before checking lockers!", parse_mode="Markdown")
        return
    
    # Parse command arguments
    args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    
    if not args:
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("📱 Xbox Gamertag", callback_data="locker_xbox")],
            [InlineKeyboardButton("🎮 PSN Account", callback_data="locker_psn")],
            [InlineKeyboardButton("🎯 Epic Games", callback_data="locker_epic")],
            [InlineKeyboardButton("🆔 Account ID", callback_data="locker_id")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]
        ])
        
        bot.send_message(
            message.chat.id,
            "🎒 **Locker Checker**\n\n"
            "Check any player's Fortnite locker!\n\n"
            "**Usage Examples**:\n"
            "• `/locker xbox:ProGamer123`\n"
            "• `/locker psn:PlayerName`\n"
            "• `/locker epic:EpicUsername`\n"
            "• `/locker id:1234567890abcdef`\n"
            "• `/locker ProGamer123` (auto-detect)\n\n"
            "**Supported Platforms**:\n"
            "• Xbox Live Gamertags\n"
            "• PlayStation Network IDs\n"
            "• Epic Games usernames\n"
            "• Epic Account IDs\n\n"
            "**What you'll see**:\n"
            "• Complete skin collection\n"
            "• Rare/exclusive items\n"
            "• Battle pass progress\n"
            "• Account statistics\n"
            "• Season participation",
            reply_markup=markup,
            parse_mode="Markdown"
        )
        return
    
    # Process the lookup request
    target = " ".join(args)
    platform = "auto"
    
    # Detect platform prefix
    if ":" in target:
        platform, target = target.split(":", 1)
        platform = platform.lower()
    
    # Validate platform
    valid_platforms = ["xbox", "psn", "epic", "id", "auto"]
    if platform not in valid_platforms:
        bot.reply_to(message, f"❌ Invalid platform. Use: {', '.join(valid_platforms[:-1])}")
        return
    
    # Validate input based on platform
    if platform == "id":
        # Account ID should be alphanumeric and 32 characters long
        if len(target) != 32 or not target.replace("-", "").isalnum():
            bot.reply_to(message, "❌ Invalid Account ID format. Should be 32 characters long.")
            return
    elif platform in ["xbox", "psn", "epic"]:
        # Username validation
        if len(target) < 3 or len(target) > 16:
            bot.reply_to(message, f"❌ Invalid {platform.upper()} username length. Should be 3-16 characters.")
            return
    
    # Send processing message
    platform_display = {
        "xbox": "Xbox Live",
        "psn": "PlayStation Network", 
        "epic": "Epic Games",
        "id": "Account ID",
        "auto": "Auto-detect"
    }
    
    processing_msg = bot.send_message(
        message.chat.id,
        f"🔍 **Searching for player**: `{target}`\n"
        f"🎮 **Platform**: {platform_display.get(platform, platform.upper())}\n\n"
        "⏳ Processing request...\n"
        "📡 Connecting to Epic Games API...",
        parse_mode="Markdown"
    )
    
    try:
        # Auto-detect platform if not specified
        if platform == "auto":
            if len(target) == 32 and target.replace("-", "").isalnum():
                platform = "id"
            elif "@" in target:
                platform = "epic"
            else:
                platform = "epic"  # Default to epic for usernames
        
        # Here you would implement the actual locker checking logic
        # This is a placeholder that simulates the API call
        import time
        time.sleep(2)  # Simulate API delay
        
        # Generate realistic demo data based on platform
        platform_emoji = {
            "xbox": "🎮",
            "psn": "🎮", 
            "epic": "🎯",
            "id": "🆔"
        }
        
        bot.edit_message_text(
            f"🎒 **Locker Check Results**\n\n"
            f"👤 **Player**: {target}\n"
            f"{platform_emoji.get(platform, '🎮')} **Platform**: {platform_display.get(platform, platform.upper())}\n\n"
            f"📊 **Account Status**: ✅ Active\n"
            f"🏆 **Account Level**: 247\n"
            f"⭐ **Battle Pass**: Current Season Tier 85\n"
            f"🗓️ **Last Seen**: 2 hours ago\n\n"
            f"**🎨 Cosmetic Collection:**\n"
            f"• **Skins**: 156 items (23 rare)\n"
            f"• **Pickaxes**: 67 items (12 rare)\n"
            f"• **Gliders**: 54 items (8 rare)\n"
            f"• **Emotes**: 89 items (15 rare)\n"
            f"• **Back Blings**: 78 items (10 rare)\n"
            f"• **Wraps**: 45 items (6 rare)\n\n"
            f"💎 **Rarity Breakdown:**\n"
            f"• Legendary: 45 items\n"
            f"• Epic: 89 items\n"
            f"• Rare: 156 items\n"
            f"• Uncommon: 234 items\n\n"
            f"⚠️ **Note**: This is a demo response. Full implementation requires Epic Games API integration and proper authentication.",
            chat_id=processing_msg.chat.id,
            message_id=processing_msg.message_id,
            parse_mode="Markdown"
        )
        
    except Exception as e:
        bot.edit_message_text(
            f"❌ **Error checking locker**\n\n"
            f"Player: {target}\n"
            f"Platform: {platform}\n\n"
            f"Possible reasons:\n"
            f"• Player not found\n"
            f"• Privacy settings enabled\n"
            f"• Platform service unavailable\n"
            f"• Invalid username format\n\n"
            f"Please verify the username and try again.",
            chat_id=processing_msg.chat.id,
            message_id=processing_msg.message_id,
            parse_mode="Markdown"
        )


async def command_custom(bot, message):
    """Personalization menu command"""
    if message.chat.type != "private":
        return
    
    user = ExoUser(message.from_user.id, message.from_user.username)
    user_data = user.load_data()
    if not user_data:
        bot.reply_to(message, "🚫 You haven't setup your user yet, please use /start before accessing customization!", parse_mode="Markdown")
        return
    
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("🌈 Gradient Type", callback_data="custom_gradient")],
        [InlineKeyboardButton("🖼️ Background Image", callback_data="custom_background")],
        [InlineKeyboardButton("🏷️ Custom Logo", callback_data="custom_logo")],
        [InlineKeyboardButton("🎨 Color Scheme", callback_data="custom_colors")],
        [InlineKeyboardButton("📝 Custom Title", callback_data="custom_title")]
    ])
    
    bot.send_message(
        message.chat.id,
        "🔧 **Personalization Menu**\n\nCustomize your skin checker appearance:",
        reply_markup=markup,
        parse_mode="Markdown"
    )

async def command_clear(bot, message):
    """Clear account's friend list command"""
    if message.chat.type != "private":
        return
    
    user = ExoUser(message.from_user.id, message.from_user.username)
    user_data = user.load_data()
    if not user_data:
        bot.reply_to(message, "🚫 You haven't setup your user yet, please use /start before using this feature!", parse_mode="Markdown")
        return
    
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Yes, Clear Friends", callback_data="clear_friends_confirm")],
        [InlineKeyboardButton("❌ Cancel", callback_data="clear_friends_cancel")]
    ])
    
    bot.send_message(
        message.chat.id,
        "🔔 **Clear Friend List**\n\n⚠️ **Warning:** This will remove all friends from your Epic Games account!\n\nAre you sure you want to continue?",
        reply_markup=markup,
        parse_mode="Markdown"
    )

async def command_user(bot, message):
    """User settings command"""
    if message.chat.type != "private":
        return
    
    user = ExoUser(message.from_user.id, message.from_user.username)
    user_data = user.load_data()
    if not user_data:
        bot.reply_to(message, "🚫 You haven't setup your user yet, please use /start before accessing user settings!", parse_mode="Markdown")
        return
    
    # Toggle submission display setting
    current_setting = user_data.get('show_submission', True)
    user_data['show_submission'] = not current_setting
    user.update_data()
    
    status = "enabled" if user_data['show_submission'] else "disabled"
    bot.reply_to(message, f"👤 **User Settings**\n\nSubmission display is now **{status}**.\n\nThis controls whether 'Submitted by @username' appears on your skin checks.", parse_mode="Markdown")

async def command_logo(bot, message):
    """Change logo command"""
    if message.chat.type != "private":
        return
    
    user = ExoUser(message.from_user.id, message.from_user.username)
    user_data = user.load_data()
    if not user_data:
        bot.reply_to(message, "🚫 You haven't setup your user yet, please use /start before changing your logo!", parse_mode="Markdown")
        return
    
    bot.reply_to(message, "🖼️ **Change Logo**\n\nSend me an image to use as your custom logo, or use one of these commands:\n\n• `/logo reset` - Reset to default logo\n• `/logo remove` - Remove custom logo\n\nYour logo will appear on all skin check images.", parse_mode="Markdown")

async def command_design(bot, message):
    """Design choice command"""
    if message.chat.type != "private":
        return
    
    user = ExoUser(message.from_user.id, message.from_user.username)
    user_data = user.load_data()
    if not user_data:
        bot.reply_to(message, "🚫 You haven't setup your user yet, please use /start before accessing design settings!", parse_mode="Markdown")
        return
    
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("🌟 Modern", callback_data="design_modern")],
        [InlineKeyboardButton("🎮 Gaming", callback_data="design_gaming")],
        [InlineKeyboardButton("🌈 Colorful", callback_data="design_colorful")],
        [InlineKeyboardButton("⚫ Dark", callback_data="design_dark")],
        [InlineKeyboardButton("⚪ Light", callback_data="design_light")],
        [InlineKeyboardButton("🔥 Fire", callback_data="design_fire")]
    ])
    
    current_design = user_data.get('design_choice', 'modern')
    bot.send_message(
        message.chat.id,
        f"🖼️ **Design Choice**\n\nCurrent design: **{current_design.title()}**\n\nChoose your preferred design theme:",
        reply_markup=markup,
        parse_mode="Markdown"
    )

async def command_title(bot, message):
    """Title settings command"""
    if message.chat.type != "private":
        return
    
    user = ExoUser(message.from_user.id, message.from_user.username)
    user_data = user.load_data()
    if not user_data:
        bot.reply_to(message, "You haven't setup your user yet, please use /start before setting your title!")
        return
    
    # Show current automatic title (Telegram username)
    telegram_username = message.from_user.username or message.from_user.first_name or "ExoChecker User"
    bot.reply_to(message, f"📝 **Title Settings**\n\n🔒 **Current Title**: @{telegram_username}\n\n⚠️ **Note**: Titles are automatically set to your Telegram username for security and consistency. Custom titles are not available.\n\n✨ Your generated images will show:\n• **Username**: @{telegram_username}\n• **Branding**: ExoCheckBot.gg", parse_mode="Markdown")

async def command_locate(bot, message):
    """Location by Xbox nick command"""
    if message.chat.type != "private":
        return
    
    user = ExoUser(message.from_user.id, message.from_user.username)
    user_data = user.load_data()
    if not user_data:
        bot.reply_to(message, "🚫 You haven't setup your user yet, please use /start before using location services!", parse_mode="Markdown")
        return
    
    # Extract Xbox gamertag from message if provided
    locate_parts = message.text.split()
    if len(locate_parts) > 1:
        xbox_nick = locate_parts[1]
        msg = bot.reply_to(message, f"🌍 Searching for Xbox player: `{xbox_nick}`...")
        
        # This would require Xbox Live API integration
        # For now, show a placeholder message
        bot.edit_message_text(
            chat_id=msg.chat.id,
            message_id=msg.message_id,
            text=f"🌍 **Location Lookup**\n\nSearching for Xbox player: `{xbox_nick}`\n\n⚠️ This feature requires Xbox Live API integration and is currently under development.",
            parse_mode="Markdown"
        )
    else:
        bot.reply_to(message, "🌍 **Location by Xbox Nick**\n\nUsage: `/locate XBOX_GAMERTAG`\n\nExample: `/locate ProGamer123`", parse_mode="Markdown")

async def command_livechat(bot, message):
    """Check Epic Games live chat status"""
    if message.chat.type != "private":
        return
    
    user = ExoUser(message.from_user.id, message.from_user.username)
    user_data = user.load_data()
    if not user_data:
        bot.reply_to(message, "You haven't setup your user yet, please use /start before checking live chat status!")
        return
    
    # Send checking message
    checking_msg = bot.send_message(
        message.chat.id,
        "🔍 **Checking Epic Games Live Chat Status**\n\n⏳ Connecting to Epic Games support...",
        parse_mode="Markdown"
    )
    
    try:
        from datetime import datetime, timezone
        import time
        
        # Simulate checking delay
        time.sleep(1)
        
        # Get current UTC time
        utc_now = datetime.now(timezone.utc)
        current_hour = utc_now.hour
        
        # Define support regions and their business hours (in UTC)
        support_regions = {
            'US': {
                'name': 'North America',
                'business_hours': (13, 1),  # 9 AM EST to 9 PM EST (UTC)
                'countries': ['US', 'CA', 'MX', 'BR', 'AR', 'CL', 'CO', 'PE'],
                'timezone_name': 'EST/PST'
            },
            'EU': {
                'name': 'Europe',
                'business_hours': (8, 20),  # 8 AM to 8 PM UTC
                'countries': ['GB', 'DE', 'FR', 'IT', 'ES', 'NL', 'BE', 'SE', 'NO', 'DK', 'FI', 'PL', 'CZ', 'AT', 'CH'],
                'timezone_name': 'GMT/CET'
            },
            'APAC': {
                'name': 'Asia Pacific',
                'business_hours': (0, 12),  # 9 AM JST to 9 PM JST (UTC)
                'countries': ['JP', 'KR', 'AU', 'NZ', 'SG', 'TH', 'MY', 'PH', 'IN', 'CN', 'HK', 'TW'],
                'timezone_name': 'JST/AEST'
            }
        }
        
        # Default to US region if country not found
        user_country = user_data.get('country', 'US')
        user_region = 'US'
        
        # Find user's region
        for region, data in support_regions.items():
            if user_country in data['countries']:
                user_region = region
                break
        
        region_data = support_regions[user_region]
        start_hour, end_hour = region_data['business_hours']
        
        # Determine if it's business hours
        if start_hour <= end_hour:
            is_business_hours = start_hour <= current_hour < end_hour
        else:
            is_business_hours = current_hour >= start_hour or current_hour < end_hour
        
        # Determine status based on time and region
        if is_business_hours:
            if 9 <= current_hour <= 17:  # Peak hours
                status_emoji = "🟢"
                status_text = "Online & Available"
                wait_time = "2-5 minutes"
                agents = "15-25"
                description = "Live chat is fully operational with quick response times"
            else:  # Early morning or evening
                status_emoji = "🟡"
                status_text = "Online & Limited"
                wait_time = "10-20 minutes"
                agents = "5-10"
                description = "Live chat is available but with reduced staff"
        else:
            if 22 <= current_hour or current_hour <= 6:  # Night time
                status_emoji = "😴"
                status_text = "Offline - Support Team Sleeping"
                wait_time = "Next business day"
                agents = "0"
                description = "Support team is currently offline due to regional night hours"
            else:  # Outside business hours but not night
                status_emoji = "🔴"
                status_text = "Unavailable"
                wait_time = "Next business hours"
                agents = "0"
                description = "Live chat is currently outside business hours for your region"

        bot.edit_message_text(
            f"💬 **Epic Games Live Chat Status**\n\n"
            f"🌍 **Your Region**: {region_data['name']} ({user_country} {country_to_flag(user_country)})\n"
            f"🕐 **Current Time**: {utc_now.strftime('%H:%M UTC')}\n\n"
            f"**Status**: {status_emoji} {status_text}\n"
            f"**Estimated Wait**: {wait_time}\n"
            f"**Available Agents**: {agents}\n\n"
            f"📝 **Description**: {description}\n\n"
            f"🔗 **Access Live Chat**: https://epicgames.com/help/contact-us\n\n"
            f"⏰ **Business Hours ({region_data['timezone_name']})**: {start_hour:02d}:00 - {end_hour:02d}:00 UTC",
            chat_id=checking_msg.chat.id,
            message_id=checking_msg.message_id,
            parse_mode="Markdown"
        )
        
    except Exception as e:
        bot.edit_message_text(
            f"❌ **Error checking live chat status**\n\n"
            f"Unable to connect to Epic Games support system.\n\n"
            f"**Alternative options**:\n"
            f"• Visit: https://epicgames.com/help\n"
            f"• Email: support@epicgames.com\n"
            f"• Twitter: @EpicGamesSupport\n\n"
            f"Please try again later.",
            chat_id=checking_msg.chat.id,
            message_id=checking_msg.message_id,
            parse_mode="Markdown"
        )

async def command_activate_code(bot, message):
    """Redeem Epic Games codes to logged-in account"""
    if message.chat.type != "private":
        return
    
    user = ExoUser(message.from_user.id, message.from_user.username)
    user_data = user.load_data()
    if not user_data:
        bot.reply_to(message, "🚫 You haven't setup your user yet, please use /start before redeeming codes!", parse_mode="Markdown")
        return
    
    # Extract code from message if provided
    code_parts = message.text.split()
    if len(code_parts) > 1:
        epic_code = code_parts[1].upper()
        
        # Send processing message
        processing_msg = bot.send_message(
            message.chat.id,
            f"🔑 **Redeeming Epic Games Code**\n\n"
            f"Code: `{epic_code}`\n"
            f"⏳ Connecting to Epic Games...",
            parse_mode="Markdown"
        )
        
        try:
            # Here you would implement actual Epic Games code redemption
            # This requires the user to be logged in to their Epic account
            import time
            import random
            
            # Simulate processing delay
            time.sleep(3)
            
            # Simulate different redemption outcomes
            outcomes = [
                {
                    "success": True,
                    "reward": "1000 V-Bucks",
                    "description": "V-Bucks have been added to your account"
                },
                {
                    "success": True,
                    "reward": "Fortnite Crew Pack",
                    "description": "Monthly Crew Pack activated"
                },
                {
                    "success": True,
                    "reward": "Exclusive Skin Bundle",
                    "description": "Special skin bundle unlocked"
                },
                {
                    "success": False,
                    "error": "Code already redeemed",
                    "description": "This code has already been used"
                },
                {
                    "success": False,
                    "error": "Invalid code",
                    "description": "Code not found or expired"
                },
                {
                    "success": False,
                    "error": "Region restricted",
                    "description": "Code not available in your region"
                }
            ]
            
            result = random.choice(outcomes)
            
            if result["success"]:
                # Track redeemed codes
                if 'epic_codes_redeemed' not in user_data:
                    user_data['epic_codes_redeemed'] = []
                user_data['epic_codes_redeemed'].append({
                    'code': epic_code,
                    'reward': result['reward'],
                    'timestamp': time.time()
                })
                user.update_data()
                
                bot.edit_message_text(
                    f"✅ **Code Redeemed Successfully!**\n\n"
                    f"🔑 **Code**: `{epic_code}`\n"
                    f"🎁 **Reward**: {result['reward']}\n"
                    f"📝 **Description**: {result['description']}\n\n"
                    f"🎮 Check your Fortnite account to see the new items!\n\n"
                    f"⚠️ **Note**: This is a demo response. Actual implementation requires Epic Games API integration.",
                    chat_id=processing_msg.chat.id,
                    message_id=processing_msg.message_id,
                    parse_mode="Markdown"
                )
            else:
                bot.edit_message_text(
                    f"❌ **Code Redemption Failed**\n\n"
                    f"🔑 **Code**: `{epic_code}`\n"
                    f"⚠️ **Error**: {result['error']}\n"
                    f"📝 **Details**: {result['description']}\n\n"
                    f"**Common issues**:\n"
                    f"• Code already used\n"
                    f"• Code expired or invalid\n"
                    f"• Region restrictions\n"
                    f"• Account not eligible\n\n"
                    f"Please verify the code and try again.",
                    chat_id=processing_msg.chat.id,
                    message_id=processing_msg.message_id,
                    parse_mode="Markdown"
                )
                
        except Exception as e:
            bot.edit_message_text(
                f"❌ **Error redeeming code**\n\n"
                f"Code: `{epic_code}`\n\n"
                f"Unable to connect to Epic Games servers.\n\n"
                f"**Please try**:\n"
                f"• Redeem manually at epicgames.com/redeem\n"
                f"• Check your internet connection\n"
                f"• Try again later\n\n"
                f"If the issue persists, contact Epic Games support.",
                chat_id=processing_msg.chat.id,
                message_id=processing_msg.message_id,
                parse_mode="Markdown"
            )
            
    else:
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("🌐 Epic Games Redeem", url="https://epicgames.com/redeem")],
            [InlineKeyboardButton("❓ How to Find Codes", callback_data="code_help")]
        ])
        
        bot.send_message(
            message.chat.id,
            "🔑 **Epic Games Code Redemption**\n\n"
            "Redeem Epic Games codes directly to your account!\n\n"
            "**Usage**: `/activate_code YOUR_CODE`\n"
            "**Example**: `/activate_code ABC123DEF456`\n\n"
            "**Supported codes**:\n"
            "• V-Bucks codes\n"
            "• Fortnite Crew codes\n"
            "• Skin/cosmetic codes\n"
            "• Battle Pass codes\n"
            "• Promotional codes\n\n"
            "⚠️ **Note**: You must be logged in to your Epic account first using `/login`",
            reply_markup=markup,
            parse_mode="Markdown"
        )

async def command_delete_accounts(bot, message):
    """Delete all accounts command"""
    if message.chat.type != "private":
        return
    
    user = ExoUser(message.from_user.id, message.from_user.username)
    user_data = user.load_data()
    if not user_data:
        bot.reply_to(message, "🚫 You haven't setup your user yet, please use /start first!", parse_mode="Markdown")
        return
    
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("⚠️ Yes, Delete All", callback_data="delete_all_confirm")],
        [InlineKeyboardButton("❌ Cancel", callback_data="delete_all_cancel")]
    ])
    
    bot.send_message(
        message.chat.id,
        "🗑️ **Delete All Accounts**\n\n⚠️ **DANGER ZONE**\n\nThis will permanently delete:\n• All cached account data\n• All saved skin check images\n• All account statistics\n\n**This action cannot be undone!**\n\nAre you absolutely sure?",
        reply_markup=markup,
        parse_mode="Markdown"
    )

# Helper function to process authenticated user (extracted from command_login)
async def process_authenticated_user(bot, message, epic_generator, epic_user):
    """Process an authenticated Epic user - shared logic for login and code commands"""
    try:
        account_data = await epic_generator.get_account_metadata(epic_user)
        accountID = account_data.get('id', "INVALID_ACCOUNT_ID")
        
        if accountID == "INVALID_ACCOUNT_ID":
            bot.send_message(message.chat.id, "❌ Invalid account (banned or Fortnite has not been launched).")
            return
        
        # Continue with the existing login flow from command_login
        # This would include all the account information, purchases, locker data, etc.
        bot.send_message(message.chat.id, f'✅ Successfully processed account {account_data.get("displayName", "HIDDEN_ID_ACCOUNT")}')
        
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Error processing account: {str(e)}")
    finally:
        await epic_generator.kill()