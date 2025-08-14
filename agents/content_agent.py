import os
import json
import random
from datetime import datetime
import logging
from typing import Dict, List, Optional
import anthropic

logger = logging.getLogger(__name__)

class ContentAgent:
    def __init__(self):
        self.client = anthropic.Anthropic(
            api_key=os.environ.get('CLAUDE_API_KEY')
        )
        self.fallback_mode = False
        self.platform_limits = {
            'twitter': 280,
            'instagram': 2200,
            'tiktok': 2200,
            'linkedin': 3000
        }
        self.trending_keywords = []
        self.ab_variants = []
        
    def generate(self, platform: str, prompt: str, optimize_for_virality: bool = True) -> Dict:
        try:
            if optimize_for_virality:
                prompt = self._enhance_with_trends(prompt)
            
            content = self._generate_with_claude(platform, prompt)
            
            if platform in self.platform_limits:
                content = self._trim_to_limit(content, self.platform_limits[platform])
            
            variants = self._create_ab_variants(content, platform)
            
            return {
                'primary_content': content,
                'variants': variants,
                'metadata': {
                    'platform': platform,
                    'generated_at': datetime.utcnow().isoformat(),
                    'virality_optimized': optimize_for_virality,
                    'character_count': len(content)
                }
            }
            
        except Exception as e:
            logger.error(f"Content generation error: {e}")
            return self._fallback_generation(platform, prompt)
    
    def _generate_with_claude(self, platform: str, prompt: str) -> str:
        try:
            system_prompt = f"""You are a social media content expert creating {platform} posts.
            Focus on engagement, authenticity, and brand safety.
            Avoid controversial topics and ensure content is inclusive.
            Platform: {platform}
            Character limit: {self.platform_limits.get(platform, 'unlimited')}"""
            
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                temperature=0.7,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.content[0].text
            
        except Exception as e:
            logger.warning(f"Claude API error: {e}, using fallback")
            self.fallback_mode = True
            raise
    
    def _fallback_generation(self, platform: str, prompt: str) -> Dict:
        templates = {
            'twitter': [
                f"🚀 {prompt[:100]}... What are your thoughts? #Innovation #AI",
                f"Breaking: {prompt[:150]} 🔥 Share if you agree!",
                f"Quick tip: {prompt[:200]} 💡 Follow for more insights!"
            ],
            'instagram': [
                f"✨ {prompt}\n\n#Trending #SocialMedia #ContentCreation #AI",
                f"Story time: {prompt}\n\nDouble tap if this resonates! ❤️",
            ],
            'default': [f"Check this out: {prompt} #Trending"]
        }
        
        platform_templates = templates.get(platform, templates['default'])
        content = random.choice(platform_templates)
        
        return {
            'primary_content': content,
            'variants': [content],
            'metadata': {
                'platform': platform,
                'generated_at': datetime.utcnow().isoformat(),
                'fallback_mode': True
            }
        }
    
    def _enhance_with_trends(self, prompt: str) -> str:
        trend_keywords = self._fetch_trends()
        if trend_keywords:
            prompt += f" (Consider trending topics: {', '.join(trend_keywords[:3])})"
        return prompt
    
    def _fetch_trends(self) -> List[str]:
        try:
            return ['AI', 'sustainability', 'innovation', 'growth', 'community']
        except:
            return []
    
    def _create_ab_variants(self, content: str, platform: str) -> List[str]:
        variants = [content]
        
        emoji_variant = self._add_emojis(content)
        if emoji_variant != content:
            variants.append(emoji_variant)
        
        question_variant = self._add_question(content)
        if question_variant != content:
            variants.append(question_variant)
        
        return variants[:3]
    
    def _add_emojis(self, content: str) -> str:
        emoji_map = {
            'great': '🎉',
            'new': '✨',
            'important': '⚡',
            'love': '❤️',
            'think': '🤔'
        }
        
        result = content
        for word, emoji in emoji_map.items():
            if word in result.lower() and emoji not in result:
                result = f"{emoji} {result}"
                break
        
        return result
    
    def _add_question(self, content: str) -> str:
        if '?' not in content:
            questions = [
                "What do you think?",
                "Agree or disagree?",
                "Your thoughts?",
                "Have you experienced this?"
            ]
            return f"{content} {random.choice(questions)}"
        return content
    
    def _trim_to_limit(self, content: str, limit: int) -> str:
        if len(content) <= limit:
            return content
        
        trimmed = content[:limit-3] + "..."
        last_space = trimmed.rfind(' ')
        if last_space > limit * 0.8:
            trimmed = trimmed[:last_space] + "..."
        
        return trimmed