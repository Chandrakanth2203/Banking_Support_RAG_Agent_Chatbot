"""
Package Structure and Best Practices Guide

Banking Support AI Agent Chatbot follows Python best practices for package structure.

=== PACKAGE ORGANIZATION ===

FastAPI Backend:
    FastAPI/
    ├── __init__.py              # Package initialization with version info
    ├── main.py                  # FastAPI application and routes
    ├── config.py                # Configuration management
    ├── models/
    │   ├── __init__.py          # Exports all schemas
    │   └── schemas.py           # Pydantic models
    └── services/
        ├── __init__.py          # Service factory and exports
        ├── chat_service.py      # Conversation management
        ├── rag_service.py       # Knowledge base search
        ├── feedback_service.py  # Feedback handling
        └── agent_service.py     # Multi-agent routing

Streamlit Frontend:
    Streamlit/
    ├── __init__.py              # Package initialization
    ├── app.py                   # Main Streamlit application
    ├── config.py                # Configuration and theme
    ├── components/
    │   ├── __init__.py          # Exports all components
    │   ├── header.py            # Header component
    │   ├── sidebar.py           # Sidebar component
    │   └── chat_interface.py    # Chat interface
    └── utils/
        ├── __init__.py          # Exports all utilities
        ├── logger.py            # Logging setup
        ├── session_manager.py   # Session state
        ├── api_client.py        # API communication
        └── api_config.py        # API configuration

=== BEST PRACTICES IMPLEMENTED ===

1. MODULE IMPORTS (__init__.py)
   ✓ All public classes/functions explicitly imported
   ✓ __all__ defined with all exported names
   ✓ Proper docstrings with usage examples
   ✓ Version info included
   ✓ Author and description metadata

2. CODE ORGANIZATION
   ✓ Separation of concerns (models, services, components)
   ✓ Single responsibility principle
   ✓ DRY (Don't Repeat Yourself)
   ✓ Clear module boundaries
   ✓ Circular import prevention

3. DOCUMENTATION
   ✓ Comprehensive docstrings (module, class, function)
   ✓ Type hints on all functions
   ✓ Usage examples in docstrings
   ✓ README files in each major package
   ✓ Setup guide with quick start

4. ERROR HANDLING
   ✓ Try-except blocks for API calls
   ✓ Logging of errors and warnings
   ✓ HTTP exception handling
   ✓ Graceful fallbacks

5. TESTING READINESS
   ✓ Service factory functions
   ✓ Dependency injection patterns
   ✓ Configurable endpoints
   ✓ Mock-friendly service design

=== IMPORT PATTERNS ===

Bad (Avoid):
    from utils import *
    from models.schemas import ChatRequest, ChatResponse, ...
    from services.chat_service import ChatService
    from services.rag_service import RAGService

Good (Use):
    from utils import setup_logger, initialize_session_state
    from models import ChatRequest, ChatResponse
    from services import ChatService, RAGService
    from components import render_header, render_sidebar

=== USAGE EXAMPLES ===

1. FastAPI Main:
    from models import ChatRequest, ChatResponse
    from services import create_services
    
    chat_svc, rag_svc, fb_svc, agent_svc = create_services()

2. Streamlit App:
    from components import render_header, render_sidebar, render_chat_interface
    from utils import setup_logger, get_api_client
    
    logger = setup_logger(__name__)
    api = get_api_client()

3. Add Models:
    from models import ChatRequest, ChatResponse, FeedbackRequest
    
    request = ChatRequest(conversation_id="...", message="...")

4. Use Services:
    from services import ChatService, RAGService
    
    chat_svc = ChatService()
    await chat_svc.initialize()

=== VERSIONING ===

Current Version: 1.0.0
Versioning Scheme: MAJOR.MINOR.PATCH
    - MAJOR: Incompatible API changes
    - MINOR: New features, backward compatible
    - PATCH: Bug fixes

Access Version:
    from FastAPI import __version__
    from Streamlit import VERSION_INFO

=== CONFIGURATION MANAGEMENT ===

Environment Variables (via .env):
    - API_BASE_URL: FastAPI server URL
    - API_PORT: FastAPI port (default: 8000)
    - MODEL_NAME: AI model (default: gpt-4)
    - TEMPERATURE: Response creativity (default: 0.7)
    - DEBUG: Debug mode (default: False)

Access Configuration:
    from config import API_CONFIG, MODEL_CONFIG
    
    host = API_CONFIG['host']
    model = MODEL_CONFIG['model_name']

=== SERVICE FACTORY PATTERN ===

Why Factory Pattern?
    - Easy testing (mock services)
    - Single point of initialization
    - Decouples service dependencies
    - Cleaner main application code

Usage:
    from services import create_services
    
    # Create all services at once
    chat_svc, rag_svc, fb_svc, agent_svc = create_services()
    
    # Or create individually
    from services import ChatService
    chat_svc = ChatService()

=== ASYNC/AWAIT PATTERNS ===

All services use async/await for:
    - Database operations (when implemented)
    - API calls
    - File I/O
    - External service calls

Usage:
    import asyncio
    
    async def main():
        service = ChatService()
        await service.initialize()
        result = await service.get_conversation_history("conv_123")
    
    asyncio.run(main())

=== LOGGING BEST PRACTICES ===

Setup Logger:
    from utils import setup_logger
    
    logger = setup_logger(__name__)
    logger.info("Application started")
    logger.error("An error occurred: %s", str(error))

Logging Levels:
    - DEBUG: Detailed diagnostic info
    - INFO: General information
    - WARNING: Warning messages
    - ERROR: Error messages
    - CRITICAL: Critical errors

=== SESSION MANAGEMENT (STREAMLIT) ===

Initialize:
    from utils import initialize_session_state
    
    initialize_session_state()

Use Session:
    from utils import add_message, get_chat_history, get_session_data
    
    add_message("user", "Hello")
    history = get_chat_history()
    model = get_session_data("model", "GPT-4")

=== API CLIENT USAGE ===

Initialize:
    from utils import get_api_client
    
    api = get_api_client("http://localhost:8000")

Send Message:
    response = api.send_message(
        conversation_id="conv_123",
        message="Hello",
        temperature=0.7
    )

Search KB:
    results = api.search_knowledge_base(
        query="account opening",
        top_k=5
    )

=== ADDING NEW MODULES ===

Steps to Add New Module:
    1. Create module file (e.g., new_module.py)
    2. Add comprehensive docstrings
    3. Export in __init__.py
    4. Update __all__
    5. Add usage examples to docstring
    6. Document in README
    7. Add unit tests

Example (in package/__init__.py):
    from .new_module import NewClass, helper_function
    
    __all__ = [
        "NewClass",
        "helper_function",
    ]

=== DEPENDENCIES MANAGEMENT ===

FastAPI Backend:
    pip install -r FastAPI/requirements.txt

Streamlit Frontend:
    pip install -r Streamlit/requirements.txt

Update Dependencies:
    pip install --upgrade package_name
    pip freeze > requirements.txt

=== DEPLOYMENT CONSIDERATIONS ===

Production Checklist:
    [ ] All imports in __init__.py
    [ ] No circular imports
    [ ] Environment variables configured
    [ ] Error handling complete
    [ ] Logging configured
    [ ] API documentation updated
    [ ] Tests written and passing
    [ ] Security measures in place
    [ ] Performance optimized
    [ ] Deployment guide created

=== TROUBLESHOOTING ===

ModuleNotFoundError:
    ✓ Ensure __init__.py exists in package
    ✓ Check import path is correct
    ✓ Verify module is in __all__

CircularImportError:
    ✓ Move imports inside functions
    ✓ Restructure module dependencies
    ✓ Use TYPE_CHECKING for type hints

Import Wrong Module:
    ✓ Verify __init__.py has correct imports
    ✓ Check __all__ for all exports
    ✓ Use absolute imports

For more information, see README.md in each package directory.
"""
