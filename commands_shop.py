import os
import json
import aiohttp
import asyncio
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from user import ExoUser
from fortnite_api_wrapper import FortniteAPIWrapper

"""
This module handles Fortnite shop and news commands.
It uses the fortnite-api package through our FortniteAPIWrapper.

Required package: pip install fortnite-api
"""

# Initialize the Fortnite API wrapper
fortnite_api = None

async def command_shop(bot, message):
    """Show the current Fortnite item shop"""
    if message.chat.type != "private":
        return
    
    user = ExoUser(message.from_user.id, message.from_user.username)
    user_data = user.load_data()
    if not user_data:
        bot.reply_to(message, "🚫 You haven't setup your user yet, please use /start before using shop features!", parse_mode="Markdown")
        return
    
    msg = bot.reply_to(message, "🛍️ *Loading Fortnite Item Shop...*\n\nPlease wait while we fetch the latest shop data.", parse_mode="Markdown")
    
    try:
        # Initialize the Fortnite API wrapper
        global fortnite_api
        if fortnite_api is None:
            fortnite_api = FortniteAPIWrapper()
            
        # Initialize the client with proper session management
        await fortnite_api.initialize()
            
        # Get shop data from Fortnite API
        shop_data = await fortnite_api.get_shop()
        
        if "error" in shop_data:
            bot.edit_message_text(
                chat_id=msg.chat.id,
                message_id=msg.message_id,
                text=f"❌ **Error Loading Shop**\n\nFailed to load the Fortnite Item Shop: {shop_data['error']}",
                parse_mode="Markdown"
            )
            return
        
        # Create shop overview message
        featured_count = len(shop_data["featured"])
        daily_count = len(shop_data["daily"])
        special_featured_count = len(shop_data["special_featured"])
        special_daily_count = len(shop_data["special_daily"])
        
        total_items = sum([
            sum([len(entry["items"]) for entry in shop_data["featured"]]),
            sum([len(entry["items"]) for entry in shop_data["daily"]]),
            sum([len(entry["items"]) for entry in shop_data["special_featured"]]),
            sum([len(entry["items"]) for entry in shop_data["special_daily"]])
        ])
        
        # Create shop overview message
        shop_date = shop_data["date"].split("T")[0]  # Format: YYYY-MM-DD
        
        shop_overview = (
            f"🛍️ **Fortnite Item Shop** - {shop_date}\n\n"
            f"📊 **Shop Overview:**\n"
            f"• ⭐ Featured Sections: {featured_count}\n"
            f"• 🔄 Daily Sections: {daily_count}\n"
            f"• 🎁 Special Featured Sections: {special_featured_count}\n"
            f"• 🎀 Special Daily Sections: {special_daily_count}\n"
            f"• 📦 Total Items: {total_items}\n\n"
            f"Select a category to browse items:"
        )
        
        # Create navigation buttons
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("⭐ Featured Items", callback_data="shop_featured_0")],
            [InlineKeyboardButton("🔄 Daily Items", callback_data="shop_daily_0")],
            [InlineKeyboardButton("🎁 Special Featured", callback_data="shop_special_featured_0")],
            [InlineKeyboardButton("🎀 Special Daily", callback_data="shop_special_daily_0")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_welcome")]
        ])
        
        bot.edit_message_text(
            chat_id=msg.chat.id,
            message_id=msg.message_id,
            text=shop_overview,
            reply_markup=markup,
            parse_mode="Markdown"
        )
        
    except Exception as e:
        bot.edit_message_text(
            chat_id=msg.chat.id,
            message_id=msg.message_id,
            text=f"❌ **Error**\n\nAn error occurred while loading the Fortnite Item Shop: {str(e)}",
            parse_mode="Markdown"
        )

