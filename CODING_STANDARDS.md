"""
CODING STANDARDS AND BEST PRACTICES
Banking Support AI Agent Chatbot Project

This document outlines the coding standards and best practices followed throughout
the Banking Support AI Agent Chatbot project.

===============================================================================
1. PYTHON STYLE GUIDE
===============================================================================

Follow PEP 8 - Style Guide for Python Code
https://www.python.org/dev/peps/pep-0008/

Key Rules:
- Line length: 88 characters (for readability)
- Indentation: 4 spaces (never tabs)
- Imports: Sorted alphabetically, grouped by type
- Naming: snake_case for functions/variables, PascalCase for classes
- Quotes: Use double quotes for strings

===============================================================================
2. MODULE AND PACKAGE STRUCTURE
===============================================================================

Every Package Must Have:
✓ __init__.py with comprehensive docstring
✓ Explicit imports of all public classes/functions
✓ __all__ tuple listing exported names
✓ Version information
✓ Author attribution
✓ Usage examples in docstring

Example __init__.py:
```python
\"\"\"
Package Name - Concise Description

Detailed description explaining the package purpose.

Modules:
    submodule1: Description
    submodule2: Description

Example:
    >>> from package import PublicClass
    >>> obj = PublicClass()
\"\"\"

from .module1 import PublicClass
from .module2 import public_function

__all__ = [
    "PublicClass",
    "public_function",
]

__version__ = "1.0.0"
__author__ = "Author Name"
```

===============================================================================
3. IMPORT ORGANIZATION
===============================================================================

Order of Imports (PEP 8 standard):
1. Standard library imports
2. Third-party imports
3. Local application imports

Each group separated by blank line.

Example:
```python
import logging
import json
from typing import Optional, Dict, Any
from datetime import datetime

import fastapi
from pydantic import BaseModel

from config import API_CONFIG
from models import ChatRequest
from services import ChatService
```

Bad Examples (Don't Do):
✗ from package import *
✗ Circular imports
✗ Mixing import styles
✗ Unused imports

===============================================================================
4. DOCUMENTATION
===============================================================================

Module-Level Docstring:
- First line: Brief description
- Blank line
- Detailed description
- Example usage (if applicable)
- Author/version info (if needed)

Class Docstring:
```python
class MyClass:
    \"\"\"
    Brief description of the class.
    
    Longer description explaining what the class does,
    how it should be used, and any important notes.
    
    Attributes:
        attr1 (str): Description of attribute 1
        attr2 (int): Description of attribute 2
    
    Example:
        >>> obj = MyClass("value")
        >>> obj.method()
    \"\"\"
```

Function/Method Docstring:
```python
def my_function(param1: str, param2: int = 10) -> bool:
    \"\"\"
    Brief description of what the function does.
    
    Longer description if needed.
    
    Args:
        param1 (str): Description of parameter 1
        param2 (int): Description of parameter 2 (default: 10)
    
    Returns:
        bool: Description of return value
    
    Raises:
        ValueError: When validation fails
        TypeError: When wrong type provided
    
    Example:
        >>> result = my_function("test")
        >>> print(result)
        True
    \"\"\"
```

Type Hints:
- Use on all functions and methods
- Specify parameter and return types
- Use Optional for nullable values
- Use Union for multiple types

Example:
```python
def process_message(
    conversation_id: str,
    message: str,
    temperature: float = 0.7,
) -> Optional[Dict[str, Any]]:
    \"\"\"Process a message and return response.\"\"\"
```

===============================================================================
5. CLASS AND FUNCTION DESIGN
===============================================================================

Single Responsibility Principle:
Each class/function should have ONE reason to change.

Bad (Multiple Responsibilities):
```python
class UserManager:
    def create_user(self, name): pass
    def delete_user(self, id): pass
    def send_email(self, email): pass  # Not user management
    def log_action(self, action): pass  # Not user management
```

Good (Single Responsibility):
```python
class UserManager:
    \"\"\"Handles user CRUD operations.\"\"\"
    def create_user(self, name): pass
    def delete_user(self, id): pass

class EmailService:
    \"\"\"Handles email operations.\"\"\"
    def send_email(self, email): pass

class Logger:
    \"\"\"Handles logging.\"\"\"
    def log_action(self, action): pass
```

DRY (Don't Repeat Yourself):
Extract common code into reusable functions/methods.

Bad (Repetition):
```python
def process_chat(msg): return generate_response(msg)
def process_feedback(msg): return generate_response(msg)
def process_search(msg): return generate_response(msg)
```

Good (DRY):
```python
def process_message(msg): return generate_response(msg)

def process_chat(msg): return process_message(msg)
def process_feedback(msg): return process_message(msg)
def process_search(msg): return process_message(msg)
```

===============================================================================
6. ERROR HANDLING
===============================================================================

Use Specific Exceptions:
```python
# Bad
try:
    result = risky_operation()
except:
    pass

# Good
try:
    result = risky_operation()
except ValueError as e:
    logger.error(f"Invalid value: {e}")
    raise
except ConnectionError as e:
    logger.error(f"Connection failed: {e}")
    return None
except Exception as e:
    logger.error(f"Unexpected error: {e}", exc_info=True)
    raise
```

Always Log Errors:
```python
import logging

logger = logging.getLogger(__name__)

try:
    result = operation()
except Exception as e:
    logger.error(f"Operation failed: {str(e)}", exc_info=True)
```

===============================================================================
7. ASYNC/AWAIT PATTERNS
===============================================================================

Use for I/O-bound Operations:
```python
async def fetch_data(url: str) -> str:
    \"\"\"Fetch data from URL asynchronously.\"\"\"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()

async def main():
    data = await fetch_data("http://example.com")
```

Never Block Async:
```python
# Bad
async def process():
    time.sleep(5)  # Blocks entire event loop

# Good
async def process():
    await asyncio.sleep(5)  # Non-blocking
```

===============================================================================
8. TESTING READINESS
===============================================================================

Design for Testability:
- Use dependency injection
- Avoid global state
- Keep functions pure when possible
- Use factory patterns

Example:
```python
class ChatService:
    def __init__(self, db=None):
        \"\"\"Dependency injection for testing.\"\"\"
        self.db = db or RealDatabase()

# In tests:
def test_chat_service():
    mock_db = MockDatabase()
    service = ChatService(db=mock_db)
    # Test with mock
```

===============================================================================
9. CONFIGURATION MANAGEMENT
===============================================================================

Use Environment Variables:
```python
import os
from dotenv import load_dotenv

load_dotenv()

API_PORT = int(os.getenv("API_PORT", 8000))
API_HOST = os.getenv("API_HOST", "0.0.0.0")
DEBUG = os.getenv("DEBUG", "False") == "True"
```

Centralized Configuration:
```python
# config.py
class Config:
    \"\"\"Base configuration.\"\"\"
    API_PORT = 8000
    API_HOST = "0.0.0.0"

class DevelopmentConfig(Config):
    \"\"\"Development configuration.\"\"\"
    DEBUG = True

class ProductionConfig(Config):
    \"\"\"Production configuration.\"\"\"
    DEBUG = False
```

===============================================================================
10. SECURITY BEST PRACTICES
===============================================================================

Never Hardcode Secrets:
```python
# Bad
API_KEY = "sk-12345678"

# Good
API_KEY = os.getenv("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY environment variable not set")
```

Input Validation:
```python
from pydantic import BaseModel, validator

class UserInput(BaseModel):
    email: str
    age: int
    
    @validator("email")
    def email_valid(cls, v):
        if "@" not in v:
            raise ValueError("Invalid email")
        return v
    
    @validator("age")
    def age_valid(cls, v):
        if v < 0 or v > 120:
            raise ValueError("Age must be 0-120")
        return v
```

SQL Injection Prevention:
```python
# Bad
query = f"SELECT * FROM users WHERE id = {user_id}"

# Good
query = "SELECT * FROM users WHERE id = ?"
execute(query, (user_id,))
```

===============================================================================
11. LOGGING BEST PRACTICES
===============================================================================

Use Appropriate Log Levels:
```python
import logging

logger = logging.getLogger(__name__)

logger.debug("Detailed diagnostic info")
logger.info("General informational message")
logger.warning("Warning about potential issue")
logger.error("Error occurred: %s", error)
logger.critical("Critical system failure")
```

Structured Logging:
```python
import json

# Bad
logger.info(f"User {user_id} logged in from {ip_address}")

# Good
logger.info("User login", extra={
    "user_id": user_id,
    "ip_address": ip_address,
})
```

===============================================================================
12. NAMING CONVENTIONS
===============================================================================

Constants:
```python
# All uppercase with underscores
MAX_RETRIES = 3
API_TIMEOUT = 30
DEFAULT_TEMPERATURE = 0.7
```

Variables and Functions:
```python
# Lowercase with underscores (snake_case)
user_name = "John"
get_user_by_id(user_id)
is_valid_email(email)
```

Classes:
```python
# PascalCase (CapWords)
class ChatService:
    pass

class UserManager:
    pass

class HTTPClient:
    pass
```

Private/Protected Members:
```python
class MyClass:
    def __init__(self):
        self.public_var = 1
        self._protected_var = 2
        self.__private_var = 3
```

===============================================================================
13. CODE REVIEW CHECKLIST
===============================================================================

Before Committing:
- [ ] All functions have docstrings
- [ ] Type hints present
- [ ] No unused imports
- [ ] No hardcoded values
- [ ] Error handling implemented
- [ ] Logging added
- [ ] PEP 8 compliant
- [ ] Tests passing
- [ ] Documentation updated

For New Features:
- [ ] Single responsibility
- [ ] DRY principle followed
- [ ] Testable code
- [ ] Performance considered
- [ ] Security reviewed
- [ ] Backward compatible
- [ ] API documented
- [ ] Example usage provided

===============================================================================
14. COMMON MISTAKES TO AVOID
===============================================================================

❌ Using mutable defaults:
```python
def add_item(item, list=[]):  # BAD - list persists between calls
    list.append(item)
    return list

def add_item(item, list=None):  # GOOD
    if list is None:
        list = []
    list.append(item)
    return list
```

❌ Bare except:
```python
try:
    risky_code()
except:  # BAD - catches everything including KeyboardInterrupt
    pass

try:
    risky_code()
except Exception:  # GOOD
    pass
```

❌ Global state:
```python
# BAD
global_cache = {}

def get_data(key):
    return global_cache[key]

# GOOD
class DataCache:
    def __init__(self):
        self.cache = {}
    
    def get(self, key):
        return self.cache[key]
```

❌ Not using context managers:
```python
# BAD
file = open("file.txt")
content = file.read()
file.close()

# GOOD
with open("file.txt") as file:
    content = file.read()
```

===============================================================================
15. USEFUL TOOLS AND COMMANDS
===============================================================================

Code Formatting:
```bash
# Format with Black
black .

# Check style with Flake8
flake8 .

# Check with pylint
pylint *.py
```

Type Checking:
```bash
# Static type checking with mypy
mypy .
```

Testing:
```bash
# Run tests
pytest

# With coverage
pytest --cov=.

# Specific test file
pytest tests/test_chat.py
```

Documentation:
```bash
# Generate from docstrings
sphinx-apidoc -o docs .
```

===============================================================================

For questions or clarifications on coding standards, refer to:
- PEP 8: https://www.python.org/dev/peps/pep-0008/
- PEP 257: https://www.python.org/dev/peps/pep-0257/ (Docstrings)
- Google Python Style Guide
- Project README files

Last Updated: May 10, 2026
Version: 1.0
"""
