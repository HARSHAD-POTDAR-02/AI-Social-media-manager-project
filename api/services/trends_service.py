"""
Trends Service for Real-time Content Strategy
Uses pytrends to fetch current trending topics and generate content recommendations
"""

import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import requests
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

try:
    from pytrends.request import TrendReq
    PYTRENDS_AVAILABLE = True
except ImportError:
    PYTRENDS_AVAILABLE = False
    print("[WARN] pytrends not installed. Install with: pip install pytrends")

class TrendsService:
    """Service for fetching trends and generating content strategy"""
    
    def __init__(self):
        self.groq_client = None
        if os.getenv("GROQ_API_KEY"):
            self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        self.pytrends = None
        if PYTRENDS_AVAILABLE:
            try:
                self.pytrends = TrendReq(hl='en-US', tz=360)
            except Exception as e:
                print(f"[WARN] Failed to initialize pytrends: {e}")
    
    def get_trending_topics(self, geo: str = 'US', category: int = 0) -> List[Dict]:
        """Get current trending topics"""
        if not self.pytrends:
            return self._get_fallback_trends()
        
        try:
            # Get trending searches
            trending_searches = self.pytrends.trending_searches(pn='united_states')
            trends = []
            
            for i, trend in enumerate(trending_searches[0][:10]):  # Top 10 trends
                trends.append({
                    'keyword': trend,
                    'rank': i + 1,
                    'category': 'trending',
                    'timestamp': datetime.now().isoformat()
                })
            
            return trends
            
        except Exception as e:
            print(f"[ERROR] Failed to fetch trends: {e}")
            return self._get_fallback_trends()
    
    def get_topic_interest_over_time(self, keywords: List[str]) -> Dict:
        """Get interest over time for specific keywords"""
        if not self.pytrends or not keywords:
            return {}
        
        try:
            self.pytrends.build_payload(keywords, cat=0, timeframe='today 7-d', geo='US')
            interest_data = self.pytrends.interest_over_time()
            
            if interest_data.empty:
                return {}
            
            # Convert to JSON-serializable format
            result = {}
            for keyword in keywords:
                if keyword in interest_data.columns:
                    result[keyword] = {
                        'current_interest': int(interest_data[keyword].iloc[-1]),
                        'avg_interest': float(interest_data[keyword].mean()),
                        'trend_direction': 'up' if interest_data[keyword].iloc[-1] > interest_data[keyword].mean() else 'down'
                    }
            
            return result
            
        except Exception as e:
            print(f"[ERROR] Failed to get interest data: {e}")
            return {}
    
    def get_related_queries(self, keyword: str) -> Dict:
        """Get related queries for a keyword"""
        if not self.pytrends:
            return {}
        
        try:
            self.pytrends.build_payload([keyword], cat=0, timeframe='today 7-d', geo='US')
            related_queries = self.pytrends.related_queries()
            
            if keyword not in related_queries or not related_queries[keyword]:
                return {}
            
            result = {}
            if related_queries[keyword]['top'] is not None:
                result['top_queries'] = related_queries[keyword]['top']['query'].tolist()[:5]
            if related_queries[keyword]['rising'] is not None:
                result['rising_queries'] = related_queries[keyword]['rising']['query'].tolist()[:5]
            
            return result
            
        except Exception as e:
            print(f"[ERROR] Failed to get related queries: {e}")
            return {}
    
    def generate_content_strategy(self, trends: List[Dict], user_niche: str = "general") -> Dict:
        """Generate content strategy based on trends"""
        if not self.groq_client:
            return self._generate_basic_strategy(trends, user_niche)
        
        try:
            # Prepare trends data for LLM
            trends_text = "\n".join([f"- {trend['keyword']} (Rank #{trend['rank']})" for trend in trends[:5]])
            
            prompt = f"""Based on these current trending topics, create a content strategy for a {user_niche} Instagram account:

Current Trends:
{trends_text}

Provide:
1. 3 specific content ideas that connect these trends to {user_niche}
2. Optimal posting strategy
3. Hashtag recommendations
4. Content format suggestions (Reels, Posts, Stories)

Keep recommendations practical and actionable."""

            response = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are a social media strategist specializing in trend-based content creation."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            return {
                'strategy': response.choices[0].message.content.strip(),
                'trends_used': trends[:5],
                'generated_at': datetime.now().isoformat(),
                'niche': user_niche
            }
            
        except Exception as e:
            print(f"[ERROR] Failed to generate strategy: {e}")
            return self._generate_basic_strategy(trends, user_niche)
    
    def _get_fallback_trends(self) -> List[Dict]:
        """Fallback trends when pytrends is unavailable"""
        fallback_trends = [
            "AI technology", "Social media marketing", "Content creation", 
            "Digital trends", "Instagram reels", "Viral content",
            "Online business", "Personal branding", "Influencer marketing", "SEO tips"
        ]
        
        return [
            {
                'keyword': trend,
                'rank': i + 1,
                'category': 'fallback',
                'timestamp': datetime.now().isoformat()
            }
            for i, trend in enumerate(fallback_trends)
        ]
    
    def _generate_basic_strategy(self, trends: List[Dict], user_niche: str) -> Dict:
        """Basic strategy when LLM is unavailable"""
        top_trends = [trend['keyword'] for trend in trends[:3]]
        
        return {
            'strategy': f"""Content Strategy for {user_niche}:

1. Trending Topics to Leverage:
   - {', '.join(top_trends)}

2. Content Ideas:
   - Create posts connecting {user_niche} to trending topics
   - Use trending hashtags in your niche
   - Post during peak hours (2-6 PM)

3. Formats to Try:
   - Reels with trending audio
   - Carousel posts explaining trends
   - Stories with polls about trends""",
            'trends_used': trends[:3],
            'generated_at': datetime.now().isoformat(),
            'niche': user_niche
        }
    
    def get_comprehensive_strategy(self) -> Dict:
        """Get comprehensive content strategy with trends"""
        # Get trending topics
        trends = self.get_trending_topics()
        
        # Determine user niche based on previous content (fallback to sports)
        user_niche = "sports"  # This could be dynamic based on user's content analysis
        
        # Generate strategy
        strategy = self.generate_content_strategy(trends, user_niche)
        
        # Get interest data for top trends
        top_keywords = [trend['keyword'] for trend in trends[:3]]
        interest_data = self.get_topic_interest_over_time(top_keywords)
        
        return {
            'content_strategy': strategy,
            'trending_topics': trends[:10],
            'interest_analysis': interest_data,
            'recommendations': self._generate_recommendations(trends, interest_data),
            'last_updated': datetime.now().isoformat()
        }
    
    def _generate_recommendations(self, trends: List[Dict], interest_data: Dict) -> List[str]:
        """Generate specific recommendations"""
        recommendations = []
        
        if trends:
            recommendations.append(f"Leverage trending topic: '{trends[0]['keyword']}' in your next post")
        
        for keyword, data in interest_data.items():
            if data['trend_direction'] == 'up':
                recommendations.append(f"'{keyword}' is trending upward - create content around this topic")
        
        recommendations.extend([
            "Post during peak engagement hours (2-6 PM)",
            "Use trending hashtags relevant to your niche",
            "Create Reels with trending audio for maximum reach"
        ])
        
        return recommendations[:5]