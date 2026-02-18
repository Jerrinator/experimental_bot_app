#!/usr/bin/env python3
"""
Test script to verify container-based storage implementation
"""

import os
import sys
import json
import logging
from datetime import datetime

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.DatabaseService import DatabaseService
from services.ConversationManager import ConversationManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_database_service():
    """Test DatabaseService functionality"""
    print("=" * 50)
    print("Testing DatabaseService")
    print("=" * 50)
    
    try:
        # Create database service for test user
        test_username = "test.user@example.com"
        db_service = DatabaseService(test_username)
        
        # Test conversation storage
        print("1. Testing conversation storage...")
        success = db_service.store_conversation(
            session_id="test_session_1",
            message_id="msg_001",
            user_message="Hello, can you help me with Python?",
            bot_response="Of course! I'd be happy to help you with Python. What specific aspect would you like to learn about?",
            context_data={"test": True}
        )
        print(f"   Conversation stored: {success}")
        
        # Test document storage
        print("2. Testing document storage...")
        success = db_service.store_document(
            filename="test_document.txt",
            content="This is a test document content for verification purposes.",
            file_type="txt"
        )
        print(f"   Document stored: {success}")
        
        # Test recent conversations retrieval
        print("3. Testing recent conversations retrieval...")
        recent_conversations = db_service.get_recent_conversations(5)
        print(f"   Retrieved {len(recent_conversations)} recent conversations")
        
        # Test keyword search
        print("4. Testing keyword search...")
        keyword_results = db_service.search_by_keywords(["python", "help"], 3)
        print(f"   Found {len(keyword_results)} keyword matches")
        
        # Test semantic search
        print("5. Testing semantic search...")
        semantic_results = db_service.semantic_search("programming assistance", 3)
        print(f"   Found {len(semantic_results)} semantic matches")
        
        # Test context injection
        print("6. Testing context injection...")
        context = db_service.get_context_for_injection("I need help with coding")
        context_length = len(context)
        print(f"   Generated context: {context_length} characters")
        
        # Test user documents
        print("7. Testing user documents retrieval...")
        documents = db_service.get_user_documents(5)
        print(f"   Retrieved {len(documents)} documents")
        
        # Test database stats
        print("8. Testing database statistics...")
        stats = db_service.get_database_stats()
        print(f"   Database stats: {json.dumps(stats, indent=2)}")
        
        print("✅ DatabaseService tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ DatabaseService test failed: {e}")
        return False

def test_conversation_manager():
    """Test ConversationManager functionality"""
    print("\n" + "=" * 50)
    print("Testing ConversationManager")
    print("=" * 50)
    
    try:
        # Create conversation manager for test user
        test_username = "test.manager@example.com"
        conv_manager = ConversationManager(test_username)
        
        # Start session
        print("1. Testing session management...")
        session_id = conv_manager.start_session()
        print(f"   Session started: {session_id}")
        
        # Add conversations
        print("2. Testing conversation addition...")
        success = conv_manager.add_conversation(
            user_message="What is machine learning?",
            bot_response="Machine learning is a subset of artificial intelligence that enables computers to learn and improve from experience without being explicitly programmed.",
            context_data={"topic": "AI/ML"}
        )
        print(f"   Conversation added: {success}")
        
        # Test context generation
        print("3. Testing context generation...")
        context = conv_manager.get_conversation_context("Tell me more about AI")
        context_length = len(context)
        print(f"   Context generated: {context_length} characters")
        
        # Test document storage via manager
        print("4. Testing document storage via manager...")
        success = conv_manager.store_document(
            filename="ai_guide.txt",
            content="Artificial Intelligence (AI) is the simulation of human intelligence in machines...",
            file_type="txt"
        )
        print(f"   Document stored via manager: {success}")
        
        # Test enhanced system prompt
        print("5. Testing enhanced system prompt...")
        base_prompt = "You are a helpful AI assistant."
        enhanced_prompt = conv_manager.build_enhanced_system_prompt(
            base_prompt=base_prompt,
            user_message="What can you tell me about the documents I uploaded?"
        )
        enhanced_length = len(enhanced_prompt)
        print(f"   Enhanced prompt: {enhanced_length} characters")
        
        # Test session stats
        print("6. Testing session statistics...")
        stats = conv_manager.get_session_stats()
        print(f"   Session stats: {json.dumps(stats, indent=2)}")
        
        # Test search functionality
        print("7. Testing conversation search...")
        search_results = conv_manager.search_conversation_history("machine learning", 5)
        print(f"   Search results: {len(search_results)} matches")
        
        print("✅ ConversationManager tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ ConversationManager test failed: {e}")
        return False

def test_data_persistence():
    """Test data persistence across manager instances"""
    print("\n" + "=" * 50)
    print("Testing Data Persistence")
    print("=" * 50)
    
    try:
        test_username = "persistence.test@example.com"
        
        # Create first manager instance and add data
        print("1. Creating first manager instance...")
        manager1 = ConversationManager(test_username)
        session_id = manager1.start_session()
        
        manager1.add_conversation(
            user_message="Test persistence message",
            bot_response="This is a test response for persistence verification",
            context_data={"persistence_test": True}
        )
        
        manager1.store_document(
            filename="persistence_test.txt",
            content="This document tests data persistence across container restarts",
            file_type="txt"
        )
        
        print("   Data added to first manager instance")
        
        # Create second manager instance and verify data exists
        print("2. Creating second manager instance...")
        manager2 = ConversationManager(test_username)
        
        # Check if data persists
        recent_conversations = manager2.db_service.get_recent_conversations(10)
        documents = manager2.db_service.get_user_documents(10)
        
        print(f"   Persisted conversations: {len(recent_conversations)}")
        print(f"   Persisted documents: {len(documents)}")
        
        # Verify specific content
        found_test_conversation = any(
            "Test persistence message" in conv.get('user_message', '') 
            for conv in recent_conversations
        )
        
        found_test_document = any(
            doc.get('filename') == 'persistence_test.txt' 
            for doc in documents
        )
        
        print(f"   Test conversation found: {found_test_conversation}")
        print(f"   Test document found: {found_test_document}")
        
        if found_test_conversation and found_test_document:
            print("✅ Data persistence tests completed successfully!")
            return True
        else:
            print("❌ Data persistence test failed: Data not found")
            return False
        
    except Exception as e:
        print(f"❌ Data persistence test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Container-based Storage Implementation Test Suite")
    print("=" * 60)
    print(f"Test started at: {datetime.now().isoformat()}")
    print()
    
    # Ensure test data directory exists
    os.makedirs('./data', exist_ok=True)
    
    results = []
    
    # Run tests
    results.append(("DatabaseService", test_database_service()))
    results.append(("ConversationManager", test_conversation_manager()))
    results.append(("Data Persistence", test_data_persistence()))
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name:25}: {status}")
        if success:
            passed += 1
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Container-based storage implementation is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    exit(main())
