#!/usr/bin/env python3
"""
Daily Update Bot System API Testing for Byke-Dream
Tests the complete daily update workflow including job management and regional customizations.
"""

import requests
import json
import time
from typing import Dict, List, Any

# Backend URL from environment
BACKEND_URL = "https://b4e17258-5cf1-4bb8-a561-56760731f05a.preview.emergentagent.com/api"

class DailyUpdateTester:
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
                    
                    # Wait for completion and check again
                    if status == "running":
                        time.sleep(10)  # Wait for job to complete
                        return self._check_job_completion(job_id)
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
    
    def _check_job_completion(self, job_id: str):
        """Check if job has completed"""
        try:
            response = requests.get(f"{self.base_url}/update-system/job-status/{job_id}", timeout=10)
            if response.status_code == 200:
                data = response.json()
                status = data.get("status")
                if status in ["completed", "failed"]:
                    duration = data.get("duration_seconds", "unknown")
                    stats = data.get("stats", {})
                    self.log_test("Job Completion Check", True, 
                                f"Job {status} in {duration}s. Stats: {stats}")
                    return True
                else:
                    self.log_test("Job Completion Check", True, f"Job still {status}")
                    return True
            else:
                self.log_test("Job Completion Check", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Job Completion Check", False, f"Error: {str(e)}")
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
                    
                    # Test with limit parameter
                    return self._test_update_history_with_limit()
                else:
                    self.log_test("Update History API", False, "Invalid data structure")
                    return False
            else:
                self.log_test("Update History API", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Update History API", False, f"Error: {str(e)}")
            return False
    
    def _test_update_history_with_limit(self):
        """Test update history with limit parameter"""
        try:
            response = requests.get(f"{self.base_url}/update-system/update-history", 
                                  params={"limit": 5}, timeout=10)
            if response.status_code == 200:
                data = response.json()
                history_count = data.get("count", 0)
                self.log_test("Update History with Limit", True, 
                            f"Retrieved {history_count} records with limit=5")
                return True
            else:
                self.log_test("Update History with Limit", False, f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Update History with Limit", False, f"Error: {str(e)}")
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
    
    def test_workflow_integration(self):
        """Test the complete daily update workflow"""
        print("\n🔄 Testing Complete Daily Update Workflow...")
        print("-" * 60)
        
        # Step 1: Trigger daily update
        success, job_id = self.test_trigger_daily_update()
        if not success:
            return False
        
        # Step 2: Monitor job status
        if job_id:
            self.test_job_status_monitoring(job_id)
        
        # Step 3: Check update history (should have new entries)
        self.test_update_history()
        
        # Step 4: Verify regional customizations
        self.test_regional_customizations()
        
        return True
    
    def run_all_tests(self):
        """Run all Daily Update Bot System tests"""
        print("🤖 Starting Daily Update Bot System API Tests")
        print("=" * 60)
        
        # Test complete workflow
        self.test_workflow_integration()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 DAILY UPDATE SYSTEM TEST SUMMARY")
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
        
        success_rate = len(passed_tests) / len(self.test_results) * 100 if self.test_results else 0
        print(f"\nSuccess Rate: {success_rate:.1f}%")
        
        return len(failed_tests) == 0

def main():
    """Main test execution"""
    tester = DailyUpdateTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 All Daily Update Bot System tests passed!")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check the details above.")
        return 1

if __name__ == "__main__":
    exit(main())