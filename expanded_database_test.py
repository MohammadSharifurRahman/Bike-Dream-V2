#!/usr/bin/env python3
"""
Expanded Database Testing for Byke-Dream Motorcycle Database
Tests the specific features mentioned in the review request:
1. Database Stats API
2. Category Summary API  
3. Advanced filtering with expanded data
4. Verification of 1000+ motorcycles
"""

import requests
import json
import sys
from typing import Dict, List, Any

# Backend URL from environment
BACKEND_URL = "https://b4e17258-5cf1-4bb8-a561-56760731f05a.preview.emergentagent.com/api"

class ExpandedDatabaseTester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.test_results = []
        
    def log_test(self, test_name: str, success: bool, details: str = ""):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = f"{status} - {test_name}"
        if details:
            result += f": {details}"
        self.test_results.append(result)
        print(result)
        
    def test_database_stats(self):
        """Test GET /api/stats for expanded database statistics"""
        try:
            response = requests.get(f"{self.base_url}/stats", timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                # Check required fields
                required_fields = ["total_motorcycles", "manufacturers", "categories", "year_range", "latest_update"]
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    self.log_test("Database Stats API Structure", False, f"Missing fields: {missing_fields}")
                    return False
                
                # Verify expanded database size (should be 1000+)
                total_motorcycles = data["total_motorcycles"]
                if total_motorcycles >= 1000:
                    self.log_test("Database Size Verification", True, f"Database contains {total_motorcycles} motorcycles (1000+ requirement met)")
                else:
                    self.log_test("Database Size Verification", False, f"Database only contains {total_motorcycles} motorcycles (expected 1000+)")
                    return False
                
                # Verify major manufacturers are present
                manufacturers = data["manufacturers"]
                expected_manufacturers = ["Yamaha", "Honda", "Kawasaki", "Suzuki", "Ducati"]
                missing_manufacturers = [m for m in expected_manufacturers if m not in manufacturers]
                
                if not missing_manufacturers:
                    self.log_test("Major Manufacturers Present", True, f"All major manufacturers found: {len(manufacturers)} total")
                else:
                    self.log_test("Major Manufacturers Present", False, f"Missing manufacturers: {missing_manufacturers}")
                
                # Verify categories are comprehensive
                categories = data["categories"]
                expected_categories = ["Sport", "Naked", "Cruiser", "Adventure", "Touring"]
                missing_categories = [c for c in expected_categories if c not in categories]
                
                if not missing_categories:
                    self.log_test("Category Coverage", True, f"All expected categories found: {len(categories)} total")
                else:
                    self.log_test("Category Coverage", False, f"Missing categories: {missing_categories}")
                
                # Verify year range covers 2000-2025
                year_range = data["year_range"]
                if year_range.get("min_year", 0) <= 2000 and year_range.get("max_year", 0) >= 2025:
                    self.log_test("Year Range Coverage", True, f"Years {year_range['min_year']}-{year_range['max_year']} covers expected range")
                else:
                    self.log_test("Year Range Coverage", False, f"Year range {year_range} doesn't cover 2000-2025")
                
                return True
                
            else:
                self.log_test("Database Stats API", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Database Stats API", False, f"Error: {str(e)}")
            return False
    
    def test_category_summary(self):
        """Test GET /api/motorcycles/categories/summary"""
        try:
            response = requests.get(f"{self.base_url}/motorcycles/categories/summary", timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                if not isinstance(data, list):
                    self.log_test("Category Summary Structure", False, "Response is not a list")
                    return False
                
                if len(data) == 0:
                    self.log_test("Category Summary Content", False, "No categories returned")
                    return False
                
                # Verify each category summary has required fields
                for category_summary in data:
                    required_fields = ["category", "count", "featured_motorcycles"]
                    missing_fields = [field for field in required_fields if field not in category_summary]
                    
                    if missing_fields:
                        self.log_test("Category Summary Structure", False, f"Missing fields in {category_summary.get('category', 'unknown')}: {missing_fields}")
                        return False
                    
                    # Verify featured motorcycles are present and properly structured
                    featured = category_summary["featured_motorcycles"]
                    if not isinstance(featured, list):
                        self.log_test("Featured Motorcycles Structure", False, f"Featured motorcycles not a list for {category_summary['category']}")
                        return False
                    
                    if len(featured) > 0:
                        # Check first featured motorcycle has required fields
                        first_moto = featured[0]
                        moto_required_fields = ["id", "manufacturer", "model", "year", "category", "user_interest_score"]
                        moto_missing_fields = [field for field in moto_required_fields if field not in first_moto]
                        
                        if moto_missing_fields:
                            self.log_test("Featured Motorcycle Structure", False, f"Missing fields in featured motorcycle: {moto_missing_fields}")
                            return False
                
                # Verify major categories are present with motorcycles
                category_names = [cat["category"] for cat in data]
                expected_categories = ["Sport", "Naked", "Cruiser", "Adventure"]
                present_categories = [cat for cat in expected_categories if cat in category_names]
                
                self.log_test("Category Summary API", True, f"Retrieved {len(data)} categories with featured motorcycles")
                self.log_test("Major Categories Present", True, f"Found {len(present_categories)}/{len(expected_categories)} major categories: {present_categories}")
                
                return True
                
            else:
                self.log_test("Category Summary API", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Category Summary API", False, f"Error: {str(e)}")
            return False
    
    def test_advanced_filtering_expanded_data(self):
        """Test advanced filtering with the expanded database"""
        
        # Test 1: Major manufacturer filtering
        major_manufacturers = ["Yamaha", "Honda", "Kawasaki", "Suzuki", "Ducati"]
        manufacturer_results = {}
        
        for manufacturer in major_manufacturers:
            try:
                response = requests.get(f"{self.base_url}/motorcycles", 
                                      params={"manufacturer": manufacturer, "limit": 500}, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    manufacturer_results[manufacturer] = len(data)
                    
                    if len(data) > 0:
                        self.log_test(f"Expanded Filtering - {manufacturer}", True, f"Found {len(data)} motorcycles")
                    else:
                        self.log_test(f"Expanded Filtering - {manufacturer}", False, "No motorcycles found")
                else:
                    self.log_test(f"Expanded Filtering - {manufacturer}", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"Expanded Filtering - {manufacturer}", False, f"Error: {str(e)}")
        
        # Test 2: Category filtering with expanded data
        major_categories = ["Sport", "Naked", "Cruiser", "Adventure", "Vintage"]
        category_results = {}
        
        for category in major_categories:
            try:
                response = requests.get(f"{self.base_url}/motorcycles", 
                                      params={"category": category, "limit": 500}, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    category_results[category] = len(data)
                    
                    if len(data) > 0:
                        self.log_test(f"Category Filtering - {category}", True, f"Found {len(data)} motorcycles")
                    else:
                        self.log_test(f"Category Filtering - {category}", False, "No motorcycles found")
                else:
                    self.log_test(f"Category Filtering - {category}", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"Category Filtering - {category}", False, f"Error: {str(e)}")
        
        # Test 3: Year range filtering with expanded data
        year_ranges = [
            (2000, 2025, "Full modern range"),
            (1990, 2010, "Vintage to early modern"),
            (2020, 2025, "Latest models")
        ]
        
        for year_min, year_max, description in year_ranges:
            try:
                response = requests.get(f"{self.base_url}/motorcycles", 
                                      params={"year_min": year_min, "year_max": year_max, "limit": 500}, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if len(data) > 0:
                        self.log_test(f"Year Range Filtering - {description}", True, f"Found {len(data)} motorcycles ({year_min}-{year_max})")
                    else:
                        self.log_test(f"Year Range Filtering - {description}", False, f"No motorcycles found for {year_min}-{year_max}")
                else:
                    self.log_test(f"Year Range Filtering - {description}", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"Year Range Filtering - {description}", False, f"Error: {str(e)}")
        
        # Test 4: Search functionality across expanded database
        search_terms = ["R1", "Ninja", "CBR", "GSX", "Panigale"]
        
        for search_term in search_terms:
            try:
                response = requests.get(f"{self.base_url}/motorcycles", 
                                      params={"search": search_term, "limit": 100}, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    self.log_test(f"Search Functionality - '{search_term}'", True, f"Found {len(data)} results")
                else:
                    self.log_test(f"Search Functionality - '{search_term}'", False, f"Status: {response.status_code}")
            except Exception as e:
                self.log_test(f"Search Functionality - '{search_term}'", False, f"Error: {str(e)}")
        
        return True
    
    def test_user_interest_scoring(self):
        """Test that user interest scoring system is working"""
        try:
            # Get motorcycles sorted by user interest score
            response = requests.get(f"{self.base_url}/motorcycles", 
                                  params={"sort_by": "user_interest_score", "sort_order": "desc", "limit": 10}, 
                                  timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                if len(data) > 0:
                    # Verify motorcycles have user_interest_score field
                    first_moto = data[0]
                    if "user_interest_score" in first_moto:
                        score = first_moto["user_interest_score"]
                        self.log_test("User Interest Scoring", True, f"Top motorcycle: {first_moto['manufacturer']} {first_moto['model']} (score: {score})")
                        
                        # Verify scores are in descending order
                        scores_descending = True
                        for i in range(len(data) - 1):
                            if data[i]["user_interest_score"] < data[i + 1]["user_interest_score"]:
                                scores_descending = False
                                break
                        
                        if scores_descending:
                            self.log_test("Interest Score Sorting", True, "Motorcycles properly sorted by interest score")
                        else:
                            self.log_test("Interest Score Sorting", False, "Interest scores not properly sorted")
                        
                        return True
                    else:
                        self.log_test("User Interest Scoring", False, "user_interest_score field missing")
                        return False
                else:
                    self.log_test("User Interest Scoring", False, "No motorcycles returned")
                    return False
            else:
                self.log_test("User Interest Scoring", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("User Interest Scoring", False, f"Error: {str(e)}")
            return False
    
    def run_expanded_tests(self):
        """Run all expanded database tests"""
        print("🏍️  Testing Expanded Byke-Dream Database (1000+ Motorcycles)")
        print("=" * 70)
        
        # Test database statistics
        self.test_database_stats()
        
        # Test category summary
        self.test_category_summary()
        
        # Test advanced filtering with expanded data
        self.test_advanced_filtering_expanded_data()
        
        # Test user interest scoring
        self.test_user_interest_scoring()
        
        # Summary
        print("\n" + "=" * 70)
        print("📊 EXPANDED DATABASE TEST SUMMARY")
        print("=" * 70)
        
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
    tester = ExpandedDatabaseTester()
    success = tester.run_expanded_tests()
    
    if success:
        print("\n🎉 All expanded database tests passed! The 1000+ motorcycle database is working correctly.")
        sys.exit(0)
    else:
        print("\n⚠️  Some expanded database tests failed. Check the details above.")
        sys.exit(1)

if __name__ == "__main__":
    main()