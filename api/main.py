"""
Vercel-compatible FastAPI application
Simplified version for serverless deployment
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from datetime import datetime
import anthropic

# Initialize Anthropic client
try:
    anthropic_client = anthropic.Anthropic(
        api_key=os.environ.get("ANTHROPIC_API_KEY", "")
    )
except:
    anthropic_client = None

app = FastAPI(
    title="NorthStar AI API",
    version="1.0.0",
    description="AI-powered social media management platform"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for Vercel deployment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class ContentGenerationRequest(BaseModel):
    prompt: str
    platform: str
    tone: Optional[str] = "professional"
    include_hashtags: bool = True
    include_emojis: bool = True
    target_audience: Optional[str] = None

class ContentResponse(BaseModel):
    id: str
    text: str
    platform: str
    variants: List[str]
    hashtags: List[str]
    confidence_score: float
    created_at: datetime

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to NorthStar AI API",
        "status": "healthy",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "northstar-api",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/api/v1/content/generate", response_model=ContentResponse)
async def generate_content(request: ContentGenerationRequest):
    """Generate AI-powered social media content"""
    
    if not anthropic_client:
        raise HTTPException(
            status_code=500, 
            detail="AI service not available. Please configure ANTHROPIC_API_KEY."
        )
    
    try:
        # Construct AI prompt based on platform and requirements
        platform_prompts = {
            "twitter": f"Create an engaging Twitter post (max 280 characters) about: {request.prompt}",
            "instagram": f"Create an engaging Instagram caption with emojis about: {request.prompt}",
            "linkedin": f"Create a professional LinkedIn post about: {request.prompt}",
            "tiktok": f"Create a fun, viral TikTok caption about: {request.prompt}"
        }
        
        ai_prompt = platform_prompts.get(request.platform.lower(), platform_prompts["twitter"])
        
        if request.tone:
            ai_prompt += f"\n\nTone: {request.tone}"
        
        if request.target_audience:
            ai_prompt += f"\nTarget audience: {request.target_audience}"
        
        if request.include_hashtags:
            ai_prompt += "\nInclude 3-5 relevant hashtags."
        
        if request.include_emojis:
            ai_prompt += "\nInclude relevant emojis."
        
        ai_prompt += "\n\nAlso provide 2 alternative variants of the same content."
        
        # Call Anthropic API
        response = anthropic_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=500,
            messages=[
                {
                    "role": "user", 
                    "content": ai_prompt
                }
            ]
        )
        
        # Extract content from response
        generated_text = response.content[0].text if response.content else "Generated content"
        
        # Simple parsing to extract main content and variants
        lines = generated_text.split('\n\n')
        main_content = lines[0] if lines else generated_text
        
        # Extract hashtags if present
        hashtags = []
        if '#' in main_content:
            import re
            hashtags = re.findall(r'#(\w+)', main_content)
        
        # Create variants (simplified)
        variants = []
        if len(lines) > 1:
            variants = [line.strip() for line in lines[1:3] if line.strip()]
        
        # Generate content ID
        import uuid
        content_id = str(uuid.uuid4())
        
        return ContentResponse(
            id=content_id,
            text=main_content,
            platform=request.platform,
            variants=variants,
            hashtags=hashtags,
            confidence_score=0.85,
            created_at=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Content generation failed: {str(e)}"
        )

@app.get("/api/v1/content/")
async def get_user_content():
    """Get user content (mock data for demo)"""
    return [
        {
            "id": "content-1",
            "text": "🚀 AI is revolutionizing content creation! Our latest features help businesses save 20+ hours weekly on social media management. #AI #productivity",
            "platform": "twitter",
            "status": "published",
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "id": "content-2",
            "text": "Behind the scenes at our AI lab where we're building the future of social media automation ✨",
            "platform": "instagram", 
            "status": "draft",
            "created_at": datetime.utcnow().isoformat()
        }
    ]

# For Vercel deployment
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)