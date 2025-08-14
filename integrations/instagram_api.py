import os
import json
import requests
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class InstagramAPI:
    def __init__(self):
        self.access_token = os.environ.get('INSTAGRAM_ACCESS_TOKEN')
        self.business_account_id = os.environ.get('INSTAGRAM_BUSINESS_ID')
        self.base_url = "https://graph.facebook.com/v18.0"
        self.mock_mode = not all([self.access_token, self.business_account_id])
        
    def create_post(self, caption: str, media_url: Optional[str] = None, 
                   media_type: str = "IMAGE") -> Dict:
        if self.mock_mode:
            return self._mock_create_post(caption)
        
        try:
            if media_url:
                container_id = self._create_media_container(media_url, caption, media_type)
                if not container_id:
                    return {'success': False, 'error': 'Failed to create media container'}
                
                return self._publish_container(container_id)
            else:
                return self._create_text_post(caption)
                
        except Exception as e:
            logger.error(f"Instagram post error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _create_media_container(self, media_url: str, caption: str, 
                               media_type: str) -> Optional[str]:
        try:
            endpoint = f"{self.base_url}/{self.business_account_id}/media"
            
            params = {
                'access_token': self.access_token,
                'caption': caption
            }
            
            if media_type == "IMAGE":
                params['image_url'] = media_url
            elif media_type == "VIDEO":
                params['video_url'] = media_url
                params['media_type'] = 'VIDEO'
            
            response = requests.post(endpoint, params=params)
            
            if response.status_code == 200:
                return response.json().get('id')
            else:
                logger.error(f"Instagram container creation error: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Container creation error: {e}")
            return None
    
    def _publish_container(self, container_id: str) -> Dict:
        try:
            endpoint = f"{self.base_url}/{self.business_account_id}/media_publish"
            
            params = {
                'access_token': self.access_token,
                'creation_id': container_id
            }
            
            response = requests.post(endpoint, params=params)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'media_id': response.json().get('id'),
                    'timestamp': datetime.utcnow().isoformat()
                }
            else:
                logger.error(f"Instagram publish error: {response.text}")
                return {'success': False, 'error': response.text}
                
        except Exception as e:
            logger.error(f"Publish error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _create_text_post(self, caption: str) -> Dict:
        return self._create_media_container(
            media_url="https://via.placeholder.com/1080",
            caption=caption,
            media_type="IMAGE"
        )
    
    def get_insights(self, media_id: str, metrics: Optional[List[str]] = None) -> Dict:
        if self.mock_mode:
            return self._mock_get_insights(media_id)
        
        try:
            if not metrics:
                metrics = ['impressions', 'reach', 'engagement', 'saved']
            
            endpoint = f"{self.base_url}/{media_id}/insights"
            
            params = {
                'access_token': self.access_token,
                'metric': ','.join(metrics)
            }
            
            response = requests.get(endpoint, params=params)
            
            if response.status_code == 200:
                data = response.json().get('data', [])
                insights = {}
                
                for metric in data:
                    insights[metric['name']] = metric['values'][0]['value']
                
                return insights
            else:
                logger.error(f"Instagram insights error: {response.text}")
                return {}
                
        except Exception as e:
            logger.error(f"Insights fetch error: {e}")
            return {}
    
    def get_comments(self, media_id: str) -> List[Dict]:
        if self.mock_mode:
            return self._mock_get_comments(media_id)
        
        try:
            endpoint = f"{self.base_url}/{media_id}/comments"
            
            params = {
                'access_token': self.access_token,
                'fields': 'id,text,username,timestamp'
            }
            
            response = requests.get(endpoint, params=params)
            
            if response.status_code == 200:
                return response.json().get('data', [])
            else:
                logger.error(f"Instagram comments error: {response.text}")
                return []
                
        except Exception as e:
            logger.error(f"Comments fetch error: {e}")
            return []
    
    def reply_to_comment(self, comment_id: str, message: str) -> Dict:
        if self.mock_mode:
            return self._mock_reply_to_comment(comment_id, message)
        
        try:
            endpoint = f"{self.base_url}/{comment_id}/replies"
            
            params = {
                'access_token': self.access_token,
                'message': message
            }
            
            response = requests.post(endpoint, params=params)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'reply_id': response.json().get('id'),
                    'timestamp': datetime.utcnow().isoformat()
                }
            else:
                logger.error(f"Instagram reply error: {response.text}")
                return {'success': False, 'error': response.text}
                
        except Exception as e:
            logger.error(f"Reply error: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_hashtag_search(self, hashtag: str) -> Dict:
        if self.mock_mode:
            return self._mock_hashtag_search(hashtag)
        
        try:
            search_endpoint = f"{self.base_url}/ig_hashtag_search"
            
            search_params = {
                'access_token': self.access_token,
                'q': hashtag
            }
            
            search_response = requests.get(search_endpoint, params=search_params)
            
            if search_response.status_code != 200:
                return {}
            
            hashtag_id = search_response.json()['data'][0]['id']
            
            media_endpoint = f"{self.base_url}/{hashtag_id}/recent_media"
            
            media_params = {
                'access_token': self.access_token,
                'fields': 'id,caption,media_type,media_url,permalink',
                'limit': 25
            }
            
            media_response = requests.get(media_endpoint, params=media_params)
            
            if media_response.status_code == 200:
                return media_response.json()
            else:
                return {}
                
        except Exception as e:
            logger.error(f"Hashtag search error: {e}")
            return {}
    
    def _mock_create_post(self, caption: str) -> Dict:
        return {
            'success': True,
            'media_id': f"mock_ig_{datetime.utcnow().timestamp()}",
            'timestamp': datetime.utcnow().isoformat(),
            'mock': True
        }
    
    def _mock_get_insights(self, media_id: str) -> Dict:
        return {
            'impressions': 5000,
            'reach': 3500,
            'engagement': 450,
            'saved': 50,
            'likes': 400,
            'comments': 30
        }
    
    def _mock_get_comments(self, media_id: str) -> List[Dict]:
        return [
            {
                'id': 'comment_1',
                'text': 'Love this post! 😍',
                'username': 'user123',
                'timestamp': datetime.utcnow().isoformat()
            },
            {
                'id': 'comment_2',
                'text': 'Amazing content!',
                'username': 'user456',
                'timestamp': datetime.utcnow().isoformat()
            }
        ]
    
    def _mock_reply_to_comment(self, comment_id: str, message: str) -> Dict:
        return {
            'success': True,
            'reply_id': f"reply_{datetime.utcnow().timestamp()}",
            'timestamp': datetime.utcnow().isoformat(),
            'mock': True
        }
    
    def _mock_hashtag_search(self, hashtag: str) -> Dict:
        return {
            'data': [
                {
                    'id': f'post_1_{hashtag}',
                    'caption': f'Post about #{hashtag}',
                    'media_type': 'IMAGE',
                    'permalink': f'https://instagram.com/p/mock_{hashtag}_1'
                }
            ]
        }