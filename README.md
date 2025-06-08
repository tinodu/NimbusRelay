# 🌩️ NimbusRelay - Minimalistic Email Management

> **A beautiful, responsive email client with AI-powered spam detection and draft generation**

NimbusRelay combines elegant minimalist design with powerful AI capabilities to revolutionize your email workflow. Built with Imperial Purple theme for grandeur and nobility.

![Imperial Purple Theme](https://img.shields.io/badge/Theme-Imperial%20Purple-4B0082?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python)
![Microsoft FAST](https://img.shields.io/badge/Frontend-Microsoft%20FAST-0078D4?style=for-the-badge)
![Flask](https://img.shields.io/badge/Backend-Flask-000000?style=for-the-badge&logo=flask)

## ✨ Features

### 🎨 **Pixel-Perfect Minimalistic Design**
- **Imperial Purple Theme**: Exudes grandeur, prestige, and nobility
- **Canvas-Based Rendering**: Game-engine style scene graph for ultra-smooth performance
- **Responsive Layout**: Beautiful on desktop, tablet, and mobile
- **FAST Components**: Microsoft's modern web component library

### 🤖 **AI-Powered Intelligence**
- **Smart Spam Detection**: Advanced LLM analysis to identify unwanted emails
- **Intelligent Draft Generation**: AI-crafted responses based on email analysis
- **Context-Aware Analysis**: Deep understanding of email content and sentiment
- **Azure OpenAI Integration**: Enterprise-grade AI capabilities

### 📧 **Professional Email Management**
- **IMAP Support**: Connect to any email provider
- **Folder Organization**: Intuitive folder structure and navigation
- **Real-time Updates**: Live synchronization with WebSocket technology
- **Secure Configuration**: Environment-based credential management

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Azure OpenAI account (for AI features)
- IMAP-enabled email account

### Installation
```powershell
# Clone the repository
git clone <repository-url>
cd NimbusRelay

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

### Configuration
1. Open http://localhost:5000 in your browser
2. Click "Configure" to set up your credentials
3. Enter your email and AI service details
4. Connect and start managing your emails!

## 🛠️ Configuration Parameters

| Parameter | Description | Example |
|-----------|-------------|---------|
| `AZURE_OPENAI_ENDPOINT` | Azure OpenAI service endpoint | `https://your-service.openai.azure.com/` |
| `AZURE_OPENAI_API_KEY` | Azure OpenAI API key | `abc123...` |
| `AZURE_OPENAI_DEPLOYMENT` | Model deployment name | `gpt-4` |
| `AZURE_OPENAI_API_VERSION` | API version | `2024-12-01-preview` |
| `IMAP_SERVER` | Email server hostname | `imap.gmail.com` |
| `IMAP_PORT` | IMAP port (usually 993) | `993` |
| `IMAP_USERNAME` | Your email address | `user@example.com` |
| `IMAP_PASSWORD` | Email account password or app password | `password123` |

## 🏗️ Architecture

### Backend (Python/Flask)
```
app.py              # Main Flask application
├── EmailService    # IMAP email operations
├── AIService       # Azure OpenAI integration
└── API Routes      # RESTful endpoints
```

### Frontend (Microsoft FAST)
```
templates/index.html    # Main application template
static/
├── css/imperial-theme.css  # Imperial purple styling
└── js/app.js              # Application logic
```

### AI Prompts
```
prompts/
├── email-spam.md      # Spam detection prompt
├── email-analyze.md   # Email analysis prompt
└── email-draft.md     # Draft generation prompt
```

## 🎯 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/config` | GET | Get configuration status |
| `/api/config` | POST | Save configuration |
| `/api/connect` | POST | Connect to services |
| `/api/folders` | GET | List email folders |
| `/api/emails` | GET | Get emails from folder |
| `/api/analyze-spam` | POST | Analyze email for spam |
| `/api/analyze-email` | POST | Comprehensive email analysis |
| `/api/generate-draft` | POST | Generate draft response |

## 🧪 Testing

### Run Backend Tests
```powershell
cd src/tests
python -m pytest test_app.py -v
```

### Demo API Functionality
```powershell
python demo.py
```

## 🎨 Design Philosophy

### Core UX Concept
> *A single, unified canvas presents your entire email workflow with game-engine‐style rendering: messages, folders, and actions all live on a lightweight 2D scene graph.*

### Key Principles
- **Minimalism**: Clean, distraction-free interface
- **Performance**: GPU-accelerated rendering with 60fps target
- **Modularity**: Reusable components and clear separation of concerns
- **Imperial Aesthetics**: Royal purple palette conveying luxury and sophistication

### Color Palette
- **Primary**: Imperial Purple (#4B0082)
- **Secondary**: Deep Navy (#1E1B45), Dark Maroon (#800020)
- **Accents**: Metallic Silver (#C0C0C0)
- **Neutrals**: Charcoal (#2D2D2D), Soft Lavender (#A88EBC)

## 📁 Project Structure

```
NimbusRelay/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── demo.py                 # API demonstration script
├── .env                    # Environment variables (create this)
├── prompts/               # AI prompt templates
│   ├── email-spam.md
│   ├── email-analyze.md
│   └── email-draft.md
├── templates/             # HTML templates
│   └── index.html
├── static/               # Static assets
│   ├── css/
│   │   └── imperial-theme.css
│   └── js/
│       └── app.js
└── src/
    └── tests/            # Test suite
        ├── test_app.py
        └── test_frontend.js
```

## 🔒 Security

- **Environment Variables**: Sensitive data stored in .env file
- **CORS Protection**: Configured for secure frontend communication
- **Input Validation**: Sanitized email content processing
- **Secure Connections**: SSL/TLS for IMAP and HTTPS for API calls

## 🌟 Roadmap

### Upcoming Features
- [ ] Drag-and-drop email organization
- [ ] Custom AI prompt templates
- [ ] Email templates and signatures
- [ ] Advanced filtering and search
- [ ] Mobile-first responsive improvements
- [ ] Plugin system for extensibility

### Performance Optimizations
- [ ] Email content caching
- [ ] Lazy loading for large inboxes
- [ ] Background sync capabilities
- [ ] Offline mode support

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Follow the SOLID principles and coding guidelines
4. Write tests for new functionality
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Microsoft FAST**: For the beautiful web components
- **Azure OpenAI**: For powerful AI capabilities
- **Flask Community**: For the robust web framework
- **Imperial Color Inspiration**: From royal design traditions

---

<div align="center">
  <strong>Built with 💜 for the modern email experience</strong>
</div>