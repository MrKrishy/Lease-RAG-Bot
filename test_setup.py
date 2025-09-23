#!/usr/bin/env python3
"""
Test script to verify the setup is correct
"""

import os
import sys

def test_setup():
    print("🧪 Testing Lease Document Q&A Setup...")
    print("=" * 50)
    
    # Check required files
    required_files = [
        "app.py", 
        "requirements.txt",
        "openai.txt",
        "README.md",
        "run.py",
        "templates/index.html"
    ]
    
    print("📁 Checking required files...")
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            missing_files.append(file_path)
    
    # Check Lease Contracts folder
    print("\n📂 Checking Lease Contracts folder...")
    if os.path.exists("Lease Contracts"):
        print("✅ Lease Contracts folder exists")
        pdf_files = []
        for root, dirs, files in os.walk("Lease Contracts"):
            for file in files:
                if file.lower().endswith('.pdf'):
                    pdf_files.append(os.path.join(root, file))
        
        if pdf_files:
            print(f"✅ Found {len(pdf_files)} PDF files:")
            for pdf in pdf_files:
                print(f"   📄 {pdf}")
        else:
            print("⚠️  No PDF files found in Lease Contracts folder")
    else:
        print("❌ Lease Contracts folder missing")
        missing_files.append("Lease Contracts/")
    
    # Check openai.txt content
    print("\n🔑 Checking OpenAI API key...")
    if os.path.exists("openai.txt"):
        with open("openai.txt", "r") as f:
            key = f.read().strip()
            if key:
                print("✅ OpenAI API key file has content")
            else:
                print("⚠️  OpenAI API key file is empty")
    else:
        print("❌ OpenAI API key file missing")
    
    # Summary
    print("\n" + "=" * 50)
    if missing_files:
        print("❌ Setup incomplete. Missing files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    else:
        print("✅ Setup looks good! Ready to run.")
        print("\n🚀 To start the application:")
        print("   python3 run.py")
        print("\n📱 Then open: http://localhost:5001")
        return True

if __name__ == "__main__":
    success = test_setup()
    sys.exit(0 if success else 1)
