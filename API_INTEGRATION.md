# API Integration Documentation

This document describes the integration of Xbox Live API and Fortnite API into the Exo-Checker bot.

## Xbox Live API Integration

The Xbox Live API integration allows the bot to retrieve player information from Xbox Live, including:

- Player profiles
- Player locations
- Online status
- Current game
- Gamerscore
- Friends list
- Game clips

### Implementation

The integration is implemented in the `xbox_api_wrapper.py` file, which provides a Python wrapper for the Xbox Live API. The wrapper is designed to work with the `@xboxreplay/xboxlive-api` npm package.

To install the npm package:
```bash
npm install @xboxreplay/xboxlive-api
```

The wrapper includes methods for:

- Getting player profiles
- Getting player presence (online status, current game)
- Getting player friends
- Getting recent players
- Getting game clips

### Usage

To use the Xbox Live API integration, you need to:

1. Set the `XBOX_API_KEY` environment variable in your `.env` file
2. Import the `XboxLiveAPIWrapper` class from `xbox_api_wrapper.py`
3. Create an instance of the `XboxLiveAPIWrapper` class
4. Initialize the client with `await xbox_api.initialize()`
5. Call the methods to retrieve player information

Example:

```python
from xbox_api_wrapper import XboxLiveAPIWrapper

# Create an instance of the Xbox API wrapper
xbox_api = XboxLiveAPIWrapper()
await xbox_api.initialize()

# Get player profile (handles spaces in gamertags correctly)
profile_data = await xbox_api.get_profile("gamertag with spaces")

# Get player presence
presence_data = await xbox_api.get_presence(xuid)

# Close the session when done
await xbox_api.close()
```

## Fortnite API Integration

The Fortnite API integration allows the bot to retrieve game information from Fortnite, including:

- Cosmetics
- Shop items
- Player statistics
- News
- Map information

### Implementation

The integration is implemented in the `fortnite_api_wrapper.py` file, which provides a Python wrapper for the official `fortnite-api` Python package.

To install the package:
```bash
pip install fortnite-api
```

The wrapper includes methods for:

- Getting cosmetics
- Getting shop items
- Getting player statistics
- Getting news
- Getting map information

### Usage

To use the Fortnite API integration, you need to:

1. Set the `FORTNITE_API_KEY` environment variable in your `.env` file
2. Import the `FortniteAPIWrapper` class from `fortnite_api_wrapper.py`
3. Create an instance of the `FortniteAPIWrapper` class
4. Initialize the client with `await fortnite_api.initialize()`
5. Call the methods to retrieve game information
6. Close the session when done with `await fortnite_api.close()`

Example:

```python
from fortnite_api_wrapper import FortniteAPIWrapper

# Create an instance of the Fortnite API wrapper
fortnite_api = FortniteAPIWrapper()

# Initialize the client
await fortnite_api.initialize()

# Get shop data
shop_data = await fortnite_api.get_shop()

# Get news data
news_data = await fortnite_api.get_news()

# Get cosmetics
cosmetics = await fortnite_api.get_cosmetics()

# Close the session when done
await fortnite_api.close()
```

## New Commands

The following new commands have been added to the bot:

- `/shop` - View the current Fortnite item shop
- `/news` - View the latest Fortnite news
- `/cosmetics` - Search for Fortnite cosmetics
- `/locate` - Location lookup by Xbox nickname (improved with Xbox Live API)

## Dependencies

The following dependencies have been added to the `requirements.txt` file:

- `fortnite-api` - Python wrapper for the Fortnite API
- `requests` - HTTP library for Python

## Environment Variables

The following environment variables have been added to the `.env.example` file:

- `XBOX_API_KEY` - API key for the Xbox Live API
- `FORTNITE_API_KEY` - API key for the Fortnite API

## Files Added/Modified

- `xbox_api_wrapper.py` - Python wrapper for the Xbox Live API (designed to work with @xboxreplay/xboxlive-api)
- `fortnite_api_wrapper.py` - Python wrapper for the Fortnite API (using the fortnite-api package)
- `commands_shop.py` - Commands for the Fortnite shop, news, and cosmetics
- `API_INTEGRATION.md` - Documentation for the API integration
- `telegram_bot.py` - Added new command handlers and imports
- `commands.py` - Updated the `/locate` command to use the Xbox Live API
- `epic_auth.py` - Updated Epic Games authentication to properly use bearer tokens
- `requirements.txt` - Added new dependencies
- `.env.example` - Added new environment variables

## Improvements Made

1. **Xbox Live API Integration**:
   - Added proper handling for gamertags with spaces
   - Improved error handling for API requests
   - Added session management to prevent resource leaks

2. **Fortnite API Integration**:
   - Updated to use the latest fortnite-api package
   - Added proper session management
   - Improved error handling for shop and news data
   - Added comprehensive error messages for users

3. **Epic Games Authentication**:
   - Fixed device code generation to properly use bearer tokens
   - Added fallback mechanisms for authentication
   - Improved error handling and user feedback

4. **General Improvements**:
   - Added proper session initialization and cleanup
   - Improved error handling throughout the codebase
   - Added documentation for API integration