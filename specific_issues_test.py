#!/usr/bin/env python3
"""
Test specific failing endpoints mentioned in test_result.md
"""

import requests
import json

BACKEND_URL = "https://b4e17258-5cf1-4bb8-a561-56760731f05a.preview.emergentagent.com/api"

def test_specific_issues():
    print("🔍 TESTING SPECIFIC REPORTED ISSUES")
    print("=" * 50)
    
    # 1. Test Region Filtering API - reported as working: false
    print("\n1. Testing Region Filtering API (reported as failing)")
    try:
        # Test basic motorcycles endpoint with region parameter
        response = requests.get(f"{BACKEND_URL}/motorcycles", 
                              params={"region": "IN", "limit": 25}, timeout=10)
        print(f"   GET /motorcycles?region=IN&limit=25: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and "motorcycles" in data:
                motorcycles = data["motorcycles"]
                pagination = data.get("pagination", {})
                total_count = pagination.get("total_count", len(motorcycles))
                print(f"   ✅ SUCCESS: Retrieved {len(motorcycles)} motorcycles (total: {total_count})")
            else:
                print(f"   ❌ ISSUE: Invalid response format: {type(data)}")
        else:
            print(f"   ❌ ISSUE: Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
    
    # Test different regions
    regions = ["US", "JP", "DE"]
    for region in regions:
        try:
            response = requests.get(f"{BACKEND_URL}/motorcycles", 
                                  params={"region": region, "limit": 25}, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and "motorcycles" in data:
                    pagination = data.get("pagination", {})
                    total_count = pagination.get("total_count", len(data["motorcycles"]))
                    print(f"   ✅ {region}: {total_count} motorcycles")
                else:
                    print(f"   ❌ {region}: Invalid format")
            else:
                print(f"   ❌ {region}: Status {response.status_code}")
        except Exception as e:
            print(f"   ❌ {region}: Error {str(e)}")
    
    # 2. Test Advanced Filtering System - reported as working: false
    print("\n2. Testing Advanced Filtering System (reported as failing)")
    
    # Test manufacturer filtering
    try:
        response = requests.get(f"{BACKEND_URL}/motorcycles", 
                              params={"manufacturer": "Yamaha", "limit": 10}, timeout=10)
        print(f"   GET /motorcycles?manufacturer=Yamaha: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and "motorcycles" in data:
                motorcycles = data["motorcycles"]
                print(f"   ✅ SUCCESS: Found {len(motorcycles)} Yamaha motorcycles")
            elif isinstance(data, list):
                print(f"   ⚠️  LEGACY FORMAT: Found {len(data)} Yamaha motorcycles (array format)")
            else:
                print(f"   ❌ ISSUE: Invalid response format: {type(data)}")
        else:
            print(f"   ❌ ISSUE: Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
    
    # Test category filtering
    try:
        response = requests.get(f"{BACKEND_URL}/motorcycles", 
                              params={"category": "Sport", "limit": 10}, timeout=10)
        print(f"   GET /motorcycles?category=Sport: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and "motorcycles" in data:
                motorcycles = data["motorcycles"]
                print(f"   ✅ SUCCESS: Found {len(motorcycles)} Sport motorcycles")
            elif isinstance(data, list):
                print(f"   ⚠️  LEGACY FORMAT: Found {len(data)} Sport motorcycles (array format)")
            else:
                print(f"   ❌ ISSUE: Invalid response format: {type(data)}")
        else:
            print(f"   ❌ ISSUE: Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
    
    # 3. Test Sorting System - reported as working: false
    print("\n3. Testing Sorting System (reported as failing)")
    
    # Test year sorting
    try:
        response = requests.get(f"{BACKEND_URL}/motorcycles", 
                              params={"sort_by": "year", "sort_order": "desc", "limit": 10}, timeout=10)
        print(f"   GET /motorcycles?sort_by=year&sort_order=desc: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and "motorcycles" in data:
                motorcycles = data["motorcycles"]
                if len(motorcycles) >= 2:
                    years = [moto.get("year", 0) for moto in motorcycles]
                    is_sorted = all(years[i] >= years[i+1] for i in range(len(years)-1))
                    print(f"   ✅ SUCCESS: {len(motorcycles)} motorcycles, sorted by year: {is_sorted}")
                    print(f"   Years: {years[:5]}...")
                else:
                    print(f"   ⚠️  INSUFFICIENT DATA: Only {len(motorcycles)} motorcycles")
            elif isinstance(data, list):
                if len(data) >= 2:
                    years = [moto.get("year", 0) for moto in data]
                    is_sorted = all(years[i] >= years[i+1] for i in range(len(years)-1))
                    print(f"   ⚠️  LEGACY FORMAT: {len(data)} motorcycles, sorted: {is_sorted}")
                else:
                    print(f"   ⚠️  INSUFFICIENT DATA: Only {len(data)} motorcycles")
            else:
                print(f"   ❌ ISSUE: Invalid response format: {type(data)}")
        else:
            print(f"   ❌ ISSUE: Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
    
    # Test price sorting
    try:
        response = requests.get(f"{BACKEND_URL}/motorcycles", 
                              params={"sort_by": "price", "sort_order": "asc", "limit": 10}, timeout=10)
        print(f"   GET /motorcycles?sort_by=price&sort_order=asc: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and "motorcycles" in data:
                motorcycles = data["motorcycles"]
                if len(motorcycles) >= 2:
                    prices = [moto.get("price_usd", 0) for moto in motorcycles]
                    is_sorted = all(prices[i] <= prices[i+1] for i in range(len(prices)-1))
                    print(f"   ✅ SUCCESS: {len(motorcycles)} motorcycles, sorted by price: {is_sorted}")
                    print(f"   Prices: {prices[:5]}...")
                else:
                    print(f"   ⚠️  INSUFFICIENT DATA: Only {len(motorcycles)} motorcycles")
            elif isinstance(data, list):
                if len(data) >= 2:
                    prices = [moto.get("price_usd", 0) for moto in data]
                    is_sorted = all(prices[i] <= prices[i+1] for i in range(len(prices)-1))
                    print(f"   ⚠️  LEGACY FORMAT: {len(data)} motorcycles, sorted: {is_sorted}")
                else:
                    print(f"   ⚠️  INSUFFICIENT DATA: Only {len(data)} motorcycles")
            else:
                print(f"   ❌ ISSUE: Invalid response format: {type(data)}")
        else:
            print(f"   ❌ ISSUE: Status {response.status_code}")
    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
    
    # 4. Test User Garage Functionality - reported as working: false
    print("\n4. Testing User Garage Functionality (reported as failing)")
    
    # First, create a test user and get token
    test_user_data = {
        "email": "garage.test@bykedream.com",
        "password": "TestPassword123!",
        "name": "Garage Test User"
    }
    
    token = None
    try:
        # Try to register or login
        response = requests.post(f"{BACKEND_URL}/auth/register", json=test_user_data, timeout=10)
        if response.status_code == 200:
            data = response.json()
            token = data.get("token")
            print(f"   User registered: {data.get('user', {}).get('name', 'Unknown')}")
        elif response.status_code == 400 and "already exists" in response.text:
            # Try login
            login_data = {"email": test_user_data["email"], "password": test_user_data["password"]}
            response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data, timeout=10)
            if response.status_code == 200:
                data = response.json()
                token = data.get("token")
                print(f"   User logged in: {data.get('user', {}).get('name', 'Unknown')}")
    except Exception as e:
        print(f"   ❌ Auth ERROR: {str(e)}")
    
    if token:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test GET garage
        try:
            response = requests.get(f"{BACKEND_URL}/garage", headers=headers, timeout=10)
            print(f"   GET /garage: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and "garage_items" in data:
                    garage_items = data["garage_items"]
                    print(f"   ✅ SUCCESS: Retrieved {len(garage_items)} garage items")
                else:
                    print(f"   ❌ ISSUE: Invalid response format: {data}")
            elif response.status_code == 500:
                print(f"   ❌ SERVER ERROR: 500 - This matches the reported issue")
            else:
                print(f"   ❌ ISSUE: Status {response.status_code}")
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
    else:
        print("   ❌ Cannot test garage - no authentication token")
    
    print("\n" + "=" * 50)
    print("SPECIFIC ISSUE TESTING COMPLETE")

if __name__ == "__main__":
    test_specific_issues()