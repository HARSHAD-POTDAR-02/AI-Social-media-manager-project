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
        
        # Simple cache with 5-minute expiry
        self._cache = {}
        self._cache_expiry = 600  # 10 minutes
        
        # Validate required credentials
        if not self.access_token:
            logger.error("INSTAGRAM_ACCESS_TOKEN not found in environment variables")
            raise ValueError("Instagram access token is required")
        if not self.instagram_account_id:
            logger.error("INSTAGRAM_PAGE_ID not found in environment variables")
            raise ValueError("Instagram page ID is required")
        
        logger.info(f"Instagram service initialized with account ID: {self.instagram_account_id}")
    
    def _get_cache_key(self, method_name, *args):
        """Generate cache key for method and arguments"""
        return f"{method_name}_{hash(str(args))}"
    
    def _get_cached_result(self, cache_key):
        """Get cached result if not expired"""
        if cache_key in self._cache:
            result, timestamp = self._cache[cache_key]
            if datetime.now().timestamp() - timestamp < self._cache_expiry:
                logger.info(f"Using cached result for {cache_key}")
                return result
            else:
                del self._cache[cache_key]
        return None
    
    def _set_cached_result(self, cache_key, result):
        """Cache the result with timestamp"""
        self._cache[cache_key] = (result, datetime.now().timestamp())
    
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
        cache_key = self._get_cache_key('get_account_info')
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            return cached_result
            
        try:
            url = f"{self.base_url}/{self.instagram_account_id}"
            params = {
                'fields': 'id,media_count,followers_count,follows_count,name,username,website,biography,profile_picture_url',
                'access_token': self.access_token
            }
            
            logger.info(f"Fetching account info from: {url}")
            response = requests.get(url, params=params, timeout=10)
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
                result = {
                    'success': True,
                    'data': mapped_data,
                    'error': None
                }
                self._set_cached_result(cache_key, result)
                return result
                
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
        cache_key = self._get_cache_key('get_media_list', limit)
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            return cached_result
            
        try:
            url = f"{self.base_url}/{self.instagram_account_id}/media"
            params = {
                'fields': 'id,media_type,media_url,thumbnail_url,permalink,caption,timestamp,like_count,comments_count,media_product_type,owner',
                'limit': limit,
                'access_token': self.access_token
            }
            
            logger.info(f"Fetching media list from: {url}")
            response = requests.get(url, params=params, timeout=10)
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
                result = {
                    'success': True,
                    'data': {
                        'data': media_list,
                        'paging': data.get('paging', {})
                    },
                    'error': None
                }
                self._set_cached_result(cache_key, result)
                return result
                
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
        try:
            logger.info(f"Fetching media insights for: {media_id}")

            # Request commonly-available post insights (exclude video_views entirely)
            url = f"{self.base_url}/{media_id}/insights"
            params = {
                'metric': 'likes,comments,shares,saved,reach',
                'access_token': self.access_token
            }

            response = requests.get(url, params=params, timeout=10)
            response.encoding = 'utf-8'

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
                    'error': data['error'].get('message', 'Unknown Facebook API error'),
                    'data': None
                }
            
            logger.info(f"Successfully fetched media insights for: {media_id}")
            logger.info(f"Media insights data: {data.get('data', [])}")
            return {
                'success': True,
                'data': data.get('data', []),
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Unexpected error getting media insights: {e}")
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}',
                'data': None
            }
    
    def get_audience_demographics(self) -> Dict:
        """Get real audience demographics via Facebook Graph API"""
        try:
            url = f"{self.base_url}/{self.instagram_account_id}/insights"
            params = {
                'metric': 'audience_gender_age',
                'period': 'lifetime',
                'access_token': self.access_token
            }
            
            logger.info(f"Fetching audience demographics from: {url}")
            response = requests.get(url, params=params, timeout=10)
            response.encoding = 'utf-8'
            
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
                    'error': data['error'].get('message', 'Unknown Facebook API error'),
                    'data': None
                }
            
            logger.info(f"Successfully fetched audience demographics")
            return {
                'success': True,
                'data': data.get('data', []),
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Unexpected error getting audience demographics: {e}")
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}',
                'data': None
            }
    
    def get_account_insights(self, period: str = "day", days: int = 7, metrics: str = None) -> Dict:
        """Get Instagram account insights via Facebook Graph API v23.0"""
        try:
            since = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
            until = datetime.now().strftime('%Y-%m-%d')
            
            # Update to v23.0
            url = f"https://graph.facebook.com/v23.0/{self.instagram_account_id}/insights"
            params = {
                'metric': metrics or 'reach,profile_views,accounts_engaged',
                'period': period,
                'since': since,
                'until': until,
                'metric_type': 'total_value',
                'access_token': self.access_token
            }
            
            logger.info(f"Fetching account insights from: {url}")
            response = requests.get(url, params=params, timeout=10)
            response.encoding = 'utf-8'
            
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
                    'error': data['error'].get('message', 'Unknown Facebook API error'),
                    'data': None
                }
            
            logger.info(f"Successfully fetched account insights")
            return {
                'success': True,
                'data': data.get('data', []),
                'error': None
            }
            
        except Exception as e:
            logger.error(f"Unexpected error getting account insights: {e}")
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}',
                'data': None
            }
    
    def get_daily_insights(self, days: int = 7) -> Dict:
        """Get daily Instagram insights for graphs"""
        cache_key = self._get_cache_key('get_daily_insights', days)
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            return cached_result
            
        try:
            insights_data = []
            
            # Get media from the last N days
            media_response = self.get_media_list(limit=100)
            if not media_response.get('success'):
                return {'success': False, 'error': 'Failed to fetch media', 'data': []}
            
            posts = media_response.get('data', {}).get('data', [])
            
            # Group posts by day
            daily_data = {}
            for i in range(days):
                date = datetime.now() - timedelta(days=i)
                date_str = date.strftime('%Y-%m-%d')
                daily_data[date_str] = {
                    'date': date_str,
                    'engagement': 0,
                    'reach': 0,
                    'impressions': 0,
                    'views': 0,
                    'saves': 0,
                    'shares': 0,
                    'likes': 0,
                    'comments': 0,
                    'posts_count': 0
                }
            
            # Aggregate data from posts
            for post in posts:
                if post.get('timestamp'):
                    post_date = datetime.fromisoformat(post['timestamp'].replace('Z', '+00:00'))
                    date_str = post_date.strftime('%Y-%m-%d')
                    
                    if date_str in daily_data:
                        daily_data[date_str]['likes'] += post.get('like_count', 0)
                        daily_data[date_str]['comments'] += post.get('comments_count', 0)
                        daily_data[date_str]['engagement'] += (post.get('like_count', 0) + post.get('comments_count', 0))
                        daily_data[date_str]['posts_count'] += 1
                        
                        # Get insights for individual posts if available
                        insights_response = self.get_media_insights(post['id'])
                        if insights_response.get('success') and insights_response.get('data'):
                            for metric in insights_response['data']:
                                if metric['name'] == 'reach':
                                    daily_data[date_str]['reach'] += metric['values'][0]['value']
                                elif metric['name'] == 'impressions':
                                    daily_data[date_str]['impressions'] += metric['values'][0]['value']
                                elif metric['name'] == 'saved':
                                    daily_data[date_str]['saves'] += metric['values'][0]['value']
                                elif metric['name'] == 'video_views' and post.get('media_type') == 'VIDEO':
                                    daily_data[date_str]['views'] += metric['values'][0]['value']
            
            # Convert to list and sort by date
            insights_data = sorted(daily_data.values(), key=lambda x: x['date'])
            
            result = {
                'success': True,
                'data': insights_data,
                'error': None
            }
            self._set_cached_result(cache_key, result)
            return result
            
        except Exception as e:
            logger.error(f"Error getting daily insights: {e}")
            return {
                'success': False,
                'error': f'Error getting daily insights: {str(e)}',
                'data': []
            }
    
    def get_hourly_engagement(self) -> Dict:
        """Get engagement patterns by hour of day"""
        cache_key = self._get_cache_key('get_hourly_engagement')
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            return cached_result
            
        try:
            # Initialize hourly buckets
            hourly_data = {i: {'hour': i, 'engagement': 0, 'posts': 0} for i in range(24)}
            
            # Get recent posts
            media_response = self.get_media_list(limit=100)
            if not media_response.get('success'):
                return {'success': False, 'error': 'Failed to fetch media', 'data': []}
            
            posts = media_response.get('data', {}).get('data', [])
            
            # Aggregate engagement by hour
            for post in posts:
                if post.get('timestamp'):
                    post_time = datetime.fromisoformat(post['timestamp'].replace('Z', '+00:00'))
                    hour = post_time.hour
                    
                    hourly_data[hour]['engagement'] += (post.get('like_count', 0) + post.get('comments_count', 0))
                    hourly_data[hour]['posts'] += 1
            
            # Calculate average engagement per post for each hour
            for hour in hourly_data:
                if hourly_data[hour]['posts'] > 0:
                    hourly_data[hour]['avg_engagement'] = hourly_data[hour]['engagement'] / hourly_data[hour]['posts']
                else:
                    hourly_data[hour]['avg_engagement'] = 0
            
            result = {
                'success': True,
                'data': list(hourly_data.values()),
                'error': None
            }
            self._set_cached_result(cache_key, result)
            return result
            
        except Exception as e:
            logger.error(f"Error getting hourly engagement: {e}")
            return {
                'success': False,
                'error': f'Error getting hourly engagement: {str(e)}',
                'data': []
            }
    
    def get_growth_metrics(self, days: int = 30) -> Dict:
        """Get follower growth metrics over time"""
        cache_key = self._get_cache_key('get_growth_metrics', days)
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            return cached_result
            
        try:
            # Get current follower count
            account_info = self.get_account_info()
            if not account_info.get('success'):
                return {'success': False, 'error': 'Failed to fetch account info', 'data': []}
            
            current_followers = account_info['data'].get('followers_count', 0)
            
            # For Instagram Graph API v23.0, we can get follower count insights
            url = f"https://graph.facebook.com/v23.0/{self.instagram_account_id}/insights"
            params = {
                'metric': 'follower_count',
                'period': 'day',
                'since': (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d'),
                'until': datetime.now().strftime('%Y-%m-%d'),
                'access_token': self.access_token
            }
            
            response = requests.get(url, params=params, timeout=10)
            growth_data = []
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and data['data']:
                    for metric in data['data']:
                        if metric['name'] == 'follower_count' and 'values' in metric:
                            for value in metric['values']:
                                growth_data.append({
                                    'date': value.get('end_time', '').split('T')[0],
                                    'followers': value.get('value', 0)
                                })
            
            # If no historical data, generate based on current count
            if not growth_data:
                # Estimate historical growth
                for i in range(days, -1, -1):
                    date = datetime.now() - timedelta(days=i)
                    # Simple linear growth assumption
                    estimated_followers = int(current_followers - (i * (current_followers * 0.001)))
                    growth_data.append({
                        'date': date.strftime('%Y-%m-%d'),
                        'followers': max(0, estimated_followers)
                    })
            
            result = {
                'success': True,
                'data': growth_data,
                'current_followers': current_followers,
                'error': None
            }
            self._set_cached_result(cache_key, result)
            return result
            
        except Exception as e:
            logger.error(f"Error getting growth metrics: {e}")
            return {
                'success': False,
                'error': f'Error getting growth metrics: {str(e)}',
                'data': []
            }
    
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