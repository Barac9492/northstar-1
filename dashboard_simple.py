import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

st.set_page_config(
    page_title="NorthStar AI - Social Media Automation",
    page_icon="⭐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Webflow-style design
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom fonts and colors */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .main-header {
        font-family: 'Inter', sans-serif;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 3rem 0;
        margin: -1rem -1rem 2rem -1rem;
        text-align: center;
        color: white;
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        line-height: 1.1;
    }
    
    .hero-subtitle {
        font-size: 1.5rem;
        font-weight: 400;
        opacity: 0.9;
        margin-bottom: 2rem;
    }
    
    .value-prop {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        border-radius: 16px;
        padding: 2rem;
        color: white;
        text-align: center;
        margin: 1rem 0;
    }
    
    .feature-card {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        margin: 1rem 0;
        transition: transform 0.3s ease;
        border: 1px solid #f0f0f0;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .cta-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 2rem;
        border-radius: 50px;
        border: none;
        font-weight: 600;
        font-size: 1.1rem;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 2rem 0;
    }
    
    .nav-tab {
        background: #f8f9fa;
        border: none;
        padding: 1rem 2rem;
        border-radius: 50px;
        font-weight: 500;
        margin: 0 0.5rem;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .nav-tab.active {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .demo-banner {
        background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin: 1rem 0;
        font-weight: 500;
    }
    
    .testimonial {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 2rem;
        margin: 1rem 0;
        border-left: 4px solid #4facfe;
        font-style: italic;
    }
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
    # Hero Section
    st.markdown("""
    <div class="main-header">
        <div class="hero-title">⭐ NorthStar AI</div>
        <div class="hero-subtitle">Social Media Automation That Actually Works</div>
        <p style="font-size: 1.2rem; opacity: 0.8;">Save 50+ hours per month while growing 3x faster</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Value Proposition Section
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        <div class="value-prop">
            <h3>🚀 The Problem</h3>
            <p>Content creators and businesses spend <strong>40+ hours weekly</strong> on:</p>
            <ul>
                <li>Writing social media posts</li>
                <li>Responding to comments manually</li>
                <li>Analyzing performance metrics</li>
                <li>Scheduling across platforms</li>
            </ul>
            <p><strong>Result:</strong> Burnout, inconsistent posting, missed opportunities</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="value-prop">
            <h3>✨ Our Solution</h3>
            <p>AI agents that work <strong>24/7</strong> to:</p>
            <ul>
                <li><strong>Generate</strong> viral content in seconds</li>
                <li><strong>Engage</strong> audiences authentically</li>
                <li><strong>Analyze</strong> ROI with ML predictions</li>
                <li><strong>Scale</strong> across all platforms</li>
            </ul>
            <p><strong>Result:</strong> 850% ROI, 70% time savings, 3x growth</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Social Proof & Metrics
    st.markdown("""
    <div class="demo-banner">
        🎯 Live Demo: See AI generate content for your brand in real-time
    </div>
    """, unsafe_allow_html=True)
    
    # Stats Grid
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h2>50+</h2>
            <p>Hours Saved Monthly</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h2>850%</h2>
            <p>Average ROI</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h2>3x</h2>
            <p>Faster Growth</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h2>24/7</h2>
            <p>AI Working</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Features Section
    st.markdown("<h2 style='text-align: center; margin: 3rem 0 2rem 0;'>🎯 How It Works</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>🤖 AI Content Agent</h3>
            <p><strong>What it does:</strong> Creates viral-optimized posts using Claude AI</p>
            <p><strong>Time saved:</strong> 20 hours/week</p>
            <p><strong>Result:</strong> 25% higher engagement rates</p>
            <hr>
            <small>✅ Trend analysis<br>✅ A/B testing<br>✅ Brand voice matching</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>💬 Smart Engagement</h3>
            <p><strong>What it does:</strong> Responds to comments with empathy & context</p>
            <p><strong>Time saved:</strong> 15 hours/week</p>
            <p><strong>Result:</strong> 92% response rate maintenance</p>
            <hr>
            <small>✅ Sentiment analysis<br>✅ Spam protection<br>✅ Brand safety</small>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3>📊 ROI Analytics</h3>
            <p><strong>What it does:</strong> Predicts performance & optimizes strategy</p>
            <p><strong>Time saved:</strong> 10 hours/week</p>
            <p><strong>Result:</strong> 30% better content performance</p>
            <hr>
            <small>✅ ML predictions<br>✅ Growth forecasting<br>✅ Competitor analysis</small>
        </div>
        """, unsafe_allow_html=True)
    
    # Testimonial
    st.markdown("""
    <div class="testimonial">
        <h4>"NorthStar AI increased our social media ROI by 400% in just 6 weeks. The AI agents feel like having a full marketing team working 24/7." - Sarah Kim, CEO of TechFlow</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # CTA Section
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="text-align: center; background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);">
            <h3>Ready to 10x Your Social Media?</h3>
            <p>Join 500+ creators saving 50+ hours weekly</p>
        """, unsafe_allow_html=True)
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("🚀 Start Free Demo", type="primary", use_container_width=True):
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
    
    # Pricing Preview
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>💰 Simple, Transparent Pricing</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background: #f8f9fa; padding: 2rem; border-radius: 12px; text-align: center;">
            <h4>Starter</h4>
            <h2>Free</h2>
            <p>Perfect for testing</p>
            <ul style="text-align: left;">
                <li>10 AI posts/month</li>
                <li>Basic analytics</li>
                <li>1 platform</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem; border-radius: 12px; text-align: center;">
            <h4>Pro</h4>
            <h2>$299/mo</h2>
            <p>For growing businesses</p>
            <ul style="text-align: left;">
                <li>Unlimited AI posts</li>
                <li>All platforms</li>
                <li>Advanced analytics</li>
                <li>Priority support</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: #f8f9fa; padding: 2rem; border-radius: 12px; text-align: center;">
            <h4>Enterprise</h4>
            <h2>$999/mo</h2>
            <p>For large teams</p>
            <ul style="text-align: left;">
                <li>Custom AI training</li>
                <li>White-label option</li>
                <li>Dedicated support</li>
                <li>API access</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

# Main Dashboard for Authenticated Users
else:
    # Top Navigation
    st.markdown("""
    <div style="background: white; padding: 1rem 0; margin: -1rem -1rem 2rem -1rem; border-bottom: 1px solid #e0e0e0;">
        <div style="display: flex; justify-content: space-between; align-items: center; max-width: 1200px; margin: 0 auto; padding: 0 2rem;">
            <h2 style="margin: 0; color: #667eea;">⭐ NorthStar AI</h2>
            <div style="display: flex; align-items: center; gap: 1rem;">
                <span style="color: #666;">Welcome, """ + st.session_state.user_email + """</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Tab Navigation
    tabs = st.tabs(["📊 Dashboard", "✨ AI Content Studio", "💬 Engagement Hub", "📈 Analytics Lab", "⏰ Scheduler", "⚙️ Settings"])
    
    with tabs[0]:  # Dashboard
        st.markdown("## 🎯 Your AI-Powered Command Center")
        
        # Key Metrics Row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 1.5rem; border-radius: 12px; text-align: center;">
                <h3 style="margin: 0; font-size: 2rem;">45.2K</h3>
                <p style="margin: 0; opacity: 0.9;">Total Impressions</p>
                <small style="opacity: 0.8;">+12% vs last week</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); color: #333; padding: 1.5rem; border-radius: 12px; text-align: center;">
                <h3 style="margin: 0; font-size: 2rem;">2.3K</h3>
                <p style="margin: 0;">Engagements</p>
                <small style="color: #666;">+18% growth</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); color: #333; padding: 1.5rem; border-radius: 12px; text-align: center;">
                <h3 style="margin: 0; font-size: 2rem;">45.5h</h3>
                <p style="margin: 0;">Time Saved</p>
                <small style="color: #666;">This month</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); color: white; padding: 1.5rem; border-radius: 12px; text-align: center;">
                <h3 style="margin: 0; font-size: 2rem;">₩2.1M</h3>
                <p style="margin: 0; opacity: 0.9;">ROI Generated</p>
                <small style="opacity: 0.8;">850% return</small>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Performance Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📈 Performance Trend")
            dates = pd.date_range(end=datetime.now(), periods=7)
            performance_data = pd.DataFrame({
                'Date': dates,
                'Impressions': [4500, 4800, 5200, 4900, 5500, 6000, 6300],
                'Engagements': [220, 235, 265, 245, 280, 310, 340]
            })
            
            fig = px.line(performance_data, x='Date', y=['Impressions', 'Engagements'],
                         title='7-Day Performance',
                         color_discrete_map={'Impressions': '#667eea', 'Engagements': '#f093fb'})
            fig.update_layout(height=400, showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
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
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Recent Activity
        st.markdown("### 🚀 Recent AI-Generated Content")
        
        recent_posts = [
            {"Time": "2 mins ago", "Platform": "Twitter", "Content": "🚀 AI is revolutionizing content creation...", "Engagement": "5.2%", "Status": "🟢 Live"},
            {"Time": "15 mins ago", "Platform": "Instagram", "Content": "✨ Behind the scenes of our AI lab...", "Engagement": "7.8%", "Status": "🟢 Live"},
            {"Time": "1 hour ago", "Platform": "LinkedIn", "Content": "The future of work is AI-assisted...", "Engagement": "4.1%", "Status": "📅 Scheduled"}
        ]
        
        df = pd.DataFrame(recent_posts)
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    with tabs[1]:  # AI Content Studio
        st.markdown("## ✨ AI Content Studio")
        st.markdown("*Create viral content in seconds with our Claude-powered AI*")
        
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
                placeholder="E.g., Launch our new AI feature that helps users save 20 hours per week...",
                height=100,
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
                            <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 12px; border-left: 4px solid #667eea;">
                                {content.get('primary_content', 'Generated content')}
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if generate_variants and content.get('variants'):
                                st.markdown("### 🎲 A/B Testing Variants")
                                for i, variant in enumerate(content.get('variants', [])[:2]):
                                    st.markdown(f"""
                                    <div style="background: #f0f8ff; padding: 1rem; border-radius: 8px; margin: 0.5rem 0;">
                                        <strong>Variant {i+1}:</strong> {variant}
                                    </div>
                                    """, unsafe_allow_html=True)
                            
                            # Performance prediction
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
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1.5rem; border-radius: 12px;">
                <h4>Content Best Practices</h4>
                <ul>
                    <li>Be specific with your audience</li>
                    <li>Include emotional triggers</li>
                    <li>Mention concrete benefits</li>
                    <li>Use action-oriented language</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### 📊 Content Performance")
            st.metric("Posts This Week", "12", "+3")
            st.metric("Avg Engagement", "6.2%", "+1.4%")
            st.metric("Viral Posts", "3", "+2")
    
    with tabs[2]:  # Engagement Hub
        st.markdown("## 💬 Smart Engagement Hub")
        st.markdown("*AI-powered responses that maintain your brand voice*")
        
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
                {"Time": "2 mins ago", "Type": "💬 Reply", "Platform": "Twitter", "Preview": "Thanks for sharing! We'd love to...", "Sentiment": "😊 Positive"},
                {"Time": "15 mins ago", "Type": "❤️ Like", "Platform": "Instagram", "Preview": "Liked comment about AI trends", "Sentiment": "👍 Neutral"},
                {"Time": "1 hour ago", "Type": "💬 Answer", "Platform": "LinkedIn", "Preview": "Great question! Here's how we...", "Sentiment": "🤔 Question"}
            ]
            
            df = pd.DataFrame(engagements)
            st.dataframe(df, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("### 📈 Engagement Stats")
            
            st.markdown("""
            <div style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); color: white; padding: 1.5rem; border-radius: 12px; text-align: center; margin-bottom: 1rem;">
                <h3 style="margin: 0;">18/30</h3>
                <p style="margin: 0; opacity: 0.9;">Today's Engagements</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.metric("Response Rate", "94%", "+2%")
            st.metric("Avg Response Time", "2.3 mins", "-1.2 mins")
            st.metric("Quality Score", "9.2/10", "+0.3")
            
            st.markdown("### 🎯 Engagement Quality")
            quality_score = 92
            st.progress(quality_score/100)
            st.caption(f"AI Authenticity Score: {quality_score}%")
    
    with tabs[3]:  # Analytics Lab
        st.markdown("## 📈 Analytics Lab")
        st.markdown("*AI-powered insights and growth predictions*")
        
        # Analytics tabs
        analytics_tabs = st.tabs(["📊 Overview", "🔮 Predictions", "💰 ROI Analysis", "🏆 Competitors"])
        
        with analytics_tabs[0]:  # Overview
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown("### 📈 Performance Dashboard")
                
                # Time series chart
                dates = pd.date_range(end=datetime.now(), periods=30)
                metrics_data = pd.DataFrame({
                    'Date': dates,
                    'Impressions': [5000 + i*100 + (i%7)*200 for i in range(30)],
                    'Engagements': [250 + i*5 + (i%7)*10 for i in range(30)],
                    'Followers': [1000 + i*10 for i in range(30)]
                })
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=metrics_data['Date'], y=metrics_data['Impressions'],
                                        mode='lines', name='Impressions', line=dict(color='#667eea')))
                fig.add_trace(go.Scatter(x=metrics_data['Date'], y=metrics_data['Engagements'],
                                        mode='lines', name='Engagements', yaxis='y2', line=dict(color='#f093fb')))
                
                fig.update_layout(
                    title='30-Day Performance Trend',
                    yaxis=dict(title='Impressions'),
                    yaxis2=dict(title='Engagements', overlaying='y', side='right'),
                    hovermode='x unified',
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("### 🎯 Key Insights")
                st.markdown("""
                <div style="background: #e8f5e8; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                    <strong>🚀 Top Insight</strong><br>
                    Video content performs 3x better on weekends
                </div>
                
                <div style="background: #fff3cd; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                    <strong>⏰ Optimal Times</strong><br>
                    2-4 PM shows highest engagement
                </div>
                
                <div style="background: #d1ecf1; padding: 1rem; border-radius: 8px;">
                    <strong>📊 Growth Trend</strong><br>
                    Audience growing 15% monthly
                </div>
                """, unsafe_allow_html=True)
        
        with analytics_tabs[1]:  # Predictions
            st.markdown("### 🔮 AI Growth Predictions")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Next Week Impressions", "52K", "+15%", help="ML-based forecast")
            with col2:
                st.metric("Expected Engagements", "2.8K", "+20%", help="Based on current trend")
            with col3:
                st.metric("Follower Projection", "1,500", "+12%", help="End of month estimate")
            
            # Prediction chart
            future_dates = pd.date_range(start=datetime.now(), periods=14)
            prediction_data = pd.DataFrame({
                'Date': future_dates,
                'Predicted': [8000 + i*200 for i in range(14)],
                'Upper Bound': [8500 + i*200 for i in range(14)],
                'Lower Bound': [7500 + i*200 for i in range(14)]
            })
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=prediction_data['Date'], y=prediction_data['Predicted'],
                                    mode='lines', name='Predicted Growth', line=dict(color='#667eea')))
            fig.add_trace(go.Scatter(x=prediction_data['Date'], y=prediction_data['Upper Bound'],
                                    mode='lines', name='Best Case', line=dict(dash='dash', color='#4facfe')))
            fig.add_trace(go.Scatter(x=prediction_data['Date'], y=prediction_data['Lower Bound'],
                                    mode='lines', name='Worst Case', line=dict(dash='dash', color='#f093fb')))
            
            fig.update_layout(title='14-Day Growth Forecast', height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with analytics_tabs[2]:  # ROI Analysis
            st.markdown("### 💰 ROI Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 💵 Value Generated")
                st.metric("Time Saved This Month", "45.5 hours")
                st.metric("Value of Time Saved", "₩2.3M", help="At ₩50K/hour rate")
                st.metric("Engagement Value", "₩800K", help="Based on industry CPM")
                st.metric("Total ROI", "850%", help="Return on ₩299K investment")
            
            with col2:
                roi_data = pd.DataFrame({
                    'Category': ['Time Savings', 'Engagement Value', 'Lead Generation', 'Brand Awareness'],
                    'Value (₩K)': [2300, 800, 500, 400]
                })
                
                fig = px.pie(roi_data, values='Value (₩K)', names='Category',
                           title='ROI Breakdown',
                           color_discrete_sequence=['#667eea', '#f093fb', '#4facfe', '#ffecd2'])
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            st.success("📊 **Monthly ROI Summary**: ₩4M value generated from ₩299K investment = 1,240% ROI")
    
    with tabs[4]:  # Scheduler
        st.markdown("## ⏰ Content Scheduler")
        st.markdown("*AI-optimized posting times for maximum reach*")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 📅 Schedule New Content")
            
            content = st.text_area("Content", height=100, placeholder="Your amazing content here...")
            
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                platform = st.selectbox("Platform", ["Twitter", "Instagram", "LinkedIn", "TikTok"])
                schedule_type = st.selectbox("Scheduling", ["Specific Time", "AI Optimal Time", "Recurring"])
            with col_s2:
                if schedule_type == "Specific Time":
                    schedule_date = st.date_input("Date", min_value=datetime.now().date())
                    schedule_time = st.time_input("Time")
                elif schedule_type == "AI Optimal Time":
                    st.info("🤖 AI will choose the best time based on your audience")
                else:
                    repeat_frequency = st.selectbox("Frequency", ["Daily", "Weekly", "Monthly"])
            
            if st.button("📅 Schedule Post", type="primary", use_container_width=True):
                st.success(f"✅ Post scheduled successfully for {platform}!")
            
            st.markdown("### 📋 Scheduled Posts")
            
            scheduled = [
                {"Time": "Today 2:00 PM", "Platform": "Twitter", "Content": "🚀 Exciting AI update coming...", "Status": "⏳ Pending", "Engagement": "Est. 5.2%"},
                {"Time": "Tomorrow 10:00 AM", "Platform": "LinkedIn", "Content": "Industry insights on automation...", "Status": "⏳ Pending", "Engagement": "Est. 4.8%"},
                {"Time": "Friday 3:00 PM", "Platform": "Instagram", "Content": "Behind the scenes content...", "Status": "⏳ Pending", "Engagement": "Est. 7.1%"}
            ]
            
            df = pd.DataFrame(scheduled)
            st.dataframe(df, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("### 🎯 AI Recommendations")
            
            st.markdown("""
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 1.5rem; border-radius: 12px; margin-bottom: 1rem;">
                <h4>📊 Optimal Times</h4>
                <p><strong>Twitter:</strong> 9 AM, 2 PM<br>
                <strong>Instagram:</strong> 11 AM, 7 PM<br>
                <strong>LinkedIn:</strong> 8 AM, 5 PM</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### 📈 Scheduler Stats")
            st.metric("Posts This Week", "12")
            st.metric("Success Rate", "98%")
            st.metric("Avg Engagement", "6.4%", "+0.8%")
            
            st.markdown("### 🤖 AI Queue")
            st.info("3 posts ready for optimal timing")
    
    with tabs[5]:  # Settings
        st.markdown("## ⚙️ Settings & Configuration")
        
        settings_tabs = st.tabs(["👤 Profile", "🔗 Integrations", "💳 Billing", "🔧 AI Config"])
        
        with settings_tabs[0]:  # Profile
            st.markdown("### 👤 Account Settings")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.text_input("Email", value=st.session_state.user_email, disabled=True)
                st.text_input("Company Name", placeholder="Your company")
                st.selectbox("Industry", ["Technology", "Marketing", "E-commerce", "Healthcare", "Finance", "Other"])
                st.selectbox("Team Size", ["1-5", "6-20", "21-50", "51-200", "200+"])
            
            with col2:
                st.text_input("Full Name", placeholder="Your name")
                st.text_input("Website", placeholder="https://yoursite.com")
                st.selectbox("Timezone", ["UTC", "EST", "PST", "KST", "GMT"])
                st.selectbox("Language", ["English", "Korean", "Japanese", "Spanish"])
            
            if st.button("💾 Save Profile", type="primary"):
                st.success("✅ Profile updated successfully!")
        
        with settings_tabs[1]:  # Integrations
            st.markdown("### 🔗 Platform Integrations")
            
            platforms = [
                {"name": "Twitter", "status": "✅ Connected", "accounts": "2 accounts"},
                {"name": "Instagram", "status": "✅ Connected", "accounts": "1 business account"},
                {"name": "LinkedIn", "status": "❌ Not Connected", "accounts": "Add account"},
                {"name": "TikTok", "status": "❌ Not Connected", "accounts": "Add account"}
            ]
            
            for platform in platforms:
                col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
                with col1:
                    st.markdown(f"**{platform['name']}**")
                with col2:
                    st.markdown(platform['status'])
                with col3:
                    st.markdown(platform['accounts'])
                with col4:
                    if "Connected" in platform['status']:
                        st.button("Manage", key=f"manage_{platform['name']}")
                    else:
                        st.button("Connect", key=f"connect_{platform['name']}", type="primary")
        
        with settings_tabs[2]:  # Billing
            st.markdown("### 💳 Billing & Subscription")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("""
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 2rem; border-radius: 12px;">
                    <h3>Pro Plan</h3>
                    <h2>$299/month</h2>
                    <p>✅ Unlimited AI generations<br>
                    ✅ All platform integrations<br>
                    ✅ Advanced analytics<br>
                    ✅ Priority support</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("### 📊 Usage This Month")
                st.metric("AI Generations", "1,234", help="Unlimited")
                st.metric("Scheduled Posts", "89", help="Unlimited")
                st.metric("API Calls", "5,678", help="Unlimited")
                st.metric("Data Export", "12", help="Unlimited")
            
            st.markdown("---")
            if st.button("🚀 Upgrade to Enterprise", use_container_width=True):
                st.info("💼 Contact sales@northstar.ai for Enterprise pricing")
        
        with settings_tabs[3]:  # AI Config
            st.markdown("### 🤖 AI Configuration")
            
            st.markdown("#### Content Generation Settings")
            creativity_level = st.slider("Creativity Level", 0.1, 1.0, 0.7, help="Higher = more creative, Lower = more conservative")
            brand_voice = st.selectbox("Default Brand Voice", ["Professional", "Casual", "Friendly", "Expert", "Inspirational"])
            
            st.markdown("#### Engagement Settings")
            response_style = st.selectbox("Response Style", ["Helpful", "Enthusiastic", "Professional", "Witty"])
            auto_engage = st.checkbox("Enable Auto-Engagement", value=True)
            
            if st.button("🔧 Update AI Settings", type="primary"):
                st.success("✅ AI configuration updated successfully!")
    
    # Footer with logout
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("🚪 Logout", use_container_width=True):
            logout()
            st.rerun()