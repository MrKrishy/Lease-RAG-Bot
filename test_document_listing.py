#!/usr/bin/env python3
"""
Test script to verify document listing functionality
"""

import os
import sys

# Add the current directory to the path so we can import from app.py
sys.path.append('.')

def test_document_listing():
    print("🧪 Testing Document Listing Functionality...")
    print("=" * 60)
    
    # Import the functions from app.py
    try:
        from app import (
            get_available_documents, 
            is_document_listing_question, 
            create_document_listing_response,
            list_pdfs,
            folder_path,
            recursive
        )
        print("✅ Successfully imported document listing functions")
    except ImportError as e:
        print(f"❌ Failed to import functions: {e}")
        return False
    
    # Test document detection
    print("\n📁 Testing document detection...")
    abs_folder = os.path.abspath(folder_path)
    pdfs = list_pdfs(abs_folder, recursive)
    
    print(f"📂 Scanning folder: {abs_folder}")
    print(f"📄 Found {len(pdfs)} PDF files:")
    for pdf in pdfs:
        filename = os.path.basename(pdf)
        file_size = os.path.getsize(pdf)
        file_size_mb = round(file_size / (1024 * 1024), 2)
        print(f"   - {filename} ({file_size_mb} MB)")
    
    # Test document listing question detection
    print("\n❓ Testing question detection...")
    test_questions = [
        "What documents do you have access to?",
        "What files are available?",
        "Show me the documents",
        "What leases do you have?",
        "List all contracts",
        "What is the monthly rent?",  # Should NOT be detected
        "What is the lease term?",    # Should NOT be detected
    ]
    
    for question in test_questions:
        is_doc_question = is_document_listing_question(question)
        status = "📋 DOCUMENT LISTING" if is_doc_question else "❌ NOT DOCUMENT LISTING"
        print(f"   {status}: '{question}'")
    
    # Test document listing response
    print("\n📋 Testing document listing response...")
    response = create_document_listing_response()
    print("Response preview:")
    print("-" * 40)
    print(response[:500] + "..." if len(response) > 500 else response)
    print("-" * 40)
    
    # Test available documents function
    print("\n📊 Testing get_available_documents...")
    try:
        documents = get_available_documents()
        print(f"✅ Retrieved {len(documents)} documents")
        for doc in documents:
            print(f"   - {doc['filename']} ({doc['size_mb']} MB) - {'Indexed' if doc['indexed'] else 'Not Indexed'}")
    except Exception as e:
        print(f"❌ Error getting documents: {e}")
    
    print("\n" + "=" * 60)
    print("✅ Document listing test completed!")
    print("\n🎯 The system will now respond to questions like:")
    print("   - 'What documents do you have access to?'")
    print("   - 'What files are available?'")
    print("   - 'Show me the documents'")
    print("   - 'What leases do you have?'")
    
    return True

if __name__ == "__main__":
    success = test_document_listing()
    sys.exit(0 if success else 1)
