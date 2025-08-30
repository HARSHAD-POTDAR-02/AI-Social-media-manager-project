# AI Social Media Manager

An intelligent social media management platform powered by AI agents that automate content creation, scheduling, analytics, and community engagement across multiple platforms.

## 🚀 Features

### AI-Powered Agents
- **Strategy Agent**: Content planning, trend analysis, and strategic recommendations
- **Content Agent**: Automated content creation and writing assistance
- **Analytics Agent**: Performance tracking and insights generation
- **Community Agent**: Automated engagement and response management
- **Publishing Agent**: Smart scheduling and cross-platform posting
- **Crisis Agent**: Real-time crisis detection and management

### Core Functionality
- **Multi-Platform Support**: Instagram, LinkedIn, Twitter, Facebook
- **Content Calendar**: Visual scheduling and planning interface
- **Real-time Analytics**: Performance metrics and engagement tracking
- **AI Chat Interface**: Natural language interaction with specialized agents
- **Task Queue**: Monitor and manage AI agent activities
- **Sentiment Analysis**: Track audience sentiment across platforms
- **Automated Workflows**: Sequential and parallel agent execution

## 🛠 Technology Stack

### Backend
- **FastAPI**: High-performance Python web framework
- **LangGraph**: Multi-agent workflow orchestration
- **OpenAI GPT**: Advanced language model integration
- **Pydantic**: Data validation and serialization
- **Uvicorn**: ASGI server for production deployment

### Frontend
- **React 18**: Modern UI framework with hooks
- **Tailwind CSS**: Utility-first styling framework
- **Heroicons**: Beautiful SVG icon library
- **Recharts**: Responsive chart library for analytics
- **Date-fns**: Modern date utility library
- **Axios**: HTTP client for API communication

## 📁 Project Structure

```
AI Social media manager project/
├── api/                          # Backend FastAPI application
│   ├── main.py                   # FastAPI server entry point
│   ├── agents/                   # AI agent implementations
│   ├── models/                   # Data models and schemas
│   └── requirements.txt          # Python dependencies
├── frontend/                     # React frontend application
│   ├── src/
│   │   ├── components/           # React components
│   │   ├── App.js               # Main application component
│   │   └── App.css              # Global styles
│   ├── public/                   # Static assets
│   └── package.json             # Node.js dependencies
├── start_dev.bat                # Development environment launcher
└── README.md                    # Project documentation
```

## 🚦 Getting Started

### Prerequisites
- **Python 3.8+** with pip
- **Node.js 16+** with npm
- **OpenAI API Key** (for AI functionality)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd "AI Social media manager project"
   ```

2. **Backend Setup**
   ```bash
   cd api
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   
   pip install -r requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

4. **Environment Configuration**
   Create a `.env` file in the `api` directory:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

### Running the Application

#### Option 1: Automated Start (Windows)
```bash
# Run the batch file to start both servers
start_dev.bat
```

#### Option 2: Manual Start

**Terminal 1 - Backend:**
```bash
cd api
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

### Access Points
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🎯 Usage Guide

### Dashboard
- View key performance metrics and analytics
- Monitor current and scheduled posts
- Access AI-generated content strategies
- Quick actions for common tasks

### AI Agents Chat
- Select specific agents or let AI choose automatically
- Natural language interaction for complex requests
- Real-time workflow progress tracking
- View generated content and agent activities

### Content Calendar
- Visual monthly/weekly/daily view of scheduled content
- Drag-and-drop scheduling interface
- Platform-specific content management
- Status tracking (draft, scheduled, published)

### Analytics
- Cross-platform performance metrics
- Engagement rate and reach analysis
- Content type performance comparison
- AI-powered insights and recommendations

### Community Management
- Centralized inbox for all platform interactions
- Sentiment analysis and priority filtering
- AI-suggested responses
- Response time and satisfaction tracking

## 🔧 Configuration

### Adding Social Media Platforms
1. Update platform configurations in `api/models/`
2. Add platform-specific styling in `frontend/src/App.css`
3. Implement platform APIs in respective agent modules

### Customizing AI Agents
- Modify agent prompts in `api/agents/`
- Adjust workflow logic in LangGraph configurations
- Update agent capabilities and descriptions

## 🚀 Deployment

### Backend Deployment
```bash
cd api
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Frontend Deployment
```bash
cd frontend
npm run build
# Deploy the 'build' folder to your hosting service
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

**Backend won't start:**
- Ensure Python virtual environment is activated
- Check if all dependencies are installed: `pip install -r requirements.txt`
- Verify OpenAI API key is set in environment variables

**Frontend compilation errors:**
- Delete `node_modules` and run `npm install` again
- Ensure Node.js version is 16 or higher
- Check for missing dependencies: `npm install`

**API connection issues:**
- Verify backend is running on port 8000
- Check CORS settings in FastAPI configuration
- Ensure firewall isn't blocking local connections

### Getting Help
- Check the API documentation at http://localhost:8000/docs
- Review browser console for frontend errors
- Check terminal output for backend error messages

## 🔮 Future Enhancements

- [ ] Multi-user support with role-based access
- [ ] Advanced A/B testing for content
- [ ] Integration with more social media platforms
- [ ] Mobile application development
- [ ] Advanced AI model fine-tuning
- [ ] Real-time collaboration features
- [ ] Enhanced security and authentication

---

**Built with ❤️ using AI and modern web technologies**