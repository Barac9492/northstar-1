import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os

st.set_page_config(
    page_title="AI Social Media Manager",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

if not st.session_state.authenticated:
    st.title("🚀 AI Social Media Manager")
    st.subheader("Automate the grind, amplify your authenticity")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("login_form"):
            st.markdown("### Login")
            email = st.text_input("Email", placeholder="your@email.com")
            password = st.text_input("Password", type="password")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                login_btn = st.form_submit_button("Login", use_container_width=True, type="primary")
            with col_btn2:
                demo_btn = st.form_submit_button("Try Demo", use_container_width=True)
            
            if login_btn and email and password:
                if login(email, password):
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials")
            
            if demo_btn:
                st.session_state.authenticated = True
                st.session_state.user_email = "demo@example.com"
                st.rerun()
    
    st.markdown("---")
    st.markdown("### 🎯 Key Features")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("**🤖 Content Generation**")
        st.markdown("AI-powered posts with A/B testing")
    with col2:
        st.markdown("**💬 Smart Engagement**")
        st.markdown("Sentiment-aware automated replies")
    with col3:
        st.markdown("**📊 ROI Analytics**")
        st.markdown("Predictive metrics & insights")
    
else:
    with st.sidebar:
        st.markdown(f"### Welcome, {st.session_state.user_email}")
        
        st.markdown("---")
        
        menu = st.radio(
            "Navigation",
            ["📊 Dashboard", "✨ Content Generator", "💬 Engagement", 
             "📈 Analytics", "⏰ Scheduler", "⚙️ Settings"]
        )
        
        st.markdown("---")
        
        if st.button("Logout", use_container_width=True):
            logout()
            st.rerun()
        
        st.markdown("---")
        st.markdown("### 📊 Quick Stats")
        st.metric("Posts Today", "12", "+3")
        st.metric("Engagement Rate", "5.2%", "+0.8%")
        st.metric("Time Saved", "4.5 hrs", "+1.2 hrs")
    
    if menu == "📊 Dashboard":
        st.title("📊 Dashboard")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Impressions", "45.2K", "+12%", help="Last 7 days")
        with col2:
            st.metric("Engagements", "2.3K", "+18%", help="Likes, comments, shares")
        with col3:
            st.metric("Followers Gained", "342", "+24%", help="Net growth")
        with col4:
            st.metric("ROI", "₩1.2M", "+15%", help="Estimated value generated")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Engagement Trend")
            
            dates = pd.date_range(end=datetime.now(), periods=7)
            engagement_data = pd.DataFrame({
                'Date': dates,
                'Impressions': [4500, 4800, 5200, 4900, 5500, 6000, 6300],
                'Engagements': [220, 235, 265, 245, 280, 310, 340]
            })
            
            fig = px.line(engagement_data, x='Date', y=['Impressions', 'Engagements'],
                         title='7-Day Performance')
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("🎯 Platform Distribution")
            
            platform_data = pd.DataFrame({
                'Platform': ['Twitter', 'Instagram', 'LinkedIn', 'TikTok'],
                'Posts': [45, 30, 20, 15]
            })
            
            fig = px.pie(platform_data, values='Posts', names='Platform',
                        title='Content Distribution')
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        st.subheader("🚀 Recent AI-Generated Content")
        
        recent_posts = [
            {"platform": "Twitter", "content": "🚀 AI is transforming how we create content...", "engagement": "5.2%", "status": "Published"},
            {"platform": "Instagram", "content": "✨ Behind the scenes of our latest innovation...", "engagement": "7.8%", "status": "Published"},
            {"platform": "LinkedIn", "content": "The future of work is here. Here's what we learned...", "engagement": "4.1%", "status": "Scheduled"}
        ]
        
        df = pd.DataFrame(recent_posts)
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    elif menu == "✨ Content Generator":
        st.title("✨ AI Content Generator")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            platform = st.selectbox(
                "Select Platform",
                ["Twitter", "Instagram", "LinkedIn", "TikTok"]
            )
            
            prompt = st.text_area(
                "Content Prompt",
                placeholder="E.g., Write about our new AI feature launch...",
                height=100
            )
            
            col_opt1, col_opt2 = st.columns(2)
            with col_opt1:
                optimize_virality = st.checkbox("🔥 Optimize for Virality", value=True)
            with col_opt2:
                generate_variants = st.checkbox("🎲 Generate A/B Variants", value=True)
            
            if st.button("Generate Content", type="primary", use_container_width=True):
                with st.spinner("🤖 AI is creating your content..."):
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
                            
                            st.markdown("### Primary Content")
                            st.info(content.get('primary_content', 'Generated content'))
                            
                            if generate_variants and content.get('variants'):
                                st.markdown("### A/B Testing Variants")
                                for i, variant in enumerate(content.get('variants', [])[:2]):
                                    st.info(f"Variant {i+1}: {variant}")
                            
                            metadata = content.get('metadata', {})
                            if metadata:
                                col_m1, col_m2, col_m3 = st.columns(3)
                                with col_m1:
                                    st.metric("Character Count", metadata.get('character_count', 0))
                                with col_m2:
                                    st.metric("Platform", metadata.get('platform', 'N/A'))
                                with col_m3:
                                    st.metric("Virality Optimized", "Yes" if metadata.get('virality_optimized') else "No")
                        else:
                            st.error("Failed to generate content")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")
        
        with col2:
            st.markdown("### 💡 Tips")
            st.markdown("""
            - Be specific with your prompts
            - Include target audience info
            - Mention desired tone/style
            - Add relevant hashtags
            """)
            
            st.markdown("### 📊 Performance Predictor")
            st.metric("Expected Engagement", "5-7%", help="Based on similar content")
            st.metric("Optimal Post Time", "2:00 PM", help="Peak audience activity")
    
    elif menu == "💬 Engagement":
        st.title("💬 Smart Engagement")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Automated Engagement Settings")
            
            platform = st.selectbox("Platform", ["Twitter", "Instagram", "LinkedIn"])
            
            engagement_level = st.slider(
                "Daily Engagement Limit",
                min_value=10,
                max_value=50,
                value=30,
                help="Maximum automated engagements per day"
            )
            
            sentiment_filter = st.multiselect(
                "Engage with sentiment",
                ["Positive", "Neutral", "Questions"],
                default=["Positive", "Questions"]
            )
            
            if st.button("Update Settings", type="primary"):
                st.success("✅ Engagement settings updated")
            
            st.markdown("---")
            
            st.subheader("Recent Engagements")
            
            engagements = [
                {"Time": "2 mins ago", "Type": "Reply", "Platform": "Twitter", "Sentiment": "Positive"},
                {"Time": "15 mins ago", "Type": "Comment", "Platform": "Instagram", "Sentiment": "Question"},
                {"Time": "1 hour ago", "Type": "Like", "Platform": "LinkedIn", "Sentiment": "Neutral"}
            ]
            
            df = pd.DataFrame(engagements)
            st.dataframe(df, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("### 📊 Engagement Stats")
            st.metric("Today's Engagements", "18/30", help="Daily limit progress")
            st.metric("Response Rate", "92%", "+5%")
            st.metric("Avg Response Time", "3 mins", "-2 mins")
            
            st.markdown("### 🎯 Engagement Quality")
            quality_score = 85
            st.progress(quality_score/100)
            st.caption(f"Quality Score: {quality_score}%")
    
    elif menu == "📈 Analytics":
        st.title("📈 Advanced Analytics")
        
        tab1, tab2, tab3 = st.tabs(["Overview", "Predictions", "ROI Analysis"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                platform_filter = st.selectbox("Platform", ["All", "Twitter", "Instagram", "LinkedIn"])
                date_range = st.selectbox("Time Period", ["Last 7 days", "Last 30 days", "Last 90 days"])
            
            with col2:
                st.markdown("### Key Insights")
                st.info("🎯 Engagement rate 25% above industry average")
                st.info("📈 Audience growing at 5% weekly")
                st.info("⏰ Peak engagement: 2-4 PM local time")
            
            st.markdown("---")
            
            dates = pd.date_range(end=datetime.now(), periods=30)
            metrics_data = pd.DataFrame({
                'Date': dates,
                'Impressions': [5000 + i*100 + (i%7)*200 for i in range(30)],
                'Engagements': [250 + i*5 + (i%7)*10 for i in range(30)],
                'Followers': [1000 + i*10 for i in range(30)]
            })
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=metrics_data['Date'], y=metrics_data['Impressions'],
                                    mode='lines', name='Impressions'))
            fig.add_trace(go.Scatter(x=metrics_data['Date'], y=metrics_data['Engagements'],
                                    mode='lines', name='Engagements', yaxis='y2'))
            
            fig.update_layout(
                title='30-Day Performance Trend',
                yaxis=dict(title='Impressions'),
                yaxis2=dict(title='Engagements', overlaying='y', side='right'),
                hovermode='x unified',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            st.subheader("🔮 Growth Predictions")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Next Week Impressions", "52K", "+15%", help="ML-based forecast")
            with col2:
                st.metric("Expected Engagements", "2.8K", "+20%", help="Based on current trend")
            with col3:
                st.metric("Follower Projection", "1,500", "+12%", help="End of month estimate")
            
            st.markdown("---")
            
            future_dates = pd.date_range(start=datetime.now(), periods=7)
            prediction_data = pd.DataFrame({
                'Date': future_dates,
                'Predicted': [8000 + i*200 for i in range(7)],
                'Upper Bound': [8500 + i*200 for i in range(7)],
                'Lower Bound': [7500 + i*200 for i in range(7)]
            })
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=prediction_data['Date'], y=prediction_data['Predicted'],
                                    mode='lines', name='Predicted', line=dict(color='blue')))
            fig.add_trace(go.Scatter(x=prediction_data['Date'], y=prediction_data['Upper Bound'],
                                    mode='lines', name='Upper', line=dict(dash='dash')))
            fig.add_trace(go.Scatter(x=prediction_data['Date'], y=prediction_data['Lower Bound'],
                                    mode='lines', name='Lower', line=dict(dash='dash')))
            
            fig.update_layout(title='7-Day Growth Forecast', height=350)
            st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            st.subheader("💰 ROI Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Time Saved This Month", "45 hours", help="Automation efficiency")
                st.metric("Cost per Engagement", "₩120", "-₩30")
                st.metric("Estimated Value Generated", "₩2.5M", "+18%")
            
            with col2:
                roi_data = pd.DataFrame({
                    'Metric': ['Time Saved', 'Engagement Value', 'Follower Value', 'Brand Awareness'],
                    'Value (₩K)': [500, 800, 700, 500]
                })
                
                fig = px.bar(roi_data, x='Metric', y='Value (₩K)',
                           title='ROI Breakdown', color='Value (₩K)')
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            st.success("📊 **ROI Summary**: 850% return on investment with 70% efficiency gain")
    
    elif menu == "⏰ Scheduler":
        st.title("⏰ Content Scheduler")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Schedule New Post")
            
            content = st.text_area("Content", height=100)
            
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                platform = st.selectbox("Platform", ["Twitter", "Instagram", "LinkedIn"])
                schedule_date = st.date_input("Date", min_value=datetime.now().date())
            with col_s2:
                schedule_time = st.time_input("Time")
                repeat = st.selectbox("Repeat", ["Never", "Daily", "Weekly"])
            
            if st.button("Schedule Post", type="primary", use_container_width=True):
                scheduled_datetime = datetime.combine(schedule_date, schedule_time)
                st.success(f"✅ Post scheduled for {scheduled_datetime}")
            
            st.markdown("---")
            
            st.subheader("Scheduled Posts")
            
            scheduled = [
                {"Time": "Today 2:00 PM", "Platform": "Twitter", "Content": "Exciting news coming...", "Status": "Pending"},
                {"Time": "Tomorrow 10:00 AM", "Platform": "LinkedIn", "Content": "Industry insights...", "Status": "Pending"},
                {"Time": "Friday 3:00 PM", "Platform": "Instagram", "Content": "Weekend vibes...", "Status": "Pending"}
            ]
            
            df = pd.DataFrame(scheduled)
            st.dataframe(df, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("### 📅 Calendar View")
            st.info("5 posts scheduled this week")
            
            st.markdown("### ⏰ Optimal Times")
            st.markdown("""
            **Twitter**: 9 AM, 2 PM  
            **Instagram**: 11 AM, 7 PM  
            **LinkedIn**: 8 AM, 5 PM
            """)
            
            st.markdown("### 📊 Schedule Stats")
            st.metric("Posts This Week", "12")
            st.metric("Completion Rate", "98%")
    
    elif menu == "⚙️ Settings":
        st.title("⚙️ Settings")
        
        tab1, tab2, tab3 = st.tabs(["Account", "Integrations", "Billing"])
        
        with tab1:
            st.subheader("Account Settings")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.text_input("Email", value=st.session_state.user_email, disabled=True)
                st.text_input("Name", placeholder="Your name")
                st.selectbox("Timezone", ["UTC", "EST", "PST", "KST"])
            
            with col2:
                st.text_input("Company", placeholder="Company name")
                st.selectbox("Industry", ["Technology", "Marketing", "E-commerce", "Other"])
                st.selectbox("Plan", ["Free", "Pro ($299/mo)", "Enterprise ($999/mo)"])
            
            if st.button("Save Changes", type="primary"):
                st.success("✅ Settings saved successfully")
        
        with tab2:
            st.subheader("Platform Integrations")
            
            platforms = [
                {"name": "Twitter", "status": "Connected", "icon": "✅"},
                {"name": "Instagram", "status": "Connected", "icon": "✅"},
                {"name": "LinkedIn", "status": "Not Connected", "icon": "❌"},
                {"name": "TikTok", "status": "Not Connected", "icon": "❌"}
            ]
            
            for platform in platforms:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"{platform['icon']} **{platform['name']}**")
                with col2:
                    st.markdown(platform['status'])
                with col3:
                    if platform['status'] == "Connected":
                        st.button("Disconnect", key=f"disc_{platform['name']}")
                    else:
                        st.button("Connect", key=f"conn_{platform['name']}", type="primary")
            
            st.markdown("---")
            
            st.subheader("API Configuration")
            st.text_input("Claude API Key", type="password", placeholder="sk-...")
            st.info("🔒 Your API keys are encrypted and secure")
        
        with tab3:
            st.subheader("Billing & Subscription")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Current Plan")
                st.info("**Pro Plan** - $299/month")
                st.markdown("""
                - Unlimited AI generations
                - All platform integrations
                - Advanced analytics
                - Priority support
                """)
            
            with col2:
                st.markdown("### Usage This Month")
                st.metric("AI Generations", "1,234", help="Unlimited")
                st.metric("Scheduled Posts", "89", help="Unlimited")
                st.metric("API Calls", "5,678", help="Unlimited")
            
            st.markdown("---")
            
            if st.button("Upgrade to Enterprise", type="primary", use_container_width=True):
                st.info("Contact sales@aisocialmedia.ai for Enterprise pricing")