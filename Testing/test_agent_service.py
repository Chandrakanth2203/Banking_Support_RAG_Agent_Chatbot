#!/usr/bin/env python
"""Test script for AgentService with LLMAgent integration."""

import sys
import asyncio
from pathlib import Path

# Add workspace root to path
workspace_root = Path(__file__).parent.parent
sys.path.insert(0, str(workspace_root))

from FastAPI.services import AgentService

async def test_agent_service():
    """Test the AgentService."""
    
    print("\n" + "="*80)
    print("AGENT SERVICE TEST")
    print("="*80)
    
    # Initialize service
    service = AgentService()
    print("\n[OK] AgentService initialized")
    
    # List agents
    print(f"\nAvailable agents ({len(service.agents)}):")
    for agent_type, agent in service.agents.items():
        status = "[AVAILABLE]" if agent["is_available"] else "[DISABLED]"
        print(f"  - {agent_type}: {agent['name']} {status}")
    
    # Check LLMAgent
    if service.llm_agent:
        print("\n[OK] LLMAgent is available")
        memory_status = service.llm_agent.get_memory_status()
        print(f"     Memory: {memory_status['memory_size']}/{memory_status['max_memory_size']} messages")
    else:
        print("\n[WARN] LLMAgent is not available")
    
    # Test financial query
    print("\n--- TEST: Financial Query Routing ---")
    test_query = "Calculate simple interest for 10000 at 5% for 2 years"
    print(f"Query: {test_query}")
    
    agent_type = await service._determine_agent(test_query.lower(), [])
    print(f"Routed to: {agent_type}")
    
    response = await service.route_to_agent(test_query, [], "test-conv-id")
    print(f"Response content (first 200 chars): {response['content'][:200]}...")
    print(f"Tool used: {response.get('tool_used', False)}")
    
    # Test EMI query
    print("\n--- TEST: EMI Query Routing ---")
    test_query2 = "What is the EMI for a home loan?"
    print(f"Query: {test_query2}")
    
    agent_type2 = await service._determine_agent(test_query2.lower(), [])
    print(f"Routed to: {agent_type2}")
    
    # Test general query
    print("\n--- TEST: General Query Routing ---")
    test_query3 = "What are your bank hours?"
    print(f"Query: {test_query3}")
    
    agent_type3 = await service._determine_agent(test_query3.lower(), [])
    print(f"Routed to: {agent_type3}")
    
    print("\n" + "="*80)
    print("OK - ALL TESTS COMPLETED")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(test_agent_service())
