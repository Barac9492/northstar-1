import os
import json
import requests
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class TwitterAPI:
    def __init__(self):
        self.api_key = os.environ.get('TWITTER_API_KEY')
        self.api_secret = os.environ.get('TWITTER_API_SECRET')
        self.access_token = os.environ.get('TWITTER_ACCESS_TOKEN')
        self.access_token_secret = os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')
        self.base_url = "https://api.twitter.com/2"
        self.mock_mode = not all([self.api_key, self.api_secret])
        
    def post_tweet(self, content: str, media_ids: Optional[List[str]] = None) -> Dict:
        if self.mock_mode:
            return self._mock_post_tweet(content)
        
        try:
            headers = self._get_headers()
            payload = {"text": content}
            
            if media_ids:
                payload["media"] = {"media_ids": media_ids}
            
            response = requests.post(
                f"{self.base_url}/tweets",
                headers=headers,
                json=payload
            )
            
            if response.status_code == 201:
                return {
                    'success': True,
                    'tweet_id': response.json()['data']['id'],
                    'timestamp': datetime.utcnow().isoformat()
                }
            else:
                logger.error(f"Twitter API error: {response.status_code}")
                return {'success': False, 'error': response.text}
                
        except Exception as e:
            logger.error(f"Twitter post error: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_mentions(self, since_id: Optional[str] = None) -> List[Dict]:
        if self.mock_mode:
            return self._mock_get_mentions()
        
        try:
            headers = self._get_headers()
            params = {"max_results": 100}
            
            if since_id:
                params["since_id"] = since_id
            
            response = requests.get(
                f"{self.base_url}/users/me/mentions",
                headers=headers,
                params=params
            )
            
            if response.status_code == 200:
                return response.json().get('data', [])
            else:
                logger.error(f"Twitter mentions error: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Twitter mentions fetch error: {e}")
            return []
    
    def get_analytics(self, tweet_ids: List[str]) -> Dict:
        if self.mock_mode:
            return self._mock_get_analytics(tweet_ids)
        
        try:
            headers = self._get_headers()
            ids = ",".join(tweet_ids)
            
            response = requests.get(
                f"{self.base_url}/tweets",
                headers=headers,
                params={
                    "ids": ids,
                    "tweet.fields": "public_metrics,created_at"
                }
            )
            
            if response.status_code == 200:
                data = response.json().get('data', [])
                analytics = {}
                
                for tweet in data:
                    analytics[tweet['id']] = {
                        'impressions': tweet['public_metrics'].get('impression_count', 0),
                        'likes': tweet['public_metrics'].get('like_count', 0),
                        'retweets': tweet['public_metrics'].get('retweet_count', 0),
                        'replies': tweet['public_metrics'].get('reply_count', 0),
                        'created_at': tweet.get('created_at')
                    }
                
                return analytics
            else:
                logger.error(f"Twitter analytics error: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"Twitter analytics fetch error: {e}")
            return {}
    
    def search_tweets(self, query: str, max_results: int = 10) -> List[Dict]:
        if self.mock_mode:
            return self._mock_search_tweets(query)
        
        try:
            headers = self._get_headers()
            
            response = requests.get(
                f"{self.base_url}/tweets/search/recent",
                headers=headers,
                params={
                    "query": query,
                    "max_results": min(max_results, 100),
                    "tweet.fields": "author_id,created_at,public_metrics"
                }
            )
            
            if response.status_code == 200:
                return response.json().get('data', [])
            else:
                logger.error(f"Twitter search error: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Twitter search error: {e}")
            return []
    
    def _get_headers(self) -> Dict:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def _mock_post_tweet(self, content: str) -> Dict:
        return {
            'success': True,
            'tweet_id': f"mock_{datetime.utcnow().timestamp()}",
            'timestamp': datetime.utcnow().isoformat(),
            'mock': True
        }
    
    def _mock_get_mentions(self) -> List[Dict]:
        return [
            {
                'id': 'mock_mention_1',
                'text': '@you Great product! Love using it!',
                'author_id': 'user123',
                'created_at': datetime.utcnow().isoformat()
            },
            {
                'id': 'mock_mention_2',
                'text': '@you How does this feature work?',
                'author_id': 'user456',
                'created_at': datetime.utcnow().isoformat()
            }
        ]
    
    def _mock_get_analytics(self, tweet_ids: List[str]) -> Dict:
        analytics = {}
        for tweet_id in tweet_ids:
            analytics[tweet_id] = {
                'impressions': 1000,
                'likes': 50,
                'retweets': 10,
                'replies': 5,
                'created_at': datetime.utcnow().isoformat()
            }
        return analytics
    
    def _mock_search_tweets(self, query: str) -> List[Dict]:
        return [
            {
                'id': 'search_result_1',
                'text': f'Sample tweet about {query}',
                'author_id': 'author1',
                'created_at': datetime.utcnow().isoformat(),
                'public_metrics': {
                    'like_count': 10,
                    'retweet_count': 2
                }
            }
        ]