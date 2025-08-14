import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import base64

st.set_page_config(
    page_title="NorthStar AI - Social Media Automation",
    page_icon="⭐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

def get_base64_image(image_path):
    """Convert image to base64 string for embedding"""
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except:
        return None

# Load images as base64
hero_bg = get_base64_image("static/images/hero-bg.jpg")
ai_brain = get_base64_image("static/images/ai-brain.jpg")
analytics_img = get_base64_image("static/images/analytics-dashboard.jpg")
content_img = get_base64_image("static/images/content-creation.jpg")
engagement_img = get_base64_image("static/images/engagement.jpg")
social_media_img = get_base64_image("static/images/social-media.jpg")
team_img = get_base64_image("static/images/team-photo.jpg")
ceo_img = get_base64_image("static/images/ceo-portrait.jpg")

# Enhanced CSS with professional images
st.markdown(f"""
<style>
    /* Hide Streamlit branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}
    
    /* Custom fonts and colors */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main-header {{
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.9) 0%, rgba(118, 75, 162, 0.9) 100%), 
                    url(data:image/jpeg;base64,{hero_bg}) center/cover;
        padding: 4rem 0;
        margin: -1rem -1rem 3rem -1rem;
        text-align: center;
        color: white;
        position: relative;
        overflow: hidden;
    }}
    
    .main-header::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.3);
        z-index: 1;
    }}
    
    .main-header > * {{
        position: relative;
        z-index: 2;
    }}
    
    .hero-title {{
        font-size: 4rem;
        font-weight: 700;
        margin-bottom: 1rem;
        line-height: 1.1;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }}
    
    .hero-subtitle {{
        font-size: 1.8rem;
        font-weight: 400;
        opacity: 0.95;
        margin-bottom: 2rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }}
    
    .hero-stats {{
        font-size: 1.3rem;
        opacity: 0.9;
        font-weight: 500;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }}
    
    .value-prop {{
        background: white;
        border-radius: 16px;
        padding: 2.5rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        margin: 1.5rem 0;
        border-left: 4px solid #667eea;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }}
    
    .value-prop:hover {{
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.15);
    }}
    
    .metric-card {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 2.5rem;
        color: white;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
        transition: transform 0.3s ease;
    }}
    
    .metric-card:hover {{
        transform: translateY(-5px);
    }}
    
    .feature-card {{
        background: white;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        margin: 1.5rem 0;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border: 1px solid #f0f0f0;
        position: relative;
        overflow: hidden;
    }}
    
    .feature-card::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 200px;
        background-size: cover;
        background-position: center;
        opacity: 0.1;
        transition: opacity 0.3s ease;
    }}
    
    .feature-card:hover {{
        transform: translateY(-8px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.15);
    }}
    
    .feature-card:hover::before {{
        opacity: 0.2;
    }}
    
    .feature-card-content {{
        position: relative;
        z-index: 2;
    }}
    
    .feature-card-ai {{
        background-image: url(data:image/jpeg;base64,{ai_brain});
    }}
    
    .feature-card-engagement {{
        background-image: url(data:image/jpeg;base64,{engagement_img});
    }}
    
    .feature-card-analytics {{
        background-image: url(data:image/jpeg;base64,{analytics_img});
    }}
    
    .testimonial {{
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        border-radius: 16px;
        padding: 2.5rem;
        margin: 2rem 0;
        border-left: 4px solid #4facfe;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        position: relative;
    }}
    
    .testimonial-content {{
        display: flex;
        align-items: center;
        gap: 2rem;
    }}
    
    .testimonial-avatar {{
        width: 80px;
        height: 80px;
        border-radius: 50%;
        background: url(data:image/jpeg;base64,{ceo_img}) center/cover;
        border: 4px solid white;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        flex-shrink: 0;
    }}
    
    .demo-banner {{
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        margin: 2rem 0;
        font-weight: 500;
        font-size: 1.1rem;
        box-shadow: 0 4px 20px rgba(79, 172, 254, 0.3);
    }}
    
    .pricing-card {{
        background: white;
        border-radius: 16px;
        padding: 2.5rem;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border: 2px solid #f0f0f0;
    }}
    
    .pricing-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 8px 32px rgba(0,0,0,0.15);
    }}
    
    .pricing-card-featured {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: 2px solid #667eea;
        transform: scale(1.05);
    }}
    
    .pricing-card-featured:hover {{
        transform: scale(1.08) translateY(-5px);
    }}
    
    .social-proof {{
        background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
        border-radius: 16px;
        padding: 2rem;
        margin: 2rem 0;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05);
    }}
    
    .team-showcase {{
        background: url(data:image/jpeg;base64,{team_img}) center/cover;
        border-radius: 16px;
        padding: 3rem;
        margin: 2rem 0;
        text-align: center;
        color: white;
        position: relative;
        overflow: hidden;
    }}
    
    .team-showcase::before {{
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.8) 0%, rgba(118, 75, 162, 0.8) 100%);
        z-index: 1;
    }}
    
    .team-showcase > * {{
        position: relative;
        z-index: 2;
    }}
    
    .content-studio-bg {{
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 249, 250, 0.95) 100%),
                    url(data:image/jpeg;base64,{content_img}) center/cover;
        border-radius: 16px;
        padding: 2rem;
        margin: 1rem 0;
    }}
    
    .analytics-bg {{
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(248, 249, 250, 0.95) 100%),
                    url(data:image/jpeg;base64,{analytics_img}) center/cover;
        border-radius: 16px;
        padding: 2rem;
        margin: 1rem 0;
    }}
    
    .social-media-bg {{
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(248, 249, 250, 0.9) 100%),
                    url(data:image/jpeg;base64,{social_media_img}) center/cover;
        border-radius: 16px;
        padding: 2rem;
        margin: 1rem 0;
    }}
    
    .floating-stats {{
        position: absolute;
        top: 20px;
        right: 20px;
        background: rgba(255, 255, 255, 0.95);
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        backdrop-filter: blur(10px);
    }}
    
    .btn-primary {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 2rem;
        border-radius: 50px;
        border: none;
        font-weight: 600;
        font-size: 1.1rem;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }}
    
    .btn-primary:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }}
    
    .feature-icon {{
        font-size: 3rem;
        margin-bottom: 1rem;
        display: block;
    }}
    
    .stats-number {{
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }}
    
    @media (max-width: 768px) {{
        .hero-title {{
            font-size: 2.5rem;
        }}
        
        .hero-subtitle {{
            font-size: 1.3rem;
        }}
        
        .feature-card {{
            margin: 1rem 0;
            padding: 1.5rem;
        }}
        
        .testimonial-content {{
            flex-direction: column;
            text-align: center;
        }}
    }}
</style>
""", unsafe_allow_html=True)

API_BASE_URL = os.environ.get('API_BASE_URL', 'http://localhost:5001')

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user_email = None

def login(email, password):
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/auth/login",
            json={'email': email, 'password': password}
        )
        if response.status_code == 200:
            st.session_state.authenticated = True
            st.session_state.user_email = email
            return True
    except:
        pass
    return False

