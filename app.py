from flask import Flask, jsonify, request, session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from functools import wraps
import os
import logging
from datetime import datetime, timedelta
import secrets

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0-mvp'
    })

@app.route('/api/auth/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    session['user_id'] = email
    session['logged_in_at'] = datetime.utcnow().isoformat()
    
    logger.info(f"User {email} logged in")
    return jsonify({
        'message': 'Login successful',
        'user': email
    })

@app.route('/api/auth/logout', methods=['POST'])
@require_auth
def logout():
    user_id = session.get('user_id')
    session.clear()
    logger.info(f"User {user_id} logged out")
    return jsonify({'message': 'Logout successful'})

@app.route('/api/agents/generate', methods=['POST'])
@require_auth
@limiter.limit("20 per hour")
def generate_content():
    data = request.get_json()
    platform = data.get('platform')
    prompt = data.get('prompt')
    
    if not platform or not prompt:
        return jsonify({'error': 'Platform and prompt required'}), 400
    
    from agents.content_agent import ContentAgent
    agent = ContentAgent()
    result = agent.generate(platform, prompt)
    
    return jsonify({
        'status': 'success',
        'content': result
    })

@app.route('/api/agents/engage', methods=['POST'])
@require_auth
@limiter.limit("50 per day")
def engage_audience():
    data = request.get_json()
    platform = data.get('platform')
    post_id = data.get('post_id')
    
    if not platform or not post_id:
        return jsonify({'error': 'Platform and post_id required'}), 400
    
    from agents.engagement_agent import EngagementAgent
    agent = EngagementAgent()
    result = agent.engage(platform, post_id)
    
    return jsonify({
        'status': 'success',
        'engagement': result
    })

@app.route('/api/analytics/summary', methods=['GET'])
@require_auth
def get_analytics():
    platform = request.args.get('platform', 'all')
    days = int(request.args.get('days', 7))
    
    from agents.analytics_agent import AnalyticsAgent
    agent = AnalyticsAgent()
    summary = agent.get_summary(platform, days)
    
    return jsonify({
        'status': 'success',
        'analytics': summary
    })

@app.route('/api/schedule/create', methods=['POST'])
@require_auth
def schedule_post():
    data = request.get_json()
    content = data.get('content')
    platform = data.get('platform')
    scheduled_time = data.get('scheduled_time')
    
    if not all([content, platform, scheduled_time]):
        return jsonify({'error': 'Content, platform, and scheduled_time required'}), 400
    
    from utils.scheduler import PostScheduler
    scheduler = PostScheduler()
    job_id = scheduler.schedule_post(content, platform, scheduled_time)
    
    return jsonify({
        'status': 'success',
        'job_id': job_id
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    debug = os.environ.get('ENV', 'development') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)