import os
import asyncio
import aiohttp
from typing import Dict, List, Optional, Any, Union

"""
This module requires the fortnite-api package to be installed.
Install it with: pip install fortnite-api

Documentation: https://github.com/Fortnite-API/py-wrapper
"""

class FortniteAPIWrapper:
    """
    A wrapper for the Fortnite API to get game information.
    This class provides methods to retrieve cosmetics, shop items, stats, and more.
    
    Uses the official Fortnite-API.com Python wrapper.
    """
    
    def __init__(self):
        # Load API key from environment variables
        self.api_key = os.getenv('FORTNITE_API_KEY', "")
        self.client = None
        self.session = None
    
    async def initialize(self):
        """Initialize the Fortnite API client with a session"""
        try:
            import fortnite_api
            
            # Create a new session if one doesn't exist or is closed
            if self.session is None or self.session.closed:
                self.session = aiohttp.ClientSession()
                
            # Initialize the Fortnite API client with our session
            if self.client is None:
                self.client = fortnite_api.Client(
                    api_key=self.api_key,
                    session=self.session
                )
                print("Successfully initialized Fortnite API client")
            return self.client
            
        except ImportError:
            print("fortnite_api package not installed. Please install it with: pip install fortnite-api")
            raise
        except Exception as e:
            print(f"Error initializing Fortnite API: {e}")
            raise
    
    async def close(self):
        """Close the Fortnite API client and session"""
        if self.client:
            await self.client.close()
            self.client = None
            
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None
            print("Closed Fortnite API client session")
    
    async def get_cosmetics(self, cosmetic_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all cosmetics or filter by type.
        
        Args:
            cosmetic_type: Optional type of cosmetic to filter by (e.g., 'outfit', 'backpack')
            
        Returns:
            List of cosmetics
        """
        client = await self.initialize()
        try:
            cosmetics = await client.fetch_cosmetics_all()
            result = []
            
            for cosmetic in cosmetics.br:
                if cosmetic_type is None or cosmetic.type.value.lower() == cosmetic_type.lower():
                    result.append({
                        "id": cosmetic.id,
                        "name": cosmetic.name,
                        "description": cosmetic.description,
                        "type": cosmetic.type.value,
                        "rarity": cosmetic.rarity.value,
                        "series": cosmetic.series.value if cosmetic.series else None,
                        "images": {
                            "icon": cosmetic.images.icon,
                            "featured": cosmetic.images.featured,
                            "small_icon": cosmetic.images.small_icon
                        },
                        "introduction": {
                            "chapter": cosmetic.introduction.chapter if cosmetic.introduction else None,
                            "season": cosmetic.introduction.season if cosmetic.introduction else None
                        },
                        "added": str(cosmetic.added)
                    })
            
            return result
        except Exception as e:
            print(f"Error fetching cosmetics: {e}")
            return []
    
    async def get_shop(self) -> Dict[str, Any]:
        """
        Get the current item shop.
        
        Returns:
            Dictionary containing shop information
        """
        try:
            client = await self.initialize()
            # Use the correct method for the current version of the API
            shop = await client.fetch_shop_br()
            
            result = {
                "date": str(shop.date),
                "featured": [],
                "daily": [],
                "special_featured": [],
                "special_daily": []
            }
            
            # Process featured items
            if hasattr(shop, 'featured'):
                for entry in shop.featured.entries:
                    try:
                        for item in entry.items:
                            item_data = {
                                "id": item.id,
                                "name": item.name,
                                "price": entry.final_price,
                                "rarity": item.rarity.value,
                                "image": item.images.icon,
                                "type": item.type.value
                            }
                            result["featured"].append(item_data)
                    except AttributeError as e:
                        print(f"Skipping featured item due to missing attribute: {str(e)}")
                        continue
            
            # Process daily items
            if hasattr(shop, 'daily'):
                for entry in shop.daily.entries:
                    try:
                        for item in entry.items:
                            item_data = {
                                "id": item.id,
                                "name": item.name,
                                "price": entry.final_price,
                                "rarity": item.rarity.value,
                                "image": item.images.icon,
                                "type": item.type.value
                            }
                            result["daily"].append(item_data)
                    except AttributeError as e:
                        print(f"Skipping daily item due to missing attribute: {str(e)}")
                        continue
            
            # Process special featured items if available
            if hasattr(shop, 'special_featured'):
                for entry in shop.special_featured.entries:
                    try:
                        for item in entry.items:
                            item_data = {
                                "id": item.id,
                                "name": item.name,
                                "price": entry.final_price,
                                "rarity": item.rarity.value,
                                "image": item.images.icon,
                                "type": item.type.value
                            }
                            result["special_featured"].append(item_data)
                    except AttributeError as e:
                        print(f"Skipping special featured item due to missing attribute: {str(e)}")
                        continue
            
            # Process special daily items if available
            if hasattr(shop, 'special_daily'):
                for entry in shop.special_daily.entries:
                    try:
                        for item in entry.items:
                            item_data = {
                                "id": item.id,
                                "name": item.name,
                                "price": entry.final_price,
                                "rarity": item.rarity.value,
                                "image": item.images.icon,
                                "type": item.type.value
                            }
                            result["special_daily"].append(item_data)
                    except AttributeError as e:
                        print(f"Skipping special daily item due to missing attribute: {str(e)}")
                        continue
            
            return result
        except Exception as e:
            print(f"Error fetching shop: {e}")
            return {"error": str(e)}
    
    async def get_player_stats(self, account_id: str) -> Dict[str, Any]:
        """
        Get player statistics by account ID.
        
        Args:
            account_id: The Epic Games account ID
            
        Returns:
            Dictionary containing player statistics
        """
        client = await self.initialize()
        try:
            stats = await client.fetch_stats_by_account(account_id)
            
            result = {
                "account": {
                    "id": stats.account.id,
                    "name": stats.account.name
                },
                "battle_pass": {
                    "level": stats.battle_pass.level,
                    "progress": stats.battle_pass.progress
                },
                "stats": {
                    "all": {},
                    "keyboardmouse": {},
                    "gamepad": {},
                    "touch": {}
                }
            }
            
            # Process all input stats
            if stats.stats.all:
                result["stats"]["all"] = {
                    "overall": {
                        "wins": stats.stats.all.overall.wins,
                        "matches": stats.stats.all.overall.matches,
                        "kills": stats.stats.all.overall.kills,
                        "deaths": stats.stats.all.overall.deaths,
                        "kd": stats.stats.all.overall.kd,
                        "win_rate": stats.stats.all.overall.win_rate
                    }
                }
                
                # Add solo, duo, trio, squad stats if available
                if stats.stats.all.solo:
                    result["stats"]["all"]["solo"] = {
                        "wins": stats.stats.all.solo.wins,
                        "matches": stats.stats.all.solo.matches,
                        "kills": stats.stats.all.solo.kills,
                        "deaths": stats.stats.all.solo.deaths,
                        "kd": stats.stats.all.solo.kd,
                        "win_rate": stats.stats.all.solo.win_rate
                    }
                
                if stats.stats.all.duo:
                    result["stats"]["all"]["duo"] = {
                        "wins": stats.stats.all.duo.wins,
                        "matches": stats.stats.all.duo.matches,
                        "kills": stats.stats.all.duo.kills,
                        "deaths": stats.stats.all.duo.deaths,
                        "kd": stats.stats.all.duo.kd,
                        "win_rate": stats.stats.all.duo.win_rate
                    }
                
                if stats.stats.all.trio:
                    result["stats"]["all"]["trio"] = {
                        "wins": stats.stats.all.trio.wins,
                        "matches": stats.stats.all.trio.matches,
                        "kills": stats.stats.all.trio.kills,
                        "deaths": stats.stats.all.trio.deaths,
                        "kd": stats.stats.all.trio.kd,
                        "win_rate": stats.stats.all.trio.win_rate
                    }
                
                if stats.stats.all.squad:
                    result["stats"]["all"]["squad"] = {
                        "wins": stats.stats.all.squad.wins,
                        "matches": stats.stats.all.squad.matches,
                        "kills": stats.stats.all.squad.kills,
                        "deaths": stats.stats.all.squad.deaths,
                        "kd": stats.stats.all.squad.kd,
                        "win_rate": stats.stats.all.squad.win_rate
                    }
            
            # Similar processing for other input types if needed
            
            return result
        except Exception as e:
            print(f"Error fetching player stats: {e}")
            return {"error": str(e)}
    
    async def get_news(self) -> Dict[str, Any]:
        """
        Get the latest Fortnite news.
        
        Returns:
            Dictionary containing news information
        """
        try:
            client = await self.initialize()
            # Use the correct method for the current version of the API
            news = await client.fetch_news()
            
            result = {
                "battle_royale": [],
                "creative": [],
                "save_the_world": []
            }
            
            # Process Battle Royale news
            if hasattr(news, 'br') and news.br:
                for item in news.br.messages:
                    result["battle_royale"].append({
                        "title": item.title,
                        "body": item.body,
                        "image": item.image,
                        "time": str(item.date) if hasattr(item, 'date') else ""
                    })
            
            # Process Creative news
            if hasattr(news, 'creative') and news.creative:
                for item in news.creative.messages:
                    result["creative"].append({
                        "title": item.title,
                        "body": item.body,
                        "image": item.image,
                        "time": str(item.date) if hasattr(item, 'date') else ""
                    })
            
            # Process Save the World news
            if hasattr(news, 'stw') and news.stw:
                for item in news.stw.messages:
                    result["save_the_world"].append({
                        "title": item.title,
                        "body": item.body,
                        "image": item.image,
                        "time": str(item.date) if hasattr(item, 'date') else ""
                    })
            
            return result
        except Exception as e:
            print(f"Error fetching news: {e}")
            return {"error": str(e)}
    
    async def get_map(self) -> Dict[str, Any]:
        """
        Get the current Fortnite map information.
        
        Returns:
            Dictionary containing map information
        """
        client = await self.initialize()
        try:
            map_data = await client.fetch_map()
            
            result = {
                "images": {
                    "blank": map_data.images.blank,
                    "pois": map_data.images.pois
                },
                "pois": []
            }
            
            # Process POIs
            for poi in map_data.pois:
                result["pois"].append({
                    "id": poi.id,
                    "name": poi.name,
                    "location": {
                        "x": poi.location.x,
                        "y": poi.location.y,
                        "z": poi.location.z
                    }
                })
            
            return result
        except Exception as e:
            print(f"Error fetching map: {e}")
            return {"error": str(e)}