# AI Agents for Social Media Management MVP

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Claude API key (get from Anthropic)
- Social media API credentials (optional for demo)

### Installation

```bash
# Clone the repository
git clone [repo-url]
cd NorthStar-1

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Environment Variables

Create a `.env` file:

```env
# Required
CLAUDE_API_KEY=your_claude_api_key
SECRET_KEY=your_secret_key_here

# Optional (for real social media integration)
TWITTER_API_KEY=your_twitter_key
TWITTER_API_SECRET=your_twitter_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_secret

INSTAGRAM_ACCESS_TOKEN=your_instagram_token
INSTAGRAM_BUSINESS_ID=your_business_id

# Configuration
ENV=development
PORT=5000
TIMEZONE=UTC
```

### Running the Application

1. **Start the Flask backend:**
```bash
python app.py
```

2. **Launch the Streamlit dashboard (in a new terminal):**
```bash
streamlit run dashboard.py
```

3. **Access the application:**
- Backend API: http://localhost:5000
- Dashboard: http://localhost:8501

### Demo Mode

The application runs in demo mode by default when social media API credentials are not provided. This allows full testing of all features with simulated data.

To try the demo:
1. Run both servers as described above
2. Open the dashboard at http://localhost:8501
3. Click "Try Demo" on the login screen
4. Explore all features with mock data

## 📁 Project Structure

```
NorthStar-1/
├── app.py                 # Flask backend server
├── dashboard.py           # Streamlit dashboard
├── agents/               # AI agent modules
│   ├── content_agent.py  # Content generation
│   ├── engagement_agent.py # Audience engagement
│   └── analytics_agent.py # Analytics & predictions
├── integrations/         # Social media APIs
│   ├── twitter_api.py
│   └── instagram_api.py
├── utils/                # Utilities
│   └── scheduler.py      # Post scheduling
└── requirements.txt      # Dependencies
```

## 🎯 Key Features

### AI Agents
- **Content Generation**: NLP-powered posts with A/B testing
- **Smart Engagement**: Sentiment-aware automated replies (50/day limit)
- **Analytics**: ROI tracking with predictive metrics

### Dashboard Features
- Real-time metrics visualization
- Content generation with virality optimization
- Automated engagement management
- Advanced analytics with ML predictions
- Post scheduling with optimal timing
- Multi-platform support

## 🔧 API Endpoints

### Authentication
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout

### Agents
- `POST /api/agents/generate` - Generate content
- `POST /api/agents/engage` - Automated engagement
- `GET /api/analytics/summary` - Get analytics

### Scheduling
- `POST /api/schedule/create` - Schedule posts

## 💰 Pricing Tiers

- **Free**: 10 posts/month, basic features
- **Pro ($299/mo)**: Unlimited posts, all features
- **Enterprise ($999/mo)**: Custom training, priority support

## 🚦 Performance Targets

- Response time: <2 seconds
- Engagement success rate: >85%
- Uptime: 99.9%
- CAC: <₩300K
- LTV: >₩1M

## 🛡️ Security & Ethics

- OAuth2 authentication
- Rate limiting on all endpoints
- Anti-spam filters for engagement
- Bias audits for AI responses
- GDPR-compliant data handling

## 📈 Metrics & KPIs

The system tracks:
- Impressions & reach
- Engagement rates
- ROI calculations
- Time saved
- Viral coefficient
- Platform-specific metrics

## 🔄 Development Workflow

1. **Local Development**: Use demo mode for testing
2. **Testing**: Run `pytest` for unit tests
3. **Linting**: Use `black` and `flake8`
4. **Deployment**: Deploy with Gunicorn/Heroku

## 📝 License

Proprietary - All rights reserved

## 🤝 Support

For issues or questions:
- Email: support@aisocialmedia.ai
- Documentation: [docs-link]
- Community: [discord-link]

---

**Built with ❤️ using Claude AI and modern Python stack**