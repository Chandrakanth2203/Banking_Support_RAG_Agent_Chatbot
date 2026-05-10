# FastAPI Backend for Banking Support AI Agent Chatbot

This directory contains the FastAPI backend API for the Banking Support AI Agent Chatbot.

## Overview

The FastAPI backend provides:
- RESTful APIs for chat processing
- RAG (Retrieval-Augmented Generation) integration
- Multi-agent routing system
- Feedback collection and analysis
- Knowledge base management
- System monitoring and status

## Project Structure

```
FastAPI/
├── main.py                 # Main FastAPI application
├── config.py               # Configuration settings
├── requirements.txt        # Python dependencies
├── models/
│   ├── __init__.py        # Package initializer
│   └── schemas.py         # Pydantic request/response schemas
├── services/
│   ├── __init__.py        # Package initializer
│   ├── chat_service.py    # Chat conversation management
│   ├── rag_service.py     # RAG knowledge base search
│   ├── feedback_service.py # User feedback handling
│   └── agent_service.py   # Multi-agent routing
└── README.md              # This file
```

## API Endpoints

### Health & Status
- `GET /health` - Health check endpoint
- `GET /system/status` - System status and metrics

### Chat Operations
- `POST /chat` - Send a message and get response
- `POST /chat/history` - Get conversation history
- `DELETE /chat/conversation/{conversation_id}` - Clear conversation

### Knowledge Base / RAG
- `POST /knowledge-base/search` - Search knowledge base
- `POST /knowledge-base/add-document` - Add document to KB
- `GET /knowledge-base/stats` - Get KB statistics

### Feedback
- `POST /feedback` - Submit feedback on response
- `GET /feedback/statistics` - Get feedback analytics

### Agents
- `GET /agents` - List available agents
- `GET /agents/{agent_type}` - Get specific agent info

## Installation

### Prerequisites
- Python 3.8+
- pip

### Setup

1. Install dependencies:
```bash
cd FastAPI
pip install -r requirements.txt
```

2. Create `.env` file (optional):
```env
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=False
MODEL_NAME=gpt-4
TEMPERATURE=0.7
MAX_TOKENS=2048
DB_TYPE=sqlite
DB_PATH=chatbot.db
REQUIRE_AUTH=False
```

## Running the Server

### Development Mode
```bash
cd FastAPI
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at:
- **Base URL**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (Swagger UI)
- **Alternative Docs**: http://localhost:8000/redoc (ReDoc)

## Services

### Chat Service
Manages conversation state and message history. Features:
- Create and manage conversations
- Store and retrieve message history
- Track conversation metadata
- Active conversation monitoring

### RAG Service
Provides knowledge base search using retrieval-augmented generation:
- Document indexing and storage
- Semantic search capabilities
- Relevance scoring
- Sample knowledge base included for testing

### Agent Service
Routes messages to appropriate specialized agents:
- **General Support Agent**: General inquiries
- **Account Management Agent**: Account-related queries
- **Loan Agent**: Loan inquiries and applications
- **Complaint Resolution Agent**: Complaint handling

### Feedback Service
Collects and analyzes user feedback:
- Save user ratings and comments
- Calculate feedback statistics
- Track satisfaction metrics

## Integration with Streamlit

The Streamlit app (`../Streamlit/`) automatically calls these APIs. No additional setup needed - just ensure the FastAPI server is running on `http://localhost:8000`.

To change the API URL, set the environment variable:
```bash
export API_BASE_URL=http://your-api-url:port
```

## API Usage Examples

### Send a Chat Message
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "conv_123",
    "message": "How do I open a new account?",
    "temperature": 0.7,
    "max_tokens": 2048
  }'
```

### Search Knowledge Base
```bash
curl -X POST "http://localhost:8000/knowledge-base/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "account opening",
    "top_k": 5
  }'
```

### Submit Feedback
```bash
curl -X POST "http://localhost:8000/feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": "conv_123",
    "message_id": "msg_456",
    "rating": 5,
    "feedback_text": "Very helpful response!"
  }'
```

### Get System Status
```bash
curl -X GET "http://localhost:8000/system/status"
```

## Features

### Multi-Agent System
- Automatic message routing to specialized agents
- Agent selection based on query content
- Fallback to general support agent

### RAG Integration
- Knowledge base search with relevance scoring
- Metadata extraction from documents
- Configurable result limits

### Feedback Loop
- Rate responses (1-5 stars)
- Text feedback collection
- Statistical analysis

### Monitoring
- Active conversation tracking
- Message processing metrics
- Agent performance stats

## Configuration

All configuration is managed through `config.py`:

```python
API_CONFIG = {
    "host": "0.0.0.0",
    "port": 8000,
    "timeout": 30,
}

MODEL_CONFIG = {
    "model_name": "gpt-4",
    "temperature": 0.7,
    "max_tokens": 2048,
}

RAG_CONFIG = {
    "top_k": 5,
    "similarity_threshold": 0.7,
}
```

## Development Notes

### Adding New Agents
1. Add agent definition to `AgentService.agents` dict
2. Implement agent-specific logic in appropriate service
3. Update routing logic in `_determine_agent()`

### Adding Documents to KB
Use the `/knowledge-base/add-document` endpoint or modify `RAGService._load_sample_knowledge_base()`.

### Database Integration
Currently uses in-memory storage. For production:
1. Implement database models
2. Update services to use database queries
3. Add migration support

## Troubleshooting

### API Not Responding
- Check if server is running: `curl http://localhost:8000/health`
- Verify port 8000 is not in use: `netstat -an | grep 8000`
- Check firewall settings

### Import Errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version compatibility (3.8+)

### Knowledge Base Empty
- The sample KB is auto-loaded on startup
- Add custom documents via the `/knowledge-base/add-document` endpoint

## Future Enhancements

- [ ] Database persistence (PostgreSQL/MongoDB)
- [ ] Real LLM integration (OpenAI, Anthropic)
- [ ] Vector embeddings for better RAG
- [ ] Authentication and authorization
- [ ] Rate limiting and API keys
- [ ] Logging and audit trails
- [ ] Performance monitoring
- [ ] Deployment to cloud platforms

## License

Banking Support AI Agent Chatbot - API Backend

## Support

For issues or questions, please contact the Banking Support Team.