async def handle_shop_navigation(bot, call):
    """Handle shop navigation callbacks"""
    data = call.data
    
    # Parse the callback data
    parts = data.split("_")
    if len(parts) < 3:
        return
    
    shop_type = parts[1]  # featured, daily, special_featured, special_daily
    page = int(parts[2])
    
    try:
        # Get shop data from Fortnite API
        shop_data = await fortnite_api.get_shop()
        
        if "error" in shop_data:
            bot.answer_callback_query(call.id, f"Error: {shop_data['error']}")
            return
        
        # Determine which shop section to display
        if shop_type == "featured":
            section_data = shop_data["featured"]
            section_title = "⭐ Featured Items"
        elif shop_type == "daily":
            section_data = shop_data["daily"]
            section_title = "🔄 Daily Items"
        elif shop_type == "special":
            if parts[2] == "featured":
                section_data = shop_data["special_featured"]
                section_title = "🎁 Special Featured Items"
                page = int(parts[3])
            else:  # daily
                section_data = shop_data["special_daily"]
                section_title = "🎀 Special Daily Items"
                page = int(parts[3])
        else:
            bot.answer_callback_query(call.id, "Invalid shop section")
            return
        
        # Check if section is empty
        if not section_data:
            bot.answer_callback_query(call.id, f"No items in {section_title}")
            return
        
        # Pagination: Show 1 item per page
        total_pages = len(section_data)
        if page >= total_pages:
            page = 0
        elif page < 0:
            page = total_pages - 1
        
        # Get current item
        current_item = section_data[page]
        
        # Create item details message
        item_details = f"🛍️ **{section_title}** (Page {page+1}/{total_pages})\n\n"
        
        # Add price information
        item_details += f"💰 **Price**: {current_item['final_price']} V-Bucks"
        if current_item['regular_price'] != current_item['final_price']:
            item_details += f" (Regular: {current_item['regular_price']} V-Bucks)"
        
        if current_item['bundle']:
            item_details += "\n🎁 **Bundle**: Yes"
        
        item_details += "\n\n📦 **Items in this offer**:\n"
        
        # Add items information
        for i, item in enumerate(current_item['items']):
            item_details += f"• {item['name']} ({item['type']})\n"
        
        # Create navigation buttons
        markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⬅️ Previous", callback_data=f"shop_{shop_type}_{page-1}"),
                InlineKeyboardButton("➡️ Next", callback_data=f"shop_{shop_type}_{page+1}")
            ],
            [InlineKeyboardButton("🔙 Back to Shop", callback_data="shop_back")]
        ])
        
        # Update the message
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=item_details,
            reply_markup=markup,
            parse_mode="Markdown"
        )
        
    except Exception as e:
        bot.answer_callback_query(call.id, f"Error: {str(e)}")

async def command_news(bot, message):
    """Show the latest Fortnite news"""
    if message.chat.type != "private":
        return
    
    user = ExoUser(message.from_user.id, message.from_user.username)
    user_data = user.load_data()
    if not user_data:
        bot.reply_to(message, "🚫 You haven't setup your user yet, please use /start before using news features!", parse_mode="Markdown")
        return
    
    msg = bot.reply_to(message, "📰 *Loading Fortnite News...*\n\nPlease wait while we fetch the latest news.", parse_mode="Markdown")
    
    try:
        # Initialize the Fortnite API wrapper if needed
        global fortnite_api
        if fortnite_api is None:
            fortnite_api = FortniteAPIWrapper()
            
        # Initialize the client with proper session management
        await fortnite_api.initialize()
            
        # Get news data from Fortnite API using the fortnite-api package
        news_data = await fortnite_api.get_news()
        
        if "error" in news_data:
            bot.edit_message_text(
                chat_id=msg.chat.id,
                message_id=msg.message_id,
                text=f"❌ **Error Loading News**\n\nFailed to load the Fortnite News: {news_data['error']}",
                parse_mode="Markdown"
            )
            return
        
        # Create news overview message
        br_count = len(news_data["battle_royale"])
        creative_count = len(news_data["creative"])
        stw_count = len(news_data["save_the_world"])
        
        news_overview = (
            f"📰 **Fortnite News**\n\n"
            f"📊 **News Overview:**\n"
            f"• 🎮 Battle Royale: {br_count} updates\n"
            f"• 🏗️ Creative: {creative_count} updates\n"
            f"• 🌍 Save The World: {stw_count} updates\n\n"
            f"Select a category to view news:"
        )
        
        # Create navigation buttons
        markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("🎮 Battle Royale", callback_data="news_br_0")],
            [InlineKeyboardButton("🏗️ Creative", callback_data="news_creative_0")],
            [InlineKeyboardButton("🌍 Save The World", callback_data="news_stw_0")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_welcome")]
        ])
        
        bot.edit_message_text(
            chat_id=msg.chat.id,
            message_id=msg.message_id,
            text=news_overview,
            reply_markup=markup,
            parse_mode="Markdown"
        )
        
    except Exception as e:
        bot.edit_message_text(
            chat_id=msg.chat.id,
            message_id=msg.message_id,
            text=f"❌ **Error**\n\nAn error occurred while loading the Fortnite News: {str(e)}",
            parse_mode="Markdown"
        )

