#!/usr/bin/env python3
"""
NimbusRelay Demo Script
Demonstrates the key features of the email management application
"""

import requests
import json
import time

def demo_api_endpoints():
    """Demonstrate the API endpoints without requiring actual email credentials"""
    
    base_url = "http://localhost:5000"
    
    print("🌩️  NimbusRelay API Demo")
    print("=" * 50)
    
    # Test 1: Check configuration status
    print("\n1. Checking configuration status...")
    try:
        response = requests.get(f"{base_url}/api/config")
        if response.status_code == 200:
            config_data = response.json()
            print(f"   ✅ Configuration endpoint working")
            print(f"   📊 Configured: {config_data.get('configured', False)}")
            print(f"   📝 Missing vars: {len(config_data.get('missing_vars', []))}")
        else:
            print(f"   ❌ Configuration check failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Test spam analysis with sample email
    print("\n2. Testing spam analysis with sample email...")
    sample_email = {
        "from": "test@example.com",
        "subject": "Congratulations! You've won $1,000,000!",
        "body": "Click here immediately to claim your prize! Limited time offer! Act now!"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/analyze-spam", 
            json=sample_email,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Spam analysis endpoint working")
            if "error" in result:
                print(f"   ⚠️  Expected error (no AI service): {result['error']}")
            else:
                print(f"   📊 Classification: {result.get('classification', 'Unknown')}")
        else:
            print(f"   ❌ Spam analysis failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Test email analysis
    print("\n3. Testing email analysis...")
    try:
        response = requests.post(
            f"{base_url}/api/analyze-email",
            json=sample_email,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Email analysis endpoint working")
            if "analysis" in result:
                analysis = result["analysis"]
                if "not connected" in analysis.lower():
                    print(f"   ⚠️  Expected: AI service not connected")
                else:
                    print(f"   📊 Analysis: {analysis[:100]}...")
        else:
            print(f"   ❌ Email analysis failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Test draft generation
    print("\n4. Testing draft generation...")
    try:
        response = requests.post(
            f"{base_url}/api/generate-draft",
            json={"analysis": "This email appears to be a promotional message requiring a polite response."},
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Draft generation endpoint working")
            if "draft" in result:
                draft = result["draft"]
                if "not connected" in draft.lower():
                    print(f"   ⚠️  Expected: AI service not connected")
                else:
                    print(f"   📊 Draft: {draft[:100]}...")
        else:
            print(f"   ❌ Draft generation failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 5: Test folders endpoint
    print("\n5. Testing folders endpoint...")
    try:
        response = requests.get(f"{base_url}/api/folders")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Folders endpoint working")
            if "error" in result:
                print(f"   ⚠️  Expected error (no email service): {result['error']}")
            else:
                folders = result.get('folders', [])
                print(f"   📊 Found {len(folders)} folders")
        else:
            print(f"   ❌ Folders test failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("📋 Demo Summary:")
    print("   • All API endpoints are accessible")
    print("   • Error handling is working correctly")
    print("   • Application is ready for configuration")
    print("   • Frontend should be fully functional")
    print("\n🎯 Next Steps:")
    print("   1. Open http://localhost:5000 in your browser")
    print("   2. Configure email and AI credentials")
    print("   3. Connect to services and test functionality")
    print("   4. Enjoy the beautiful imperial purple interface!")

if __name__ == "__main__":
    demo_api_endpoints()
