# Exo-Checker Bot Commands

This document provides a comprehensive overview of all available commands in the Exo-Checker Bot.

## Basic Commands

### `/start`
- **Description**: Register to Exo-Checker and setup your user profile
- **Usage**: `/start`
- **Note**: Only needs to be used once when first using the bot

### `/help`
- **Description**: Display comprehensive help information and command list
- **Usage**: `/help`
- **Features**: Shows all available commands with descriptions

## Authentication & Login

### `/login`
- **Description**: Skincheck your Epic Games Fortnite account using device code
- **Usage**: `/login`
- **Process**: 
  1. Bot generates a login link
  2. User logs in through Epic Games website
  3. Bot processes account data and displays comprehensive information

### `/code`
- **Description**: Alternative login method using authorization code
- **Usage**: `/code YOUR_AUTH_CODE`
- **Example**: `/code ABC123DEF456`
- **Note**: Get authorization code from Epic Games and use with this command

## Settings & Configuration

### `/menu`
- **Description**: Access main settings menu with interactive buttons
- **Usage**: `/menu`
- **Features**: 
  - Style Settings
  - Badge Settings
  - Logo Settings
  - Design Settings
  - Title Settings
  - User Settings
  - Statistics

### `/style`
- **Description**: Choose your skincheck rendering style
- **Usage**: `/style`
- **Available Styles**:
  - Exo (Default)
  - Easy
  - Raika
  - Kayy
  - Storm

### `/custom`
- **Description**: Access personalization menu
- **Usage**: `/custom`
- **Features**:
  - Gradient Type (Normal, Rainbow, Golden, Silver)
  - Background Image
  - Custom Logo
  - Color Scheme
  - Custom Title

### `/design`
- **Description**: Choose design theme for your skinchecks
- **Usage**: `/design`
- **Available Designs**:
  - Modern
  - Gaming
  - Colorful
  - Dark
  - Light
  - Fire

## Account Management

### `/badges`
- **Description**: Toggle your achieved badges on skinchecks
- **Usage**: `/badges`
- **Available Badges**:
  - Alpha Tester 1, 2, 3
  - Epic Games Badge
  - Achievement Badges

### `/user`
- **Description**: Toggle user display settings
- **Usage**: `/user`
- **Function**: Enable/disable showing "Submitted by @username" on skinchecks

### `/stats`
- **Description**: View your account statistics and settings
- **Usage**: `/stats`
- **Information Displayed**:
  - Accounts checked
  - Current style
  - Badge status
  - User settings

## Customization

### `/logo`
- **Description**: Change your custom logo
- **Usage**: 
  - `/logo` - Instructions for uploading custom logo
  - `/logo reset` - Reset to default logo
  - `/logo remove` - Remove custom logo
- **Note**: Send an image after using the command to set as logo

### `/title`
- **Description**: Set custom title for your skinchecks
- **Usage**: `/title YOUR_NEW_TITLE`
- **Example**: `/title Pro Fortnite Player`
- **Limit**: Maximum 50 characters

## Viewing & Checking

### `/locker`
- **Description**: View specific player locker (requires player to be logged in)
- **Usage**: `/locker USERNAME`
- **Example**: `/locker Ninja`
- **Note**: Feature requires Epic Games API integration

### `/rocket`
- **Description**: Rocket League inventory checker
- **Usage**: `/rocket`
- **Status**: Currently under development
- **Planned Features**:
  - Rocket League inventory checking
  - Item rarity analysis
  - Trading value estimation

## Utility Commands

### `/clear`
- **Description**: Clear your Epic Games account's friend list
- **Usage**: `/clear`
- **Warning**: This will remove ALL friends from your Epic Games account
- **Confirmation**: Requires user confirmation before execution

### `/locate`
- **Description**: Location lookup by Xbox gamertag
- **Usage**: `/locate XBOX_GAMERTAG`
- **Example**: `/locate ProGamer123`
- **Note**: Requires Xbox Live API integration (under development)

### `/livechat`
- **Description**: Toggle live chat status for real-time notifications
- **Usage**: `/livechat`
- **Function**: Enable/disable real-time notifications and updates

## Special Commands

### `/activate_code`
- **Description**: Activate promotional codes for special features
- **Usage**: `/activate_code YOUR_CODE`
- **Example**: `/activate_code ALPHA2024`
- **Available Codes**:
  - `ALPHA2024` - Alpha Tester 3 Badge
  - `EPIC2024` - Epic Games Badge
  - `PREMIUM` - Premium Style Unlock
  - `GRADIENT` - Golden Gradient

### `/delete_accounts`
- **Description**: Delete all cached account data (DANGER ZONE)
- **Usage**: `/delete_accounts`
- **Warning**: Permanently deletes:
  - All cached account data
  - All saved skin check images
  - All account statistics
- **Note**: This action cannot be undone

## Interactive Features

Many commands feature interactive buttons for easy navigation:

- **Style Selection**: Navigate through styles with ◀️ ▶️ buttons
- **Badge Management**: Toggle badges with ✅/❌ buttons
- **Menu Navigation**: Access different settings through button menus
- **Confirmation Dialogs**: Safety confirmations for destructive actions

## Security & Privacy

- **No Data Storage**: Account credentials are never stored
- **Private Processing**: All authentication is handled securely
- **User Control**: Users have full control over their data and settings

## Developer Information

**Developed by**: ExoCheckBot.gg

## Notes

- All commands work only in private messages with the bot
- Some features require Epic Games API integration and may be under development
- User must be registered (use `/start`) before using most commands
- Interactive features use callback buttons for better user experience

For support or questions, use the `/help` command for the most up-to-date information.