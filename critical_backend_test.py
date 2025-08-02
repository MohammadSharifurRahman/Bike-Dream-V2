#!/usr/bin/env python3
"""
Critical Backend API Testing for Byke-Dream Motorcycle Database
Focuses on the specific areas mentioned in the review request:
1. Search Functionality
2. Region Filtering 
3. Image Loading
4. Database Connectivity
5. Authentication
6. Comparison Tool
7. User Management
"""

import requests
import json
import sys
from typing import Dict, List, Any

# Backend URL from environment
BACKEND_URL = "https://b4e17258-5cf1-4bb8-a561-56760731f05a.preview.emergentagent.com/api"

class CriticalAPITester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.test_results = []
        self.motorcycle_ids = []
        self.test_user_token = None
        self.test_user_data = {
            "email": "critical.test@bykedream.com",
            "password": "TestPassword123!",
            "name": "Critical Test User"
        }
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = f"{status} - {test_name}"
        if details:
            result += f": {details}"
        self.test_results.append(result)
        print(result)
        return success
        
    def test_database_connectivity(self):
        """Test basic database connectivity and stats"""
        print("\n🔗 TESTING DATABASE CONNECTIVITY")
        print("=" * 50)
        
        try:
            response = requests.get(f"{self.base_url}/stats", timeout=10)
            if response.status_code == 200:
                data = response.json()
                total_motorcycles = data.get("total_motorcycles", 0)
                manufacturers = len(data.get("manufacturers", []))
                categories = len(data.get("categories", []))
                
                return self.log_test("Database Connectivity", True, 
                    f"Connected - {total_motorcycles} motorcycles, {manufacturers} manufacturers, {categories} categories")
            else:
                return self.log_test("Database Connectivity", False, f"Status: {response.status_code}")
        except Exception as e:
            return self.log_test("Database Connectivity", False, f"Error: {str(e)}")
    
    def test_search_functionality(self):
        """Test search suggestions and motorcycle search"""
        print("\n🔍 TESTING SEARCH FUNCTIONALITY")
        print("=" * 50)
        
        all_passed = True
        
        # Test search suggestions
        search_queries = ["honda", "ninja", "yamaha", "ducati"]
        for query in search_queries:
            try:
                response = requests.get(f"{self.base_url}/motorcycles/search/suggestions", 
                                      params={"q": query}, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    suggestions = data.get("suggestions", [])
                    if len(suggestions) > 0:
                        all_passed &= self.log_test(f"Search Suggestions - '{query}'", True, 
                            f"Found {len(suggestions)} suggestions")
                    else:
                        all_passed &= self.log_test(f"Search Suggestions - '{query}'", False, 
                            "No suggestions returned")
                else:
                    all_passed &= self.log_test(f"Search Suggestions - '{query}'", False, 
                        f"Status: {response.status_code}")
            except Exception as e:
                all_passed &= self.log_test(f"Search Suggestions - '{query}'", False, f"Error: {str(e)}")
        
        # Test motorcycle search with filters
        try:
            response = requests.get(f"{self.base_url}/motorcycles", 
                                  params={"search": "honda", "limit": 25}, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and "motorcycles" in data:
                    motorcycles = data["motorcycles"]
                    self.motorcycle_ids = [moto.get("id") for moto in motorcycles[:3] if moto.get("id")]
                    all_passed &= self.log_test("Motorcycle Search", True, 
                        f"Found {len(motorcycles)} Honda motorcycles")
                else:
                    all_passed &= self.log_test("Motorcycle Search", False, "Invalid response format")
            else:
                all_passed &= self.log_test("Motorcycle Search", False, f"Status: {response.status_code}")
        except Exception as e:
            all_passed &= self.log_test("Motorcycle Search", False, f"Error: {str(e)}")
        
        return all_passed
    
    def test_region_filtering(self):
        """Test region filtering functionality - CRITICAL AREA"""
        print("\n🌍 TESTING REGION FILTERING (CRITICAL)")
        print("=" * 50)
        
        all_passed = True
        regions = ["IN", "US", "JP", "DE", "All"]
        
        for region in regions:
            try:
                # Test stats with region
                response = requests.get(f"{self.base_url}/stats", 
                                      params={"region": region}, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    total_motorcycles = data.get("total_motorcycles", 0)
                    all_passed &= self.log_test(f"Region Stats - {region}", True, 
                        f"{total_motorcycles} motorcycles in {region}")
                else:
                    all_passed &= self.log_test(f"Region Stats - {region}", False, 
                        f"Status: {response.status_code}")
                
                # Test motorcycles with region
                response = requests.get(f"{self.base_url}/motorcycles", 
                                      params={"region": region, "limit": 25}, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, dict) and "motorcycles" in data:
                        motorcycles = data["motorcycles"]
                        pagination = data.get("pagination", {})
                        total_count = pagination.get("total_count", len(motorcycles))
                        all_passed &= self.log_test(f"Region Motorcycles - {region}", True, 
                            f"Retrieved {len(motorcycles)} motorcycles (total: {total_count})")
                    else:
                        all_passed &= self.log_test(f"Region Motorcycles - {region}", False, 
                            "Invalid response format")
                else:
                    all_passed &= self.log_test(f"Region Motorcycles - {region}", False, 
                        f"Status: {response.status_code}")
                
                # Test categories with region
                response = requests.get(f"{self.base_url}/motorcycles/categories/summary", 
                                      params={"region": region}, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        categories_count = len(data)
                        total_motorcycles = sum(cat.get("count", 0) for cat in data)
                        all_passed &= self.log_test(f"Region Categories - {region}", True, 
                            f"{categories_count} categories, {total_motorcycles} total motorcycles")
                    else:
                        all_passed &= self.log_test(f"Region Categories - {region}", False, 
                            "Invalid response format")
                else:
                    all_passed &= self.log_test(f"Region Categories - {region}", False, 
                        f"Status: {response.status_code}")
                        
            except Exception as e:
                all_passed &= self.log_test(f"Region Filtering - {region}", False, f"Error: {str(e)}")
        
        return all_passed
    
    def test_image_loading(self):
        """Test motorcycle image URLs accessibility"""
        print("\n🖼️ TESTING IMAGE LOADING")
        print("=" * 50)
        
        if not self.motorcycle_ids:
            # Get some motorcycles first
            try:
                response = requests.get(f"{self.base_url}/motorcycles", 
                                      params={"limit": 10}, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, dict) and "motorcycles" in data:
                        motorcycles = data["motorcycles"]
                        self.motorcycle_ids = [moto.get("id") for moto in motorcycles[:5] if moto.get("id")]
            except Exception as e:
                return self.log_test("Image Loading Setup", False, f"Error getting motorcycles: {str(e)}")
        
        if not self.motorcycle_ids:
            return self.log_test("Image Loading", False, "No motorcycle IDs available")
        
        all_passed = True
        accessible_images = 0
        total_images = 0
        
        for motorcycle_id in self.motorcycle_ids:
            try:
                # Get motorcycle details
                response = requests.get(f"{self.base_url}/motorcycles/{motorcycle_id}", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    image_url = data.get("image_url")
                    if image_url:
                        total_images += 1
                        # Test image accessibility
                        try:
                            img_response = requests.head(image_url, timeout=5)
                            if img_response.status_code == 200:
                                accessible_images += 1
                                self.log_test(f"Image Access - {data.get('manufacturer', 'Unknown')} {data.get('model', 'Unknown')}", 
                                            True, "Image accessible")
                            else:
                                self.log_test(f"Image Access - {data.get('manufacturer', 'Unknown')} {data.get('model', 'Unknown')}", 
                                            False, f"Image status: {img_response.status_code}")
                                all_passed = False
                        except Exception as e:
                            self.log_test(f"Image Access - {data.get('manufacturer', 'Unknown')} {data.get('model', 'Unknown')}", 
                                        False, f"Image error: {str(e)}")
                            all_passed = False
                    else:
                        self.log_test(f"Image URL - {motorcycle_id[:8]}...", False, "No image URL")
                        all_passed = False
            except Exception as e:
                self.log_test(f"Image Loading - {motorcycle_id[:8]}...", False, f"Error: {str(e)}")
                all_passed = False
        
        if total_images > 0:
            success_rate = (accessible_images / total_images) * 100
            self.log_test("Image Loading Summary", success_rate >= 80, 
                f"{accessible_images}/{total_images} images accessible ({success_rate:.1f}%)")
        
        return all_passed
    
    def test_authentication(self):
        """Test login/register endpoints"""
        print("\n🔐 TESTING AUTHENTICATION")
        print("=" * 50)
        
        all_passed = True
        
        # Test user registration
        try:
            response = requests.post(f"{self.base_url}/auth/register", 
                                   json=self.test_user_data, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "token" in data:
                    self.test_user_token = data["token"]
                    all_passed &= self.log_test("User Registration", True, 
                        f"User registered: {data.get('user', {}).get('name', 'Unknown')}")
                else:
                    all_passed &= self.log_test("User Registration", False, "No token in response")
            elif response.status_code == 400 and "already exists" in response.text:
                # User already exists, try login instead
                all_passed &= self.log_test("User Registration", True, "User already exists (expected)")
            else:
                all_passed &= self.log_test("User Registration", False, 
                    f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            all_passed &= self.log_test("User Registration", False, f"Error: {str(e)}")
        
        # Test user login
        try:
            login_data = {
                "email": self.test_user_data["email"],
                "password": self.test_user_data["password"]
            }
            response = requests.post(f"{self.base_url}/auth/login", 
                                   json=login_data, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "token" in data:
                    self.test_user_token = data["token"]
                    all_passed &= self.log_test("User Login", True, 
                        f"User logged in: {data.get('user', {}).get('name', 'Unknown')}")
                else:
                    all_passed &= self.log_test("User Login", False, "No token in response")
            else:
                all_passed &= self.log_test("User Login", False, 
                    f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            all_passed &= self.log_test("User Login", False, f"Error: {str(e)}")
        
        # Test Google OAuth endpoint
        try:
            google_data = {
                "email": "test.google@bykedream.com",
                "name": "Google Test User",
                "picture": "https://example.com/avatar.jpg",
                "google_id": "google_test_123"
            }
            response = requests.post(f"{self.base_url}/auth/google", 
                                   json=google_data, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "token" in data:
                    all_passed &= self.log_test("Google OAuth", True, 
                        f"Google user authenticated: {data.get('user', {}).get('name', 'Unknown')}")
                else:
                    all_passed &= self.log_test("Google OAuth", False, "No token in response")
            else:
                all_passed &= self.log_test("Google OAuth", False, 
                    f"Status: {response.status_code}")
        except Exception as e:
            all_passed &= self.log_test("Google OAuth", False, f"Error: {str(e)}")
        
        return all_passed
    
    def test_comparison_tool(self):
        """Test motorcycle comparison functionality"""
        print("\n⚖️ TESTING COMPARISON TOOL")
        print("=" * 50)
        
        if not self.motorcycle_ids:
            return self.log_test("Comparison Tool", False, "No motorcycle IDs available")
        
        all_passed = True
        
        # Test single motorcycle comparison
        try:
            response = requests.post(f"{self.base_url}/motorcycles/compare", 
                                   json=[self.motorcycle_ids[0]], timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "motorcycles" in data and len(data["motorcycles"]) == 1:
                    all_passed &= self.log_test("Single Motorcycle Comparison", True, 
                        f"Comparison generated with ID: {data.get('comparison_id', 'Unknown')}")
                else:
                    all_passed &= self.log_test("Single Motorcycle Comparison", False, 
                        "Invalid comparison response")
            else:
                all_passed &= self.log_test("Single Motorcycle Comparison", False, 
                    f"Status: {response.status_code}")
        except Exception as e:
            all_passed &= self.log_test("Single Motorcycle Comparison", False, f"Error: {str(e)}")
        
        # Test multiple motorcycle comparison
        if len(self.motorcycle_ids) >= 2:
            try:
                response = requests.post(f"{self.base_url}/motorcycles/compare", 
                                       json=self.motorcycle_ids[:2], timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if "motorcycles" in data and len(data["motorcycles"]) == 2:
                        all_passed &= self.log_test("Multiple Motorcycle Comparison", True, 
                            f"Compared {len(data['motorcycles'])} motorcycles")
                    else:
                        all_passed &= self.log_test("Multiple Motorcycle Comparison", False, 
                            "Invalid comparison response")
                else:
                    all_passed &= self.log_test("Multiple Motorcycle Comparison", False, 
                        f"Status: {response.status_code}")
            except Exception as e:
                all_passed &= self.log_test("Multiple Motorcycle Comparison", False, f"Error: {str(e)}")
        
        # Test comparison with invalid ID
        try:
            response = requests.post(f"{self.base_url}/motorcycles/compare", 
                                   json=["invalid_id_123"], timeout=10)
            if response.status_code == 404:
                all_passed &= self.log_test("Comparison Error Handling", True, 
                    "Correctly handled invalid motorcycle ID")
            else:
                all_passed &= self.log_test("Comparison Error Handling", False, 
                    f"Expected 404, got {response.status_code}")
        except Exception as e:
            all_passed &= self.log_test("Comparison Error Handling", False, f"Error: {str(e)}")
        
        return all_passed
    
    def test_user_management(self):
        """Test favorites, garage, and user profile features"""
        print("\n👤 TESTING USER MANAGEMENT")
        print("=" * 50)
        
        if not self.test_user_token:
            return self.log_test("User Management", False, "No user token available")
        
        if not self.motorcycle_ids:
            return self.log_test("User Management", False, "No motorcycle IDs available")
        
        all_passed = True
        headers = {"Authorization": f"Bearer {self.test_user_token}"}
        
        # Test add to favorites
        try:
            motorcycle_id = self.motorcycle_ids[0]
            response = requests.post(f"{self.base_url}/motorcycles/{motorcycle_id}/favorite", 
                                   headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get("favorited") is True:
                    all_passed &= self.log_test("Add to Favorites", True, 
                        f"Added motorcycle to favorites")
                else:
                    all_passed &= self.log_test("Add to Favorites", False, 
                        f"Unexpected response: {data}")
            else:
                all_passed &= self.log_test("Add to Favorites", False, 
                    f"Status: {response.status_code}")
        except Exception as e:
            all_passed &= self.log_test("Add to Favorites", False, f"Error: {str(e)}")
        
        # Test get favorites
        try:
            response = requests.get(f"{self.base_url}/motorcycles/favorites", 
                                  headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    all_passed &= self.log_test("Get Favorites", True, 
                        f"Retrieved {len(data)} favorite motorcycles")
                else:
                    all_passed &= self.log_test("Get Favorites", False, 
                        "Invalid response format")
            else:
                all_passed &= self.log_test("Get Favorites", False, 
                    f"Status: {response.status_code}")
        except Exception as e:
            all_passed &= self.log_test("Get Favorites", False, f"Error: {str(e)}")
        
        # Test add to garage
        try:
            garage_data = {
                "motorcycle_id": self.motorcycle_ids[0],
                "status": "owned",
                "purchase_price": 15000,
                "current_mileage": 5000,
                "notes": "Great bike for testing!"
            }
            response = requests.post(f"{self.base_url}/garage", 
                                   headers=headers, json=garage_data, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "message" in data and "added" in data["message"].lower():
                    all_passed &= self.log_test("Add to Garage", True, 
                        f"Added motorcycle to garage")
                else:
                    all_passed &= self.log_test("Add to Garage", False, 
                        f"Unexpected response: {data}")
            else:
                all_passed &= self.log_test("Add to Garage", False, 
                    f"Status: {response.status_code}")
        except Exception as e:
            all_passed &= self.log_test("Add to Garage", False, f"Error: {str(e)}")
        
        # Test get garage
        try:
            response = requests.get(f"{self.base_url}/garage", 
                                  headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and "garage_items" in data:
                    garage_items = data["garage_items"]
                    all_passed &= self.log_test("Get Garage", True, 
                        f"Retrieved {len(garage_items)} garage items")
                else:
                    all_passed &= self.log_test("Get Garage", False, 
                        "Invalid response format")
            else:
                all_passed &= self.log_test("Get Garage", False, 
                    f"Status: {response.status_code}")
        except Exception as e:
            all_passed &= self.log_test("Get Garage", False, f"Error: {str(e)}")
        
        return all_passed
    
    def test_pagination_system(self):
        """Test pagination system implementation"""
        print("\n📄 TESTING PAGINATION SYSTEM")
        print("=" * 50)
        
        all_passed = True
        
        # Test default pagination
        try:
            response = requests.get(f"{self.base_url}/motorcycles", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and "motorcycles" in data and "pagination" in data:
                    motorcycles = data["motorcycles"]
                    pagination = data["pagination"]
                    
                    required_fields = ["page", "limit", "total_count", "total_pages", "has_next", "has_previous"]
                    missing_fields = [field for field in required_fields if field not in pagination]
                    
                    if not missing_fields:
                        all_passed &= self.log_test("Pagination Structure", True, 
                            f"Page {pagination['page']}/{pagination['total_pages']}, {len(motorcycles)} items")
                    else:
                        all_passed &= self.log_test("Pagination Structure", False, 
                            f"Missing fields: {missing_fields}")
                else:
                    all_passed &= self.log_test("Pagination Structure", False, 
                        "Invalid pagination response format")
            else:
                all_passed &= self.log_test("Pagination Structure", False, 
                    f"Status: {response.status_code}")
        except Exception as e:
            all_passed &= self.log_test("Pagination Structure", False, f"Error: {str(e)}")
        
        # Test specific page
        try:
            response = requests.get(f"{self.base_url}/motorcycles", 
                                  params={"page": 2, "limit": 10}, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and "pagination" in data:
                    pagination = data["pagination"]
                    if pagination.get("page") == 2 and pagination.get("limit") == 10:
                        all_passed &= self.log_test("Pagination Navigation", True, 
                            f"Successfully navigated to page 2")
                    else:
                        all_passed &= self.log_test("Pagination Navigation", False, 
                            f"Page/limit mismatch: {pagination}")
                else:
                    all_passed &= self.log_test("Pagination Navigation", False, 
                        "Invalid pagination response")
            else:
                all_passed &= self.log_test("Pagination Navigation", False, 
                    f"Status: {response.status_code}")
        except Exception as e:
            all_passed &= self.log_test("Pagination Navigation", False, f"Error: {str(e)}")
        
        return all_passed
    
    def run_all_tests(self):
        """Run all critical tests"""
        print("🎯 CRITICAL BACKEND API TESTING")
        print("=" * 60)
        print("Testing areas mentioned in review request:")
        print("1. Backend API Testing")
        print("2. Search Functionality") 
        print("3. Region Filtering")
        print("4. Image Loading")
        print("5. Database Connectivity")
        print("6. Authentication")
        print("7. Comparison Tool")
        print("8. User Management")
        print("=" * 60)
        
        # Run all tests
        tests = [
            self.test_database_connectivity,
            self.test_search_functionality,
            self.test_region_filtering,
            self.test_image_loading,
            self.test_authentication,
            self.test_comparison_tool,
            self.test_user_management,
            self.test_pagination_system
        ]
        
        passed = 0
        total = len(tests)
        
        for test in tests:
            if test():
                passed += 1
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 CRITICAL TESTING SUMMARY")
        print("=" * 60)
        
        for result in self.test_results:
            print(result)
        
        print(f"\nTests Passed: {passed}/{total}")
        print(f"Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            print("🎉 ALL CRITICAL TESTS PASSED!")
        else:
            print(f"⚠️  {total-passed} CRITICAL TESTS FAILED")
        
        return passed == total

if __name__ == "__main__":
    tester = CriticalAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)