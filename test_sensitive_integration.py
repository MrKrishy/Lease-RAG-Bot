#!/usr/bin/env python3
"""
Test script to verify sensitive data protection integration
"""

from sensitive_data_protection import SensitiveDataProtector

def test_integration():
    print("🧪 Testing Sensitive Data Protection Integration...")
    print("=" * 60)
    
    protector = SensitiveDataProtector()
    
    # Test questions that should be blocked
    sensitive_questions = [
        "What is the tenant's social security number?",
        "What is John's phone number?",
        "Can you tell me the credit card number?",
        "What is the bank account information?",
        "What is the email address?",
        "What is the home address?"
    ]
    
    # Test questions that should be allowed
    safe_questions = [
        "What is the monthly rent?",
        "What is the lease term?",
        "When does the lease expire?",
        "What are the tenant responsibilities?",
        "What is the pet policy?",
        "What is the security deposit amount?"
    ]
    
    print("🚨 Testing Sensitive Questions (Should be BLOCKED):")
    print("-" * 50)
    for question in sensitive_questions:
        is_sensitive = protector.is_question_about_sensitive_data(question)
        detected_types = list(protector.detect_sensitive_data(question).keys())
        
        status = "🚨 BLOCKED" if is_sensitive else "❌ NOT BLOCKED"
        print(f"  {status}: '{question}'")
        if detected_types:
            print(f"    Detected types: {detected_types}")
        
        if is_sensitive:
            warning = protector.create_sensitive_data_warning(question, detected_types)
            print(f"    Response: {warning[:100]}...")
        print()
    
    print("✅ Testing Safe Questions (Should be ALLOWED):")
    print("-" * 50)
    for question in safe_questions:
        is_sensitive = protector.is_question_about_sensitive_data(question)
        status = "✅ ALLOWED" if not is_sensitive else "❌ INCORRECTLY BLOCKED"
        print(f"  {status}: '{question}'")
    
    print("\n" + "=" * 60)
    print("🔒 Testing Document Masking:")
    print("-" * 30)
    
    # Test document masking
    sample_document = """
    LEASE AGREEMENT
    
    Tenant: John Doe
    SSN: 123-45-6789
    Phone: (555) 123-4567
    Email: john.doe@example.com
    Address: 123 Main Street, Anytown, ST 12345
    
    Monthly Rent: $1,500
    Lease Term: 12 months
    Security Deposit: $1,500
    """
    
    masked_doc, masked_info = protector.mask_sensitive_data(sample_document)
    
    print("📄 Original document:")
    print(sample_document)
    print("\n🔒 Masked document:")
    print(masked_doc)
    
    print("\n📊 Masking summary:")
    for category, masks in masked_info.items():
        print(f"  {category}: {len(masks)} items masked")
        for mask_info in masks:
            print(f"    {mask_info['original']} -> {mask_info['masked']}")
    
    print("\n✅ Integration test completed!")
    print("🎯 The system will now:")
    print("  1. Mask sensitive data in documents before storing")
    print("  2. Block questions asking for sensitive information")
    print("  3. Provide helpful warnings instead of sensitive data")
    print("  4. Show visual indicators in the web interface")

if __name__ == "__main__":
    test_integration()
