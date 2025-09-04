"""
Sentiment Analysis Service
Analyzes sentiment of Instagram comments and captions
"""

import re
from typing import List, Dict, Any
from collections import Counter

class SentimentAnalyzer:
    def __init__(self):
        # Simple keyword-based sentiment analysis
        self.positive_words = {
            'love', 'amazing', 'awesome', 'great', 'excellent', 'fantastic', 'wonderful', 
            'beautiful', 'perfect', 'best', 'good', 'nice', 'cool', 'super', 'brilliant',
            'outstanding', 'incredible', 'fabulous', 'marvelous', 'spectacular', 'divine',
            'gorgeous', 'stunning', 'impressive', 'remarkable', 'extraordinary', 'magnificent',
            'like', 'liked', 'likes', 'heart', '❤️', '😍', '🔥', '👏', '🙌', '💯', '✨',
            'happy', 'joy', 'excited', 'thrilled', 'delighted', 'pleased', 'satisfied'
        }
        
        self.negative_words = {
            'hate', 'terrible', 'awful', 'bad', 'horrible', 'disgusting', 'ugly', 'worst',
            'stupid', 'dumb', 'boring', 'lame', 'sucks', 'pathetic', 'ridiculous', 'annoying',
            'disappointing', 'useless', 'worthless', 'trash', 'garbage', 'fake', 'scam',
            'angry', 'mad', 'furious', 'upset', 'frustrated', 'disappointed', 'sad', 'depressed',
            'dislike', 'disliked', 'dislikes', '😡', '😠', '👎', '💔', '😢', '😭', '🤮'
        }
        
        self.neutral_words = {
            'okay', 'ok', 'fine', 'alright', 'normal', 'average', 'decent', 'fair',
            'maybe', 'perhaps', 'possibly', 'might', 'could', 'would', 'should',
            'think', 'believe', 'guess', 'suppose', 'wonder', 'question', 'ask'
        }

    def clean_text(self, text: str) -> str:
        """Clean and normalize text for analysis"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove mentions and hashtags for sentiment (keep the text)
        text = re.sub(r'[@#]\w+', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text

    def analyze_text_sentiment(self, text: str) -> Dict[str, Any]:
        """Analyze sentiment of a single text"""
        if not text:
            return {'sentiment': 'neutral', 'score': 0, 'confidence': 0}
        
        cleaned_text = self.clean_text(text)
        words = cleaned_text.split()
        
        positive_count = sum(1 for word in words if word in self.positive_words)
        negative_count = sum(1 for word in words if word in self.negative_words)
        neutral_count = sum(1 for word in words if word in self.neutral_words)
        
        total_sentiment_words = positive_count + negative_count + neutral_count
        
        if total_sentiment_words == 0:
            return {'sentiment': 'neutral', 'score': 0, 'confidence': 0.1}
        
        # Calculate sentiment score (-1 to 1)
        score = (positive_count - negative_count) / len(words) if words else 0
        
        # Determine sentiment
        if score > 0.1:
            sentiment = 'positive'
        elif score < -0.1:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        # Calculate confidence based on sentiment word density
        confidence = min(total_sentiment_words / len(words), 1.0) if words else 0
        
        return {
            'sentiment': sentiment,
            'score': score,
            'confidence': confidence,
            'positive_words': positive_count,
            'negative_words': negative_count,
            'neutral_words': neutral_count
        }

    def analyze_comments_sentiment(self, comments: List[str]) -> Dict[str, Any]:
        """Analyze sentiment of multiple comments"""
        if not comments:
            return {
                'overall_sentiment': 'neutral',
                'positive_percentage': 0,
                'negative_percentage': 0,
                'neutral_percentage': 100,
                'total_comments': 0,
                'sentiment_breakdown': {'positive': 0, 'negative': 0, 'neutral': 0}
            }
        
        sentiments = []
        for comment in comments:
            analysis = self.analyze_text_sentiment(comment)
            sentiments.append(analysis['sentiment'])
        
        # Count sentiments
        sentiment_counts = Counter(sentiments)
        total = len(sentiments)
        
        positive_count = sentiment_counts.get('positive', 0)
        negative_count = sentiment_counts.get('negative', 0)
        neutral_count = sentiment_counts.get('neutral', 0)
        
        # Calculate percentages
        positive_pct = round((positive_count / total) * 100) if total > 0 else 0
        negative_pct = round((negative_count / total) * 100) if total > 0 else 0
        neutral_pct = round((neutral_count / total) * 100) if total > 0 else 100
        
        # Determine overall sentiment
        if positive_pct > negative_pct and positive_pct > neutral_pct:
            overall = 'positive'
        elif negative_pct > positive_pct and negative_pct > neutral_pct:
            overall = 'negative'
        else:
            overall = 'neutral'
        
        return {
            'overall_sentiment': overall,
            'positive_percentage': positive_pct,
            'negative_percentage': negative_pct,
            'neutral_percentage': neutral_pct,
            'total_comments': total,
            'sentiment_breakdown': {
                'positive': positive_count,
                'negative': negative_count,
                'neutral': neutral_count
            }
        }

# Global sentiment analyzer instance
sentiment_analyzer = SentimentAnalyzer()