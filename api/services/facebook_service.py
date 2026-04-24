import requests
import os
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FacebookService:
    def __init__(self):
        self.user_access_token = os.getenv('INSTAGRAM_ACCESS_TOKEN')
        self.facebook_page_id = os.getenv('FACEBOOK_PAGE_ID')
        self.base_url = "https://graph.facebook.com/v21.0"
        
        self._cache = {}
        self._cache_expiry = 600
        self._page_access_token = None
        
        if not self.user_access_token:
            logger.error("INSTAGRAM_ACCESS_TOKEN not found")
            raise ValueError("Access token is required")
        if not self.facebook_page_id:
            logger.error("FACEBOOK_PAGE_ID not found")
            raise ValueError("Facebook page ID is required")
        
        # Get Page Access Token on initialization
        self._page_access_token = self._get_page_token()
        if not self._page_access_token:
            logger.warning("Could not get Page Access Token, using user token")
            self._page_access_token = self.user_access_token
        
        logger.info(f"Facebook service initialized with page ID: {self.facebook_page_id}")
    
    @property
    def access_token(self):
        """Return the page access token"""
        return self._page_access_token
    
    def _get_cache_key(self, method_name, *args):
        return f"{method_name}_{hash(str(args))}"
    
    def _get_cached_result(self, cache_key):
        if cache_key in self._cache:
            result, timestamp = self._cache[cache_key]
            if datetime.now().timestamp() - timestamp < self._cache_expiry:
                logger.info(f"Using cached result for {cache_key}")
                return result
            else:
                del self._cache[cache_key]
        return None
    
    def _set_cached_result(self, cache_key, result):
        self._cache[cache_key] = (result, datetime.now().timestamp())
    
    def _get_page_token(self) -> Optional[str]:
        """Get Facebook Page Access Token"""
        try:
            url = f"{self.base_url}/{self.facebook_page_id}"
            params = {
                "fields": "access_token",
                "access_token": self.user_access_token
            }
            
            logger.info("Fetching Facebook Page Access Token...")
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                page_token = data.get("access_token")
                if page_token:
                    logger.info("Successfully retrieved Facebook Page Access Token")
                    return page_token
            else:
                logger.error(f"Failed to get page token: {response.status_code} - {response.text}")
            return None
        except Exception as e:
            logger.error(f"Error getting page token: {e}")
            return None
    
    def get_account_info(self) -> Dict:
        """Get Facebook Page information"""
        cache_key = self._get_cache_key('get_account_info')
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            return cached_result
            
        try:
            url = f"{self.base_url}/{self.facebook_page_id}"
            params = {
                'fields': 'id,name,username,fan_count,followers_count,about,website,picture',
                'access_token': self.access_token
            }
            
            logger.info(f"Fetching Facebook page info from: {url}")
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code != 200:
                logger.error(f"HTTP {response.status_code}: {response.text}")
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text}',
                    'data': None
                }
            
            data = response.json()
            
            if 'error' in data:
                logger.error(f"Facebook API error: {data['error']}")
                return {
                    'success': False,
                    'error': data['error'].get('message', 'Unknown error'),
                    'data': None
                }
            
            # Get post count separately
            posts_url = f"{self.base_url}/{self.facebook_page_id}/posts"
            posts_params = {
                'limit': 1,
                'summary': 'true',
                'access_token': self.access_token
            }
            posts_response = requests.get(posts_url, params=posts_params, timeout=10)
            media_count = 0
            if posts_response.status_code == 200:
                posts_data = posts_response.json()
                # Try to get count from summary or count data
                if 'summary' in posts_data:
                    media_count = posts_data['summary'].get('total_count', 0)
                else:
                    # Fallback: get all posts and count them
                    all_posts_params = {'limit': 100, 'access_token': self.access_token}
                    all_posts_response = requests.get(posts_url, params=all_posts_params, timeout=10)
                    if all_posts_response.status_code == 200:
                        all_posts_data = all_posts_response.json()
                        media_count = len(all_posts_data.get('data', []))
            
            mapped_data = {
                'id': data.get('id'),
                'username': data.get('username', ''),
                'name': data.get('name'),
                'followers_count': data.get('followers_count', data.get('fan_count', 0)),
                'follows_count': 0,
                'media_count': media_count,
                'biography': data.get('about', ''),
                'website': data.get('website', ''),
                'profile_picture_url': data.get('picture', {}).get('data', {}).get('url', '')
            }
            
            logger.info(f"Successfully fetched Facebook page info for: {mapped_data.get('name', 'Unknown')}")
            result = {
                'success': True,
                'data': mapped_data,
                'error': None
            }
            self._set_cached_result(cache_key, result)
            return result
            
        except Exception as e:
            logger.error(f"Error getting Facebook account info: {e}")
            return {
                'success': False,
                'error': f'Error: {str(e)}',
                'data': None
            }
    
    def get_media_list(self, limit: int = 25) -> Dict:
        """Get recent Facebook posts"""
        cache_key = self._get_cache_key('get_media_list', limit)
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            return cached_result
            
        try:
            url = f"{self.base_url}/{self.facebook_page_id}/posts"
            params = {
                'fields': 'id,message,created_time,full_picture,permalink_url,likes.summary(true),comments.summary(true),shares',
                'limit': limit,
                'access_token': self.access_token
            }
            
            logger.info(f"Fetching Facebook posts from: {url}")
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code != 200:
                logger.error(f"HTTP {response.status_code}: {response.text}")
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text}',
                    'data': []
                }
            
            data = response.json()
            
            if 'error' in data:
                logger.error(f"Facebook API error: {data['error']}")
                return {
                    'success': False,
                    'error': data['error'].get('message', 'Unknown error'),
                    'data': []
                }
            
            media_list = []
            if 'data' in data and data['data']:
                for item in data['data']:
                    mapped_item = {
                        'id': item.get('id'),
                        'media_type': 'IMAGE' if item.get('full_picture') else 'TEXT',
                        'media_url': item.get('full_picture', ''),
                        'thumbnail_url': item.get('full_picture', ''),
                        'permalink': item.get('permalink_url', ''),
                        'caption': item.get('message', ''),
                        'timestamp': item.get('created_time', ''),
                        'like_count': item.get('likes', {}).get('summary', {}).get('total_count', 0),
                        'comments_count': item.get('comments', {}).get('summary', {}).get('total_count', 0),
                        'shares_count': item.get('shares', {}).get('count', 0),
                        'media_product_type': 'FEED',
                        'owner': {}
                    }
                    media_list.append(mapped_item)
            
            # Get total post count
            media_count = len(media_list)
            
            logger.info(f"Successfully fetched {len(media_list)} Facebook posts")
            result = {
                'success': True,
                'data': {
                    'data': media_list,
                    'paging': data.get('paging', {}),
                    'media_count': media_count
                },
                'error': None
            }
            self._set_cached_result(cache_key, result)
            return result
            
        except Exception as e:
            logger.error(f"Error getting Facebook media list: {e}")
            return {
                'success': False,
                'error': f'Error: {str(e)}',
                'data': []
            }
    
    def get_media_insights(self, post_id: str) -> Dict:
        """Get insights for a specific Facebook post"""
        try:
            logger.info(f"Fetching Facebook post insights for: {post_id}")
            
            url = f"{self.base_url}/{post_id}/insights"
            params = {
                'metric': 'post_impressions,post_engaged_users,post_clicks,post_reactions_by_type_total',
                'access_token': self.access_token
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code != 200:
                logger.error(f"HTTP {response.status_code}: {response.text}")
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text}',
                    'data': None
                }
            
            data = response.json()
            
            if 'error' in data:
                logger.error(f"Facebook API error: {data['error']}")
                return {
                    'success': False,
                    'error': data['error'].get('message', 'Unknown error'),
                    'data': None
                }
            
            logger.info(f"Successfully fetched Facebook post insights")
            return {
                'success': True,
                'data': data.get('data', []),
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Error getting Facebook post insights: {e}")
            return {
                'success': False,
                'error': f'Error: {str(e)}',
                'data': None
            }
    
    def get_page_insights(self, metrics: str = None, period: str = 'day', days: int = 7) -> Dict:
        """Get Facebook Page insights"""
        try:
            since = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            until = datetime.now().strftime('%Y-%m-%d')
            
            url = f"{self.base_url}/{self.facebook_page_id}/insights"
            params = {
                'metric': metrics or 'page_impressions,page_engaged_users,page_post_engagements,page_fans',
                'period': period,
                'since': since,
                'until': until,
                'access_token': self.access_token
            }
            
            logger.info(f"Fetching Facebook page insights")
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code != 200:
                logger.error(f"HTTP {response.status_code}: {response.text}")
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}: {response.text}',
                    'data': None
                }
            
            data = response.json()
            
            if 'error' in data:
                logger.error(f"Facebook API error: {data['error']}")
                return {
                    'success': False,
                    'error': data['error'].get('message', 'Unknown error'),
                    'data': None
                }
            
            logger.info(f"Successfully fetched Facebook page insights")
            return {
                'success': True,
                'data': data.get('data', []),
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Error getting Facebook page insights: {e}")
            return {
                'success': False,
                'error': f'Error: {str(e)}',
                'data': None
            }
    
    def get_top_posts(self, limit: int = 10) -> Dict:
        """Get top performing Facebook posts"""
        try:
            media_response = self.get_media_list(limit=50)
            
            if not media_response.get('success', False):
                return {
                    'success': False,
                    'error': media_response.get('error', 'Failed to fetch posts'),
                    'data': []
                }
            
            media_data = media_response.get('data', {})
            if 'data' not in media_data or not media_data['data']:
                return {
                    'success': True,
                    'data': [],
                    'error': None
                }
            
            posts = []
            for post in media_data['data']:
                engagement = (post.get('like_count', 0) + 
                            post.get('comments_count', 0) + 
                            post.get('shares_count', 0))
                posts.append({
                    'id': post['id'],
                    'caption': post.get('caption', '')[:100] + '...' if post.get('caption') else '',
                    'media_url': post.get('media_url', ''),
                    'permalink': post.get('permalink', ''),
                    'timestamp': post.get('timestamp', ''),
                    'likes': post.get('like_count', 0),
                    'comments': post.get('comments_count', 0),
                    'shares': post.get('shares_count', 0),
                    'engagement': engagement,
                    'media_type': post.get('media_type', '')
                })
            
            sorted_posts = sorted(posts, key=lambda x: x['engagement'], reverse=True)[:limit]
            
            logger.info(f"Successfully processed {len(sorted_posts)} top Facebook posts")
            return {
                'success': True,
                'data': sorted_posts,
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Error getting top Facebook posts: {e}")
            return {
                'success': False,
                'error': f'Error: {str(e)}',
                'data': []
            }
