import requests
import os
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class InstagramService:
    def __init__(self):
        self.access_token = os.getenv('INSTAGRAM_ACCESS_TOKEN')
        self.instagram_account_id = os.getenv('INSTAGRAM_PAGE_ID')
        self.facebook_page_id = os.getenv('FACEBOOK_PAGE_ID')
        self.base_url = "https://graph.facebook.com/v19.0"
        
        # Validate required credentials
        if not self.access_token:
            logger.error("INSTAGRAM_ACCESS_TOKEN not found in environment variables")
            raise ValueError("Instagram access token is required")
        if not self.instagram_account_id:
            logger.error("INSTAGRAM_PAGE_ID not found in environment variables")
            raise ValueError("Instagram page ID is required")
        
        logger.info(f"Instagram service initialized with account ID: {self.instagram_account_id}")
    
    def validate_connection(self) -> Dict:
        """Validate Instagram API connection and credentials"""
        try:
            # Test with a simple account info request
            result = self.get_account_info()
            if result.get('success', False):
                return {
                    'success': True,
                    'message': 'Instagram API connection successful',
                    'account_info': result.get('data', {})
                }
            else:
                return {
                    'success': False,
                    'message': f'Instagram API connection failed: {result.get("error", "Unknown error")}',
                    'account_info': None
                }
        except Exception as e:
            logger.error(f"Connection validation error: {e}")
            return {
                'success': False,
                'message': f'Connection validation error: {str(e)}',
                'account_info': None
            }
        
    def get_account_info(self) -> Dict:
        """Get Instagram business account information via Facebook Graph API"""
        try:
            url = f"{self.base_url}/{self.instagram_account_id}"
            params = {
                'fields': 'id,media_count,followers_count,follows_count,name,username,website,biography,profile_picture_url',
                'access_token': self.access_token
            }
            
            logger.info(f"Fetching account info from: {url}")
            response = requests.get(url, params=params, timeout=30)
            response.encoding = 'utf-8'
            
            # Check HTTP status
            if response.status_code != 200:
                logger.error(f"HTTP {response.status_code}: {response.text}")
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text}',
                    'data': None
                }
            
            # Parse JSON response
            try:
                data = response.json()
                
                # Check for Facebook API errors
                if 'error' in data:
                    logger.error(f"Facebook API error: {data['error']}")
                    return {
                        'success': False,
                        'error': data['error'].get('message', 'Unknown Facebook API error'),
                        'data': None
                    }
                
                # Map fields to match frontend expectations
                mapped_data = {
                    'id': data.get('id'),
                    'username': data.get('username'),
                    'name': data.get('name'),
                    'followers_count': data.get('followers_count', 0),
                    'follows_count': data.get('follows_count', 0),
                    'media_count': data.get('media_count', 0),
                    'biography': data.get('biography', ''),
                    'website': data.get('website', ''),
                    'profile_picture_url': data.get('profile_picture_url', '')
                }
                
                logger.info(f"Successfully fetched account info for: {mapped_data.get('username', 'Unknown')}")
                return {
                    'success': True,
                    'data': mapped_data,
                    'error': None
                }
                
            except ValueError as e:
                logger.error(f"JSON decode error: {e}")
                return {
                    'success': False,
                    'error': f'Invalid JSON response: {str(e)}',
                    'data': None
                }
                
        except requests.exceptions.Timeout:
            logger.error("Request timeout")
            return {
                'success': False,
                'error': 'Request timeout - Instagram API is not responding',
                'data': None
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            return {
                'success': False,
                'error': f'Network error: {str(e)}',
                'data': None
            }
        except Exception as e:
            logger.error(f"Unexpected error getting account info: {e}")
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}',
                'data': None
            }
    
    def get_media_list(self, limit: int = 25) -> Dict:
        """Get recent Instagram media posts via Facebook Graph API"""
        try:
            url = f"{self.base_url}/{self.instagram_account_id}/media"
            params = {
                'fields': 'id,media_type,media_url,thumbnail_url,permalink,caption,timestamp,like_count,comments_count,media_product_type,owner',
                'limit': limit,
                'access_token': self.access_token
            }
            
            logger.info(f"Fetching media list from: {url}")
            response = requests.get(url, params=params, timeout=30)
            response.encoding = 'utf-8'
            
            # Check HTTP status
            if response.status_code != 200:
                logger.error(f"HTTP {response.status_code}: {response.text}")
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text}',
                    'data': []
                }
            
            # Parse JSON response
            try:
                data = response.json()
                
                # Check for Facebook API errors
                if 'error' in data:
                    logger.error(f"Facebook API error: {data['error']}")
                    return {
                        'success': False,
                        'error': data['error'].get('message', 'Unknown Facebook API error'),
                        'data': []
                    }
                
                # Map and process media data
                media_list = []
                if 'data' in data and data['data']:
                    for item in data['data']:
                        mapped_item = {
                            'id': item.get('id'),
                            'media_type': item.get('media_type', 'IMAGE'),
                            'media_url': item.get('media_url', ''),
                            'thumbnail_url': item.get('thumbnail_url', ''),
                            'permalink': item.get('permalink', ''),
                            'caption': item.get('caption', ''),
                            'timestamp': item.get('timestamp', ''),
                            'like_count': item.get('like_count', 0),
                            'comments_count': item.get('comments_count', 0),
                            'media_product_type': item.get('media_product_type', ''),
                            'owner': item.get('owner', {})
                        }
                        media_list.append(mapped_item)
                
                logger.info(f"Successfully fetched {len(media_list)} media items")
                return {
                    'success': True,
                    'data': {
                        'data': media_list,
                        'paging': data.get('paging', {})
                    },
                    'error': None
                }
                
            except ValueError as e:
                logger.error(f"JSON decode error: {e}")
                return {
                    'success': False,
                    'error': f'Invalid JSON response: {str(e)}',
                    'data': []
                }
                
        except requests.exceptions.Timeout:
            logger.error("Request timeout")
            return {
                'success': False,
                'error': 'Request timeout - Instagram API is not responding',
                'data': []
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            return {
                'success': False,
                'error': f'Network error: {str(e)}',
                'data': []
            }
        except Exception as e:
            logger.error(f"Unexpected error getting media list: {e}")
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}',
                'data': []
            }
    
    def get_media_insights(self, media_id: str) -> Dict:
        """Get insights for a specific Instagram media post via Facebook Graph API"""
        url = f"{self.base_url}/{media_id}/insights"
        params = {
            'metric': 'engagement,impressions,reach,saved,video_views,likes,comments,shares',
            'access_token': self.access_token
        }
        
        response = requests.get(url, params=params)
        response.encoding = 'utf-8'
        
        import json
        try:
            return json.loads(response.text)
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return {'error': f'JSON decode error: {e}'}
    
    def get_account_insights(self, period: str = "day", days: int = 7) -> Dict:
        """Get Instagram account insights via Facebook Graph API"""
        since = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        until = datetime.now().strftime('%Y-%m-%d')
        
        url = f"{self.base_url}/{self.instagram_account_id}/insights"
        params = {
            'metric': 'impressions,reach,profile_views,website_clicks,follower_count,email_contacts,phone_call_clicks,text_message_clicks,get_directions_clicks',
            'period': period,
            'since': since,
            'until': until,
            'access_token': self.access_token
        }
        
        response = requests.get(url, params=params)
        response.encoding = 'utf-8'
        
        import json
        try:
            return json.loads(response.text)
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return {'error': f'JSON decode error: {e}'}
    
    def get_top_posts(self, limit: int = 10) -> Dict:
        """Get top performing posts based on engagement"""
        try:
            media_response = self.get_media_list(limit=50)
            
            # Check if the media request was successful
            if not media_response.get('success', False):
                logger.error(f"Failed to get media list: {media_response.get('error', 'Unknown error')}")
                return {
                    'success': False,
                    'error': media_response.get('error', 'Failed to fetch media data'),
                    'data': []
                }
            
            media_data = media_response.get('data', {})
            if 'data' not in media_data or not media_data['data']:
                logger.info("No media data available")
                return {
                    'success': True,
                    'data': [],
                    'error': None
                }
            
            # Sort by engagement (likes + comments)
            posts = []
            for post in media_data['data']:
                engagement = (post.get('like_count', 0) + post.get('comments_count', 0))
                posts.append({
                    'id': post['id'],
                    'caption': post.get('caption', '')[:100] + '...' if post.get('caption') else '',
                    'media_url': post.get('media_url', ''),
                    'permalink': post.get('permalink', ''),
                    'timestamp': post.get('timestamp', ''),
                    'likes': post.get('like_count', 0),
                    'comments': post.get('comments_count', 0),
                    'engagement': engagement,
                    'media_type': post.get('media_type', '')
                })
            
            sorted_posts = sorted(posts, key=lambda x: x['engagement'], reverse=True)[:limit]
            
            logger.info(f"Successfully processed {len(sorted_posts)} top posts")
            return {
                'success': True,
                'data': sorted_posts,
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Unexpected error getting top posts: {e}")
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}',
                'data': []
            }
    
    def get_hashtag_insights(self, hashtag_id: str) -> Dict:
        """Get insights for a specific hashtag"""
        url = f"{self.base_url}/{hashtag_id}"
        params = {
            'fields': 'id,name,media_count',
            'access_token': self.access_token
        }
        
        response = requests.get(url, params=params)
        response.encoding = 'utf-8'
        
        import json
        try:
            return json.loads(response.text)
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return {'error': f'JSON decode error: {e}'}
    
    def get_stories(self) -> Dict:
        """Get Instagram Stories"""
        url = f"{self.base_url}/{self.instagram_account_id}/stories"
        params = {
            'fields': 'id,media_type,media_url,thumbnail_url,timestamp',
            'access_token': self.access_token
        }
        
        response = requests.get(url, params=params)
        response.encoding = 'utf-8'
        
        import json
        try:
            return json.loads(response.text)
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return {'error': f'JSON decode error: {e}'}
    
    def get_comments(self, media_id: str) -> Dict:
        """Get comments for a specific media post"""
        url = f"{self.base_url}/{media_id}/comments"
        params = {
            'fields': 'id,text,timestamp,username,like_count,replies',
            'access_token': self.access_token
        }
        
        response = requests.get(url, params=params)
        response.encoding = 'utf-8'
        
        import json
        try:
            return json.loads(response.text)
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")
            return {'error': f'JSON decode error: {e}'}