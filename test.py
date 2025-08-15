"""
Simple test endpoint for NorthStar AI
"""
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
async def test_homepage():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>NorthStar AI - Test</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center;
            padding: 3rem;
            margin: 0;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            background: rgba(255,255,255,0.1);
            padding: 2rem;
            border-radius: 16px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>⭐ NorthStar AI</h1>
        <h2>🚀 System Test Successful!</h2>
        <p>Your deployment is working correctly.</p>
        <p>FastAPI backend is running on Vercel.</p>
        <p>Ready for AI-powered content generation!</p>
    </div>
</body>
</html>
    """

@app.get("/health")
async def health():
    return {"status": "healthy", "message": "NorthStar AI is running"}