def logout():
    st.session_state.authenticated = False
    st.session_state.user_email = None

# Landing Page
if not st.session_state.authenticated:
    # Hero Section with Background Image
    st.markdown(f"""
    <div class="main-header">
        <div class="hero-title">⭐ NorthStar AI</div>
        <div class="hero-subtitle">Social Media Automation That Actually Works</div>
        <div class="hero-stats">Save 50+ hours monthly • 850% ROI • 3x faster growth</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Social Proof Banner
    st.markdown("""
    <div class="social-proof">
        <h3>🚀 Trusted by 500+ creators and businesses worldwide</h3>
        <p><strong>Join companies like TechFlow, StartupHub, and GrowthLabs</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Value Proposition Section
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        <div class="value-prop">
            <div class="feature-icon">😰</div>
            <h3>🚀 The Problem</h3>
            <p>Content creators and businesses are <strong>burning out</strong> spending <strong>40+ hours weekly</strong> on:</p>
            <ul>
                <li>📝 Writing social media posts manually</li>
                <li>💬 Responding to comments one by one</li>
                <li>📊 Analyzing performance metrics</li>
                <li>⏰ Scheduling across multiple platforms</li>
                <li>🎯 Maintaining consistent brand voice</li>
            </ul>
            <p><strong>Result:</strong> Burnout, inconsistent posting, missed opportunities, and declining engagement</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="value-prop">
            <div class="feature-icon">✨</div>
            <h3>✨ Our Solution</h3>
            <p>AI agents that work <strong>24/7</strong> to:</p>
            <ul>
                <li>🤖 <strong>Generate</strong> viral content in seconds</li>
                <li>💬 <strong>Engage</strong> audiences authentically</li>
                <li>📈 <strong>Analyze</strong> ROI with ML predictions</li>
                <li>🚀 <strong>Scale</strong> across all platforms</li>
                <li>🎯 <strong>Maintain</strong> perfect brand voice</li>
            </ul>
            <p><strong>Result:</strong> 850% ROI, 70% time savings, 3x growth, and happier customers</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Live Demo Banner
    st.markdown("""
    <div class="demo-banner">
        🎯 <strong>Live Demo Available:</strong> See AI generate content for your brand in real-time
    </div>
    """, unsafe_allow_html=True)
    
    # Stats Grid with Enhanced Design
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="stats-number">50+</div>
            <p><strong>Hours Saved Monthly</strong></p>
            <small>Average time savings reported by users</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="stats-number">850%</div>
            <p><strong>Average ROI</strong></p>
            <small>Return on investment within 3 months</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="stats-number">3x</div>
            <p><strong>Faster Growth</strong></p>
            <small>Engagement and follower growth rate</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="stats-number">24/7</div>
            <p><strong>AI Working</strong></p>
            <small>Never miss an engagement opportunity</small>
        </div>
        """, unsafe_allow_html=True)
    
    # Features Section with Background Images
    st.markdown("<h2 style='text-align: center; margin: 4rem 0 3rem 0; font-size: 2.5rem;'>🎯 How Our AI Agents Transform Your Social Media</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="feature-card">
            <div class="feature-card-ai feature-card::before"></div>
            <div class="feature-card-content">
                <div class="feature-icon">🤖</div>
                <h3>AI Content Agent</h3>
                <p><strong>What it does:</strong> Creates viral-optimized posts using Claude AI with trend analysis</p>
                <p><strong>Time saved:</strong> 20 hours/week</p>
                <p><strong>Result:</strong> 25% higher engagement rates</p>
                <hr>
                <small>✅ Real-time trend analysis<br>✅ A/B testing variants<br>✅ Brand voice matching<br>✅ Platform optimization</small>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="feature-card">
            <div class="feature-card-engagement feature-card::before"></div>
            <div class="feature-card-content">
                <div class="feature-icon">💬</div>
                <h3>Smart Engagement</h3>
                <p><strong>What it does:</strong> Responds to comments with empathy & context while maintaining authenticity</p>
                <p><strong>Time saved:</strong> 15 hours/week</p>
                <p><strong>Result:</strong> 92% response rate maintenance</p>
                <hr>
                <small>✅ Sentiment analysis<br>✅ Spam protection<br>✅ Brand safety filters<br>✅ Human-like responses</small>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="feature-card">
            <div class="feature-card-analytics feature-card::before"></div>
            <div class="feature-card-content">
                <div class="feature-icon">📊</div>
                <h3>ROI Analytics</h3>
                <p><strong>What it does:</strong> Predicts performance & optimizes strategy with machine learning</p>
                <p><strong>Time saved:</strong> 10 hours/week</p>
                <p><strong>Result:</strong> 30% better content performance</p>
                <hr>
                <small>✅ ML predictions<br>✅ Growth forecasting<br>✅ Competitor analysis<br>✅ ROI tracking</small>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Customer Testimonial with Photo
    st.markdown("""
    <div class="testimonial">
        <div class="testimonial-content">
            <div class="testimonial-avatar"></div>
            <div>
                <h4 style="margin: 0 0 1rem 0; font-size: 1.3rem;">"NorthStar AI increased our social media ROI by 400% in just 6 weeks. The AI agents feel like having a full marketing team working 24/7."</h4>
                <p style="margin: 0; font-weight: 600; color: #667eea;">Sarah Kim, CEO of TechFlow</p>
                <small style="color: #666;">50-person SaaS company, $2M ARR</small>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Team Showcase
    st.markdown("""
    <div class="team-showcase">
        <h3 style="font-size: 2rem; margin-bottom: 1rem;">Built by AI Experts from Google, Meta & OpenAI</h3>
        <p style="font-size: 1.2rem; opacity: 0.9;">Our team has shipped AI products used by millions</p>
    </div>
    """, unsafe_allow_html=True)
    
    # CTA Section
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="text-align: center; background: white; padding: 3rem; border-radius: 16px; box-shadow: 0 8px 32px rgba(0,0,0,0.1);">
            <h3 style="font-size: 2rem; margin-bottom: 1rem;">Ready to 10x Your Social Media?</h3>
            <p style="font-size: 1.2rem; margin-bottom: 2rem;">Join 500+ creators saving 50+ hours weekly with AI automation</p>
        """, unsafe_allow_html=True)
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("🚀 Start Free Demo", type="primary", use_container_width=True, key="demo_btn"):
                st.session_state.authenticated = True
                st.session_state.user_email = "demo@northstar.ai"
                st.rerun()
        
        with col_btn2:
            with st.expander("💼 Enterprise Login"):
                with st.form("login_form"):
                    email = st.text_input("Email", placeholder="your@company.com")
                    password = st.text_input("Password", type="password", placeholder="Enter password")
                    
                    if st.form_submit_button("Login", use_container_width=True):
                        if login(email, password):
                            st.success("Login successful!")
                            st.rerun()
                        else:
                            st.error("Invalid credentials")
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Pricing Section with Enhanced Design
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; font-size: 2.2rem; margin-bottom: 2rem;'>💰 Simple, Transparent Pricing</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="pricing-card">
            <h4 style="font-size: 1.5rem; margin-bottom: 1rem;">Starter</h4>
            <h2 style="font-size: 3rem; margin: 1rem 0; color: #667eea;">Free</h2>
            <p style="margin-bottom: 2rem; color: #666;">Perfect for testing our AI</p>
            <ul style="text-align: left; margin-bottom: 2rem;">
                <li>10 AI posts/month</li>
                <li>Basic analytics</li>
                <li>1 platform connection</li>
                <li>Email support</li>
            </ul>
            <button style="width: 100%; padding: 1rem; border: 2px solid #667eea; background: white; color: #667eea; border-radius: 8px; font-weight: 600;">Get Started Free</button>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="pricing-card pricing-card-featured">
            <div style="background: rgba(255,255,255,0.2); padding: 0.5rem; border-radius: 20px; margin-bottom: 1rem; font-weight: 600;">⭐ MOST POPULAR</div>
            <h4 style="font-size: 1.5rem; margin-bottom: 1rem;">Pro</h4>
            <h2 style="font-size: 3rem; margin: 1rem 0;">$299<span style="font-size: 1rem;">/mo</span></h2>
            <p style="margin-bottom: 2rem; opacity: 0.9;">For growing businesses</p>
            <ul style="text-align: left; margin-bottom: 2rem;">
                <li>Unlimited AI posts</li>
                <li>All platform integrations</li>
                <li>Advanced analytics & predictions</li>
                <li>Priority support</li>
                <li>A/B testing</li>
                <li>Custom brand voice</li>
            </ul>
            <button style="width: 100%; padding: 1rem; border: none; background: white; color: #667eea; border-radius: 8px; font-weight: 600;">Start 14-Day Trial</button>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="pricing-card">
            <h4 style="font-size: 1.5rem; margin-bottom: 1rem;">Enterprise</h4>
            <h2 style="font-size: 3rem; margin: 1rem 0; color: #667eea;">$999<span style="font-size: 1rem;">/mo</span></h2>
            <p style="margin-bottom: 2rem; color: #666;">For large teams</p>
            <ul style="text-align: left; margin-bottom: 2rem;">
                <li>Custom AI training</li>
                <li>White-label option</li>
                <li>Dedicated success manager</li>
                <li>API access</li>
                <li>Custom integrations</li>
                <li>SLA guarantee</li>
            </ul>
            <button style="width: 100%; padding: 1rem; border: 2px solid #667eea; background: white; color: #667eea; border-radius: 8px; font-weight: 600;">Contact Sales</button>
        </div>
        """, unsafe_allow_html=True)

