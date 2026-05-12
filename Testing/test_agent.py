#!/usr/bin/env python
"""Test script for LLMAgent functionality."""

import sys
import logging
from pathlib import Path

# Add workspace root to path
workspace_root = Path(__file__).parent.parent
sys.path.insert(0, str(workspace_root))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)

from RAG import LLMAgent

def test_agent():
    """Test the LLMAgent with various queries."""
    
    print("\n" + "="*80)
    print("LLM AGENT TEST SUITE")
    print("="*80)
    
    # Initialize agent
    agent = LLMAgent()
    print(f"\n[OK] Agent initialized with {len(agent.tools)} tools")
    
    # Test 1: Simple Interest Query
    print("\n--- TEST 1: Simple Interest Query ---")
    response1 = agent.process_query("Calculate simple interest for 1000 at 5% for 2 years")
    print(f"Response: {response1['content'][:300]}...")
    
    # Test 2: Compound Interest Query
    print("\n--- TEST 2: Compound Interest Query ---")
    response2 = agent.process_query("What is compound interest on 5000 at 4% for 3 years?")
    print(f"Response: {response2['content'][:300]}...")
    
    # Test 3: EMI Query
    print("\n--- TEST 3: EMI Calculation Query ---")
    response3 = agent.process_query("Calculate EMI for a 500000 loan at 8% interest for 5 years")
    print(f"Response: {response3['content'][:300]}...")
    
    # Test 4: Rate of Return Query
    print("\n--- TEST 4: Rate of Return Query ---")
    response4 = agent.process_query("What is my rate of return if I invested 50000 and got 75000 back in 2 years?")
    print(f"Response: {response4['content'][:300]}...")
    
    # Check memory
    print("\n--- MEMORY STATUS ---")
    memory_status = agent.get_memory_status()
    print(f"Messages stored: {memory_status['memory_size']}/{memory_status['max_memory_size']}")
    print(f"Recent messages:")
    for msg in memory_status['messages'][-4:]:
        role = msg['role'].upper()
        content = msg['content'][:80]
        print(f"  [{role}] {content}...")
    
    # Available tools
    print("\n--- AVAILABLE TOOLS ---")
    for tool in agent.get_tools_info():
        print(f"  * {tool['name']}: {tool['description']}")
    
    print("\n" + "="*80)
    print("OK - ALL TESTS COMPLETED SUCCESSFULLY")
    print("="*80)

if __name__ == "__main__":
    test_agent()
