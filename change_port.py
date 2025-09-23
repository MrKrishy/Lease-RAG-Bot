#!/usr/bin/env python3
"""
Simple script to change the port in app.py
"""

import re
import sys

def change_port(new_port):
    """Change the port in app.py"""
    try:
        # Read the current app.py
        with open('app.py', 'r') as f:
            content = f.read()
        
        # Replace the port in the app.run() call
        old_pattern = r'app\.run\(debug=True, host=\'0\.0\.0\.0\', port=\d+\)'
        new_port_line = f"app.run(debug=True, host='0.0.0.0', port={new_port})"
        
        new_content = re.sub(old_pattern, new_port_line, content)
        
        # Also update the print statement
        old_print_pattern = r'http://localhost:\d+'
        new_print_line = f'http://localhost:{new_port}'
        new_content = re.sub(old_print_pattern, new_print_line, new_content)
        
        # Write back to file
        with open('app.py', 'w') as f:
            f.write(new_content)
        
        print(f"✅ Port changed to {new_port}")
        print(f"📱 Your app will now run on: http://localhost:{new_port}")
        return True
        
    except Exception as e:
        print(f"❌ Error changing port: {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 change_port.py <new_port>")
        print("Example: python3 change_port.py 8080")
        sys.exit(1)
    
    try:
        new_port = int(sys.argv[1])
        if new_port < 1024 or new_port > 65535:
            print("❌ Port must be between 1024 and 65535")
            sys.exit(1)
    except ValueError:
        print("❌ Port must be a number")
        sys.exit(1)
    
    if change_port(new_port):
        print(f"\n🚀 To start with new port:")
        print(f"   python3 run.py")
        print(f"📱 Then open: http://localhost:{new_port}")

if __name__ == "__main__":
    main()

