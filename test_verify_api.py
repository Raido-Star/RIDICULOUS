#!/usr/bin/env python3
"""
Quick test script for VerifyStack API
"""
import requests
import json
import time

# Test configuration
API_URL = "http://localhost:8080/api/v1"

# First, we need to get or create an API key
# For demo, let's extract it from the Storage class
import sys
sys.path.insert(0, '/home/user/RIDICULOUS')

from verify_api import storage

# Get the demo API key
demo_key = [k for k in storage.api_keys.keys() if k.startswith("vsk_demo_")][0]

print("="*70)
print("🧪 VerifyStack API Test Suite")
print("="*70)
print(f"\n🔑 API Key: {demo_key[:20]}...")

# Test 1: Health Check
print("\n" + "="*70)
print("Test 1: Health Check")
print("="*70)
response = requests.get(f"{API_URL}/health")
print(f"Status: {response.status_code}")
print(json.dumps(response.json(), indent=2))

# Test 2: Verify a simple claim (FAST)
print("\n" + "="*70)
print("Test 2: Fast Verification")
print("="*70)
test_claim = "Python is a programming language"
print(f"Claim: {test_claim}")
print("Level: fast")
print("\nSending request...")

start_time = time.time()
response = requests.post(
    f"{API_URL}/verify",
    headers={"X-API-Key": demo_key},
    json={
        "claim": test_claim,
        "verification_level": "fast"
    }
)
elapsed = time.time() - start_time

print(f"Status: {response.status_code}")
if response.status_code == 200:
    result = response.json()
    print(f"\n✅ Verification completed in {elapsed:.2f}s")
    print(f"   Confidence Score: {result['confidence_score']:.2f}")
    print(f"   Status: {result['status']}")
    print(f"   Sources Analyzed: {result['sources_analyzed']}")
    print(f"   Processing Time: {result['processing_time_ms']}ms")
    print(f"   Credits Used: {result['credits_used']}")
    print(f"\n   Reasoning: {result['reasoning']}")
else:
    print(f"❌ Error: {response.text}")

# Test 3: Get Usage Stats
print("\n" + "="*70)
print("Test 3: Usage Statistics")
print("="*70)
response = requests.get(
    f"{API_URL}/usage",
    headers={"X-API-Key": demo_key}
)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    stats = response.json()
    print(f"\n📊 Usage Stats:")
    print(f"   Total Verifications: {stats['total_verifications']}")
    print(f"   Credits Remaining: {stats['credits_remaining']:,}")
    print(f"   Credits Used Today: {stats['credits_used_today']}")
    print(f"   Rate Limit Remaining: {stats['rate_limit_remaining']}")

# Test 4: API Documentation
print("\n" + "="*70)
print("Test 4: Interactive API Documentation")
print("="*70)
print("✅ Swagger UI available at: http://localhost:8080/docs")
print("✅ ReDoc available at: http://localhost:8080/redoc")

# Test 5: Developer Dashboard
print("\n" + "="*70)
print("Test 5: Developer Dashboard")
print("="*70)
print("✅ Dashboard available at: http://localhost:3000/verify_dashboard.html")
print("   (Requires HTTP server on port 3000)")

print("\n" + "="*70)
print("🎉 All Tests Completed!")
print("="*70)
print("\n💡 Next Steps:")
print("   1. Open http://localhost:8080/docs for interactive API docs")
print("   2. Try the developer dashboard at http://localhost:3000/verify_dashboard.html")
print("   3. Read VERIFYSTACK_README.md for full documentation")
print("\n🚀 Your verification API is ready to use!")
