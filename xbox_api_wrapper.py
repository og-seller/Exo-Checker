import os
import json
import aiohttp
import asyncio
from typing import Dict, List, Optional, Any, Union

"""
This module is designed to work with the @xboxreplay/xboxlive-api npm package.
When the package is installed via npm, you'll need to set up a Node.js bridge or API
to communicate with this package.

For now, we're using a direct API approach, but this should be replaced with the actual
npm package integration when available.

To install the package:
$ npm install @xboxreplay/xboxlive-api

Documentation: https://github.com/XboxReplay/xboxlive-api
"""

class XboxLiveAPIWrapper:
    """
    A wrapper for the Xbox Live API to get player information.
    This class provides methods to retrieve player profiles, presence, and location.
    
    This implementation will be replaced with the @xboxreplay/xboxlive-api npm package
    when it's properly installed and configured.
    """
    
    def __init__(self):
        # Base URL for the Xbox Live API
        self.base_url = "https://xbl.io/api/v2"
        self.api_key = os.getenv('XBOX_API_KEY', "")
        self.session = None
        self.headers = {
            "X-Authorization": self.api_key,
            "Content-Type": "application/json",
            "Accept-Language": "en-US",
            "Authorization": f"Bearer {self.api_key}"  # Try both header formats
        }
    
    async def initialize(self):
        """Initialize the Xbox Live API client session"""
        if self.session is None:
            self.session = aiohttp.ClientSession(headers=self.headers)
        return self
    
    async def close(self):
        """Close the Xbox Live API client session"""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None
    
    async def get_profile(self, gamertag: str) -> Dict[str, Any]:
        """
        Get Xbox Live profile information for a gamertag.
        Handles gamertags with spaces properly.
        
        Args:
            gamertag: The Xbox Live gamertag
            
        Returns:
            Dictionary containing profile information
        """
        try:
            if not self.session:
                await self.initialize()
                
            # URL encode the gamertag to handle spaces
            encoded_gamertag = gamertag.replace(" ", "%20")
            
            async with self.session.get(f"{self.base_url}/profile/gamertag/{encoded_gamertag}") as response:
                if response.status != 200:
                    error_text = await response.text()
                    print(f"Error getting Xbox profile: {response.status}")
                    print(f"Error response: {error_text}")
                    return {"error": f"Failed to get profile: {response.status}"}
                
                data = await response.json()
                return data.get("profileUsers", [{}])[0] if data.get("profileUsers") else {}
        except Exception as e:
            print(f"Exception getting Xbox profile: {str(e)}")
            return {"error": str(e)}
    
    async def get_presence(self, xuid: str) -> Dict[str, Any]:
        """
        Get Xbox Live presence information for a user.
        
        Args:
            xuid: The Xbox Live user ID
            
        Returns:
            Dictionary containing presence information
        """
        session = await self.initialize()
        try:
            async with session.get(f"{self.base_url}/presence/{xuid}") as response:
                if response.status != 200:
                    error_text = await response.text()
                    print(f"Error getting Xbox presence: {response.status}")
                    print(f"Error response: {error_text}")
                    return {"error": f"Failed to get presence: {response.status}"}
                
                data = await response.json()
                return data
        except Exception as e:
            print(f"Exception getting Xbox presence: {str(e)}")
            return {"error": str(e)}
    
    async def get_achievements(self, xuid: str, title_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get Xbox Live achievements for a user.
        
        Args:
            xuid: The Xbox Live user ID
            title_id: Optional game title ID to filter achievements
            
        Returns:
            Dictionary containing achievements information
        """
        session = await self.initialize()
        try:
            url = f"{self.base_url}/achievements/{xuid}"
            if title_id:
                url += f"/{title_id}"
                
            async with session.get(url) as response:
                if response.status != 200:
                    error_text = await response.text()
                    print(f"Error getting Xbox achievements: {response.status}")
                    print(f"Error response: {error_text}")
                    return {"error": f"Failed to get achievements: {response.status}"}
                
                data = await response.json()
                return data
        except Exception as e:
            print(f"Exception getting Xbox achievements: {str(e)}")
            return {"error": str(e)}
    
    async def get_game_clips(self, xuid: str) -> Dict[str, Any]:
        """
        Get Xbox Live game clips for a user.
        
        Args:
            xuid: The Xbox Live user ID
            
        Returns:
            Dictionary containing game clips information
        """
        session = await self.initialize()
        try:
            async with session.get(f"{self.base_url}/dvr/{xuid}/clips") as response:
                if response.status != 200:
                    error_text = await response.text()
                    print(f"Error getting Xbox game clips: {response.status}")
                    print(f"Error response: {error_text}")
                    return {"error": f"Failed to get game clips: {response.status}"}
                
                data = await response.json()
                return data
        except Exception as e:
            print(f"Exception getting Xbox game clips: {str(e)}")
            return {"error": str(e)}
    
    async def get_friends(self, xuid: str) -> Dict[str, Any]:
        """
        Get Xbox Live friends for a user.
        
        Args:
            xuid: The Xbox Live user ID
            
        Returns:
            Dictionary containing friends information
        """
        session = await self.initialize()
        try:
            async with session.get(f"{self.base_url}/friends/{xuid}") as response:
                if response.status != 200:
                    error_text = await response.text()
                    print(f"Error getting Xbox friends: {response.status}")
                    print(f"Error response: {error_text}")
                    return {"error": f"Failed to get friends: {response.status}"}
                
                data = await response.json()
                return data
        except Exception as e:
            print(f"Exception getting Xbox friends: {str(e)}")
            return {"error": str(e)}