import os
import json
import random
import time
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional
import anthropic

logger = logging.getLogger(__name__)

class EngagementAgent:
    def __init__(self):
        self.client = anthropic.Anthropic(
            api_key=os.environ.get('CLAUDE_API_KEY')
        )
        self.daily_limit = 50
        self.engagement_count = 0
        self.last_reset = datetime.utcnow()
        self.spam_keywords = ['buy now', 'click here', 'limited offer', 'act now']
        self.sentiment_threshold = 0.3
        
    def engage(self, platform: str, post_id: str, context: Optional[Dict] = None) -> Dict:
        try:
            if not self._check_rate_limit():
                return {
                    'status': 'rate_limited',
                    'message': 'Daily engagement limit reached',
                    'retry_after': self._get_reset_time()
                }
            
            engagement_type = self._determine_engagement_type(platform, context)
            response = self._generate_response(platform, post_id, engagement_type, context)
            
            if self._check_spam_filter(response['content']):
                response = self._regenerate_safe_response(platform, post_id, context)
            
            self.engagement_count += 1
            
            return {
                'status': 'success',
                'engagement': response,
                'metadata': {
                    'platform': platform,
                    'post_id': post_id,
                    'type': engagement_type,
                    'timestamp': datetime.utcnow().isoformat(),
                    'daily_count': self.engagement_count
                }
            }
            
        except Exception as e:
            logger.error(f"Engagement error: {e}")
            return self._fallback_engagement(platform, post_id)
    
    def _check_rate_limit(self) -> bool:
        if datetime.utcnow() - self.last_reset > timedelta(days=1):
            self.engagement_count = 0
            self.last_reset = datetime.utcnow()
        
        return self.engagement_count < self.daily_limit
    
    def _get_reset_time(self) -> str:
        reset_time = self.last_reset + timedelta(days=1)
        return reset_time.isoformat()
    
    def _determine_engagement_type(self, platform: str, context: Optional[Dict]) -> str:
        if not context:
            return 'generic_reply'
        
        sentiment = context.get('sentiment', 'neutral')
        
        if sentiment == 'positive':
            return random.choice(['supportive_reply', 'amplification', 'appreciation'])
        elif sentiment == 'negative':
            return random.choice(['empathetic_reply', 'constructive_feedback'])
        elif context.get('is_question', False):
            return 'helpful_answer'
        else:
            return random.choice(['thoughtful_comment', 'value_add'])
    
    def _generate_response(self, platform: str, post_id: str, 
                          engagement_type: str, context: Optional[Dict]) -> Dict:
        try:
            prompt = self._build_engagement_prompt(platform, engagement_type, context)
            
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=200,
                temperature=0.6,
                system="""You are a helpful social media engagement assistant.
                Create authentic, valuable responses that add to conversations.
                Be empathetic, constructive, and brand-safe.
                Avoid spam, self-promotion, or controversial statements.""",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return {
                'content': response.content[0].text,
                'type': engagement_type,
                'confidence': 0.85
            }
            
        except Exception as e:
            logger.warning(f"Claude API error in engagement: {e}")
            raise
    
    def _build_engagement_prompt(self, platform: str, engagement_type: str, 
                                context: Optional[Dict]) -> str:
        base_prompt = f"Create a {engagement_type} for {platform}."
        
        if context:
            if 'post_content' in context:
                base_prompt += f"\nOriginal post: {context['post_content'][:200]}"
            if 'topic' in context:
                base_prompt += f"\nTopic: {context['topic']}"
            if 'brand_voice' in context:
                base_prompt += f"\nBrand voice: {context['brand_voice']}"
        
        type_instructions = {
            'supportive_reply': "Show genuine support and encouragement.",
            'amplification': "Add valuable insights that extend the discussion.",
            'appreciation': "Express authentic gratitude or recognition.",
            'empathetic_reply': "Show understanding and offer support.",
            'constructive_feedback': "Provide helpful suggestions respectfully.",
            'helpful_answer': "Give a clear, useful response to the question.",
            'thoughtful_comment': "Add meaningful perspective to the conversation.",
            'value_add': "Share relevant information or resources."
        }
        
        base_prompt += f"\n{type_instructions.get(engagement_type, 'Be helpful and authentic.')}"
        
        return base_prompt
    
    def _check_spam_filter(self, content: str) -> bool:
        content_lower = content.lower()
        
        for keyword in self.spam_keywords:
            if keyword in content_lower:
                return True
        
        excessive_caps = sum(1 for c in content if c.isupper()) / max(len(content), 1) > 0.3
        excessive_punctuation = content.count('!') > 2 or content.count('?') > 2
        
        return excessive_caps or excessive_punctuation
    
    def _regenerate_safe_response(self, platform: str, post_id: str, 
                                 context: Optional[Dict]) -> Dict:
        safe_templates = [
            "Thanks for sharing this perspective!",
            "This is really interesting, appreciate you posting this.",
            "Great point! This adds valuable context to the discussion.",
            "Love seeing thoughtful content like this.",
            "This resonates with many people, thanks for sharing."
        ]
        
        return {
            'content': random.choice(safe_templates),
            'type': 'safe_fallback',
            'confidence': 0.6
        }
    
    def _fallback_engagement(self, platform: str, post_id: str) -> Dict:
        fallback_responses = {
            'twitter': [
                "Great thread! 🙌",
                "Thanks for sharing this insight!",
                "This is so important 💯"
            ],
            'instagram': [
                "Love this! ❤️",
                "So inspiring! ✨",
                "This is everything! 🔥"
            ],
            'linkedin': [
                "Thank you for sharing these insights.",
                "This is a valuable perspective.",
                "Excellent points raised here."
            ],
            'default': [
                "Thanks for sharing!",
                "Great post!",
                "Interesting perspective!"
            ]
        }
        
        responses = fallback_responses.get(platform, fallback_responses['default'])
        
        return {
            'status': 'success',
            'engagement': {
                'content': random.choice(responses),
                'type': 'fallback',
                'confidence': 0.5
            },
            'metadata': {
                'platform': platform,
                'post_id': post_id,
                'fallback_mode': True,
                'timestamp': datetime.utcnow().isoformat()
            }
        }
    
    def get_engagement_stats(self) -> Dict:
        return {
            'daily_limit': self.daily_limit,
            'engagements_today': self.engagement_count,
            'remaining': self.daily_limit - self.engagement_count,
            'reset_time': self._get_reset_time()
        }