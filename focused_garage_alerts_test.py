#!/usr/bin/env python3
"""
Focused Backend API Testing for Virtual Garage and Price Alerts GET Endpoints
Tests the FIXED aggregation pipeline issues that were causing 500 errors.
"""

import requests
import json
import sys
from typing import Dict, List, Any

# Backend URL from environment
BACKEND_URL = "https://b4e17258-5cf1-4bb8-a561-56760731f05a.preview.emergentagent.com/api"

class FocusedGarageAlertsAPITester:
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
    
    def test_get_motorcycles(self):
        """Test GET /api/motorcycles to get motorcycle IDs for testing"""
        try:
            response = requests.get(f"{self.base_url}/motorcycles", timeout=10)
            if response.status_code == 200:
                data = response.json()
                # Handle new pagination format
                if isinstance(data, dict) and "motorcycles" in data:
                    motorcycles = data["motorcycles"]
                    if len(motorcycles) > 0:
                        # Store some motorcycle IDs for testing
                        self.motorcycle_ids = [moto.get("id") for moto in motorcycles[:3] if moto.get("id")]
                        self.log_test("Get Motorcycles", True, f"Retrieved {len(motorcycles)} motorcycles")
                        return True
                    else:
                        self.log_test("Get Motorcycles", False, "No motorcycles returned")
                        return False
                # Handle legacy format for backward compatibility
                elif isinstance(data, list) and len(data) > 0:
                    self.motorcycle_ids = [moto.get("id") for moto in data[:3] if moto.get("id")]
                    self.log_test("Get Motorcycles", True, f"Retrieved {len(data)} motorcycles (legacy format)")
                    return True
                else:
                    self.log_test("Get Motorcycles", False, "No motorcycles returned or invalid format")
                    return False
            else:
                self.log_test("Get Motorcycles", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Get Motorcycles", False, f"Error: {str(e)}")
            return False

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

    def test_virtual_garage_get_endpoint(self):
        """Test GET /api/garage - Retrieve user's garage items (FIXED aggregation pipeline)"""
        if not self.test_user_session:
            self.log_test("Virtual Garage GET - Authentication", False, "No user session available")
            return False
        
        try:
            headers = {"X-Session-Id": self.test_user_session}
            
            # First, add a motorcycle to garage to ensure we have data to test
            if self.motorcycle_ids:
                garage_data = {
                    "motorcycle_id": self.motorcycle_ids[0],
                    "status": "owned",
                    "purchase_price": 15000.0,
                    "current_mileage": 5000,
                    "notes": "Test garage item for API testing"
                }
                
                add_response = requests.post(f"{self.base_url}/garage", 
                                           headers=headers, json=garage_data, timeout=10)
                if add_response.status_code != 200:
                    self.log_test("Virtual Garage GET - Setup", False, 
                                f"Failed to add test item: {add_response.status_code}")
                    return False
            
            # Test GET /api/garage
            response = requests.get(f"{self.base_url}/garage", headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                if "garage_items" not in data or "pagination" not in data:
                    self.log_test("Virtual Garage GET - Structure", False, 
                                "Missing 'garage_items' or 'pagination' in response")
                    return False
                
                garage_items = data["garage_items"]
                pagination = data["pagination"]
                
                # Verify pagination structure
                required_pagination_fields = ["page", "limit", "total_count", "total_pages", "has_next", "has_previous"]
                missing_pagination = [field for field in required_pagination_fields if field not in pagination]
                if missing_pagination:
                    self.log_test("Virtual Garage GET - Pagination", False, 
                                f"Missing pagination fields: {missing_pagination}")
                    return False
                
                # Verify garage items structure and motorcycle details
                if garage_items:
                    first_item = garage_items[0]
                    required_item_fields = ["id", "user_id", "motorcycle_id", "status", "created_at"]
                    missing_item_fields = [field for field in required_item_fields if field not in first_item]
                    if missing_item_fields:
                        self.log_test("Virtual Garage GET - Item Structure", False, 
                                    f"Missing garage item fields: {missing_item_fields}")
                        return False
                    
                    # Verify motorcycle details are properly joined
                    if "motorcycle" not in first_item:
                        self.log_test("Virtual Garage GET - Motorcycle Join", False, 
                                    "Motorcycle details not joined with garage item")
                        return False
                    
                    motorcycle = first_item["motorcycle"]
                    required_moto_fields = ["id", "manufacturer", "model", "year", "category", "price_usd"]
                    missing_moto_fields = [field for field in required_moto_fields if field not in motorcycle]
                    if missing_moto_fields:
                        self.log_test("Virtual Garage GET - Motorcycle Details", False, 
                                    f"Missing motorcycle fields: {missing_moto_fields}")
                        return False
                    
                    self.log_test("Virtual Garage GET - Complete", True, 
                                f"Retrieved {len(garage_items)} garage items with complete motorcycle details")
                    return True
                else:
                    self.log_test("Virtual Garage GET - Empty", True, 
                                "No garage items found (empty garage)")
                    return True
                    
            elif response.status_code == 401:
                self.log_test("Virtual Garage GET", False, "Authentication required (401)")
                return False
            else:
                self.log_test("Virtual Garage GET", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Virtual Garage GET", False, f"Error: {str(e)}")
            return False

    def test_virtual_garage_status_filtering(self):
        """Test GET /api/garage with status filtering"""
        if not self.test_user_session:
            self.log_test("Virtual Garage Status Filter", False, "No user session available")
            return False
        
        try:
            headers = {"X-Session-Id": self.test_user_session}
            
            # Test different status filters
            status_filters = ["owned", "wishlist", "previously_owned", "test_ridden"]
            all_passed = True
            
            for status in status_filters:
                response = requests.get(f"{self.base_url}/garage", 
                                      headers=headers, params={"status": status}, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    garage_items = data.get("garage_items", [])
                    
                    # Verify all items match the status filter
                    valid_status = all(item.get("status") == status for item in garage_items)
                    if valid_status:
                        self.log_test(f"Virtual Garage Status Filter - {status}", True, 
                                    f"Found {len(garage_items)} items with status '{status}'")
                    else:
                        self.log_test(f"Virtual Garage Status Filter - {status}", False, 
                                    "Some items don't match status filter")
                        all_passed = False
                else:
                    self.log_test(f"Virtual Garage Status Filter - {status}", False, 
                                f"Status: {response.status_code}")
                    all_passed = False
            
            return all_passed
            
        except Exception as e:
            self.log_test("Virtual Garage Status Filter", False, f"Error: {str(e)}")
            return False

    def test_price_alerts_get_endpoint(self):
        """Test GET /api/price-alerts - Retrieve user's active price alerts (FIXED aggregation pipeline)"""
        if not self.test_user_session:
            self.log_test("Price Alerts GET - Authentication", False, "No user session available")
            return False
        
        try:
            headers = {"X-Session-Id": self.test_user_session}
            
            # First, create a price alert to ensure we have data to test
            if self.motorcycle_ids:
                alert_data = {
                    "motorcycle_id": self.motorcycle_ids[0],
                    "target_price": 12000.0,
                    "condition": "below",
                    "region": "US"
                }
                
                add_response = requests.post(f"{self.base_url}/price-alerts", 
                                           headers=headers, json=alert_data, timeout=10)
                if add_response.status_code != 200:
                    self.log_test("Price Alerts GET - Setup", False, 
                                f"Failed to create test alert: {add_response.status_code}")
                    return False
            
            # Test GET /api/price-alerts
            response = requests.get(f"{self.base_url}/price-alerts", headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                if "price_alerts" not in data:
                    self.log_test("Price Alerts GET - Structure", False, 
                                "Missing 'price_alerts' in response")
                    return False
                
                price_alerts = data["price_alerts"]
                
                # Verify price alerts structure and motorcycle details
                if price_alerts:
                    first_alert = price_alerts[0]
                    required_alert_fields = ["id", "user_id", "motorcycle_id", "target_price", "condition", "is_active", "created_at"]
                    missing_alert_fields = [field for field in required_alert_fields if field not in first_alert]
                    if missing_alert_fields:
                        self.log_test("Price Alerts GET - Alert Structure", False, 
                                    f"Missing price alert fields: {missing_alert_fields}")
                        return False
                    
                    # Verify motorcycle details are properly joined
                    if "motorcycle" not in first_alert:
                        self.log_test("Price Alerts GET - Motorcycle Join", False, 
                                    "Motorcycle details not joined with price alert")
                        return False
                    
                    motorcycle = first_alert["motorcycle"]
                    required_moto_fields = ["id", "manufacturer", "model", "year", "category", "price_usd"]
                    missing_moto_fields = [field for field in required_moto_fields if field not in motorcycle]
                    if missing_moto_fields:
                        self.log_test("Price Alerts GET - Motorcycle Details", False, 
                                    f"Missing motorcycle fields: {missing_moto_fields}")
                        return False
                    
                    # Verify all alerts are active
                    all_active = all(alert.get("is_active", False) for alert in price_alerts)
                    if not all_active:
                        self.log_test("Price Alerts GET - Active Filter", False, 
                                    "Some inactive alerts returned")
                        return False
                    
                    self.log_test("Price Alerts GET - Complete", True, 
                                f"Retrieved {len(price_alerts)} active price alerts with complete motorcycle details")
                    return True
                else:
                    self.log_test("Price Alerts GET - Empty", True, 
                                "No price alerts found (empty alerts)")
                    return True
                    
            elif response.status_code == 401:
                self.log_test("Price Alerts GET", False, "Authentication required (401)")
                return False
            else:
                self.log_test("Price Alerts GET", False, 
                            f"Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            self.log_test("Price Alerts GET", False, f"Error: {str(e)}")
            return False

    def test_objectid_conversion(self):
        """Test that ObjectId conversion is working properly in both endpoints"""
        if not self.test_user_session:
            self.log_test("ObjectId Conversion", False, "No user session available")
            return False
        
        try:
            headers = {"X-Session-Id": self.test_user_session}
            all_passed = True
            
            # Test Virtual Garage ObjectId conversion
            garage_response = requests.get(f"{self.base_url}/garage", headers=headers, timeout=10)
            if garage_response.status_code == 200:
                garage_data = garage_response.json()
                garage_items = garage_data.get("garage_items", [])
                
                for item in garage_items:
                    # Check that _id fields are strings (not ObjectId)
                    if "_id" in item and not isinstance(item["_id"], str):
                        self.log_test("ObjectId Conversion - Garage Items", False, 
                                    f"Garage item _id is not string: {type(item['_id'])}")
                        all_passed = False
                        break
                    
                    if "motorcycle" in item and "_id" in item["motorcycle"]:
                        if not isinstance(item["motorcycle"]["_id"], str):
                            self.log_test("ObjectId Conversion - Garage Motorcycles", False, 
                                        f"Motorcycle _id is not string: {type(item['motorcycle']['_id'])}")
                            all_passed = False
                            break
                
                if all_passed:
                    self.log_test("ObjectId Conversion - Garage", True, 
                                "All ObjectIds properly converted to strings in garage endpoint")
            
            # Test Price Alerts ObjectId conversion
            alerts_response = requests.get(f"{self.base_url}/price-alerts", headers=headers, timeout=10)
            if alerts_response.status_code == 200:
                alerts_data = alerts_response.json()
                price_alerts = alerts_data.get("price_alerts", [])
                
                for alert in price_alerts:
                    # Check that _id fields are strings (not ObjectId)
                    if "_id" in alert and not isinstance(alert["_id"], str):
                        self.log_test("ObjectId Conversion - Price Alerts", False, 
                                    f"Price alert _id is not string: {type(alert['_id'])}")
                        all_passed = False
                        break
                    
                    if "motorcycle" in alert and "_id" in alert["motorcycle"]:
                        if not isinstance(alert["motorcycle"]["_id"], str):
                            self.log_test("ObjectId Conversion - Alert Motorcycles", False, 
                                        f"Motorcycle _id is not string: {type(alert['motorcycle']['_id'])}")
                            all_passed = False
                            break
                
                if all_passed:
                    self.log_test("ObjectId Conversion - Price Alerts", True, 
                                "All ObjectIds properly converted to strings in price alerts endpoint")
            
            return all_passed
            
        except Exception as e:
            self.log_test("ObjectId Conversion", False, f"Error: {str(e)}")
            return False

    def get_summary(self):
        """Return test results summary"""
        return self.test_results

    def run_focused_tests(self):
        """Run focused tests for Virtual Garage and Price Alerts GET endpoints"""
        print("🎯 Starting FOCUSED Virtual Garage and Price Alerts GET Endpoint Testing...")
        print("=" * 80)
        
        # Basic connectivity
        if not self.test_api_root():
            print("❌ API connectivity failed. Stopping tests.")
            return self.get_summary()
        
        # Ensure we have motorcycles and user authentication
        if not self.test_get_motorcycles():
            print("❌ Failed to get motorcycles. Cannot test garage/alerts.")
            return self.get_summary()
        
        if not self.test_user_authentication():
            print("❌ User authentication failed. Cannot test protected endpoints.")
            return self.get_summary()
        
        print("\n🔧 Testing FIXED Virtual Garage GET Endpoints...")
        print("-" * 50)
        
        # Virtual Garage GET endpoint tests
        self.test_virtual_garage_get_endpoint()
        self.test_virtual_garage_status_filtering()
        
        print("\n💰 Testing FIXED Price Alerts GET Endpoints...")
        print("-" * 50)
        
        # Price Alerts GET endpoint tests
        self.test_price_alerts_get_endpoint()
        
        print("\n🔄 Testing ObjectId Conversion...")
        print("-" * 50)
        
        # ObjectId conversion tests
        self.test_objectid_conversion()
        
        return self.get_summary()

if __name__ == "__main__":
    tester = FocusedGarageAlertsAPITester()
    summary = tester.run_focused_tests()
    
    print("\n" + "=" * 60)
    print("🏁 FOCUSED TESTING COMPLETE")
    print("=" * 60)
    
    for result in summary:
        print(result)
    
    # Count results
    passed = sum(1 for result in summary if "✅ PASS" in result)
    failed = sum(1 for result in summary if "❌ FAIL" in result)
    total = len(summary)
    
    print(f"\n📊 SUMMARY: {passed}/{total} tests passed ({failed} failed)")
    
    if failed == 0:
        print("🎉 All focused tests passed! The FIXED Virtual Garage and Price Alerts GET endpoints are working perfectly.")
        sys.exit(0)
    else:
        print(f"⚠️ {failed} test(s) failed. Please check the API implementation.")
        sys.exit(1)