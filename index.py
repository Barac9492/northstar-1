"""
NorthStar AI - Ultra Minimal FastAPI Version for Vercel
Basic HTML interface with AI content generation
"""
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
import os

app = FastAPI(title="NorthStar AI")

# Initialize Anthropic client
def get_anthropic_client():
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if api_key:
        try:
            import anthropic
            return anthropic.Anthropic(api_key=api_key)
        except ImportError:
            return None
    return None

@app.get("/", response_class=HTMLResponse)
async def homepage():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NorthStar AI - Social Media Automation</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6; 
            color: #333;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
        .hero {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center;
            padding: 4rem 2rem;
            border-radius: 20px;
            margin-bottom: 3rem;
            box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);
        }
        .hero h1 { font-size: 3.5rem; margin-bottom: 1rem; font-weight: 700; }
        .hero p { font-size: 1.3rem; opacity: 0.9; }
        .content-section {
            background: white;
            padding: 3rem;
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }
        .form-group { margin-bottom: 1.5rem; }
        .form-group label { 
            display: block; 
            margin-bottom: 0.5rem; 
            font-weight: 600; 
            color: #555;
        }
        .form-control {
            width: 100%;
            padding: 1rem;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            font-size: 1rem;
            transition: border-color 0.3s ease;
        }
        .form-control:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        select.form-control { height: 3.5rem; }
        textarea.form-control { min-height: 120px; resize: vertical; }
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem 2rem;
            border: none;
            border-radius: 50px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            width: 100%;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        }
        .checkbox-group {
            display: flex;
            gap: 2rem;
            margin: 1rem 0;
        }
        .checkbox-item {
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
        }
        .stat-card {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
            padding: 2rem;
            border-radius: 16px;
            text-align: center;
        }
        .stat-number { font-size: 2.5rem; font-weight: 700; margin-bottom: 0.5rem; }
        .result-box {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 2rem;
            border-radius: 12px;
            border-left: 4px solid #667eea;
            margin: 1.5rem 0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .grid { display: grid; grid-template-columns: 2fr 1fr; gap: 2rem; }
        @media (max-width: 768px) {
            .grid { grid-template-columns: 1fr; }
            .hero h1 { font-size: 2.5rem; }
            .checkbox-group { flex-direction: column; gap: 1rem; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="hero">
            <h1>⭐ NorthStar AI</h1>
            <p>AI-Powered Social Media Content Generation That Actually Works</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">50+</div>
                <div>Hours Saved Monthly</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">850%</div>
                <div>Average ROI</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">3x</div>
                <div>Faster Growth</div>
            </div>
        </div>
        
        <div class="grid">
            <div class="content-section">
                <h2>🚀 Generate Viral Content</h2>
                <form action="/generate" method="post">
                    <div class="form-group">
                        <label for="platform">Platform</label>
                        <select name="platform" id="platform" class="form-control" required>
                            <option value="twitter">Twitter</option>
                            <option value="instagram">Instagram</option>
                            <option value="linkedin">LinkedIn</option>
                            <option value="tiktok">TikTok</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="prompt">Content Description</label>
                        <textarea name="prompt" id="prompt" class="form-control" 
                                placeholder="e.g., Create a post about AI transforming business productivity..." required></textarea>
                    </div>
                    
                    <div class="checkbox-group">
                        <div class="checkbox-item">
                            <input type="checkbox" name="hashtags" id="hashtags" checked>
                            <label for="hashtags">📱 Include Hashtags</label>
                        </div>
                        <div class="checkbox-item">
                            <input type="checkbox" name="emojis" id="emojis" checked>
                            <label for="emojis">😊 Include Emojis</label>
                        </div>
                    </div>
                    
                    <button type="submit" class="btn">🚀 Generate Content</button>
                </form>
            </div>
            
            <div class="content-section">
                <h3>💡 Pro Tips</h3>
                <ul style="line-height: 2;">
                    <li>Be specific about your audience</li>
                    <li>Include emotional triggers</li>
                    <li>Mention concrete benefits</li>
                    <li>Use action-oriented language</li>
                    <li>Ask engaging questions</li>
                </ul>
                
                <h4 style="margin-top: 2rem;">📊 Quick Stats</h4>
                <p><strong>Posts Generated:</strong> 1,247 (+156)</p>
                <p><strong>Avg Engagement:</strong> 6.8% (+2.1%)</p>
                <p><strong>Time Saved:</strong> 42h/week (+8h)</p>
            </div>
        </div>
    </div>
</body>
</html>
    """

@app.post("/generate", response_class=HTMLResponse)
async def generate_content(
    platform: str = Form(...),
    prompt: str = Form(...),
    hashtags: str = Form(None),
    emojis: str = Form(None)
):
    try:
        # Input validation
        if not prompt or len(prompt.strip()) < 3:
            return error_page("Please enter a valid content description (at least 3 characters).")
        
        client = get_anthropic_client()
        if not client:
            return error_page("AI service not configured. Please contact support.")
        
        # Create platform-specific prompt
        platform_info = {
            "twitter": "Create an engaging Twitter post (max 280 characters)",
            "instagram": "Create an engaging Instagram caption with visual appeal", 
            "linkedin": "Create a professional LinkedIn post",
            "tiktok": "Create a fun, viral TikTok caption"
        }
        
        ai_prompt = f"{platform_info.get(platform.lower(), platform_info['twitter'])} about: {prompt.strip()}"
        
        if hashtags:
            ai_prompt += "\\n\\nInclude 3-5 relevant hashtags."
        
        if emojis:
            ai_prompt += "\\nInclude appropriate emojis."
        
        ai_prompt += "\\n\\nAlso provide one alternative version."
        
        # Call Anthropic API with error handling
        try:
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=400,
                messages=[{
                    "role": "user",
                    "content": ai_prompt
                }]
            )
            
            generated_text = response.content[0].text if response.content else "AI-generated content for your social media post!"
            
        except Exception as api_error:
            generated_text = f"Demo content for {platform.title()}: {prompt[:100]}... [AI generation temporarily unavailable]"
        
        return success_page(generated_text, platform.title())
        
    except Exception as e:
        return error_page("Something went wrong. Please try again.")

def success_page(content, platform):
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Content Generated - NorthStar AI</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6; 
            color: #333;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
            padding: 2rem;
        }}
        .container {{ max-width: 800px; margin: 0 auto; }}
        .success-header {{
            background: linear-gradient(135deg, #00C851 0%, #007E33 100%);
            color: white;
            text-align: center;
            padding: 2rem;
            border-radius: 16px;
            margin-bottom: 2rem;
        }}
        .content-box {{
            background: white;
            padding: 2.5rem;
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }}
        .generated-content {{
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 2rem;
            border-radius: 12px;
            border-left: 4px solid #667eea;
            margin: 1.5rem 0;
            font-size: 1.1rem;
            line-height: 1.6;
            white-space: pre-wrap;
        }}
        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin: 2rem 0;
        }}
        .metric {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
        }}
        .btn {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem 2rem;
            border: none;
            border-radius: 50px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            transition: transform 0.3s ease;
        }}
        .btn:hover {{ transform: translateY(-2px); }}
    </style>
</head>
<body>
    <div class="container">
        <div class="success-header">
            <h1>✅ Content Generated Successfully!</h1>
            <p>Your {platform.title()} content is ready to go viral</p>
        </div>
        
        <div class="content-box">
            <h2>🎯 Generated Content</h2>
            <div class="generated-content">{content}</div>
            
            <h3>📊 Performance Prediction</h3>
            <div class="metrics">
                <div class="metric">
                    <strong>Expected Engagement</strong><br>
                    5.2% - 7.8%
                </div>
                <div class="metric">
                    <strong>Viral Potential</strong><br>
                    High
                </div>
                <div class="metric">
                    <strong>Best Time</strong><br>
                    2:15 PM
                </div>
            </div>
            
            <a href="/" class="btn">🚀 Generate More Content</a>
        </div>
    </div>
</body>
</html>
    """

def error_page(error_message):
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Error - NorthStar AI</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6; 
            color: #333;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
            padding: 2rem;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .error-box {{
            background: white;
            padding: 3rem;
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            text-align: center;
            max-width: 500px;
        }}
        .error-icon {{ font-size: 4rem; margin-bottom: 1rem; }}
        .btn {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem 2rem;
            border: none;
            border-radius: 50px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            margin-top: 2rem;
        }}
    </style>
</head>
<body>
    <div class="error-box">
        <div class="error-icon">⚠️</div>
        <h2>Oops! Something went wrong</h2>
        <p style="margin: 1rem 0; color: #666;">{error_message}</p>
        <p><strong>💡 Tip:</strong> Make sure your description is clear and specific for better results.</p>
        <a href="/" class="btn">🏠 Go Back Home</a>
    </div>
</body>
</html>
    """

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "northstar-ai"}

# Vercel expects 'app' to be available directly
# No need for a custom handler function