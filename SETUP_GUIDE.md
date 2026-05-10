# Banking Support AI Agent Chatbot - Complete Setup & API Documentation

## Project Overview

The Banking Support AI Agent Chatbot is a comprehensive multi-agent chatbot system combining:
- **Streamlit Frontend**: Interactive web UI for user conversations
- **FastAPI Backend**: RESTful API for processing messages, RAG, and agent routing
- **RAG System**: Knowledge base search with relevance scoring
- **Multi-Agent System**: Specialized agents for different support domains

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   Streamlit Frontend                            │
│                  (port 8501)                                    │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ Chat Interface │ Sidebar │ Session Management              │ │
│  └────────────┬───────────────────────────────────────────────┘ │
│               │ HTTP Requests (JSON)                            │
└───────────────┼─────────────────────────────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────────────────────────────┐
│                  FastAPI Backend                                │
│                  (port 8000)                                    │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ ┌─────────────┐ ┌────────────┐ ┌─────────────────────────┐ │ │
│  │ │ Chat        │ │ RAG        │ │ Multi-Agent System      │ │ │
│  │ │ Service     │ │ Service    │ │                         │ │ │
│  │ └─────────────┘ └────────────┘ └─────────────────────────┘ │ │
│  │                                                            │ │
│  │ ┌──────────────────┐ ┌──────────────────────────────────┐  │ │
│  │ │ Feedback Service │ │ Knowledge Base Management        │  │ │
│  │ └──────────────────┘ └──────────────────────────────────┘  │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## File Structure

```
Support_Resolution_Multi_Agent_AG_Chatbot/
├── Streamlit/                          # Frontend Application
│   ├── app.py                          # Main Streamlit app
│   ├── config.py                       # Configuration
│   ├── requirements.txt                # Dependencies
│   ├── .env.example                    # Environment template
│   ├── components/
│   │   ├── header.py                   # Header component
│   │   ├── sidebar.py                  # Sidebar component
│   │   └── chat_interface.py           # Chat interface (API-integrated)
│   └── utils/
│       ├── api_client.py               # FastAPI client
│       ├── api_config.py               # API configuration
│       ├── logger.py                   # Logging
│       └── session_manager.py          # Session management
│
├── FastAPI/                            # Backend API
│   ├── main.py                         # FastAPI application
│   ├── config.py                       # Configuration
│   ├── requirements.txt                # Dependencies
│   ├── .env.example                    # Environment template
│   ├── README.md                       # API Documentation
│   ├── models/
│   │   └── schemas.py                  # Request/Response schemas
│   └── services/
│       ├── chat_service.py             # Chat management
│       ├── rag_service.py              # RAG/Knowledge base
│       ├── feedback_service.py         # Feedback handling
│       └── agent_service.py            # Multi-agent routing
│
└── README.md                           # Main documentation
```

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Clone/Download Project
```bash
cd Support_Resolution_Multi_Agent_AG_Chatbot
```

### Step 2: Install FastAPI Backend

```bash
# Navigate to FastAPI directory
cd FastAPI

# Install dependencies
pip install -r requirements.txt

# Create .env file (optional, uses defaults if not present)
cp .env.example .env
```

### Step 3: Install Streamlit Frontend

```bash
# Navigate to Streamlit directory
cd ../Streamlit

# Install dependencies
pip install -r requirements.txt

# Create .env file (optional, uses defaults if not present)
cp .env.example .env
```

## Running the Application

### Terminal 1: Start FastAPI Backend

```bash
cd FastAPI
python main.py
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

The API will be available at:
- **Base URL**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### Terminal 2: Start Streamlit Frontend

```bash
cd Streamlit
streamlit run app.py
```

Expected output:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

### Open in Browser

- **Streamlit App**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs

## API Endpoints Reference

### Health & System

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/system/status` | GET | System status and metrics |

### Chat Management

| Endpoint | Method | Request | Response |
|----------|--------|---------|----------|
| `/chat` | POST | `{conversation_id, message, temperature, max_tokens}` | Chat response with agent info |
| `/chat/history` | POST | `{conversation_id}` | List of messages |
| `/chat/conversation/{id}` | DELETE | - | Confirmation |

### Knowledge Base (RAG)

| Endpoint | Method | Request | Response |
|----------|--------|---------|----------|
| `/knowledge-base/search` | POST | `{query, top_k}` | Ranked documents |
| `/knowledge-base/add-document` | POST | `{title, content, category}` | Document ID |
| `/knowledge-base/stats` | GET | - | Statistics |

### Feedback

| Endpoint | Method | Request | Response |
|----------|--------|---------|----------|
| `/feedback` | POST | `{conversation_id, message_id, rating, feedback_text}` | Feedback ID |
| `/feedback/statistics` | GET | - | Feedback analytics |

### Agents

| Endpoint | Method | Response |
|----------|--------|----------|
| `/agents` | GET | List of available agents |
| `/agents/{type}` | GET | Agent details |

## Usage Examples

### Example 1: Basic Conversation

1. Open Streamlit app at http://localhost:8501
2. Type a message: "How do I open a new account?"
3. The message is sent to FastAPI backend
4. Backend routes to Account Management Agent
5. RAG searches knowledge base for relevant documents
6. Response is generated and displayed

