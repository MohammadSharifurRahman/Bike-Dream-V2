#!/usr/bin/env python3
"""
Backend API Testing for Byke-Dream Motorcycle Database
Tests all motorcycle database functionality including CRUD operations, search, filtering, and seeding.
"""

import requests
import json
import sys
from typing import Dict, List, Any

# Backend URL from environment
BACKEND_URL = "https://520ad038-1a58-4477-a4bd-359442f3f1a5.preview.emergentagent.com/api"

class MotorcycleAPITester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.test_results = []
        self.motorcycle_ids = []
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = f"{status} - {test_name}"
        if details:
            result += f": {details}"
        self.test_results.append(result)
        print(result)
        
    def test_api_root(self):
        """Test basic API connectivity"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if "Welcome to Byke-Dream API" in data.get("message", ""):
                    self.log_test("API Root Connectivity", True, "API is accessible")
                    return True
                else:
                    self.log_test("API Root Connectivity", False, f"Unexpected message: {data}")
                    return False
            else:
                self.log_test("API Root Connectivity", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("API Root Connectivity", False, f"Connection error: {str(e)}")
            return False
    
    def test_seed_database(self):
        """Test POST /api/motorcycles/seed"""
        try:
            response = requests.post(f"{self.base_url}/motorcycles/seed", timeout=15)
            if response.status_code == 200:
                data = response.json()
                if "Successfully seeded" in data.get("message", ""):
                    self.log_test("Database Seeding", True, data["message"])
                    return True
                else:
                    self.log_test("Database Seeding", False, f"Unexpected response: {data}")
                    return False
            else:
                self.log_test("Database Seeding", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Database Seeding", False, f"Error: {str(e)}")
            return False
    
    def test_get_all_motorcycles(self):
        """Test GET /api/motorcycles without filters"""
        try:
            response = requests.get(f"{self.base_url}/motorcycles", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    # Store some motorcycle IDs for individual testing
                    self.motorcycle_ids = [moto.get("id") for moto in data[:3] if moto.get("id")]
                    self.log_test("Get All Motorcycles", True, f"Retrieved {len(data)} motorcycles")
                    
                    # Verify motorcycle structure
                    first_moto = data[0]
                    required_fields = ["id", "manufacturer", "model", "year", "category", "price_usd"]
                    missing_fields = [field for field in required_fields if field not in first_moto]
                    if missing_fields:
                        self.log_test("Motorcycle Data Structure", False, f"Missing fields: {missing_fields}")
                        return False
                    else:
                        self.log_test("Motorcycle Data Structure", True, "All required fields present")
                        return True
                else:
                    self.log_test("Get All Motorcycles", False, "No motorcycles returned or invalid format")
                    return False
            else:
                self.log_test("Get All Motorcycles", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Get All Motorcycles", False, f"Error: {str(e)}")
            return False
    
    def test_search_functionality(self):
        """Test text search functionality"""
        search_tests = [
            ("Harley", "manufacturer search"),
            ("Sport", "category search"),
            ("V-Twin", "engine type search"),
            ("racing", "description search")
        ]
        
        all_passed = True
        for search_term, test_type in search_tests:
            try:
                response = requests.get(f"{self.base_url}/motorcycles", 
                                      params={"search": search_term}, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        self.log_test(f"Search - {test_type} ('{search_term}')", True, 
                                    f"Found {len(data)} results")
                    else:
                        self.log_test(f"Search - {test_type} ('{search_term}')", False, 
                                    "Invalid response format")
                        all_passed = False
                else:
                    self.log_test(f"Search - {test_type} ('{search_term}')", False, 
                                f"Status: {response.status_code}")
                    all_passed = False
            except Exception as e:
                self.log_test(f"Search - {test_type} ('{search_term}')", False, f"Error: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_manufacturer_filter(self):
        """Test manufacturer filtering"""
        manufacturers = ["Yamaha", "Harley-Davidson", "Ducati"]
        all_passed = True
        
        for manufacturer in manufacturers:
            try:
                response = requests.get(f"{self.base_url}/motorcycles", 
                                      params={"manufacturer": manufacturer}, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        # Verify all results match the manufacturer filter
                        valid_results = all(manufacturer.lower() in moto.get("manufacturer", "").lower() 
                                          for moto in data)
                        if valid_results:
                            self.log_test(f"Manufacturer Filter - {manufacturer}", True, 
                                        f"Found {len(data)} matching motorcycles")
                        else:
                            self.log_test(f"Manufacturer Filter - {manufacturer}", False, 
                                        "Some results don't match filter")
                            all_passed = False
                    else:
                        self.log_test(f"Manufacturer Filter - {manufacturer}", False, 
                                    "Invalid response format")
                        all_passed = False
                else:
                    self.log_test(f"Manufacturer Filter - {manufacturer}", False, 
                                f"Status: {response.status_code}")
                    all_passed = False
            except Exception as e:
                self.log_test(f"Manufacturer Filter - {manufacturer}", False, f"Error: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_category_filter(self):
        """Test category filtering"""
        categories = ["Sport", "Cruiser", "Touring"]
        all_passed = True
        
        for category in categories:
            try:
                response = requests.get(f"{self.base_url}/motorcycles", 
                                      params={"category": category}, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        # Verify all results match the category filter
                        valid_results = all(category.lower() in moto.get("category", "").lower() 
                                          for moto in data)
                        if valid_results:
                            self.log_test(f"Category Filter - {category}", True, 
                                        f"Found {len(data)} matching motorcycles")
                        else:
                            self.log_test(f"Category Filter - {category}", False, 
                                        "Some results don't match filter")
                            all_passed = False
                    else:
                        self.log_test(f"Category Filter - {category}", False, 
                                    "Invalid response format")
                        all_passed = False
                else:
                    self.log_test(f"Category Filter - {category}", False, 
                                f"Status: {response.status_code}")
                    all_passed = False
            except Exception as e:
                self.log_test(f"Category Filter - {category}", False, f"Error: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_year_range_filter(self):
        """Test year range filtering"""
        year_tests = [
            (2020, 2024, "Recent models"),
            (1950, 1970, "Vintage models"),
            (2023, None, "2023 and newer")
        ]
        
        all_passed = True
        for year_min, year_max, description in year_tests:
            try:
                params = {"year_min": year_min}
                if year_max:
                    params["year_max"] = year_max
                
                response = requests.get(f"{self.base_url}/motorcycles", 
                                      params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        # Verify all results are within year range
                        valid_results = True
                        for moto in data:
                            year = moto.get("year", 0)
                            if year < year_min or (year_max and year > year_max):
                                valid_results = False
                                break
                        
                        if valid_results:
                            self.log_test(f"Year Range Filter - {description}", True, 
                                        f"Found {len(data)} motorcycles in range")
                        else:
                            self.log_test(f"Year Range Filter - {description}", False, 
                                        "Some results outside year range")
                            all_passed = False
                    else:
                        self.log_test(f"Year Range Filter - {description}", False, 
                                    "Invalid response format")
                        all_passed = False
                else:
                    self.log_test(f"Year Range Filter - {description}", False, 
                                f"Status: {response.status_code}")
                    all_passed = False
            except Exception as e:
                self.log_test(f"Year Range Filter - {description}", False, f"Error: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_price_range_filter(self):
        """Test price range filtering"""
        price_tests = [
            (10000, 30000, "Mid-range bikes"),
            (5000, 15000, "Budget to mid-range"),
            (25000, None, "Premium bikes")
        ]
        
        all_passed = True
        for price_min, price_max, description in price_tests:
            try:
                params = {"price_min": price_min}
                if price_max:
                    params["price_max"] = price_max
                
                response = requests.get(f"{self.base_url}/motorcycles", 
                                      params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        # Verify all results are within price range
                        valid_results = True
                        for moto in data:
                            price = moto.get("price_usd", 0)
                            if price < price_min or (price_max and price > price_max):
                                valid_results = False
                                break
                        
                        if valid_results:
                            self.log_test(f"Price Range Filter - {description}", True, 
                                        f"Found {len(data)} motorcycles in range")
                        else:
                            self.log_test(f"Price Range Filter - {description}", False, 
                                        "Some results outside price range")
                            all_passed = False
                    else:
                        self.log_test(f"Price Range Filter - {description}", False, 
                                    "Invalid response format")
                        all_passed = False
                else:
                    self.log_test(f"Price Range Filter - {description}", False, 
                                f"Status: {response.status_code}")
                    all_passed = False
            except Exception as e:
                self.log_test(f"Price Range Filter - {description}", False, f"Error: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_sorting_functionality(self):
        """Test sorting by different fields"""
        sort_tests = [
            ("year", "desc", "Newest first"),
            ("year", "asc", "Oldest first"),
            ("price", "desc", "Most expensive first"),
            ("price", "asc", "Cheapest first"),
            ("horsepower", "desc", "Most powerful first")
        ]
        
        all_passed = True
        for sort_by, sort_order, description in sort_tests:
            try:
                response = requests.get(f"{self.base_url}/motorcycles", 
                                      params={"sort_by": sort_by, "sort_order": sort_order}, 
                                      timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list) and len(data) > 1:
                        # Verify sorting is correct
                        is_sorted = True
                        for i in range(len(data) - 1):
                            current_val = data[i].get(sort_by, 0)
                            next_val = data[i + 1].get(sort_by, 0)
                            
                            if sort_order == "desc" and current_val < next_val:
                                is_sorted = False
                                break
                            elif sort_order == "asc" and current_val > next_val:
                                is_sorted = False
                                break
                        
                        if is_sorted:
                            self.log_test(f"Sorting - {description}", True, 
                                        f"Correctly sorted {len(data)} results")
                        else:
                            self.log_test(f"Sorting - {description}", False, 
                                        "Results not properly sorted")
                            all_passed = False
                    else:
                        self.log_test(f"Sorting - {description}", False, 
                                    "Insufficient data to verify sorting")
                        all_passed = False
                else:
                    self.log_test(f"Sorting - {description}", False, 
                                f"Status: {response.status_code}")
                    all_passed = False
            except Exception as e:
                self.log_test(f"Sorting - {description}", False, f"Error: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_get_single_motorcycle(self):
        """Test GET /api/motorcycles/{id}"""
        if not self.motorcycle_ids:
            self.log_test("Get Single Motorcycle", False, "No motorcycle IDs available for testing")
            return False
        
        all_passed = True
        for motorcycle_id in self.motorcycle_ids[:2]:  # Test first 2 IDs
            try:
                response = requests.get(f"{self.base_url}/motorcycles/{motorcycle_id}", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, dict) and data.get("id") == motorcycle_id:
                        self.log_test(f"Get Single Motorcycle - ID {motorcycle_id[:8]}...", True, 
                                    f"Retrieved {data.get('manufacturer')} {data.get('model')}")
                    else:
                        self.log_test(f"Get Single Motorcycle - ID {motorcycle_id[:8]}...", False, 
                                    "Invalid response or ID mismatch")
                        all_passed = False
                elif response.status_code == 404:
                    self.log_test(f"Get Single Motorcycle - ID {motorcycle_id[:8]}...", False, 
                                "Motorcycle not found (404)")
                    all_passed = False
                else:
                    self.log_test(f"Get Single Motorcycle - ID {motorcycle_id[:8]}...", False, 
                                f"Status: {response.status_code}")
                    all_passed = False
            except Exception as e:
                self.log_test(f"Get Single Motorcycle - ID {motorcycle_id[:8]}...", False, 
                            f"Error: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_filter_options_api(self):
        """Test GET /api/motorcycles/filters/options"""
        try:
            response = requests.get(f"{self.base_url}/motorcycles/filters/options", timeout=10)
            if response.status_code == 200:
                data = response.json()
                required_keys = ["manufacturers", "categories", "year_range", "price_range"]
                missing_keys = [key for key in required_keys if key not in data]
                
                if missing_keys:
                    self.log_test("Filter Options API", False, f"Missing keys: {missing_keys}")
                    return False
                
                # Verify data structure
                if (isinstance(data["manufacturers"], list) and 
                    isinstance(data["categories"], list) and
                    isinstance(data["year_range"], dict) and
                    isinstance(data["price_range"], dict)):
                    
                    manufacturers_count = len(data["manufacturers"])
                    categories_count = len(data["categories"])
                    self.log_test("Filter Options API", True, 
                                f"Retrieved {manufacturers_count} manufacturers, {categories_count} categories")
                    return True
                else:
                    self.log_test("Filter Options API", False, "Invalid data structure")
                    return False
            else:
                self.log_test("Filter Options API", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Filter Options API", False, f"Error: {str(e)}")
            return False
    
    def test_combined_filters(self):
        """Test multiple filters combined"""
        try:
            params = {
                "manufacturer": "Yamaha",
                "category": "Sport",
                "year_min": 2020,
                "price_max": 20000
            }
            
            response = requests.get(f"{self.base_url}/motorcycles", params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    # Verify all filters are applied correctly
                    valid_results = True
                    for moto in data:
                        if (not ("yamaha" in moto.get("manufacturer", "").lower()) or
                            not ("sport" in moto.get("category", "").lower()) or
                            moto.get("year", 0) < 2020 or
                            moto.get("price_usd", 0) > 20000):
                            valid_results = False
                            break
                    
                    if valid_results:
                        self.log_test("Combined Filters", True, 
                                    f"Found {len(data)} motorcycles matching all criteria")
                        return True
                    else:
                        self.log_test("Combined Filters", False, 
                                    "Some results don't match all filter criteria")
                        return False
                else:
                    self.log_test("Combined Filters", False, "Invalid response format")
                    return False
            else:
                self.log_test("Combined Filters", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Combined Filters", False, f"Error: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🏍️  Starting Byke-Dream Backend API Tests")
        print("=" * 60)
        
        # Test basic connectivity first
        if not self.test_api_root():
            print("❌ API not accessible. Stopping tests.")
            return False
        
        # Seed database
        self.test_seed_database()
        
        # Core functionality tests
        self.test_get_all_motorcycles()
        self.test_search_functionality()
        self.test_manufacturer_filter()
        self.test_category_filter()
        self.test_year_range_filter()
        self.test_price_range_filter()
        self.test_sorting_functionality()
        self.test_get_single_motorcycle()
        self.test_filter_options_api()
        self.test_combined_filters()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed_tests = [result for result in self.test_results if "✅ PASS" in result]
        failed_tests = [result for result in self.test_results if "❌ FAIL" in result]
        
        print(f"Total Tests: {len(self.test_results)}")
        print(f"Passed: {len(passed_tests)}")
        print(f"Failed: {len(failed_tests)}")
        
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  {test}")
        
        success_rate = len(passed_tests) / len(self.test_results) * 100
        print(f"\nSuccess Rate: {success_rate:.1f}%")
        
        return len(failed_tests) == 0

def main():
    """Main test execution"""
    tester = MotorcycleAPITester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests passed! Backend API is working correctly.")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed. Check the details above.")
        sys.exit(1)

if __name__ == "__main__":
    main()