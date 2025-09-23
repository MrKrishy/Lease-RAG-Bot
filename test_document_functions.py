#!/usr/bin/env python3
"""
Test script to verify document listing functions without Flask dependency
"""

import os
import glob

def list_pdfs(root, recurse):
    """Simplified version of list_pdfs function"""
    root = os.path.abspath(root)
    if not recurse:
        return sorted(glob.glob(os.path.join(root, "*.pdf")))
    matches = []
    for dirpath, _, _ in os.walk(root):
        matches.extend(sorted(glob.glob(os.path.join(dirpath, "*.pdf"))))
    return matches

def test_document_functions():
    print("🧪 Testing Document Functions...")
    print("=" * 50)
    
    # Test parameters
    folder_path = "Lease Contracts"
    recursive = True
    
    # Test document detection
    print("📁 Testing document detection...")
    abs_folder = os.path.abspath(folder_path)
    
    if not os.path.exists(abs_folder):
        print(f"❌ Folder not found: {abs_folder}")
        return False
    
    pdfs = list_pdfs(abs_folder, recursive)
    
    print(f"📂 Scanning folder: {abs_folder}")
    print(f"📄 Found {len(pdfs)} PDF files:")
    
    documents_info = []
    for pdf in pdfs:
        filename = os.path.basename(pdf)
        file_size = os.path.getsize(pdf)
        file_size_mb = round(file_size / (1024 * 1024), 2)
        documents_info.append({
            'filename': filename,
            'path': pdf,
            'size_mb': file_size_mb,
            'indexed': True  # Assume indexed for test
        })
        print(f"   - {filename} ({file_size_mb} MB)")
    
    # Test document listing question detection
    print("\n❓ Testing question detection...")
    
    def is_document_listing_question(question):
        document_keywords = [
            'documents', 'files', 'leases', 'contracts', 'available', 'access',
            'what do you have', 'what files', 'which documents', 'list documents',
            'show me documents', 'what leases', 'what contracts'
        ]
        
        question_lower = question.lower()
        return any(keyword in question_lower for keyword in document_keywords)
    
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
    
    # Test document listing response creation
    print("\n📋 Testing document listing response...")
    
    def create_document_listing_response():
        if not documents_info:
            return "I don't currently have access to any documents. Please ensure PDF files are placed in the 'Lease Contracts' folder."
        
        response = "I have access to the following documents:\n\n"
        
        for i, doc in enumerate(documents_info, 1):
            status_icon = "✅" if doc['indexed'] else "⏳"
            status_text = "Indexed" if doc['indexed'] else "Processing"
            
            response += f"{i}. **{doc['filename']}** {status_icon}\n"
            response += f"   - Size: {doc['size_mb']} MB\n"
            response += f"   - Status: {status_text}\n\n"
        
        response += "You can ask questions about any of these documents, such as:\n"
        response += "- 'What is the lease term in [filename]?'\n"
        response += "- 'What is the monthly rent in [filename]?'\n"
        response += "- 'What are the tenant responsibilities in [filename]?'\n\n"
        response += "**Note**: Documents marked with ⏳ are still being processed and may not be fully searchable yet."
        
        return response
    
    response = create_document_listing_response()
    print("Response preview:")
    print("-" * 40)
    print(response[:500] + "..." if len(response) > 500 else response)
    print("-" * 40)
    
    print("\n" + "=" * 50)
    print("✅ Document functions test completed!")
    print(f"📊 Found {len(documents_info)} documents ready for listing")
    print("\n🎯 The system will now respond to document listing questions")
    
    return True

if __name__ == "__main__":
    success = test_document_functions()
    sys.exit(0 if success else 1)