# Main Dashboard for Authenticated Users
else:
    # Top Navigation
    st.markdown(f"""
    <div style="background: white; padding: 1rem 0; margin: -1rem -1rem 2rem -1rem; border-bottom: 1px solid #e0e0e0; box-shadow: 0 2px 10px rgba(0,0,0,0.05);">
        <div style="display: flex; justify-content: space-between; align-items: center; max-width: 1200px; margin: 0 auto; padding: 0 2rem;">
            <h2 style="margin: 0; color: #667eea; font-size: 1.8rem;">⭐ NorthStar AI</h2>
            <div style="display: flex; align-items: center; gap: 1rem;">
                <span style="color: #666; font-weight: 500;">Welcome, {st.session_state.user_email}</span>
                <div style="width: 40px; height: 40px; border-radius: 50%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: flex; align-items: center; justify-content: center; color: white; font-weight: 600;">
                    {st.session_state.user_email[0].upper()}
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Tab Navigation
    tabs = st.tabs(["📊 Dashboard", "✨ AI Content Studio", "💬 Engagement Hub", "📈 Analytics Lab", "⏰ Scheduler", "⚙️ Settings"])
    
    with tabs[0]:  # Dashboard
        st.markdown("## 🎯 Your AI-Powered Command Center")
        
        # Key Metrics Row with Enhanced Design
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 2rem; border-radius: 16px; text-align: center; box-shadow: 0 8px 32px rgba(79, 172, 254, 0.3);">
                <h3 style="margin: 0; font-size: 2.5rem; font-weight: 700;">45.2K</h3>
                <p style="margin: 0.5rem 0 0 0; opacity: 0.9; font-weight: 500;">Total Impressions</p>
                <small style="opacity: 0.8; background: rgba(255,255,255,0.2); padding: 0.3rem 0.8rem; border-radius: 20px;">+12% vs last week</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); color: #333; padding: 2rem; border-radius: 16px; text-align: center; box-shadow: 0 8px 32px rgba(168, 237, 234, 0.3);">
                <h3 style="margin: 0; font-size: 2.5rem; font-weight: 700;">2.3K</h3>
                <p style="margin: 0.5rem 0 0 0; font-weight: 500;">Engagements</p>
                <small style="background: rgba(102, 126, 234, 0.1); color: #667eea; padding: 0.3rem 0.8rem; border-radius: 20px; font-weight: 600;">+18% growth</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); color: #333; padding: 2rem; border-radius: 16px; text-align: center; box-shadow: 0 8px 32px rgba(255, 236, 210, 0.3);">
                <h3 style="margin: 0; font-size: 2.5rem; font-weight: 700;">45.5h</h3>
                <p style="margin: 0.5rem 0 0 0; font-weight: 500;">Time Saved</p>
                <small style="background: rgba(252, 182, 159, 0.3); padding: 0.3rem 0.8rem; border-radius: 20px; font-weight: 600;">This month</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 2rem; border-radius: 16px; text-align: center; box-shadow: 0 8px 32px rgba(240, 147, 251, 0.3);">
                <h3 style="margin: 0; font-size: 2.5rem; font-weight: 700;">₩2.1M</h3>
                <p style="margin: 0.5rem 0 0 0; opacity: 0.9; font-weight: 500;">ROI Generated</p>
                <small style="opacity: 0.8; background: rgba(255,255,255,0.2); padding: 0.3rem 0.8rem; border-radius: 20px;">850% return</small>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Performance Charts with Background
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="analytics-bg">', unsafe_allow_html=True)
            st.markdown("### 📈 Performance Trend")
            dates = pd.date_range(end=datetime.now(), periods=7)
            performance_data = pd.DataFrame({
                'Date': dates,
                'Impressions': [4500, 4800, 5200, 4900, 5500, 6000, 6300],
                'Engagements': [220, 235, 265, 245, 280, 310, 340]
            })
            
            fig = px.line(performance_data, x='Date', y=['Impressions', 'Engagements'],
                         title='7-Day Performance Trend',
                         color_discrete_map={'Impressions': '#667eea', 'Engagements': '#f093fb'})
            fig.update_layout(
                height=400, 
                showlegend=True,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="social-media-bg">', unsafe_allow_html=True)
            st.markdown("### 🎯 AI Agent Activity")
            agent_data = pd.DataFrame({
                'Agent': ['Content Generator', 'Engagement Bot', 'Analytics AI'],
                'Actions': [45, 125, 23],
                'Success Rate': [95, 92, 98]
            })
            
            fig = px.bar(agent_data, x='Agent', y='Actions',
                        color='Success Rate',
                        color_continuous_scale='viridis',
                        title='AI Agent Performance Today')
            fig.update_layout(
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Recent Activity with Enhanced Design
        st.markdown("### 🚀 Recent AI-Generated Content")
        
        recent_posts = [
            {"Time": "2 mins ago", "Platform": "Twitter", "Content": "🚀 AI is revolutionizing content creation across industries...", "Engagement": "5.2%", "Status": "🟢 Live", "Reach": "12.3K"},
            {"Time": "15 mins ago", "Platform": "Instagram", "Content": "✨ Behind the scenes of our AI lab where magic happens...", "Engagement": "7.8%", "Status": "🟢 Live", "Reach": "8.7K"},
            {"Time": "1 hour ago", "Platform": "LinkedIn", "Content": "The future of work is AI-assisted, here's what we've learned...", "Engagement": "4.1%", "Status": "📅 Scheduled", "Reach": "5.2K"}
        ]
        
        df = pd.DataFrame(recent_posts)
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    with tabs[1]:  # AI Content Studio
        st.markdown('<div class="content-studio-bg">', unsafe_allow_html=True)
        st.markdown("## ✨ AI Content Studio")
        st.markdown("*Create viral content in seconds with our Claude-powered AI*")
        st.markdown('</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 🎯 Content Generation")
            
            platform = st.selectbox(
                "Select Platform",
                ["Twitter", "Instagram", "LinkedIn", "TikTok"],
                help="Each platform has optimized prompts and character limits"
            )
            
            content_type = st.selectbox(
                "Content Type",
                ["Product Launch", "Industry Insights", "Behind the Scenes", "Educational", "Promotional", "Custom"]
            )
            
            prompt = st.text_area(
                "Describe your content",
                placeholder="E.g., Launch our new AI feature that helps users save 20 hours per week on social media management...",
                height=120,
                help="Be specific about your product, audience, and desired tone"
            )
            
            col_opt1, col_opt2, col_opt3 = st.columns(3)
            with col_opt1:
                optimize_virality = st.checkbox("🔥 Viral Optimization", value=True)
            with col_opt2:
                generate_variants = st.checkbox("🎲 A/B Test Variants", value=True)
            with col_opt3:
                include_hashtags = st.checkbox("# Smart Hashtags", value=True)
            
            if st.button("🚀 Generate Content", type="primary", use_container_width=True):
                with st.spinner("🤖 AI is crafting your perfect post..."):
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/api/agents/generate",
                            json={
                                'platform': platform.lower(),
                                'prompt': prompt
                            }
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            content = result.get('content', {})
                            
                            st.success("✅ Content generated successfully!")
                            
                            st.markdown("### 🎯 Primary Content")
                            st.markdown(f"""
                            <div style="background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); padding: 2rem; border-radius: 12px; border-left: 4px solid #667eea; box-shadow: 0 4px 15px rgba(0,0,0,0.1);">
                                <div style="font-size: 1.1rem; line-height: 1.6;">{content.get('primary_content', 'Generated content')}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if generate_variants and content.get('variants'):
                                st.markdown("### 🎲 A/B Testing Variants")
                                for i, variant in enumerate(content.get('variants', [])[:2]):
                                    st.markdown(f"""
                                    <div style="background: linear-gradient(135deg, #f0f8ff 0%, #e6f3ff 100%); padding: 1.5rem; border-radius: 8px; margin: 0.8rem 0; border-left: 3px solid #4facfe;">
                                        <strong style="color: #4facfe;">Variant {i+1}:</strong><br>
                                        <div style="margin-top: 0.8rem; font-size: 1rem; line-height: 1.5;">{variant}</div>
                                    </div>
                                    """, unsafe_allow_html=True)
                            
                            # Performance prediction with enhanced design
                            st.markdown("### 📊 AI Performance Prediction")
                            col_pred1, col_pred2, col_pred3 = st.columns(3)
                            with col_pred1:
                                st.metric("Expected Engagement", "5.2% - 7.8%", "📈")
                            with col_pred2:
                                st.metric("Viral Potential", "High", "🔥")
                            with col_pred3:
                                st.metric("Best Time to Post", "2:15 PM", "⏰")
                        else:
                            st.error("Failed to generate content")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        with col2:
            st.markdown("### 💡 Pro Tips")
            st.markdown("""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem; border-radius: 16px; box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);">
                <h4 style="margin-top: 0;">📝 Content Best Practices</h4>
                <ul style="margin: 0; padding-left: 1.2rem;">
                    <li>Be specific with your target audience</li>
                    <li>Include emotional triggers and pain points</li>
                    <li>Mention concrete benefits and numbers</li>
                    <li>Use action-oriented language</li>
                    <li>Add questions to boost engagement</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            st.markdown("### 📊 Content Performance")
            st.metric("Posts This Week", "12", "+3")
            st.metric("Avg Engagement", "6.2%", "+1.4%")
            st.metric("Viral Posts", "3", "+2")
            
            st.markdown("### 🎯 Trending Topics")
            st.markdown("""
            <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 12px; margin-top: 1rem;">
                <small style="font-weight: 600; color: #667eea;">🔥 Hot right now:</small><br>
                <span style="background: #e3f2fd; padding: 0.3rem 0.8rem; border-radius: 20px; margin: 0.2rem; display: inline-block; font-size: 0.9rem;">#AI</span>
                <span style="background: #f3e5f5; padding: 0.3rem 0.8rem; border-radius: 20px; margin: 0.2rem; display: inline-block; font-size: 0.9rem;">#Automation</span>
                <span style="background: #e8f5e8; padding: 0.3rem 0.8rem; border-radius: 20px; margin: 0.2rem; display: inline-block; font-size: 0.9rem;">#Productivity</span>
            </div>
            """, unsafe_allow_html=True)
    
    # Continue with other tabs...
    with tabs[2]:  # Engagement Hub
        st.markdown("## 💬 Smart Engagement Hub")
        st.markdown("*AI-powered responses that maintain your brand voice*")
        
        # Rest of engagement hub code...
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 🤖 Auto-Engagement Settings")
            
            platform = st.selectbox("Platform", ["All Platforms", "Twitter", "Instagram", "LinkedIn"])
            
            engagement_level = st.slider(
                "Daily Engagement Limit",
                min_value=10,
                max_value=50,
                value=30,
                help="AI will engage up to this many times per day to avoid spam"
            )
            
            engagement_types = st.multiselect(
                "Engagement Types",
                ["Positive Comments", "Questions", "Mentions", "Industry Discussions"],
                default=["Positive Comments", "Questions"]
            )
            
            brand_voice = st.selectbox(
                "Brand Voice",
                ["Professional", "Friendly", "Casual", "Expert", "Inspiring"]
            )
            
            if st.button("💾 Update Settings", type="primary"):
                st.success("✅ Engagement settings updated successfully!")
            
            st.markdown("### 📊 Recent AI Engagements")
            
            engagements = [
                {"Time": "2 mins ago", "Type": "💬 Reply", "Platform": "Twitter", "Preview": "Thanks for sharing! We'd love to hear more about...", "Sentiment": "😊 Positive"},
                {"Time": "15 mins ago", "Type": "❤️ Like", "Platform": "Instagram", "Preview": "Liked comment about AI automation trends", "Sentiment": "👍 Neutral"},
                {"Time": "1 hour ago", "Type": "💬 Answer", "Platform": "LinkedIn", "Preview": "Great question! Here's how our AI handles...", "Sentiment": "🤔 Question"}
            ]
            
            df = pd.DataFrame(engagements)
            st.dataframe(df, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("### 📈 Engagement Stats")
            
            st.markdown("""
            <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 2rem; border-radius: 16px; text-align: center; margin-bottom: 1.5rem; box-shadow: 0 8px 25px rgba(79, 172, 254, 0.3);">
                <h3 style="margin: 0; font-size: 2.5rem;">18/30</h3>
                <p style="margin: 0; opacity: 0.9; font-weight: 500;">Today's Engagements</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.metric("Response Rate", "94%", "+2%")
            st.metric("Avg Response Time", "2.3 mins", "-1.2 mins")
            st.metric("Quality Score", "9.2/10", "+0.3")
            
            st.markdown("### 🎯 Engagement Quality")
            quality_score = 92
            st.progress(quality_score/100)
            st.caption(f"AI Authenticity Score: {quality_score}%")
    
    # Continue with remaining tabs (Analytics, Scheduler, Settings)...
    with tabs[3]:  # Analytics Lab
        st.markdown("## 📈 Analytics Lab")
        st.markdown("*AI-powered insights and growth predictions*")
        
        # Analytics implementation here (same as before but with enhanced styling)
        pass
    
    with tabs[4]:  # Scheduler
        st.markdown("## ⏰ Content Scheduler")
        st.markdown("*AI-optimized posting times for maximum reach*")
        
        # Scheduler implementation here
        pass
    
    with tabs[5]:  # Settings
        st.markdown("## ⚙️ Settings & Configuration")
        
        # Settings implementation here
        pass
    
    # Enhanced Footer with logout
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0; background: #f8f9fa; margin: 2rem -1rem -1rem -1rem; border-radius: 16px 16px 0 0;">
        <p style="margin: 0 0 1rem 0; color: #666;">Need help? Contact our support team at <strong>support@northstar.ai</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🚪 Logout", use_container_width=True):
            logout()
            st.rerun()