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
BACKEND_URL = "https://0e248d18-d2ce-4948-8791-4e5fc4e5eb4d.preview.emergentagent.com/api"

class MotorcycleAPITester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.test_results = []
        self.motorcycle_ids = []
        self.test_user_session = None
        self.test_user_data = {
            "email": "test.rider@bykedream.com",
            "name": "Test Rider",
            "picture": "https://example.com/avatar.jpg",
            "session_token": "test_session_token_12345"
        }
        
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
                if "Bike-Dream API" in data.get("message", ""):
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
    
    def test_database_stats_api(self):
        """Test GET /api/stats"""
        try:
            response = requests.get(f"{self.base_url}/stats", timeout=10)
            if response.status_code == 200:
                data = response.json()
                required_keys = ["total_motorcycles", "manufacturers", "categories", "year_range", "latest_update"]
                missing_keys = [key for key in required_keys if key not in data]
                
                if missing_keys:
                    self.log_test("Database Stats API", False, f"Missing keys: {missing_keys}")
                    return False
                
                # Verify data structure
                if (isinstance(data["manufacturers"], list) and 
                    isinstance(data["categories"], list) and
                    isinstance(data["year_range"], dict) and
                    isinstance(data["total_motorcycles"], int)):
                    
                    total_count = data["total_motorcycles"]
                    manufacturers_count = len(data["manufacturers"])
                    categories_count = len(data["categories"])
                    self.log_test("Database Stats API", True, 
                                f"Total: {total_count}, Manufacturers: {manufacturers_count}, Categories: {categories_count}")
                    return True
                else:
                    self.log_test("Database Stats API", False, "Invalid data structure")
                    return False
            else:
                self.log_test("Database Stats API", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Database Stats API", False, f"Error: {str(e)}")
            return False
    
    def test_category_summary_api(self):
        """Test GET /api/motorcycles/categories/summary"""
        try:
            response = requests.get(f"{self.base_url}/motorcycles/categories/summary", timeout=10)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    # Verify category structure
                    first_category = data[0]
                    required_keys = ["category", "count", "featured_motorcycles"]
                    missing_keys = [key for key in required_keys if key not in first_category]
                    
                    if missing_keys:
                        self.log_test("Category Summary API", False, f"Missing keys: {missing_keys}")
                        return False
                    
                    # Verify featured motorcycles structure
                    if (isinstance(first_category["featured_motorcycles"], list) and
                        len(first_category["featured_motorcycles"]) > 0):
                        
                        categories_count = len(data)
                        total_featured = sum(len(cat["featured_motorcycles"]) for cat in data)
                        self.log_test("Category Summary API", True, 
                                    f"Retrieved {categories_count} categories with {total_featured} featured motorcycles")
                        return True
                    else:
                        self.log_test("Category Summary API", False, "No featured motorcycles found")
                        return False
                else:
                    self.log_test("Category Summary API", False, "No categories returned or invalid format")
                    return False
            else:
                self.log_test("Category Summary API", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Category Summary API", False, f"Error: {str(e)}")
            return False

    # Daily Update System Tests
    def test_trigger_daily_update(self):
        """Test POST /api/update-system/run-daily-update"""
        try:
            response = requests.post(f"{self.base_url}/update-system/run-daily-update", timeout=30)
            if response.status_code == 200:
                data = response.json()
                required_keys = ["job_id", "status", "message", "check_status_url"]
                missing_keys = [key for key in required_keys if key not in data]
                
                if missing_keys:
                    self.log_test("Daily Update Trigger", False, f"Missing keys: {missing_keys}")
                    return False, None
                
                if data.get("status") == "initiated":
                    job_id = data.get("job_id")
                    self.log_test("Daily Update Trigger", True, 
                                f"Update job initiated with ID: {job_id[:8]}...")
                    return True, job_id
                else:
                    self.log_test("Daily Update Trigger", False, f"Unexpected status: {data.get('status')}")
                    return False, None
            else:
                self.log_test("Daily Update Trigger", False, f"Status: {response.status_code}")
                return False, None
        except Exception as e:
            self.log_test("Daily Update Trigger", False, f"Error: {str(e)}")
            return False, None
    
    def test_job_status_monitoring(self, job_id: str):
        """Test GET /api/update-system/job-status/{job_id}"""
        if not job_id:
            self.log_test("Job Status Monitoring", False, "No job ID provided")
            return False
        
        try:
            # Wait a bit for the job to process
            import time
            time.sleep(3)
            
            response = requests.get(f"{self.base_url}/update-system/job-status/{job_id}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                required_keys = ["job_id", "status", "message", "started_at"]
                missing_keys = [key for key in required_keys if key not in data]
                
                if missing_keys:
                    self.log_test("Job Status Monitoring", False, f"Missing keys: {missing_keys}")
                    return False
                
                if data.get("job_id") == job_id:
                    status = data.get("status")
                    message = data.get("message", "")
                    self.log_test("Job Status Monitoring", True, 
                                f"Job status: {status} - {message}")
                    return True
                else:
                    self.log_test("Job Status Monitoring", False, "Job ID mismatch")
                    return False
            elif response.status_code == 404:
                self.log_test("Job Status Monitoring", False, "Job not found (404)")
                return False
            else:
                self.log_test("Job Status Monitoring", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Job Status Monitoring", False, f"Error: {str(e)}")
            return False
    
    def test_update_history(self):
        """Test GET /api/update-system/update-history"""
        try:
            response = requests.get(f"{self.base_url}/update-system/update-history", timeout=10)
            if response.status_code == 200:
                data = response.json()
                required_keys = ["update_history", "count"]
                missing_keys = [key for key in required_keys if key not in data]
                
                if missing_keys:
                    self.log_test("Update History API", False, f"Missing keys: {missing_keys}")
                    return False
                
                if isinstance(data["update_history"], list) and isinstance(data["count"], int):
                    history_count = data["count"]
                    self.log_test("Update History API", True, 
                                f"Retrieved {history_count} update history records")
                    return True
                else:
                    self.log_test("Update History API", False, "Invalid data structure")
                    return False
            else:
                self.log_test("Update History API", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Update History API", False, f"Error: {str(e)}")
            return False
    
    def test_regional_customizations(self):
        """Test GET /api/update-system/regional-customizations"""
        try:
            # Test without region filter
            response = requests.get(f"{self.base_url}/update-system/regional-customizations", timeout=10)
            if response.status_code == 200:
                data = response.json()
                required_keys = ["customizations", "available_regions"]
                missing_keys = [key for key in required_keys if key not in data]
                
                if missing_keys:
                    self.log_test("Regional Customizations API", False, f"Missing keys: {missing_keys}")
                    return False
                
                if (isinstance(data["customizations"], list) and 
                    isinstance(data["available_regions"], list)):
                    
                    customizations_count = len(data["customizations"])
                    regions_count = len(data["available_regions"])
                    self.log_test("Regional Customizations API", True, 
                                f"Retrieved {customizations_count} customizations for {regions_count} regions")
                    
                    # Test with specific region filter if regions are available
                    if data["available_regions"]:
                        test_region = data["available_regions"][0]
                        return self._test_regional_filter(test_region)
                    return True
                else:
                    self.log_test("Regional Customizations API", False, "Invalid data structure")
                    return False
            else:
                self.log_test("Regional Customizations API", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Regional Customizations API", False, f"Error: {str(e)}")
            return False
    
    def _test_regional_filter(self, region: str):
        """Test regional customizations with specific region filter"""
        try:
            response = requests.get(f"{self.base_url}/update-system/regional-customizations", 
                                  params={"region": region}, timeout=10)
            if response.status_code == 200:
                data = response.json()
                # Verify all customizations are for the specified region
                region_specific = all(
                    custom.get("region") == region 
                    for custom in data.get("customizations", [])
                    if custom.get("region")
                )
                
                if region_specific or len(data.get("customizations", [])) == 0:
                    self.log_test(f"Regional Filter - {region}", True, 
                                f"Found {len(data.get('customizations', []))} customizations for {region}")
                    return True
                else:
                    self.log_test(f"Regional Filter - {region}", False, 
                                "Some customizations don't match region filter")
                    return False
            else:
                self.log_test(f"Regional Filter - {region}", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test(f"Regional Filter - {region}", False, f"Error: {str(e)}")
            return False

    # NEW USER INTERACTION API TESTS
    def test_user_authentication(self):
        """Test POST /api/auth/profile - User authentication with Emergent session data"""
        try:
            response = requests.post(f"{self.base_url}/auth/profile", 
                                   json=self.test_user_data, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if (data.get("message") == "Authentication successful" and 
                    "user" in data and 
                    data["user"].get("email") == self.test_user_data["email"]):
                    
                    self.test_user_session = self.test_user_data["session_token"]
                    self.log_test("User Authentication", True, 
                                f"User authenticated: {data['user']['name']}")
                    return True
                else:
                    self.log_test("User Authentication", False, f"Unexpected response: {data}")
                    return False
            else:
                self.log_test("User Authentication", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("User Authentication", False, f"Error: {str(e)}")
            return False

    def test_get_current_user(self):
        """Test GET /api/auth/me - Get current user information"""
        if not self.test_user_session:
            self.log_test("Get Current User", False, "No user session available")
            return False
        
        try:
            headers = {"X-Session-Id": self.test_user_session}
            response = requests.get(f"{self.base_url}/auth/me", headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if (data.get("email") == self.test_user_data["email"] and
                    data.get("name") == self.test_user_data["name"]):
                    
                    self.log_test("Get Current User", True, 
                                f"Retrieved user info: {data['name']} ({data['email']})")
                    return True
                else:
                    self.log_test("Get Current User", False, f"User data mismatch: {data}")
                    return False
            elif response.status_code == 401:
                self.log_test("Get Current User", False, "Authentication required (401)")
                return False
            else:
                self.log_test("Get Current User", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Get Current User", False, f"Error: {str(e)}")
            return False

    def test_add_to_favorites(self):
        """Test POST /api/motorcycles/{motorcycle_id}/favorite - Add to favorites"""
        if not self.test_user_session or not self.motorcycle_ids:
            self.log_test("Add to Favorites", False, "No user session or motorcycle IDs available")
            return False
        
        try:
            motorcycle_id = self.motorcycle_ids[0]
            headers = {"X-Session-Id": self.test_user_session}
            response = requests.post(f"{self.base_url}/motorcycles/{motorcycle_id}/favorite", 
                                   headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("favorited") is True:
                    self.log_test("Add to Favorites", True, 
                                f"Added motorcycle {motorcycle_id[:8]}... to favorites")
                    return True
                else:
                    self.log_test("Add to Favorites", False, f"Unexpected response: {data}")
                    return False
            elif response.status_code == 401:
                self.log_test("Add to Favorites", False, "Authentication required (401)")
                return False
            elif response.status_code == 404:
                self.log_test("Add to Favorites", False, "Motorcycle not found (404)")
                return False
            else:
                self.log_test("Add to Favorites", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Add to Favorites", False, f"Error: {str(e)}")
            return False

    def test_get_favorite_motorcycles(self):
        """Test GET /api/motorcycles/favorites - Get user's favorite motorcycles"""
        if not self.test_user_session:
            self.log_test("Get Favorite Motorcycles", False, "No user session available")
            return False
        
        try:
            headers = {"X-Session-Id": self.test_user_session}
            response = requests.get(f"{self.base_url}/motorcycles/favorites", 
                                  headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Get Favorite Motorcycles", True, 
                                f"Retrieved {len(data)} favorite motorcycles")
                    return True
                else:
                    self.log_test("Get Favorite Motorcycles", False, "Invalid response format")
                    return False
            elif response.status_code == 401:
                self.log_test("Get Favorite Motorcycles", False, "Authentication required (401)")
                return False
            else:
                self.log_test("Get Favorite Motorcycles", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Get Favorite Motorcycles", False, f"Error: {str(e)}")
            return False

    def test_remove_from_favorites(self):
        """Test DELETE /api/motorcycles/{motorcycle_id}/favorite - Remove from favorites"""
        if not self.test_user_session or not self.motorcycle_ids:
            self.log_test("Remove from Favorites", False, "No user session or motorcycle IDs available")
            return False
        
        try:
            motorcycle_id = self.motorcycle_ids[0]
            headers = {"X-Session-Id": self.test_user_session}
            response = requests.delete(f"{self.base_url}/motorcycles/{motorcycle_id}/favorite", 
                                     headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("favorited") is False:
                    self.log_test("Remove from Favorites", True, 
                                f"Removed motorcycle {motorcycle_id[:8]}... from favorites")
                    return True
                else:
                    self.log_test("Remove from Favorites", False, f"Unexpected response: {data}")
                    return False
            elif response.status_code == 401:
                self.log_test("Remove from Favorites", False, "Authentication required (401)")
                return False
            else:
                self.log_test("Remove from Favorites", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Remove from Favorites", False, f"Error: {str(e)}")
            return False

    def test_rate_motorcycle(self):
        """Test POST /api/motorcycles/{motorcycle_id}/rate - Rate a motorcycle with review"""
        if not self.test_user_session or not self.motorcycle_ids:
            self.log_test("Rate Motorcycle", False, "No user session or motorcycle IDs available")
            return False
        
        try:
            motorcycle_id = self.motorcycle_ids[0]
            headers = {"X-Session-Id": self.test_user_session}
            rating_data = {
                "motorcycle_id": motorcycle_id,
                "rating": 5,
                "review_text": "Amazing bike! Love the performance and design."
            }
            
            response = requests.post(f"{self.base_url}/motorcycles/{motorcycle_id}/rate", 
                                   headers=headers, json=rating_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "Rating" in data.get("message", ""):
                    self.log_test("Rate Motorcycle", True, 
                                f"Successfully rated motorcycle: {data['message']}")
                    return True
                else:
                    self.log_test("Rate Motorcycle", False, f"Unexpected response: {data}")
                    return False
            elif response.status_code == 401:
                self.log_test("Rate Motorcycle", False, "Authentication required (401)")
                return False
            elif response.status_code == 404:
                self.log_test("Rate Motorcycle", False, "Motorcycle not found (404)")
                return False
            else:
                self.log_test("Rate Motorcycle", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Rate Motorcycle", False, f"Error: {str(e)}")
            return False

    def test_get_motorcycle_ratings(self):
        """Test GET /api/motorcycles/{motorcycle_id}/ratings - Get motorcycle ratings"""
        if not self.motorcycle_ids:
            self.log_test("Get Motorcycle Ratings", False, "No motorcycle IDs available")
            return False
        
        try:
            motorcycle_id = self.motorcycle_ids[0]
            response = requests.get(f"{self.base_url}/motorcycles/{motorcycle_id}/ratings", 
                                  timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Get Motorcycle Ratings", True, 
                                f"Retrieved {len(data)} ratings for motorcycle")
                    return True
                else:
                    self.log_test("Get Motorcycle Ratings", False, "Invalid response format")
                    return False
            else:
                self.log_test("Get Motorcycle Ratings", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Get Motorcycle Ratings", False, f"Error: {str(e)}")
            return False

    def test_add_comment(self):
        """Test POST /api/motorcycles/{motorcycle_id}/comment - Add comment to motorcycle"""
        if not self.test_user_session or not self.motorcycle_ids:
            self.log_test("Add Comment", False, "No user session or motorcycle IDs available")
            return False
        
        try:
            motorcycle_id = self.motorcycle_ids[0]
            headers = {"X-Session-Id": self.test_user_session}
            comment_data = {
                "motorcycle_id": motorcycle_id,
                "comment_text": "This is a fantastic motorcycle! I've been riding it for months and it never disappoints."
            }
            
            response = requests.post(f"{self.base_url}/motorcycles/{motorcycle_id}/comment", 
                                   headers=headers, json=comment_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("message") == "Comment added" and "comment_id" in data:
                    self.comment_id = data["comment_id"]  # Store for like test
                    self.log_test("Add Comment", True, 
                                f"Comment added with ID: {data['comment_id'][:8]}...")
                    return True
                else:
                    self.log_test("Add Comment", False, f"Unexpected response: {data}")
                    return False
            elif response.status_code == 401:
                self.log_test("Add Comment", False, "Authentication required (401)")
                return False
            elif response.status_code == 404:
                self.log_test("Add Comment", False, "Motorcycle not found (404)")
                return False
            else:
                self.log_test("Add Comment", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Add Comment", False, f"Error: {str(e)}")
            return False

    def test_get_motorcycle_comments(self):
        """Test GET /api/motorcycles/{motorcycle_id}/comments - Get motorcycle comments"""
        if not self.motorcycle_ids:
            self.log_test("Get Motorcycle Comments", False, "No motorcycle IDs available")
            return False
        
        try:
            motorcycle_id = self.motorcycle_ids[0]
            response = requests.get(f"{self.base_url}/motorcycles/{motorcycle_id}/comments", 
                                  timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    self.log_test("Get Motorcycle Comments", True, 
                                f"Retrieved {len(data)} comments for motorcycle")
                    return True
                else:
                    self.log_test("Get Motorcycle Comments", False, "Invalid response format")
                    return False
            else:
                self.log_test("Get Motorcycle Comments", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Get Motorcycle Comments", False, f"Error: {str(e)}")
            return False

    def test_like_comment(self):
        """Test POST /comments/{comment_id}/like - Like/unlike comments"""
        if not self.test_user_session or not hasattr(self, 'comment_id'):
            self.log_test("Like Comment", False, "No user session or comment ID available")
            return False
        
        try:
            headers = {"X-Session-Id": self.test_user_session}
            response = requests.post(f"{self.base_url}/comments/{self.comment_id}/like", 
                                   headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "liked" in data:
                    action = "liked" if data["liked"] else "unliked"
                    self.log_test("Like Comment", True, 
                                f"Comment {action}: {data['message']}")
                    return True
                else:
                    self.log_test("Like Comment", False, f"Unexpected response: {data}")
                    return False
            elif response.status_code == 401:
                self.log_test("Like Comment", False, "Authentication required (401)")
                return False
            else:
                self.log_test("Like Comment", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Like Comment", False, f"Error: {str(e)}")
            return False

    def test_browse_limit_fix(self):
        """Test GET /api/motorcycles with limit=3000 - Verify all motorcycles are returned"""
        try:
            response = requests.get(f"{self.base_url}/motorcycles", 
                                  params={"limit": 3000}, timeout=15)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    total_count = len(data)
                    if total_count >= 1307:  # Should return 1307+ motorcycles
                        self.log_test("Browse Limit Fix", True, 
                                    f"Successfully retrieved {total_count} motorcycles (exceeds 1307+ requirement)")
                        return True
                    else:
                        self.log_test("Browse Limit Fix", False, 
                                    f"Only retrieved {total_count} motorcycles, expected 1307+")
                        return False
                else:
                    self.log_test("Browse Limit Fix", False, "Invalid response format")
                    return False
            else:
                self.log_test("Browse Limit Fix", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Browse Limit Fix", False, f"Error: {str(e)}")
            return False

    # NEW TESTS FOR TECHNICAL FEATURES DATABASE ENHANCEMENT
    def test_technical_features_database_enhancement(self):
        """Test that all motorcycles have complete technical features and use 'specialisations' field"""
        try:
            response = requests.get(f"{self.base_url}/motorcycles", 
                                  params={"limit": 50}, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    # Check technical features on first few motorcycles
                    technical_features = [
                        "mileage_kmpl", "transmission_type", "number_of_gears", 
                        "ground_clearance_mm", "seat_height_mm", "abs_available",
                        "braking_system", "suspension_type", "tyre_type", 
                        "wheel_size_inches", "headlight_type", "fuel_type"
                    ]
                    
                    all_features_present = True
                    specialisations_consistent = True
                    
                    for i, moto in enumerate(data[:10]):  # Check first 10 motorcycles
                        # Check technical features
                        missing_features = [feature for feature in technical_features if feature not in moto]
                        if missing_features:
                            self.log_test("Technical Features - Complete Data", False, 
                                        f"Motorcycle {i+1} missing features: {missing_features}")
                            all_features_present = False
                            break
                        
                        # Check specialisations field (not features)
                        if "specialisations" not in moto:
                            self.log_test("Technical Features - Specialisations Field", False, 
                                        f"Motorcycle {i+1} missing 'specialisations' field")
                            specialisations_consistent = False
                            break
                        
                        # Check that old 'features' field is not present
                        if "features" in moto:
                            self.log_test("Technical Features - Field Consistency", False, 
                                        f"Motorcycle {i+1} still has old 'features' field")
                            specialisations_consistent = False
                            break
                    
                    if all_features_present:
                        self.log_test("Technical Features - Complete Data", True, 
                                    "All motorcycles have complete technical features")
                    
                    if specialisations_consistent:
                        self.log_test("Technical Features - Specialisations Field", True, 
                                    "All motorcycles use 'specialisations' field consistently")
                    
                    return all_features_present and specialisations_consistent
                else:
                    self.log_test("Technical Features Database Enhancement", False, 
                                "No motorcycles returned or invalid format")
                    return False
            else:
                self.log_test("Technical Features Database Enhancement", False, 
                            f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Technical Features Database Enhancement", False, f"Error: {str(e)}")
            return False

    def test_suzuki_ducati_technical_data(self):
        """Test that Suzuki and Ducati motorcycles have complete technical data"""
        manufacturers = ["Suzuki", "Ducati"]
        all_passed = True
        
        for manufacturer in manufacturers:
            try:
                response = requests.get(f"{self.base_url}/motorcycles", 
                                      params={"manufacturer": manufacturer, "limit": 10}, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list) and len(data) > 0:
                        # Check first motorcycle from this manufacturer
                        moto = data[0]
                        technical_features = [
                            "mileage_kmpl", "transmission_type", "number_of_gears", 
                            "ground_clearance_mm", "seat_height_mm", "abs_available",
                            "braking_system", "suspension_type", "tyre_type", 
                            "wheel_size_inches", "headlight_type", "fuel_type"
                        ]
                        
                        missing_features = [feature for feature in technical_features if feature not in moto]
                        if missing_features:
                            self.log_test(f"Technical Data - {manufacturer}", False, 
                                        f"Missing features: {missing_features}")
                            all_passed = False
                        else:
                            self.log_test(f"Technical Data - {manufacturer}", True, 
                                        f"Complete technical data present")
                    else:
                        self.log_test(f"Technical Data - {manufacturer}", False, 
                                    f"No {manufacturer} motorcycles found")
                        all_passed = False
                else:
                    self.log_test(f"Technical Data - {manufacturer}", False, 
                                f"Status: {response.status_code}")
                    all_passed = False
            except Exception as e:
                self.log_test(f"Technical Data - {manufacturer}", False, f"Error: {str(e)}")
                all_passed = False
        
        return all_passed

    def test_technical_features_filtering(self):
        """Test filtering by technical features"""
        filter_tests = [
            ("transmission_type", "Manual", "Manual transmission filter"),
            ("braking_system", "Disc", "Disc braking system filter"),
            ("fuel_type", "Petrol", "Petrol fuel type filter"),
            ("abs_available", True, "ABS available filter")
        ]
        
        all_passed = True
        for filter_field, filter_value, description in filter_tests:
            try:
                params = {filter_field: filter_value, "limit": 20}
                response = requests.get(f"{self.base_url}/motorcycles", 
                                      params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        # Verify all results match the filter
                        valid_results = True
                        for moto in data:
                            if filter_field == "abs_available":
                                if moto.get(filter_field) != filter_value:
                                    valid_results = False
                                    break
                            else:
                                if filter_value.lower() not in str(moto.get(filter_field, "")).lower():
                                    valid_results = False
                                    break
                        
                        if valid_results:
                            self.log_test(f"Technical Filter - {description}", True, 
                                        f"Found {len(data)} matching motorcycles")
                        else:
                            self.log_test(f"Technical Filter - {description}", False, 
                                        "Some results don't match filter")
                            all_passed = False
                    else:
                        self.log_test(f"Technical Filter - {description}", False, 
                                    "Invalid response format")
                        all_passed = False
                else:
                    self.log_test(f"Technical Filter - {description}", False, 
                                f"Status: {response.status_code}")
                    all_passed = False
            except Exception as e:
                self.log_test(f"Technical Filter - {description}", False, f"Error: {str(e)}")
                all_passed = False
        
        return all_passed

    def test_numeric_range_filtering(self):
        """Test numeric range filtering for technical features"""
        range_tests = [
            ("mileage_min", "mileage_max", 20, 40, "mileage_kmpl", "Mileage range filter"),
            ("ground_clearance_min", "ground_clearance_max", 150, 200, "ground_clearance_mm", "Ground clearance range filter"),
            ("seat_height_min", "seat_height_max", 750, 850, "seat_height_mm", "Seat height range filter")
        ]
        
        all_passed = True
        for min_param, max_param, min_val, max_val, field_name, description in range_tests:
            try:
                params = {min_param: min_val, max_param: max_val, "limit": 20}
                response = requests.get(f"{self.base_url}/motorcycles", 
                                      params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        # Verify all results are within range
                        valid_results = True
                        for moto in data:
                            value = moto.get(field_name, 0)
                            if value < min_val or value > max_val:
                                valid_results = False
                                break
                        
                        if valid_results:
                            self.log_test(f"Numeric Range - {description}", True, 
                                        f"Found {len(data)} motorcycles in range")
                        else:
                            self.log_test(f"Numeric Range - {description}", False, 
                                        "Some results outside range")
                            all_passed = False
                    else:
                        self.log_test(f"Numeric Range - {description}", False, 
                                    "Invalid response format")
                        all_passed = False
                else:
                    self.log_test(f"Numeric Range - {description}", False, 
                                f"Status: {response.status_code}")
                    all_passed = False
            except Exception as e:
                self.log_test(f"Numeric Range - {description}", False, f"Error: {str(e)}")
                all_passed = False
        
        return all_passed

    # NEW TESTS FOR DUAL-LEVEL SORTING IMPLEMENTATION
    def test_dual_level_sorting_default(self):
        """Test dual-level sorting: year descending (new to old), then price ascending (low to high)"""
        try:
            response = requests.get(f"{self.base_url}/motorcycles", 
                                  params={"sort_by": "default", "limit": 50}, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 10:
                    # Verify dual-level sorting
                    is_sorted = True
                    for i in range(len(data) - 1):
                        current_year = data[i].get("year", 0)
                        next_year = data[i + 1].get("year", 0)
                        current_price = data[i].get("price_usd", 0)
                        next_price = data[i + 1].get("price_usd", 0)
                        
                        # Primary sort: year descending (newer first)
                        if current_year < next_year:
                            is_sorted = False
                            break
                        # Secondary sort: within same year, price ascending (lower first)
                        elif current_year == next_year and current_price > next_price:
                            is_sorted = False
                            break
                    
                    if is_sorted:
                        self.log_test("Dual-Level Sorting - Default", True, 
                                    f"Correctly sorted {len(data)} motorcycles by year desc, then price asc")
                        return True
                    else:
                        self.log_test("Dual-Level Sorting - Default", False, 
                                    "Results not properly sorted by dual-level criteria")
                        return False
                else:
                    self.log_test("Dual-Level Sorting - Default", False, 
                                "Insufficient data to verify sorting")
                    return False
            else:
                self.log_test("Dual-Level Sorting - Default", False, 
                            f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Dual-Level Sorting - Default", False, f"Error: {str(e)}")
            return False

    def test_compare_default_vs_single_field_sorting(self):
        """Compare default dual-level sorting vs single-field sorting"""
        try:
            # Get default sorting
            response_default = requests.get(f"{self.base_url}/motorcycles", 
                                          params={"sort_by": "default", "limit": 20}, timeout=10)
            
            # Get single-field year sorting
            response_year = requests.get(f"{self.base_url}/motorcycles", 
                                       params={"sort_by": "year", "sort_order": "desc", "limit": 20}, timeout=10)
            
            # Get single-field price sorting
            response_price = requests.get(f"{self.base_url}/motorcycles", 
                                        params={"sort_by": "price_usd", "sort_order": "asc", "limit": 20}, timeout=10)
            
            if (response_default.status_code == 200 and 
                response_year.status_code == 200 and 
                response_price.status_code == 200):
                
                data_default = response_default.json()
                data_year = response_year.json()
                data_price = response_price.json()
                
                if (isinstance(data_default, list) and 
                    isinstance(data_year, list) and 
                    isinstance(data_price, list)):
                    
                    # Verify that default sorting is different from single-field sorting
                    default_different_from_year = data_default != data_year
                    default_different_from_price = data_default != data_price
                    
                    if default_different_from_year and default_different_from_price:
                        self.log_test("Sorting Comparison - Default vs Single-Field", True, 
                                    "Default dual-level sorting produces different results than single-field sorting")
                        return True
                    else:
                        self.log_test("Sorting Comparison - Default vs Single-Field", False, 
                                    "Default sorting appears identical to single-field sorting")
                        return False
                else:
                    self.log_test("Sorting Comparison - Default vs Single-Field", False, 
                                "Invalid response format")
                    return False
            else:
                self.log_test("Sorting Comparison - Default vs Single-Field", False, 
                            "One or more sorting requests failed")
                return False
        except Exception as e:
            self.log_test("Sorting Comparison - Default vs Single-Field", False, f"Error: {str(e)}")
            return False

    def test_database_count_verification(self):
        """Verify total motorcycle count remains consistent (1307+ motorcycles)"""
        try:
            response = requests.get(f"{self.base_url}/stats", timeout=10)
            if response.status_code == 200:
                data = response.json()
                total_motorcycles = data.get("total_motorcycles", 0)
                
                if total_motorcycles >= 1307:
                    self.log_test("Database Count Verification", True, 
                                f"Database contains {total_motorcycles} motorcycles (exceeds 1307+ requirement)")
                    return True
                else:
                    self.log_test("Database Count Verification", False, 
                                f"Database only contains {total_motorcycles} motorcycles, expected 1307+")
                    return False
            else:
                self.log_test("Database Count Verification", False, 
                            f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Database Count Verification", False, f"Error: {str(e)}")
            return False

    def test_manufacturer_counts_verification(self):
        """Verify manufacturer counts (Yamaha, Honda, Kawasaki, Suzuki, Ducati)"""
        expected_manufacturers = ["Yamaha", "Honda", "Kawasaki", "Suzuki", "Ducati"]
        all_passed = True
        
        for manufacturer in expected_manufacturers:
            try:
                response = requests.get(f"{self.base_url}/motorcycles", 
                                      params={"manufacturer": manufacturer, "limit": 1000}, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, list):
                        count = len(data)
                        if count > 0:
                            self.log_test(f"Manufacturer Count - {manufacturer}", True, 
                                        f"Found {count} {manufacturer} motorcycles")
                        else:
                            self.log_test(f"Manufacturer Count - {manufacturer}", False, 
                                        f"No {manufacturer} motorcycles found")
                            all_passed = False
                    else:
                        self.log_test(f"Manufacturer Count - {manufacturer}", False, 
                                    "Invalid response format")
                        all_passed = False
                else:
                    self.log_test(f"Manufacturer Count - {manufacturer}", False, 
                                f"Status: {response.status_code}")
                    all_passed = False
            except Exception as e:
                self.log_test(f"Manufacturer Count - {manufacturer}", False, f"Error: {str(e)}")
                all_passed = False
        
        return all_passed

    # NEW AUTHENTICATION SYSTEM TESTS
    def test_email_password_registration(self):
        """Test POST /api/auth/register with valid email/password/name"""
        try:
            import time
            registration_data = {
                "email": f"test.rider.{int(time.time())}@bikedream.com",
                "password": "SecurePassword123!",
                "name": "Test Rider"
            }
            
            response = requests.post(f"{self.base_url}/auth/register", 
                                   json=registration_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if (data.get("message") == "Registration successful" and 
                    "token" in data and "user" in data):
                    
                    # Store token for further tests
                    self.jwt_token = data["token"]
                    self.registered_user = data["user"]
                    self.log_test("Email/Password Registration", True, 
                                f"User registered: {data['user']['name']}")
                    return True
                else:
                    self.log_test("Email/Password Registration", False, f"Unexpected response: {data}")
                    return False
            elif response.status_code == 400:
                # User might already exist, try with different email
                registration_data["email"] = f"test.rider.{int(time.time())}.{int(time.time() % 1000)}@bikedream.com"
                response = requests.post(f"{self.base_url}/auth/register", 
                                       json=registration_data, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    self.jwt_token = data["token"]
                    self.registered_user = data["user"]
                    self.log_test("Email/Password Registration", True, 
                                f"User registered with unique email: {data['user']['name']}")
                    return True
                else:
                    self.log_test("Email/Password Registration", False, 
                                f"Registration failed even with unique email: {response.text}")
                    return False
            else:
                self.log_test("Email/Password Registration", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Email/Password Registration", False, f"Error: {str(e)}")
            return False

    def test_email_password_login(self):
        """Test POST /api/auth/login with valid credentials"""
        if not hasattr(self, 'registered_user'):
            self.log_test("Email/Password Login", False, "No registered user available for login test")
            return False
        
        try:
            login_data = {
                "email": self.registered_user["email"],
                "password": "SecurePassword123!"
            }
            
            response = requests.post(f"{self.base_url}/auth/login", 
                                   json=login_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if (data.get("message") == "Login successful" and 
                    "token" in data and "user" in data):
                    
                    self.jwt_token = data["token"]  # Update token
                    self.log_test("Email/Password Login", True, 
                                f"User logged in: {data['user']['name']}")
                    return True
                else:
                    self.log_test("Email/Password Login", False, f"Unexpected response: {data}")
                    return False
            elif response.status_code == 401:
                self.log_test("Email/Password Login", False, "Invalid credentials (401)")
                return False
            else:
                self.log_test("Email/Password Login", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Email/Password Login", False, f"Error: {str(e)}")
            return False

    def test_google_oauth(self):
        """Test POST /api/auth/google with sample Google user data"""
        try:
            import time
            google_data = {
                "email": f"google.user.{int(time.time())}@gmail.com",
                "name": "Google Test User",
                "picture": "https://lh3.googleusercontent.com/a/default-user",
                "google_id": f"google_id_{int(time.time())}"
            }
            
            response = requests.post(f"{self.base_url}/auth/google", 
                                   json=google_data, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if (data.get("message") == "Google authentication successful" and 
                    "token" in data and "user" in data):
                    
                    self.google_jwt_token = data["token"]
                    self.google_user = data["user"]
                    self.log_test("Google OAuth Authentication", True, 
                                f"Google user authenticated: {data['user']['name']}")
                    return True
                else:
                    self.log_test("Google OAuth Authentication", False, f"Unexpected response: {data}")
                    return False
            else:
                self.log_test("Google OAuth Authentication", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Google OAuth Authentication", False, f"Error: {str(e)}")
            return False

    def test_jwt_token_validation(self):
        """Test JWT token validation by accessing protected endpoints with Authorization header"""
        if not hasattr(self, 'jwt_token'):
            self.log_test("JWT Token Validation", False, "No JWT token available for testing")
            return False
        
        try:
            headers = {"Authorization": f"Bearer {self.jwt_token}"}
            response = requests.get(f"{self.base_url}/auth/me", headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if "email" in data and "name" in data:
                    self.log_test("JWT Token Validation", True, 
                                f"JWT token valid, retrieved user: {data['name']}")
                    return True
                else:
                    self.log_test("JWT Token Validation", False, f"Invalid user data: {data}")
                    return False
            elif response.status_code == 401:
                self.log_test("JWT Token Validation", False, "JWT token invalid or expired (401)")
                return False
            else:
                self.log_test("JWT Token Validation", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("JWT Token Validation", False, f"Error: {str(e)}")
            return False

    def test_session_based_authentication(self):
        """Test session-based authentication (legacy support) with X-Session-ID header"""
        try:
            import time
            # First authenticate with Emergent session data
            session_data = {
                "email": f"session.user.{int(time.time())}@bikedream.com",
                "name": "Session Test User",
                "picture": "https://example.com/session-avatar.jpg",
                "session_token": f"session_token_{int(time.time())}"
            }
            
            response = requests.post(f"{self.base_url}/auth/profile", 
                                   json=session_data, timeout=10)
            
            if response.status_code == 200:
                # Now test accessing protected endpoint with session ID
                headers = {"X-Session-Id": session_data["session_token"]}
                response = requests.get(f"{self.base_url}/auth/me", headers=headers, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("email") == session_data["email"]:
                        self.log_test("Session-Based Authentication", True, 
                                    f"Session authentication working: {data['name']}")
                        return True
                    else:
                        self.log_test("Session-Based Authentication", False, 
                                    f"User data mismatch: {data}")
                        return False
                else:
                    self.log_test("Session-Based Authentication", False, 
                                f"Session validation failed: {response.status_code}")
                    return False
            else:
                self.log_test("Session-Based Authentication", False, 
                            f"Session creation failed: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Session-Based Authentication", False, f"Error: {str(e)}")
            return False

    def test_invalid_credentials_handling(self):
        """Test invalid credentials and error handling for all auth endpoints"""
        tests_passed = 0
        total_tests = 0
        
        # Test invalid registration
        try:
            total_tests += 1
            invalid_registration = {
                "email": "invalid-email",  # Invalid email format
                "password": "123",  # Too short password
                "name": ""  # Empty name
            }
            response = requests.post(f"{self.base_url}/auth/register", 
                                   json=invalid_registration, timeout=10)
            if response.status_code == 400:
                tests_passed += 1
                self.log_test("Invalid Registration Handling", True, "Properly rejected invalid registration")
            else:
                self.log_test("Invalid Registration Handling", False, 
                            f"Should reject invalid registration, got: {response.status_code}")
        except Exception as e:
            self.log_test("Invalid Registration Handling", False, f"Error: {str(e)}")
        
        # Test invalid login
        try:
            total_tests += 1
            invalid_login = {
                "email": "nonexistent@example.com",
                "password": "wrongpassword"
            }
            response = requests.post(f"{self.base_url}/auth/login", 
                                   json=invalid_login, timeout=10)
            if response.status_code == 401:
                tests_passed += 1
                self.log_test("Invalid Login Handling", True, "Properly rejected invalid login")
            else:
                self.log_test("Invalid Login Handling", False, 
                            f"Should reject invalid login, got: {response.status_code}")
        except Exception as e:
            self.log_test("Invalid Login Handling", False, f"Error: {str(e)}")
        
        # Test accessing protected endpoint without auth
        try:
            total_tests += 1
            response = requests.get(f"{self.base_url}/auth/me", timeout=10)
            if response.status_code == 401:
                tests_passed += 1
                self.log_test("Unauthorized Access Handling", True, "Properly rejected unauthorized access")
            else:
                self.log_test("Unauthorized Access Handling", False, 
                            f"Should reject unauthorized access, got: {response.status_code}")
        except Exception as e:
            self.log_test("Unauthorized Access Handling", False, f"Error: {str(e)}")
        
        return tests_passed == total_tests

    # NEW PAGINATION SYSTEM TESTS
    def test_pagination_basic_functionality(self):
        """Test motorcycles endpoint GET /api/motorcycles with new pagination parameters (page, limit)"""
        try:
            # Test basic pagination
            response = requests.get(f"{self.base_url}/motorcycles", 
                                  params={"page": 1, "limit": 25}, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and "motorcycles" in data and "pagination" in data:
                    motorcycles = data["motorcycles"]
                    pagination = data["pagination"]
                    
                    # Verify response structure
                    required_pagination_fields = ["page", "limit", "total_count", "total_pages", "has_next", "has_previous"]
                    missing_fields = [field for field in required_pagination_fields if field not in pagination]
                    
                    if missing_fields:
                        self.log_test("Pagination Basic Functionality", False, 
                                    f"Missing pagination fields: {missing_fields}")
                        return False
                    
                    if (len(motorcycles) <= 25 and 
                        pagination["page"] == 1 and 
                        pagination["limit"] == 25):
                        
                        self.log_test("Pagination Basic Functionality", True, 
                                    f"Retrieved {len(motorcycles)} motorcycles with proper pagination structure")
                        return True
                    else:
                        self.log_test("Pagination Basic Functionality", False, 
                                    f"Pagination values incorrect: got {len(motorcycles)} motorcycles, page {pagination['page']}")
                        return False
                else:
                    self.log_test("Pagination Basic Functionality", False, 
                                "Response missing 'motorcycles' or 'pagination' fields")
                    return False
            else:
                self.log_test("Pagination Basic Functionality", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Pagination Basic Functionality", False, f"Error: {str(e)}")
            return False

    def test_pagination_response_format(self):
        """Verify pagination response format includes motorcycles array and pagination metadata"""
        try:
            response = requests.get(f"{self.base_url}/motorcycles", 
                                  params={"page": 1, "limit": 10}, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify top-level structure
                if not isinstance(data, dict):
                    self.log_test("Pagination Response Format", False, "Response is not a dictionary")
                    return False
                
                if "motorcycles" not in data or "pagination" not in data:
                    self.log_test("Pagination Response Format", False, 
                                "Missing 'motorcycles' or 'pagination' in response")
                    return False
                
                # Verify motorcycles array
                motorcycles = data["motorcycles"]
                if not isinstance(motorcycles, list):
                    self.log_test("Pagination Response Format", False, 
                                "'motorcycles' is not an array")
                    return False
                
                # Verify pagination metadata
                pagination = data["pagination"]
                required_fields = ["page", "limit", "total_count", "total_pages", "has_next", "has_previous"]
                
                for field in required_fields:
                    if field not in pagination:
                        self.log_test("Pagination Response Format", False, 
                                    f"Missing pagination field: {field}")
                        return False
                
                # Verify data types
                if (isinstance(pagination["page"], int) and 
                    isinstance(pagination["limit"], int) and
                    isinstance(pagination["total_count"], int) and
                    isinstance(pagination["total_pages"], int) and
                    isinstance(pagination["has_next"], bool) and
                    isinstance(pagination["has_previous"], bool)):
                    
                    self.log_test("Pagination Response Format", True, 
                                "Pagination response format is correct with all required fields and types")
                    return True
                else:
                    self.log_test("Pagination Response Format", False, 
                                "Pagination fields have incorrect data types")
                    return False
            else:
                self.log_test("Pagination Response Format", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Pagination Response Format", False, f"Error: {str(e)}")
            return False

    def test_pagination_navigation(self):
        """Test page navigation (page=1, page=2, etc.) with limit=25"""
        try:
            # Test first page
            response1 = requests.get(f"{self.base_url}/motorcycles", 
                                   params={"page": 1, "limit": 25}, timeout=10)
            
            # Test second page
            response2 = requests.get(f"{self.base_url}/motorcycles", 
                                   params={"page": 2, "limit": 25}, timeout=10)
            
            if response1.status_code == 200 and response2.status_code == 200:
                data1 = response1.json()
                data2 = response2.json()
                
                motorcycles1 = data1["motorcycles"]
                motorcycles2 = data2["motorcycles"]
                pagination1 = data1["pagination"]
                pagination2 = data2["pagination"]
                
                # Verify different motorcycles on different pages
                ids1 = {moto["id"] for moto in motorcycles1}
                ids2 = {moto["id"] for moto in motorcycles2}
                
                if ids1.intersection(ids2):
                    self.log_test("Pagination Navigation", False, 
                                "Same motorcycles appear on different pages")
                    return False
                
                # Verify pagination metadata
                if (pagination1["page"] == 1 and pagination2["page"] == 2 and
                    pagination1["has_previous"] == False and pagination1["has_next"] == True and
                    pagination2["has_previous"] == True):
                    
                    self.log_test("Pagination Navigation", True, 
                                f"Page navigation working correctly: Page 1 ({len(motorcycles1)} items), Page 2 ({len(motorcycles2)} items)")
                    return True
                else:
                    self.log_test("Pagination Navigation", False, 
                                f"Pagination metadata incorrect: P1 has_prev={pagination1['has_previous']}, has_next={pagination1['has_next']}")
                    return False
            else:
                self.log_test("Pagination Navigation", False, 
                            f"Status codes: Page 1: {response1.status_code}, Page 2: {response2.status_code}")
                return False
        except Exception as e:
            self.log_test("Pagination Navigation", False, f"Error: {str(e)}")
            return False

    def test_pagination_metadata_accuracy(self):
        """Verify total_count, total_pages, has_next, has_previous values are correct"""
        try:
            # Get first page
            response = requests.get(f"{self.base_url}/motorcycles", 
                                  params={"page": 1, "limit": 25}, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                pagination = data["pagination"]
                
                total_count = pagination["total_count"]
                total_pages = pagination["total_pages"]
                limit = pagination["limit"]
                
                # Verify total_pages calculation
                expected_total_pages = (total_count + limit - 1) // limit  # Ceiling division
                if total_pages != expected_total_pages:
                    self.log_test("Pagination Metadata Accuracy", False, 
                                f"total_pages incorrect: expected {expected_total_pages}, got {total_pages}")
                    return False
                
                # Test last page to verify has_next/has_previous
                if total_pages > 1:
                    last_page_response = requests.get(f"{self.base_url}/motorcycles", 
                                                    params={"page": total_pages, "limit": 25}, timeout=10)
                    
                    if last_page_response.status_code == 200:
                        last_page_data = last_page_response.json()
                        last_pagination = last_page_data["pagination"]
                        
                        if (last_pagination["has_next"] == False and 
                            last_pagination["has_previous"] == True):
                            
                            self.log_test("Pagination Metadata Accuracy", True, 
                                        f"Pagination metadata accurate: {total_count} total, {total_pages} pages")
                            return True
                        else:
                            self.log_test("Pagination Metadata Accuracy", False, 
                                        f"Last page metadata incorrect: has_next={last_pagination['has_next']}, has_previous={last_pagination['has_previous']}")
                            return False
                    else:
                        self.log_test("Pagination Metadata Accuracy", False, 
                                    f"Failed to fetch last page: {last_page_response.status_code}")
                        return False
                else:
                    # Only one page
                    if (pagination["has_next"] == False and pagination["has_previous"] == False):
                        self.log_test("Pagination Metadata Accuracy", True, 
                                    f"Single page metadata correct: {total_count} total motorcycles")
                        return True
                    else:
                        self.log_test("Pagination Metadata Accuracy", False, 
                                    "Single page should have has_next=False and has_previous=False")
                        return False
            else:
                self.log_test("Pagination Metadata Accuracy", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Pagination Metadata Accuracy", False, f"Error: {str(e)}")
            return False

    def test_pagination_with_filtering(self):
        """Test filtering combined with pagination works correctly"""
        try:
            # Test pagination with manufacturer filter
            response = requests.get(f"{self.base_url}/motorcycles", 
                                  params={"manufacturer": "Yamaha", "page": 1, "limit": 10}, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                motorcycles = data["motorcycles"]
                pagination = data["pagination"]
                
                # Verify all motorcycles match the filter
                yamaha_count = sum(1 for moto in motorcycles if "yamaha" in moto.get("manufacturer", "").lower())
                
                if yamaha_count == len(motorcycles):
                    # Verify pagination works with filtering
                    if pagination["total_count"] > 0 and len(motorcycles) <= 10:
                        self.log_test("Pagination with Filtering", True, 
                                    f"Filtering + pagination working: {len(motorcycles)} Yamaha motorcycles, total: {pagination['total_count']}")
                        return True
                    else:
                        self.log_test("Pagination with Filtering", False, 
                                    f"Pagination not working with filter: got {len(motorcycles)} motorcycles")
                        return False
                else:
                    self.log_test("Pagination with Filtering", False, 
                                f"Filter not applied correctly: {yamaha_count}/{len(motorcycles)} are Yamaha")
                    return False
            else:
                self.log_test("Pagination with Filtering", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Pagination with Filtering", False, f"Error: {str(e)}")
            return False

    def test_pagination_with_sorting(self):
        """Test sorting combined with pagination works correctly"""
        try:
            # Test pagination with sorting
            response = requests.get(f"{self.base_url}/motorcycles", 
                                  params={"sort_by": "price", "sort_order": "asc", "page": 1, "limit": 15}, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                motorcycles = data["motorcycles"]
                pagination = data["pagination"]
                
                # Verify sorting is maintained with pagination
                if len(motorcycles) > 1:
                    is_sorted = True
                    for i in range(len(motorcycles) - 1):
                        if motorcycles[i].get("price_usd", 0) > motorcycles[i + 1].get("price_usd", 0):
                            is_sorted = False
                            break
                    
                    if is_sorted and len(motorcycles) <= 15:
                        self.log_test("Pagination with Sorting", True, 
                                    f"Sorting + pagination working: {len(motorcycles)} motorcycles sorted by price")
                        return True
                    else:
                        self.log_test("Pagination with Sorting", False, 
                                    f"Sorting not maintained with pagination: sorted={is_sorted}, count={len(motorcycles)}")
                        return False
                else:
                    self.log_test("Pagination with Sorting", True, 
                                "Insufficient data to verify sorting, but pagination structure correct")
                    return True
            else:
                self.log_test("Pagination with Sorting", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Pagination with Sorting", False, f"Error: {str(e)}")
            return False

    # NEW VENDOR PRICING IMPROVEMENTS TESTS
    def test_regional_currencies_support(self):
        """Test vendor pricing with new regional currencies (BD, NP, TH, MY, ID, AE, SA)"""
        if not self.motorcycle_ids:
            self.log_test("Regional Currencies Support", False, "No motorcycle IDs available")
            return False
        
        new_regions = ["BD", "NP", "TH", "MY", "ID", "AE", "SA"]
        all_passed = True
        
        for region in new_regions:
            try:
                motorcycle_id = self.motorcycle_ids[0]
                response = requests.get(f"{self.base_url}/motorcycles/{motorcycle_id}/pricing", 
                                      params={"region": region}, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if ("currency" in data and "vendor_prices" in data and 
                        data["region"] == region):
                        
                        self.log_test(f"Regional Currency - {region}", True, 
                                    f"Pricing available in {data['currency']} for {region}")
                    else:
                        self.log_test(f"Regional Currency - {region}", False, 
                                    f"Invalid pricing response structure")
                        all_passed = False
                else:
                    self.log_test(f"Regional Currency - {region}", False, 
                                f"Status: {response.status_code}")
                    all_passed = False
            except Exception as e:
                self.log_test(f"Regional Currency - {region}", False, f"Error: {str(e)}")
                all_passed = False
        
        return all_passed

    def test_discontinued_motorcycle_handling(self):
        """Test discontinued motorcycle handling - should return proper discontinued message"""
        try:
            # First, let's get a motorcycle and check its availability
            response = requests.get(f"{self.base_url}/motorcycles", 
                                  params={"limit": 50}, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                motorcycles = data.get("motorcycles", [])
                
                # Look for a discontinued motorcycle
                discontinued_moto = None
                for moto in motorcycles:
                    if moto.get("availability", "").lower() == "discontinued":
                        discontinued_moto = moto
                        break
                
                if discontinued_moto:
                    # Test pricing for discontinued motorcycle
                    pricing_response = requests.get(f"{self.base_url}/motorcycles/{discontinued_moto['id']}/pricing", 
                                                  params={"region": "US"}, timeout=10)
                    
                    if pricing_response.status_code == 200:
                        pricing_data = pricing_response.json()
                        vendor_prices = pricing_data.get("vendor_prices", [])
                        
                        # Check if discontinued status is properly handled
                        discontinued_handling = any(
                            "discontinued" in vendor.get("availability", "").lower() or
                            "not available" in vendor.get("availability", "").lower()
                            for vendor in vendor_prices
                        )
                        
                        if discontinued_handling or len(vendor_prices) == 0:
                            self.log_test("Discontinued Motorcycle Handling", True, 
                                        f"Discontinued motorcycle properly handled: {discontinued_moto['manufacturer']} {discontinued_moto['model']}")
                            return True
                        else:
                            self.log_test("Discontinued Motorcycle Handling", False, 
                                        "Discontinued motorcycle not properly marked in vendor pricing")
                            return False
                    else:
                        self.log_test("Discontinued Motorcycle Handling", False, 
                                    f"Failed to get pricing for discontinued motorcycle: {pricing_response.status_code}")
                        return False
                else:
                    self.log_test("Discontinued Motorcycle Handling", True, 
                                "No discontinued motorcycles found in database (all available)")
                    return True
            else:
                self.log_test("Discontinued Motorcycle Handling", False, 
                            f"Failed to get motorcycles: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Discontinued Motorcycle Handling", False, f"Error: {str(e)}")
            return False

    def test_verified_vendor_urls(self):
        """Verify only verified vendor URLs are returned (no fake/placeholder links)"""
        if not self.motorcycle_ids:
            self.log_test("Verified Vendor URLs", False, "No motorcycle IDs available")
            return False
        
        try:
            motorcycle_id = self.motorcycle_ids[0]
            response = requests.get(f"{self.base_url}/motorcycles/{motorcycle_id}/pricing", 
                                  params={"region": "US"}, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                vendor_prices = data.get("vendor_prices", [])
                
                if vendor_prices:
                    fake_url_indicators = ["example.com", "placeholder", "fake", "test.com", "localhost"]
                    verified_urls = True
                    
                    for vendor in vendor_prices:
                        website_url = vendor.get("website_url", "")
                        if any(indicator in website_url.lower() for indicator in fake_url_indicators):
                            verified_urls = False
                            break
                    
                    if verified_urls:
                        self.log_test("Verified Vendor URLs", True, 
                                    f"All {len(vendor_prices)} vendor URLs appear to be verified (no fake/placeholder links)")
                        return True
                    else:
                        self.log_test("Verified Vendor URLs", False, 
                                    "Some vendor URLs appear to be fake or placeholder links")
                        return False
                else:
                    self.log_test("Verified Vendor URLs", True, 
                                "No vendor prices returned (acceptable for testing)")
                    return True
            else:
                self.log_test("Verified Vendor URLs", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Verified Vendor URLs", False, f"Error: {str(e)}")
            return False

    def test_currency_conversion(self):
        """Test currency conversion is working for different regions"""
        if not self.motorcycle_ids:
            self.log_test("Currency Conversion", False, "No motorcycle IDs available")
            return False
        
        try:
            motorcycle_id = self.motorcycle_ids[0]
            
            # Test US pricing (baseline)
            us_response = requests.get(f"{self.base_url}/motorcycles/{motorcycle_id}/pricing", 
                                     params={"region": "US"}, timeout=10)
            
            # Test different region pricing
            eu_response = requests.get(f"{self.base_url}/motorcycles/{motorcycle_id}/pricing", 
                                     params={"region": "EU"}, timeout=10)
            
            if us_response.status_code == 200 and eu_response.status_code == 200:
                us_data = us_response.json()
                eu_data = eu_response.json()
                
                us_currency = us_data.get("currency", "USD")
                eu_currency = eu_data.get("currency", "EUR")
                
                if us_currency != eu_currency:
                    self.log_test("Currency Conversion", True, 
                                f"Currency conversion working: US uses {us_currency}, EU uses {eu_currency}")
                    return True
                else:
                    self.log_test("Currency Conversion", False, 
                                f"Same currency for different regions: {us_currency}")
                    return False
            else:
                self.log_test("Currency Conversion", False, 
                            f"Failed to get pricing: US: {us_response.status_code}, EU: {eu_response.status_code}")
                return False
        except Exception as e:
            self.log_test("Currency Conversion", False, f"Error: {str(e)}")
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
        
        # Database and category APIs
        self.test_database_stats_api()
        self.test_category_summary_api()
        
        # Daily Update System Tests
        print("\n🤖 Testing Daily Update Bot System APIs...")
        print("-" * 60)
        
        # Test daily update trigger and get job ID
        success, job_id = self.test_trigger_daily_update()
        
        # Test job status monitoring if we have a job ID
        if success and job_id:
            self.test_job_status_monitoring(job_id)
        
        # Test update history
        self.test_update_history()
        
        # Test regional customizations
        self.test_regional_customizations()
        
        # NEW USER INTERACTION API TESTS
        print("\n👤 Testing User Interaction APIs...")
        print("-" * 60)
        
        # Authentication & User Management
        self.test_user_authentication()
        self.test_get_current_user()
        
        # Favorites System
        self.test_add_to_favorites()
        self.test_get_favorite_motorcycles()
        self.test_remove_from_favorites()
        
        # Rating System
        self.test_rate_motorcycle()
        self.test_get_motorcycle_ratings()
        
        # Comments & Discussion
        self.test_add_comment()
        self.test_get_motorcycle_comments()
        self.test_like_comment()
        
        # Browse Limit Fix
        self.test_browse_limit_fix()
        
        # NEW TESTS FOR TECHNICAL FEATURES DATABASE ENHANCEMENT AND DUAL-LEVEL SORTING
        print("\n🔧 Testing Technical Features Database Enhancement...")
        print("-" * 60)
        
        self.test_technical_features_database_enhancement()
        self.test_suzuki_ducati_technical_data()
        self.test_technical_features_filtering()
        self.test_numeric_range_filtering()
        
        print("\n📊 Testing Dual-Level Sorting Implementation...")
        print("-" * 60)
        
        self.test_dual_level_sorting_default()
        self.test_compare_default_vs_single_field_sorting()
        
        print("\n📈 Testing Database Count Verification...")
        print("-" * 60)
        
        self.test_database_count_verification()
        self.test_manufacturer_counts_verification()
        
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