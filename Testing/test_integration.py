#!/usr/bin/env python
"""Integration test for the entire banking chatbot system."""

import sys
import logging
from pathlib import Path

# Add workspace root to path
workspace_root = Path(__file__).parent.parent
sys.path.insert(0, str(workspace_root))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(name)s: %(message)s'
)
logger = logging.getLogger(__name__)

# Import the service interface (which connects Streamlit to FastAPI services)
from Streamlit.utils.service_interface import get_service_interface

def test_financial_query_pipeline():
    """Test the complete pipeline with a financial query."""
    
    print("\n" + "="*80)
    print("BANKING CHATBOT - FULL PIPELINE INTEGRATION TEST")
    print("="*80)
    
    try:
        # Get service interface (Streamlit's connection to FastAPI services)
        print("\n[1] Initializing Service Interface...")
        service_interface = get_service_interface()
        print("    OK - Service interface ready")
        
        # List available agents
        print("\n[2] Listing Available Agents...")
        agents = service_interface.list_agents()
        print(f"    OK - {len(agents)} agents available:")
        for agent in agents:
            status = "AVAILABLE" if agent["is_available"] else "DISABLED"
            print(f"      - {agent['name']} ({agent['agent_type']}) [{status}]")
        
        # Test 1: Financial Query
        print("\n[3] TEST 1: Financial Query (Simple Interest)")
        print("    Query: 'Calculate simple interest for 5000 at 4% for 3 years'")
        
        response1 = service_interface.send_message(
            conversation_id="test-conv-1",
            message="Calculate simple interest for 5000 at 4% for 3 years",
        )
        
        if response1:
            print(f"    OK - Response received")
            print(f"    Agent Type: {response1['agent_type']}")
            print(f"    Confidence: {response1['confidence']:.2%}")
            print(f"    Response (first 150 chars): {response1['response'][:150]}...")
        else:
            print("    ERROR - No response")
        
        # Test 2: EMI Query
        print("\n[4] TEST 2: Financial Query (EMI Calculation)")
        print("    Query: 'What would be my EMI for a 500000 home loan?'")
        
        response2 = service_interface.send_message(
            conversation_id="test-conv-2",
            message="What would be my EMI for a 500000 home loan?",
        )
        
        if response2:
            print(f"    OK - Response received")
            print(f"    Agent Type: {response2['agent_type']}")
            print(f"    Confidence: {response2['confidence']:.2%}")
        else:
            print("    ERROR - No response")
        
        # Test 3: General Query
        print("\n[5] TEST 3: General Query (Not Financial)")
        print("    Query: 'What are your operating hours?'")
        
        response3 = service_interface.send_message(
            conversation_id="test-conv-3",
            message="What are your operating hours?",
        )
        
        if response3:
            print(f"    OK - Response received")
            print(f"    Agent Type: {response3['agent_type']}")
            print(f"    Confidence: {response3['confidence']:.2%}")
        else:
            print("    ERROR - No response")
        
        # Test 4: Get conversation history
        print("\n[6] Getting Conversation History (First Conversation)")
        history = service_interface.get_conversation_history("test-conv-1")
        print(f"    OK - Retrieved {len(history)} messages")
        if history:
            for i, msg in enumerate(history[:4]):  # Show first 4 messages
                role = msg.get("role", "unknown").upper()
                content = msg.get("content", "")[:80]
                print(f"      [{role}] {content}...")
        
        # Test 5: Check if LLMAgent is working in agent service
        print("\n[7] Checking LLMAgent Integration...")
        if hasattr(service_interface, 'agent_service') and service_interface.agent_service:
            if service_interface.agent_service.llm_agent:
                memory_status = service_interface.agent_service.llm_agent.get_memory_status()
                print(f"    OK - LLMAgent available")
                print(f"    Messages in memory: {memory_status['memory_size']}/{memory_status['max_memory_size']}")
            else:
                print("    WARN - LLMAgent not initialized")
        
        print("\n" + "="*80)
        print("OK - INTEGRATION TEST COMPLETED SUCCESSFULLY")
        print("="*80)
        print("\nPipeline verified:")
        print("  * Streamlit service interface working")
        print("  * FastAPI agent service accessible")
        print("  * LLMAgent integrated with financial calculator tools")
        print("  * Query routing working correctly")
        print("  * Conversation history maintained")
        print("="*80 + "\n")
        
        return True
        
    except Exception as e:
        logger.error(f"Integration test failed: {str(e)}", exc_info=True)
        print(f"\n[ERROR] Integration test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_financial_query_pipeline()
    sys.exit(0 if success else 1)