async def handle_news_navigation(bot, call):
    """Handle news navigation callbacks"""
    data = call.data
    
    # Parse the callback data
    parts = data.split("_")
    if len(parts) < 3:
        return
    
    news_type = parts[1]  # br, creative, stw
    page = int(parts[2])
    
    try:
        # Get news data from Fortnite API
        news_data = await fortnite_api.get_news()
        
        if "error" in news_data:
            bot.answer_callback_query(call.id, f"Error: {news_data['error']}")
            return
        
        # Determine which news section to display
        if news_type == "br":
            section_data = news_data["battle_royale"]
            section_title = "🎮 Battle Royale News"
        elif news_type == "creative":
            section_data = news_data["creative"]
            section_title = "🏗️ Creative News"
        elif news_type == "stw":
            section_data = news_data["save_the_world"]
            section_title = "🌍 Save The World News"
        else:
            bot.answer_callback_query(call.id, "Invalid news section")
            return
        
        # Check if section is empty
        if not section_data:
            bot.answer_callback_query(call.id, f"No news in {section_title}")
            return
        
        # Pagination: Show 1 news item per page
        total_pages = len(section_data)
        if page >= total_pages:
            page = 0
        elif page < 0:
            page = total_pages - 1
        
        # Get current news item
        current_news = section_data[page]
        
        # Create news details message
        news_details = (
            f"📰 **{section_title}** (Page {page+1}/{total_pages})\n\n"
            f"📌 **{current_news['title']}**\n\n"
            f"{current_news['body']}\n\n"
            f"📅 {current_news['time'].split('T')[0]}"
        )
        
        # Create navigation buttons
        markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("⬅️ Previous", callback_data=f"news_{news_type}_{page-1}"),
                InlineKeyboardButton("➡️ Next", callback_data=f"news_{news_type}_{page+1}")
            ],
            [InlineKeyboardButton("🔙 Back to News", callback_data="news_back")]
        ])
        
        # Update the message
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=news_details,
            reply_markup=markup,
            parse_mode="Markdown"
        )
        
    except Exception as e:
        bot.answer_callback_query(call.id, f"Error: {str(e)}")

async def command_cosmetics(bot, message):
    """Search for Fortnite cosmetics"""
    if message.chat.type != "private":
        return
    
    user = ExoUser(message.from_user.id, message.from_user.username)
    user_data = user.load_data()
    if not user_data:
        bot.reply_to(message, "🚫 You haven't setup your user yet, please use /start before using cosmetic search!", parse_mode="Markdown")
        return
    
    # Extract search query from message if provided
    parts = message.text.split(maxsplit=1)
    if len(parts) > 1:
        search_query = parts[1].strip()
        msg = bot.reply_to(message, f"🔍 *Searching for cosmetic:* `{search_query}`...\n\nPlease wait while we search the database.", parse_mode="Markdown")
        
        try:
            # Get all cosmetics from Fortnite API
            cosmetics = await fortnite_api.get_cosmetics()
            
            # Filter cosmetics by search query
            search_query = search_query.lower()
            matching_cosmetics = [
                c for c in cosmetics 
                if search_query in c["name"].lower() or 
                   search_query in c["description"].lower() or
                   search_query in c["id"].lower()
            ]
            
            if not matching_cosmetics:
                bot.edit_message_text(
                    chat_id=msg.chat.id,
                    message_id=msg.message_id,
                    text=f"❌ **No Results Found**\n\nNo cosmetics found matching: `{search_query}`\n\nTry a different search term.",
                    parse_mode="Markdown"
                )
                return
            
            # Sort by name
            matching_cosmetics.sort(key=lambda x: x["name"])
            
            # Limit to first 10 results
            if len(matching_cosmetics) > 10:
                results_text = f"🔍 **Search Results** (showing 10 of {len(matching_cosmetics)} matches)\n\n"
                matching_cosmetics = matching_cosmetics[:10]
            else:
                results_text = f"🔍 **Search Results** ({len(matching_cosmetics)} matches)\n\n"
            
            # Create results message
            for i, cosmetic in enumerate(matching_cosmetics):
                results_text += f"{i+1}. **{cosmetic['name']}** ({cosmetic['type']})\n"
                results_text += f"   • Rarity: {cosmetic['rarity'].title()}\n"
                if cosmetic['series']:
                    results_text += f"   • Series: {cosmetic['series']}\n"
                results_text += f"   • Added: {cosmetic['added']}\n\n"
            
            # Create navigation buttons
            markup = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_welcome")]
            ])
            
            bot.edit_message_text(
                chat_id=msg.chat.id,
                message_id=msg.message_id,
                text=results_text,
                reply_markup=markup,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            bot.edit_message_text(
                chat_id=msg.chat.id,
                message_id=msg.message_id,
                text=f"❌ **Error**\n\nAn error occurred while searching for cosmetics: {str(e)}",
                parse_mode="Markdown"
            )
    else:
        # No search query provided
        bot.reply_to(
            message, 
            "🔍 **Cosmetic Search**\n\nUsage: `/cosmetics SEARCH_TERM`\n\nExample: `/cosmetics Peely`\n\nSearch for any Fortnite cosmetic by name or description.",
            parse_mode="Markdown"
        )