#!/usr/bin/env python3
"""
Test script to verify API connectivity
"""

import requests
import json

def test_api():
    base_url = "http://localhost:5001"
    
    print("🧪 Testing NorthStar AI API")
    print("=" * 40)
    
    # Test 1: Health check
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Health check: PASS")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check: FAIL ({response.status_code})")
            return
    except Exception as e:
        print(f"❌ Health check: ERROR - {e}")
        return
    
    # Test 2: Login
    try:
        login_data = {"email": "test@example.com", "password": "test123"}
        response = requests.post(f"{base_url}/api/auth/login", 
                               json=login_data, timeout=5)
        if response.status_code == 200:
            print("✅ Login: PASS")
            cookies = response.cookies
        else:
            print(f"❌ Login: FAIL ({response.status_code})")
            return
    except Exception as e:
        print(f"❌ Login: ERROR - {e}")
        return
    
    # Test 3: Content Generation
    try:
        content_data = {
            "platform": "twitter",
            "prompt": "Test our new AI automation feature"
        }
        response = requests.post(f"{base_url}/api/agents/generate",
                               json=content_data, cookies=cookies, timeout=10)
        if response.status_code == 200:
            print("✅ Content Generation: PASS")
            result = response.json()
            content = result.get('content', {}).get('primary_content', '')
            print(f"   Generated: {content[:100]}...")
        else:
            print(f"❌ Content Generation: FAIL ({response.status_code})")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Content Generation: ERROR - {e}")
    
    print("=" * 40)
    print("🎯 API Test Complete")

if __name__ == "__main__":
    test_api()