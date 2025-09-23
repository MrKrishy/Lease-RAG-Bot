#!/usr/bin/env python3
"""
Sensitive Data Protection Module for Lease Document Q&A System
Detects and protects sensitive information like SSNs, credit card numbers, etc.
"""

import re
import hashlib
from typing import List, Dict, Tuple, Optional

class SensitiveDataProtector:
    def __init__(self):
        # Define patterns for sensitive information
        self.patterns = {
            'ssn': [
                r'\b\d{3}-?\d{2}-?\d{4}\b',  # Standard SSN format
                r'\b\d{9}\b',                # 9 consecutive digits
                r'\b\d{3}\s\d{2}\s\d{4}\b'   # SSN with spaces
            ],
            'credit_card': [
                r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',  # Credit card
                r'\b\d{13,19}\b'  # Long number sequences
            ],
            'bank_account': [
                r'\b\d{8,12}\b',  # Bank account numbers
                r'routing.*?\d{9}',  # Routing numbers
            ],
            'phone': [
                r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # US phone numbers
                r'\(\d{3}\)\s?\d{3}[-.]?\d{4}',     # (123) 456-7890
            ],
            'email': [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            ],
            'address': [
                r'\b\d+\s+[A-Za-z\s]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd)\b'
            ]
        }
        
        # Compile patterns for efficiency
        self.compiled_patterns = {}
        for category, pattern_list in self.patterns.items():
            self.compiled_patterns[category] = [
                re.compile(pattern, re.IGNORECASE) for pattern in pattern_list
            ]
    
    def detect_sensitive_data(self, text: str) -> Dict[str, List[str]]:
        """
        Detect sensitive information in text
        Returns dict with categories and found sensitive data
        """
        found_data = {}
        
        for category, patterns in self.compiled_patterns.items():
            matches = []
            for pattern in patterns:
                matches.extend(pattern.findall(text))
            
            if matches:
                found_data[category] = list(set(matches))  # Remove duplicates
        
        return found_data
    
    def mask_sensitive_data(self, text: str) -> Tuple[str, Dict[str, List[str]]]:
        """
        Mask sensitive information in text
        Returns masked text and information about what was masked
        """
        detected = self.detect_sensitive_data(text)
        masked_text = text
        masked_info = {}
        
        for category, matches in detected.items():
            masked_info[category] = []
            for match in matches:
                # Create a hash for consistent masking
                hash_obj = hashlib.md5(match.encode())
                mask = f"[{category.upper()}_MASKED_{hash_obj.hexdigest()[:8]}]"
                
                # Replace in text
                masked_text = masked_text.replace(match, mask)
                masked_info[category].append({
                    'original': match,
                    'masked': mask
                })
        
        return masked_text, masked_info
    
    def is_question_about_sensitive_data(self, question: str) -> bool:
        """
        Check if a question is asking about sensitive information
        """
        sensitive_keywords = [
            'social security', 'ssn', 'social security number',
            'credit card', 'card number', 'bank account',
            'account number', 'routing number', 'phone number',
            'address', 'email address', 'personal information',
            'private information', 'confidential', 'sensitive'
        ]
        
        question_lower = question.lower()
        return any(keyword in question_lower for keyword in sensitive_keywords)
    
    def create_sensitive_data_warning(self, question: str, detected_types: List[str]) -> str:
        """
        Create a warning message for sensitive data requests
        """
        if not detected_types:
            detected_types = ['personal information']
        
        types_str = ', '.join(detected_types)
        
        return f"""I cannot provide sensitive information such as {types_str}. 

This information is protected for privacy and security reasons. If you need specific details from the lease documents, please ask about non-sensitive information such as:

- Lease terms and dates
- Rent amounts and payment schedules  
- Property details and amenities
- Tenant and landlord responsibilities
- Maintenance procedures
- Lease renewal terms

For sensitive information, please contact the appropriate parties directly."""

def test_sensitive_data_protection():
    """Test the sensitive data protection functionality"""
    protector = SensitiveDataProtector()
    
    # Test data
    test_text = """
    John Doe's Social Security Number is 123-45-6789.
    His phone number is (555) 123-4567.
    Email: john.doe@email.com
    Address: 123 Main Street, City, State 12345
    Credit Card: 4532-1234-5678-9012
    """
    
    print("🧪 Testing Sensitive Data Protection...")
    print("=" * 50)
    
    # Test detection
    detected = protector.detect_sensitive_data(test_text)
    print("📊 Detected sensitive data:")
    for category, matches in detected.items():
        print(f"  {category}: {matches}")
    
    # Test masking
    masked_text, masked_info = protector.mask_sensitive_data(test_text)
    print(f"\n🔒 Masked text:\n{masked_text}")
    
    # Test question detection
    test_questions = [
        "What is the tenant's social security number?",
        "What is the monthly rent?",
        "What is the lease term?",
        "What is John's phone number?",
        "When does the lease expire?"
    ]
    
    print(f"\n❓ Testing question sensitivity:")
    for question in test_questions:
        is_sensitive = protector.is_question_about_sensitive_data(question)
        print(f"  '{question}' -> {'🚨 SENSITIVE' if is_sensitive else '✅ Safe'}")
    
    print("\n✅ Sensitive data protection test completed!")

if __name__ == "__main__":
    test_sensitive_data_protection()
