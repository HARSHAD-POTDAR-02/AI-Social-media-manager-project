# AI Social Media Manager - Web Application

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Setup Instructions

1. **Install Backend Dependencies**
   ```bash
   pip install fastapi uvicorn python-multipart
   ```

2. **Install Frontend Dependencies**
   ```bash
   cd frontend
   npm install
   ```

3. **Start Development Servers**
   ```bash
   # Option 1: Use the batch script (Windows)
   start_dev.bat
   
   # Option 2: Manual start
   # Terminal 1 - Backend
   cd api
   python main.py
   
   # Terminal 2 - Frontend  
   cd frontend
   npm start
   ```

4. **Access the Application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## 🎯 Features

### Chat Interface
- **Natural Language Input**: Ask anything about social media management
- **Real-time Processing**: See your request being processed live
- **Smart Suggestions**: Quick-start examples for common tasks

### Workflow Visualization
- **Sequential Workflow Progress**: Visual progress bar showing agent execution
- **Agent Status Tracking**: See which agents are active, completed, or pending
- **Real-time Updates**: Live status updates as agents process your request

### Results Display
- **Generated Content**: Clean preview of created content
- **Agent Activities**: Detailed breakdown of what each agent accomplished
- **Error Handling**: Clear error messages and recovery suggestions

## 🏗️ Architecture

```
AI Social Media Manager/
├── api/                    # FastAPI Backend
│   └── main.py            # API endpoints and WebSocket handlers
├── frontend/              # React Frontend
│   ├── src/
│   │   ├── App.js         # Main chat interface
│   │   ├── App.css        # Tailwind styles
│   │   └── index.js       # React entry point
│   └── public/
├── agents/                # Your existing agent system
├── graph_setup.py         # LangGraph workflow
├── central_router.py      # Task routing and decomposition
└── start_dev.bat         # Development startup script
```

## 🔧 API Endpoints

### POST /chat
Process user messages and return structured responses
```json
{
  "message": "Create a post about summer sale",
  "session_id": "optional-session-id",
  "context_data": {}
}
```

### GET /health
Health check endpoint for monitoring

## 🎨 UI Components

### Chat Interface
- **Message Bubbles**: User and bot messages with timestamps
- **Workflow Progress**: Visual progress indicator for sequential workflows
- **Content Preview**: Rich display of generated content
- **Agent Activities**: Breakdown of agent actions and results

### Interactive Elements
- **Auto-resize Input**: Textarea that grows with content
- **Quick Examples**: Clickable example queries
- **Loading States**: Smooth loading animations
- **Error Handling**: User-friendly error messages

## 🚀 Deployment

### Development
```bash
# Backend
cd api && python main.py

# Frontend
cd frontend && npm start
```

### Production
```bash
# Backend
cd api && uvicorn main:app --host 0.0.0.0 --port 8000

# Frontend
cd frontend && npm run build
# Serve build folder with nginx/apache
```

## 🔍 Troubleshooting

### Common Issues

1. **CORS Errors**
   - Ensure backend is running on port 8000
   - Check CORS settings in api/main.py

2. **Module Import Errors**
   - Verify Python path includes project root
   - Check all dependencies are installed

3. **Frontend Build Errors**
   - Run `npm install` in frontend directory
   - Ensure Node.js version is 16+

### Debug Mode
- Backend logs: Check terminal running `python main.py`
- Frontend logs: Open browser developer tools
- API testing: Visit http://localhost:8000/docs

## 📝 Next Steps

1. **Add Authentication**: User login and session management
2. **Real-time Updates**: WebSocket integration for live agent progress
3. **Content Management**: Save, edit, and manage generated content
4. **Analytics Dashboard**: Visual charts and metrics
5. **Scheduling Interface**: Calendar view for content scheduling
6. **Mobile Responsive**: Optimize for mobile devices