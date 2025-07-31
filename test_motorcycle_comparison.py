#!/usr/bin/env python3
"""
Focused testing for Motorcycle Comparison API (Phase 2)
Tests the POST /api/motorcycles/compare endpoint with all required scenarios.
"""

import requests
import json
import sys

# Backend URL from environment
BACKEND_URL = "https://b4e17258-5cf1-4bb8-a561-56760731f05a.preview.emergentagent.com/api"

class MotorcycleComparisonTester:
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
        
    def setup_motorcycle_ids(self):
        """Get motorcycle IDs for testing"""
        try:
            response = requests.get(f"{self.base_url}/motorcycles", params={"limit": 10}, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and "motorcycles" in data:
                    motorcycles = data["motorcycles"]
                elif isinstance(data, list):
                    motorcycles = data
                else:
                    print("❌ Could not get motorcycle data for testing")
                    return False
                
                self.motorcycle_ids = [moto.get("id") for moto in motorcycles[:5] if moto.get("id")]
                print(f"✅ Setup: Retrieved {len(self.motorcycle_ids)} motorcycle IDs for testing")
                return len(self.motorcycle_ids) >= 3
            else:
                print(f"❌ Setup failed: Status {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Setup error: {str(e)}")
            return False

    def test_motorcycle_comparison_single_bike(self):
        """Test POST /api/motorcycles/compare with single motorcycle ID"""
        if not self.motorcycle_ids:
            self.log_test("Single Motorcycle Comparison", False, "No motorcycle IDs available")
            return False
        
        try:
            payload = [self.motorcycle_ids[0]]
            
            response = requests.post(f"{self.base_url}/motorcycles/compare", 
                                   json=payload, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                required_keys = ["comparison_id", "motorcycles", "comparison_count", "generated_at", "comparison_categories"]
                missing_keys = [key for key in required_keys if key not in data]
                
                if missing_keys:
                    self.log_test("Single Motorcycle Comparison", False, f"Missing keys: {missing_keys}")
                    return False
                
                if (data["comparison_count"] == 1 and 
                    len(data["motorcycles"]) == 1 and
                    isinstance(data["comparison_categories"], list)):
                    
                    motorcycle = data["motorcycles"][0]
                    required_sections = ["technical_specs", "features", "pricing", "ratings", "metadata"]
                    missing_sections = [section for section in required_sections if section not in motorcycle]
                    
                    if missing_sections:
                        self.log_test("Single Motorcycle Comparison", False, f"Missing sections: {missing_sections}")
                        return False
                    
                    self.log_test("Single Motorcycle Comparison", True, 
                                f"Successfully compared 1 motorcycle: {motorcycle.get('manufacturer')} {motorcycle.get('model')}")
                    return True
                else:
                    self.log_test("Single Motorcycle Comparison", False, "Invalid comparison structure")
                    return False
            else:
                self.log_test("Single Motorcycle Comparison", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Single Motorcycle Comparison", False, f"Error: {str(e)}")
            return False

    def test_motorcycle_comparison_two_bikes(self):
        """Test POST /api/motorcycles/compare with 2 motorcycle IDs"""
        if len(self.motorcycle_ids) < 2:
            self.log_test("Two Motorcycles Comparison", False, "Need at least 2 motorcycle IDs")
            return False
        
        try:
            payload = self.motorcycle_ids[:2]
            
            response = requests.post(f"{self.base_url}/motorcycles/compare", 
                                   json=payload, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if (data["comparison_count"] == 2 and 
                    len(data["motorcycles"]) == 2):
                    
                    bike1 = data["motorcycles"][0]
                    bike2 = data["motorcycles"][1]
                    self.log_test("Two Motorcycles Comparison", True, 
                                f"Successfully compared 2 motorcycles: {bike1.get('manufacturer')} {bike1.get('model')} vs {bike2.get('manufacturer')} {bike2.get('model')}")
                    return True
                else:
                    self.log_test("Two Motorcycles Comparison", False, "Invalid comparison count")
                    return False
            else:
                self.log_test("Two Motorcycles Comparison", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Two Motorcycles Comparison", False, f"Error: {str(e)}")
            return False

    def test_motorcycle_comparison_three_bikes(self):
        """Test POST /api/motorcycles/compare with 3 motorcycle IDs (maximum allowed)"""
        if len(self.motorcycle_ids) < 3:
            self.log_test("Three Motorcycles Comparison", False, "Need at least 3 motorcycle IDs")
            return False
        
        try:
            payload = self.motorcycle_ids[:3]
            
            response = requests.post(f"{self.base_url}/motorcycles/compare", 
                                   json=payload, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if (data["comparison_count"] == 3 and 
                    len(data["motorcycles"]) == 3):
                    
                    bikes = [f"{bike.get('manufacturer')} {bike.get('model')}" for bike in data["motorcycles"]]
                    self.log_test("Three Motorcycles Comparison", True, 
                                f"Successfully compared 3 motorcycles: {', '.join(bikes)}")
                    return True
                else:
                    self.log_test("Three Motorcycles Comparison", False, "Invalid comparison count")
                    return False
            else:
                self.log_test("Three Motorcycles Comparison", False, f"Status: {response.status_code}, Response: {response.text}")
                return False
        except Exception as e:
            self.log_test("Three Motorcycles Comparison", False, f"Error: {str(e)}")
            return False

    def test_motorcycle_comparison_too_many_bikes(self):
        """Test POST /api/motorcycles/compare with more than 3 motorcycle IDs (should return error)"""
        if len(self.motorcycle_ids) < 4:
            # Create dummy IDs for this test
            test_ids = self.motorcycle_ids + ["dummy_id_1", "dummy_id_2"]
        else:
            test_ids = self.motorcycle_ids[:4]
        
        try:
            payload = test_ids
            
            response = requests.post(f"{self.base_url}/motorcycles/compare", 
                                   json=payload, timeout=15)
            
            if response.status_code == 400:
                data = response.json()
                if "Maximum 3 motorcycles" in data.get("detail", ""):
                    self.log_test("Too Many Motorcycles Error", True, 
                                "Correctly rejected request with more than 3 motorcycles")
                    return True
                else:
                    self.log_test("Too Many Motorcycles Error", False, 
                                f"Wrong error message: {data.get('detail')}")
                    return False
            else:
                self.log_test("Too Many Motorcycles Error", False, 
                            f"Expected 400 status, got: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Too Many Motorcycles Error", False, f"Error: {str(e)}")
            return False

    def test_motorcycle_comparison_empty_list(self):
        """Test POST /api/motorcycles/compare with empty list (should return error)"""
        try:
            payload = []
            
            response = requests.post(f"{self.base_url}/motorcycles/compare", 
                                   json=payload, timeout=15)
            
            if response.status_code == 400:
                data = response.json()
                if "At least one motorcycle ID is required" in data.get("detail", ""):
                    self.log_test("Empty List Error", True, 
                                "Correctly rejected empty motorcycle list")
                    return True
                else:
                    self.log_test("Empty List Error", False, 
                                f"Wrong error message: {data.get('detail')}")
                    return False
            else:
                self.log_test("Empty List Error", False, 
                            f"Expected 400 status, got: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Empty List Error", False, f"Error: {str(e)}")
            return False

    def test_motorcycle_comparison_duplicate_ids(self):
        """Test POST /api/motorcycles/compare with duplicate motorcycle IDs (should remove duplicates)"""
        if not self.motorcycle_ids:
            self.log_test("Duplicate IDs Handling", False, "No motorcycle IDs available")
            return False
        
        try:
            # Use same ID multiple times
            motorcycle_id = self.motorcycle_ids[0]
            payload = [motorcycle_id, motorcycle_id, motorcycle_id]
            
            response = requests.post(f"{self.base_url}/motorcycles/compare", 
                                   json=payload, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                if (data["comparison_count"] == 1 and 
                    len(data["motorcycles"]) == 1):
                    
                    self.log_test("Duplicate IDs Handling", True, 
                                "Successfully removed duplicates and returned 1 unique motorcycle")
                    return True
                else:
                    self.log_test("Duplicate IDs Handling", False, 
                                f"Expected 1 motorcycle, got {data['comparison_count']}")
                    return False
            else:
                self.log_test("Duplicate IDs Handling", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Duplicate IDs Handling", False, f"Error: {str(e)}")
            return False

    def test_motorcycle_comparison_invalid_id(self):
        """Test POST /api/motorcycles/compare with invalid motorcycle ID (should return 404)"""
        try:
            payload = ["invalid_motorcycle_id_12345"]
            
            response = requests.post(f"{self.base_url}/motorcycles/compare", 
                                   json=payload, timeout=15)
            
            if response.status_code == 404:
                data = response.json()
                if "not found" in data.get("detail", "").lower():
                    self.log_test("Invalid ID Error", True, 
                                "Correctly returned 404 for invalid motorcycle ID")
                    return True
                else:
                    self.log_test("Invalid ID Error", False, 
                                f"Wrong error message: {data.get('detail')}")
                    return False
            else:
                self.log_test("Invalid ID Error", False, 
                            f"Expected 404 status, got: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Invalid ID Error", False, f"Error: {str(e)}")
            return False

    def test_motorcycle_comparison_mixed_valid_invalid(self):
        """Test POST /api/motorcycles/compare with mix of valid and invalid IDs"""
        if not self.motorcycle_ids:
            self.log_test("Mixed Valid/Invalid IDs", False, "No motorcycle IDs available")
            return False
        
        try:
            # Mix valid and invalid IDs
            payload = [self.motorcycle_ids[0], "invalid_id_12345"]
            
            response = requests.post(f"{self.base_url}/motorcycles/compare", 
                                   json=payload, timeout=15)
            
            if response.status_code == 404:
                data = response.json()
                if "not found" in data.get("detail", "").lower():
                    self.log_test("Mixed Valid/Invalid IDs", True, 
                                "Correctly returned 404 when any motorcycle ID is invalid")
                    return True
                else:
                    self.log_test("Mixed Valid/Invalid IDs", False, 
                                f"Wrong error message: {data.get('detail')}")
                    return False
            else:
                self.log_test("Mixed Valid/Invalid IDs", False, 
                            f"Expected 404 status, got: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Mixed Valid/Invalid IDs", False, f"Error: {str(e)}")
            return False

    def test_response_structure_detailed(self):
        """Test detailed response structure of motorcycle comparison API"""
        if not self.motorcycle_ids:
            self.log_test("Response Structure Validation", False, "No motorcycle IDs available")
            return False
        
        try:
            payload = self.motorcycle_ids[:2]
            
            response = requests.post(f"{self.base_url}/motorcycles/compare", 
                                   json=payload, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check top-level structure
                required_keys = ["comparison_id", "motorcycles", "comparison_count", "generated_at", "comparison_categories"]
                missing_keys = [key for key in required_keys if key not in data]
                
                if missing_keys:
                    self.log_test("Response Structure Validation", False, f"Missing top-level keys: {missing_keys}")
                    return False
                
                # Check comparison categories
                expected_categories = [
                    "Technical Specifications",
                    "Features & Technology", 
                    "Pricing & Availability",
                    "Ratings & Reviews",
                    "Additional Information"
                ]
                
                if not all(cat in data["comparison_categories"] for cat in expected_categories):
                    self.log_test("Response Structure Validation", False, "Missing expected comparison categories")
                    return False
                
                # Check motorcycle structure
                if data["motorcycles"]:
                    motorcycle = data["motorcycles"][0]
                    required_sections = ["technical_specs", "features", "pricing", "ratings", "metadata"]
                    missing_sections = [section for section in required_sections if section not in motorcycle]
                    
                    if missing_sections:
                        self.log_test("Response Structure Validation", False, f"Missing sections: {missing_sections}")
                        return False
                    
                    # Check vendor pricing structure
                    pricing = motorcycle.get("pricing", {})
                    vendor_pricing = pricing.get("vendor_pricing", {})
                    if "vendors" not in vendor_pricing or "message" not in vendor_pricing:
                        self.log_test("Response Structure Validation", False, "Vendor pricing structure incomplete")
                        return False
                    
                    # Check ratings structure
                    ratings = motorcycle.get("ratings", {})
                    required_rating_fields = ["average_rating", "total_ratings", "rating_distribution", "comments_count"]
                    missing_rating_fields = [field for field in required_rating_fields if field not in ratings]
                    
                    if missing_rating_fields:
                        self.log_test("Response Structure Validation", False, f"Missing rating fields: {missing_rating_fields}")
                        return False
                
                self.log_test("Response Structure Validation", True, 
                            "Response structure is complete with all required sections and fields")
                return True
            else:
                self.log_test("Response Structure Validation", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Response Structure Validation", False, f"Error: {str(e)}")
            return False

    def run_all_tests(self):
        """Run all motorcycle comparison tests"""
        print("🏍️ MOTORCYCLE COMPARISON API TESTING (Phase 2)")
        print("=" * 60)
        
        # Setup
        if not self.setup_motorcycle_ids():
            print("❌ Setup failed - cannot proceed with tests")
            return False
        
        # Run all tests
        test_methods = [
            self.test_motorcycle_comparison_single_bike,
            self.test_motorcycle_comparison_two_bikes,
            self.test_motorcycle_comparison_three_bikes,
            self.test_motorcycle_comparison_too_many_bikes,
            self.test_motorcycle_comparison_empty_list,
            self.test_motorcycle_comparison_duplicate_ids,
            self.test_motorcycle_comparison_invalid_id,
            self.test_motorcycle_comparison_mixed_valid_invalid,
            self.test_response_structure_detailed
        ]
        
        passed = 0
        total = len(test_methods)
        
        print("\n🔍 Running Motorcycle Comparison Tests...")
        print("-" * 40)
        
        for test_method in test_methods:
            if test_method():
                passed += 1
        
        # Print summary
        print("\n" + "=" * 60)
        print("📊 MOTORCYCLE COMPARISON API TEST SUMMARY")
        print("=" * 60)
        
        success_rate = (passed / total) * 100
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {total - passed}")
        print(f"Success Rate: {success_rate:.1f}%")
        
        if total - passed > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if "❌ FAIL" in result:
                    print(f"  {result}")
        
        print("\n" + "=" * 60)
        
        if success_rate >= 85:
            print("✅ MOTORCYCLE COMPARISON API IS WORKING CORRECTLY")
        else:
            print("❌ MOTORCYCLE COMPARISON API HAS ISSUES THAT NEED FIXING")
        
        return success_rate >= 85

if __name__ == "__main__":
    tester = MotorcycleComparisonTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)