### Example 2: Using cURL to Test API

```bash
# Send a chat message
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "test_conv_1",
    "message": "How do I reset my password?",
    "temperature": 0.7,
    "max_tokens": 2048
  }'

# Search knowledge base
curl -X POST "http://localhost:8000/knowledge-base/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "password reset",
    "top_k": 5
  }'

# Get system status
curl -X GET "http://localhost:8000/system/status"
```

## Configuration

### Streamlit Configuration (Streamlit/config.py)

```python
PAGE_CONFIG = {
    "page_title": "Banking Support AI Agent Chatbot",
    "page_icon": "🤖",
    "layout": "wide",
}

CHAT_CONFIG = {
    "max_messages": 100,
    "enable_message_rating": True,
}

MODEL_CONFIG = {
    "model_name": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 2048,
}
```

### FastAPI Configuration (FastAPI/config.py)

```python
API_CONFIG = {
    "host": "0.0.0.0",
    "port": 8000,
    "timeout": 30,
}

RAG_CONFIG = {
    "chunk_size": 512,
    "top_k": 5,
    "similarity_threshold": 0.7,
}
```

## Features

### 1. Multi-Agent System
- **General Support Agent**: Handles general inquiries
- **Account Management Agent**: Account-related queries
- **Loan Agent**: Loan inquiries
- **Complaint Resolution Agent**: Complaint handling

### 2. RAG (Retrieval-Augmented Generation)
- Knowledge base search with relevance scoring
- Document retrieval based on query similarity
- Sample KB included with banking documents
- Easy to add custom documents

### 3. Session Management
- Conversation history tracking
- Unique conversation IDs
- Session state persistence

### 4. Feedback System
- Rate responses (1-5 stars)
- Submit feedback text
- View feedback statistics

### 5. Real-time Processing
- Message processing with typing indicators
- Token count tracking
- Response metadata (agent, confidence, timestamp)

## Testing the Application

### Test 1: Basic Chat
1. Go to http://localhost:8501
2. Try saying: "Hello"
3. You should get a greeting response

### Test 2: Account Inquiry
1. Type: "How do I check my balance?"
2. The Account Management Agent should respond

### Test 3: Knowledge Base Search
1. Open API docs at http://localhost:8000/docs
2. Try POST /knowledge-base/search with query "transfer money"

### Test 4: Feedback
1. After getting a response, click "👍 Helpful"
2. It submits feedback via the API

## Troubleshooting

### Issue: API Connection Failed
**Solution**: 
- Ensure FastAPI is running on port 8000
- Check firewall settings
- Verify API_BASE_URL in Streamlit config

```bash
# Test API connection
curl http://localhost:8000/health
```

### Issue: Streamlit Not Loading
**Solution**:
- Check port 8501 is available
- Verify Python dependencies: `pip install -r requirements.txt`
- Clear Streamlit cache: `streamlit cache clear`

### Issue: Knowledge Base Empty
**Solution**:
- Sample KB loads automatically on startup
- Add custom documents via `/knowledge-base/add-document` endpoint
- Check FastAPI logs for loading status

### Issue: Port Already in Use
**Solution**:
```bash
# Find process using port 8000
netstat -tulpn | grep 8000

# Kill the process (example)
kill -9 <PID>

# Or use different port
python main.py --port 8001
```

## Performance Optimization

### For Production:
1. Use process manager (PM2, Gunicorn)
2. Add reverse proxy (Nginx)
3. Enable database persistence
4. Implement caching
5. Add rate limiting
6. Use async workers

### FastAPI Production Setup:
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
```

### Streamlit Production Setup:
```bash
streamlit run app.py --logger.level=warning
```

## Development Notes

### Adding New Agents
1. Define agent in `FastAPI/services/agent_service.py`
2. Update `_determine_agent()` routing logic
3. Add agent-specific response generation

### Extending Knowledge Base
1. Use `/knowledge-base/add-document` endpoint
2. Or modify `_load_sample_knowledge_base()` in RAG service
3. Documents auto-loaded on API startup

### Database Integration
Current: In-memory storage
Future: Add database layer (PostgreSQL/MongoDB)

## API Documentation

### Auto-generated Docs
Visit http://localhost:8000/docs for:
- Interactive API explorer
- Try-it-out functionality
- Request/response schemas
- Parameter documentation

## Deployment

### Docker (Optional)
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY FastAPI/requirements.txt .
RUN pip install -r requirements.txt

COPY FastAPI/ .

CMD ["python", "main.py"]
```

### Cloud Deployment
- AWS: EC2 + Application Load Balancer
- Azure: App Service + Azure SQL
- GCP: Cloud Run + Cloud SQL

## Support & Contact

For issues or questions:
1. Check API logs: FastAPI terminal output
2. Check Streamlit logs: Streamlit terminal output
3. Review API docs at http://localhost:8000/docs
4. Check sample knowledge base in RAG service

## Future Enhancements

- [ ] Real LLM integration (OpenAI API)
- [ ] Vector embeddings (Pinecone/Weaviate)
- [ ] Database persistence
- [ ] User authentication
- [ ] Admin dashboard
- [ ] Analytics reporting
- [ ] Email notifications
- [ ] SMS integration

## License

Banking Support AI Agent Chatbot

---

**Happy chatting!** 🤖
