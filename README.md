# CVE Analysis Platform 🛡️

A comprehensive AI-powered cybersecurity platform for CVE (Common Vulnerabilities and Exposures) analysis, risk assessment, and security research.

## 🌟 Features

### 🔍 CVE Search & Analysis
- **Advanced Search**: Multi-criteria search across local database and NVD (National Vulnerability Database)
- **Real-time Results**: Live search with filtering by severity, CVSS score, date range, and more
- **Detailed View**: Comprehensive CVE information including CVSS metrics, affected components, and mitigation strategies

### 🤖 AI-Powered Analysis
- **Intelligent Analysis**: AI-powered vulnerability assessment and risk scoring
- **Smart Recommendations**: Automated mitigation suggestions and security advice
- **Proof-of-Concept Generation**: AI-generated exploit code for security testing

### 📊 Dashboard & Monitoring
- **Real-time Metrics**: Live dashboard with vulnerability statistics and trends
- **Timeline Visualization**: Interactive charts showing vulnerability discovery patterns
- **Alert System**: Customizable notifications for new high-risk vulnerabilities

### 🔐 Security Features
- **JWT Authentication**: Secure user authentication and session management
- **Role-based Access**: Admin and user roles with appropriate permissions
- **API Security**: Rate limiting and authentication for all API endpoints

### 🎯 Watchlist Management
- **Custom Watchlists**: Track specific CVEs and get alerts for updates
- **Priority System**: Organize vulnerabilities by importance and urgency
- **Export Capabilities**: Download watchlists in multiple formats

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js (for frontend development)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/cve2.git
   cd cve2
   ```

2. **Set up Python environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Initialize database**
   ```bash
   python setup_app.py
   ```

5. **Start the application**
   ```bash
   python run.py --host 127.0.0.1 --port 8000
   ```

6. **Access the platform**
   - Open http://127.0.0.1:8000 in your browser
   - Default admin credentials: `admin/admin123`

## 🏗️ Architecture

```
cve2/
├── app/
│   ├── api/                 # REST API endpoints
│   ├── ai/                  # AI services and models
│   ├── core/                # Core functionality and security
│   ├── services/            # Business logic services
│   └── static/              # Frontend assets
├── config/                  # Configuration files
├── docs/                    # Documentation
├── tests/                   # Test suites
└── scripts/                 # Deployment scripts
```

## 🔧 API Endpoints

### Authentication
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration
- `GET /api/v1/auth/me` - Get current user info

### CVE Operations
- `GET /api/v1/cve/` - List CVEs with pagination
- `GET /api/v1/cve/{id}` - Get specific CVE details
- `POST /api/v1/cve/search/advanced` - Advanced CVE search

### AI Analysis
- `POST /api/v1/analysis/cve/analyze` - Analyze CVE with AI
- `GET /api/v1/analysis/{id}` - Get analysis results

### Watchlist Management
- `POST /api/v1/watchlist/` - Create watchlist
- `GET /api/v1/watchlist/` - Get user watchlists
- `POST /api/v1/watchlist/{id}/cves` - Add CVEs to watchlist

## 🧪 Testing

Run the comprehensive test suite:
```bash
python test_full_application.py
```

Test specific components:
```bash
python test_api_integration.py
python test_auth_integration.py
```

## 🐳 Docker Deployment

```bash
docker-compose up -d
```

## 📋 Configuration

Key configuration options in `.env`:

```env
# Database
DATABASE_URL=sqlite:///cve_platform.db

# API Keys
NVD_API_KEY=your_nvd_api_key

# AI Services
OLLAMA_BASE_URL=http://localhost:11434
AI_MODEL=llama2

# Security
SECRET_KEY=your_secret_key
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📊 Current Status

✅ **Working Features:**
- CVE Search & Display
- AI-Powered Analysis
- User Authentication
- Watchlist Management
- Dashboard Metrics
- Proof-of-Concept Generation

🔧 **Recent Fixes:**
- Fixed search results display
- Resolved API authentication issues
- Updated watchlist functionality
- Improved error handling

## 🛠️ Technologies Used

- **Backend**: FastAPI, SQLAlchemy, Pydantic
- **Frontend**: Vanilla JavaScript, HTML5, CSS3, Tailwind CSS
- **Database**: SQLite (development), PostgreSQL (production ready)
- **AI/ML**: Ollama, Custom AI models
- **Authentication**: JWT tokens
- **API Integration**: NVD API, Custom CVE databases

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the [documentation](docs/)
- Review the [API documentation](COMPREHENSIVE_API_INTEGRATION_SUMMARY.md)

## 🔮 Roadmap

- [ ] Advanced ML models for vulnerability prediction
- [ ] Integration with more security databases
- [ ] Mobile app development
- [ ] Enterprise SSO integration
- [ ] Advanced reporting and analytics

---

**⚠️ Security Notice**: This platform is designed for security research and testing purposes. Always follow responsible disclosure practices and obtain proper authorization before testing vulnerabilities.
