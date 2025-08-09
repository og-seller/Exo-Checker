# How to Get API Keys for Exo-Checker

This guide explains how to obtain the necessary API keys for the Exo-Checker bot.

## Fortnite API Key

The Fortnite API key is required for accessing Fortnite game data, including shop items, news, and player statistics.

### Steps to Get a Fortnite API Key:

1. Visit the official Fortnite-API website: [https://fortnite-api.com/](https://fortnite-api.com/)

2. Click on the "Register" button in the top-right corner to create an account.

3. Fill in the registration form with your details and submit.

4. After registration, log in to your account.

5. Navigate to the "Dashboard" section.

6. In your dashboard, you'll find your API key. It should look something like: `11111111-1111-1111-1111-111111111111`

7. Copy this API key and add it to your `.env` file:
   ```
   FORTNITE_API_KEY=your_api_key_here
   ```

### Usage Limits:

- Free tier: 10,000 requests per day
- Check the website for current rate limits and paid plans if you need more requests

## Xbox Live API Key

The Xbox Live API key is required for accessing Xbox Live data, including player profiles, presence information, and game data.

### Steps to Get an Xbox Live API Key:

1. Visit the XboxAPI website: [https://xbl.io](https://xbl.io)

2. Click on the "Sign Up" button to create an account.

3. Sign in with your Microsoft account.

4. After signing in, you'll be redirected to the dashboard.

5. In the dashboard, you'll find your API key under "Your API Key".

6. Copy this API key and add it to your `.env` file:
   ```
   XBOX_API_KEY=your_api_key_here
   ```

### Usage Limits:

- Free tier: Limited number of requests per day
- Check the website for current rate limits and paid plans if you need more requests

## Epic Games API

For Epic Games authentication, the bot uses predefined client tokens that are already included in the code. However, if these tokens expire, you'll need to update them.

### If Epic Games Tokens Expire:

1. The tokens are defined in `epic_auth.py`:
   ```python
   EPIC_API_SWITCH_TOKEN = "..."
   EPIC_API_IOS_CLIENT_TOKEN = "..."
   ```

2. If authentication stops working, you may need to update these tokens.

3. You can find updated tokens by:
   - Checking the Fortnite community forums
   - Looking at open-source Fortnite projects on GitHub
   - Contacting the developer for assistance

## Setting Up Environment Variables

After obtaining your API keys, you need to add them to your environment:

1. Create or edit the `.env` file in the root directory of the bot:
   ```
   FORTNITE_API_KEY=your_fortnite_api_key
   XBOX_API_KEY=your_xbox_api_key
   ```

2. Restart the bot for the changes to take effect.

## Troubleshooting

If you encounter issues with the API keys:

1. **Invalid API Key**: Make sure you've copied the full API key correctly without any extra spaces.

2. **Rate Limiting**: If you're getting rate limit errors, you may have exceeded your daily request limit.

3. **API Changes**: APIs occasionally change their authentication methods. Check the respective API documentation for updates.

4. **Epic Games Authentication Issues**: If Epic Games authentication stops working, the client tokens may have expired. Contact the developer for updated tokens.

For any other issues, please contact the developer for assistance.