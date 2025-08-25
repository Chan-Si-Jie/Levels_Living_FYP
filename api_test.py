#!/usr/bin/env python3
"""
Comprehensive API Testing Script for Levels Living Microservices
Tests UserMS, CustomerMS, and InventoryMS with Docker-based endpoints
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Optional, Dict, Any, Tuple
import argparse

# Configuration
CONFIG = {
    'base_urls': {
        'user': 'http://localhost:5001',
        'customer': 'http://localhost:5002',
        'inventory': 'http://localhost:5003'
    },
    'timeout': 30,
    'retry_attempts': 3,
    'retry_delay': 2
}

# Global state
session_data = {
    'access_token': None,
    'refresh_token': None,
    'session_id': None,
    'user_data': None
}

test_results = {
    'total': 0,
    'passed': 0,
    'failed': 0,
    'errors': []
}

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_colored(text: str, color: str = Colors.ENDC) -> None:
    """Print colored text to terminal"""
    print(f"{color}{text}{Colors.ENDC}")

def print_separator(title: str, char: str = "=", width: int = 80) -> None:
    """Print a separator with title"""
    print_colored(f"\n{char * width}", Colors.BLUE)
    print_colored(f" {title.upper()}", Colors.BOLD + Colors.BLUE)
    print_colored(f"{char * width}", Colors.BLUE)

def log_test_result(test_name: str, passed: bool, response: Optional[requests.Response] = None, 
                   error: Optional[str] = None) -> None:
    """Log test result and update statistics"""
    test_results['total'] += 1
    
    if passed:
        test_results['passed'] += 1
        print_colored(f"[PASS] {test_name}", Colors.GREEN)
    else:
        test_results['failed'] += 1
        print_colored(f"[FAIL] {test_name}", Colors.RED)
        
        if error:
            test_results['errors'].append(f"{test_name}: {error}")
            print_colored(f"  Error: {error}", Colors.RED)
        elif response:
            try:
                error_detail = response.json().get('error', 'Unknown error')
                test_results['errors'].append(f"{test_name}: HTTP {response.status_code} - {error_detail}")
                print_colored(f"  HTTP {response.status_code}: {error_detail}", Colors.RED)
                if response.status_code >= 500:
                    print_colored(f"  Server Error - Check service logs", Colors.YELLOW)
            except:
                test_results['errors'].append(f"{test_name}: HTTP {response.status_code} - {response.text[:100]}")
                print_colored(f"  HTTP {response.status_code}: {response.text[:100]}", Colors.RED)

def make_request(method: str, url: str, data: Optional[Dict] = None, 
                headers: Optional[Dict] = None, expected_status: int = 200,
                timeout: int = None) -> Tuple[Optional[requests.Response], Optional[Dict]]:
    """Make HTTP request with error handling and retries"""
    if timeout is None:
        timeout = CONFIG['timeout']
    
    if headers is None:
        headers = {'Content-Type': 'application/json'}
    
    for attempt in range(CONFIG['retry_attempts']):
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout, params=data)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)
            elif method.upper() == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=timeout)
            elif method.upper() == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Try to parse JSON response
            try:
                response_data = response.json()
            except ValueError:
                # Not JSON or empty response
                response_data = {'raw_text': response.text} if response.text else {}
            except Exception:
                response_data = {'raw_text': response.text} if response.text else {}
            
            # Return the response regardless of status code
            return response, response_data
            
        except requests.exceptions.ConnectionError as e:
            if attempt < CONFIG['retry_attempts'] - 1:
                print_colored(f"Connection error, retrying in {CONFIG['retry_delay']}s... ({attempt + 1}/{CONFIG['retry_attempts']})", Colors.YELLOW)
                time.sleep(CONFIG['retry_delay'])
            else:
                print_colored(f"Connection failed after {CONFIG['retry_attempts']} attempts: {str(e)}", Colors.RED)
                return None, None
        except requests.exceptions.Timeout as e:
            if attempt < CONFIG['retry_attempts'] - 1:
                print_colored(f"Request timeout, retrying in {CONFIG['retry_delay']}s... ({attempt + 1}/{CONFIG['retry_attempts']})", Colors.YELLOW)
                time.sleep(CONFIG['retry_delay'])
            else:
                print_colored(f"Request timed out after {CONFIG['retry_attempts']} attempts", Colors.RED)
                return None, None
        except Exception as e:
            print_colored(f"Unexpected request error: {type(e).__name__}: {str(e)}", Colors.RED)
            return None, None
    
    return None, None

def get_auth_headers() -> Dict[str, str]:
    """Get authorization headers with current token"""
    headers = {'Content-Type': 'application/json'}
    if session_data['access_token']:
        headers['Authorization'] = f"Bearer {session_data['access_token']}"
    return headers

def test_service_health(service_name: str, base_url: str) -> bool:
    """Test service health endpoint"""
    print_colored(f"\nTesting {service_name} Health...", Colors.BLUE)
    
    response, data = make_request('GET', f"{base_url}/health")
    
    if response is not None and response.status_code == 200:
        log_test_result(f"{service_name} Health Check", True)
        if data:
            print(f"  Status: {data.get('status', 'N/A')}")
            print(f"  Database: {data.get('database', 'N/A')}")
            print(f"  Redis: {data.get('redis', 'N/A')}")
        return True
    else:
        log_test_result(f"{service_name} Health Check", False, response)
        return False

def test_user_registration() -> bool:
    """Test user registration endpoints"""
    print_colored(f"\nTesting User Registration...", Colors.BLUE)
    base_url = CONFIG['base_urls']['user']
    
    # Test cases for user registration
    test_cases = [
        {
            'name': 'Valid Admin Registration',
            'data': {
                'email': 'admin@levels.sg',
                'password': 'securePassword123!',
                'role': 'admin'
            },
            'expected_status': 201,
            'should_pass': True
        },
        {
            'name': 'Valid Customer Service Registration',
            'data': {
                'email': 'cs@levels.sg',
                'password': 'securePassword123!',
                'role': 'customer_service'
            },
            'expected_status': 201,
            'should_pass': True
        },
        {
            'name': 'Valid Warehouse Registration',
            'data': {
                'email': 'warehouse@levels.sg',
                'password': 'securePassword123!',
                'role': 'warehouse'
            },
            'expected_status': 201,
            'should_pass': True
        },
        {
            'name': 'Invalid Email Format',
            'data': {
                'email': 'invalid-email',
                'password': 'securePassword123!',
                'role': 'admin'
            },
            'expected_status': 400,
            'should_pass': False
        },
        {
            'name': 'Weak Password',
            'data': {
                'email': 'test@levels.sg',
                'password': '123',
                'role': 'admin'
            },
            'expected_status': 400,
            'should_pass': False
        },
        {
            'name': 'Invalid Role',
            'data': {
                'email': 'test2@levels.sg',
                'password': 'securePassword123!',
                'role': 'invalid_role'
            },
            'expected_status': 400,
            'should_pass': False
        },
        {
            'name': 'Missing Required Fields',
            'data': {
                'email': 'test3@levels.sg'
                # Missing password and role
            },
            'expected_status': 400,
            'should_pass': False
        }
    ]
    
    all_passed = True
    for test_case in test_cases:
        response, data = make_request('POST', f"{base_url}/auth/register", test_case['data'])
        if response is not None:
            # For tests that should pass: accept both 201 (created) and 409 (user exists)
            # For tests that should fail: check if we get the expected error status
            if test_case['should_pass']:
                passed = response.status_code in [test_case['expected_status'], 409]  # Accept user exists
            else:
                passed = response.status_code == test_case['expected_status']
            log_test_result(test_case['name'], passed, response)
            if not passed:
                all_passed = False
        else:
            log_test_result(test_case['name'], False, None, "Connection failed")
            all_passed = False
    
    # Test duplicate registration
    duplicate_data = {
        'email': 'admin@levels.sg',
        'password': 'securePassword123!',
        'role': 'admin'
    }
    response, data = make_request('POST', f"{base_url}/auth/register", duplicate_data)
    passed = response is not None and response.status_code == 409
    log_test_result('Duplicate Email Registration (should fail)', passed, response)
    if not passed:
        all_passed = False
    
    return all_passed

def test_user_authentication() -> bool:
    """Test user login and authentication"""
    print_colored(f"\nTesting User Authentication...", Colors.BLUE)
    base_url = CONFIG['base_urls']['user']
    
    # Create a fresh user for login testing
    test_user_data = {
        'email': 'login_test@levels.sg',
        'password': 'securePassword123!',
        'role': 'admin'
    }
    
    print("  Creating test user for login...")
    response, data = make_request('POST', f"{base_url}/auth/register", test_user_data)
    if response is not None and response.status_code in [201, 409]:  # Success or already exists
        print("  Test user ready")
    else:
        print("  Could not create test user, trying with existing admin user")
    
    # Valid login with the test user
    login_data = {
        'email': 'login_test@levels.sg',
        'password': 'securePassword123!'
    }
    
    response, data = make_request('POST', f"{base_url}/auth/login", login_data)
    
    if response is not None and response.status_code == 200 and data:
        session_data['access_token'] = data.get('access_token')
        session_data['refresh_token'] = data.get('refresh_token')
        session_data['session_id'] = data.get('session_id')
        session_data['user_data'] = data.get('user')
        
        log_test_result('Valid Login', True)
        print(f"  User ID: {data.get('user', {}).get('user_id', 'N/A')}")
        print(f"  Role: {data.get('user', {}).get('role', 'N/A')}")
        print(f"  Token received: {'Yes' if session_data['access_token'] else 'No'}")
    else:
        log_test_result('Valid Login', False, response)
        return False
    
    # Test invalid credentials
    invalid_login = {
        'email': 'login_test@levels.sg',
        'password': 'wrongpassword'
    }
    response, data = make_request('POST', f"{base_url}/auth/login", invalid_login)
    passed = response is not None and response.status_code == 401
    log_test_result('Invalid Password (should fail)', passed, response)
    
    # Test missing fields
    incomplete_login = {'email': 'login_test@levels.sg'}
    response, data = make_request('POST', f"{base_url}/auth/login", incomplete_login)
    passed = response is not None and response.status_code == 400
    log_test_result('Missing Password (should fail)', passed, response)
    
    return True

def test_protected_user_endpoints() -> bool:
    """Test protected user endpoints"""
    print_colored(f"\nTesting Protected User Endpoints...", Colors.BLUE)
    base_url = CONFIG['base_urls']['user']
    
    if not session_data['access_token']:
        print_colored("No access token available, skipping protected endpoint tests", Colors.YELLOW)
        return False
    
    headers = get_auth_headers()
    all_passed = True
    
    # Test get profile
    response, data = make_request('GET', f"{base_url}/auth/profile", headers=headers)
    passed = response is not None and response.status_code == 200
    log_test_result('Get User Profile', passed, response)
    if not passed:
        all_passed = False
    
    # Test token validation
    response, data = make_request('POST', f"{base_url}/auth/validate", headers=headers)
    passed = response is not None and response.status_code == 200
    log_test_result('Token Validation', passed, response)
    if not passed:
        all_passed = False
    
    # Test list users (admin only)
    response, data = make_request('GET', f"{base_url}/auth/users", headers=headers)
    passed = response is not None and response.status_code == 200
    log_test_result('List Users (Admin)', passed, response)
    if not passed:
        all_passed = False
    
    return all_passed

def test_customer_operations() -> bool:
    """Test customer service operations"""
    print_colored(f"\nTesting Customer Operations...", Colors.BLUE)
    base_url = CONFIG['base_urls']['customer']
    
    if not session_data['access_token']:
        print_colored("No access token available, skipping customer tests", Colors.YELLOW)
        return False
    
    headers = get_auth_headers()
    all_passed = True
    customer_id = None
    
    # Test customer creation
    customer_data = {
        'customer_contact': '+6591234567',
        'customer_street': '123 Orchard Road',
        'customer_unit': '#12-34',
        'customer_postal_code': '238123',
        'housing_type': 'Condo',
        'delivery_preferences': {
            'preferred_time': 'morning',
            'special_instructions': 'Call before delivery'
        },
        'communication_preferences': {
            'sms': True,
            'email': False
        }
    }
    
    response, data = make_request('POST', f"{base_url}/customers", customer_data, headers)
    if response is not None and response.status_code == 201 and data:
        customer_id = data.get('customer', {}).get('customer_id')
        log_test_result('Create Valid Customer', True)
        print(f"  Customer ID: {customer_id}")
    else:
        log_test_result('Create Valid Customer', False, response)
        all_passed = False
    
    # Test another customer
    customer_data2 = {
        'customer_contact': '+6598765432',
        'customer_street': '456 Marina Bay',
        'customer_unit': '#05-67',
        'customer_postal_code': '179103',
        'housing_type': 'HDB'
    }
    response, data = make_request('POST', f"{base_url}/customers", customer_data2, headers)
    passed = response is not None and response.status_code == 201
    log_test_result('Create Second Customer', passed, response)
    if not passed:
        all_passed = False
    
    # Test invalid customer data
    invalid_customer = {
        'customer_contact': '1234567',  # Invalid format
        'customer_postal_code': '238123'
    }
    response, data = make_request('POST', f"{base_url}/customers", invalid_customer, headers)
    passed = response is not None and response.status_code == 400
    log_test_result('Invalid Contact Format (should fail)', passed, response)
    if not passed:
        all_passed = False
    
    # Test duplicate customer
    response, data = make_request('POST', f"{base_url}/customers", customer_data, headers)
    passed = response is not None and response.status_code == 409
    log_test_result('Duplicate Customer (should fail)', passed, response)
    if not passed:
        all_passed = False
    
    # Test customer retrieval
    if customer_id:
        response, data = make_request('GET', f"{base_url}/customers/{customer_id}", headers=headers)
        passed = response is not None and response.status_code == 200
        log_test_result('Get Customer by ID', passed, response)
        if not passed:
            all_passed = False
        
        response, data = make_request('GET', f"{base_url}/customers/contact/+6591234567", headers=headers)
        passed = response is not None and response.status_code == 200
        log_test_result('Get Customer by Contact', passed, response)
        if not passed:
            all_passed = False
    
    # Test search customers
    response, data = make_request('GET', f"{base_url}/customers", headers=headers)
    passed = response is not None and response.status_code == 200
    log_test_result('Search All Customers', passed, response)
    if not passed:
        all_passed = False
    
    # Test customer validation
    validation_data = {
        'customer_contact': '+6587654321',
        'customer_postal_code': '560123',
        'housing_type': 'HDB'
    }
    response, data = make_request('POST', f"{base_url}/customers/validate", validation_data, headers)
    passed = response is not None and response.status_code == 200
    log_test_result('Valid Customer Data Validation', passed, response)
    if not passed:
        all_passed = False
    
    return all_passed

def test_inventory_operations() -> bool:
    """Test inventory service operations"""
    print_colored(f"\nTesting Inventory Operations...", Colors.BLUE)
    base_url = CONFIG['base_urls']['inventory']
    
    if not session_data['access_token']:
        print_colored("No access token available, skipping inventory tests", Colors.YELLOW)
        return False
    
    headers = get_auth_headers()
    all_passed = True
    test_sku = None
    
    # Test product creation (admin/hq only)
    product_data = {
        'sku': 'TEST001',
        'item_name': 'Test Office Chair',
        'variant': 'Standard',
        'category': 'Furniture',
        'subcategory': 'Seating',
        'description': 'Ergonomic office chair for testing',
        'unit_price': 299.99,
        'weight_per_unit': 15.5,
        'volume_per_unit': 0.8,
        'delivery_type': 'standard',
        'special_handling_required': False,
        'assembly_required': False,
        'showroom_item': False,
        'handling_instructions': 'Handle with care',
        'storage_location': 'A-01-05',
        'supplier': 'Test Supplier Co.',
        'supplier_sku': 'TS-CHAIR-001',
        'dimensions': {
            'length': 60,
            'width': 60,
            'height': 110
        },
        'image_urls': [
            'https://example.com/chair1.jpg',
            'https://example.com/chair2.jpg'
        ],
        'product_tags': ['office', 'ergonomic', 'chair']
    }
    
    response, data = make_request('POST', f"{base_url}/inventory/products", product_data, headers)
    if response is not None and response.status_code == 201:
        test_sku = product_data['sku']
        log_test_result('Create Product', True)
        print(f"  Created SKU: {test_sku}")
    else:
        log_test_result('Create Product', False, response)
        all_passed = False
    
    # Test another product with different delivery type
    heavy_product_data = {
        'sku': 'HEAVY001',
        'item_name': 'Heavy Desk',
        'category': 'Furniture',
        'delivery_type': 'heavy_item',
        'weight_per_unit': 85.0,
        'volume_per_unit': 3.2,
        'special_handling_required': True,
        'assembly_required': True,
        'unit_price': 899.99
    }
    
    response, data = make_request('POST', f"{base_url}/inventory/products", heavy_product_data, headers)
    passed = response is not None and response.status_code == 201
    log_test_result('Create Heavy Item Product', passed, response)
    if not passed:
        all_passed = False
    
    # Test duplicate SKU
    response, data = make_request('POST', f"{base_url}/inventory/products", product_data, headers)
    passed = response is not None and response.status_code == 409
    log_test_result('Duplicate SKU (should fail)', passed, response)
    if not passed:
        all_passed = False
    
    # Test invalid delivery type
    invalid_product = {
        'sku': 'INVALID001',
        'item_name': 'Invalid Product',
        'delivery_type': 'invalid_type'
    }
    response, data = make_request('POST', f"{base_url}/inventory/products", invalid_product, headers)
    passed = response is not None and response.status_code == 400
    log_test_result('Invalid Delivery Type (should fail)', passed, response)
    if not passed:
        all_passed = False
    
    # Test get product by SKU
    if test_sku:
        response, data = make_request('GET', f"{base_url}/inventory/products/{test_sku}", headers=headers)
        passed = response is not None and response.status_code == 200
        log_test_result('Get Product by SKU', passed, response)
        if not passed:
            all_passed = False
    
    # Test search products
    response, data = make_request('GET', f"{base_url}/inventory/products", headers=headers)
    passed = response is not None and response.status_code == 200
    log_test_result('Search All Products', passed, response)
    if not passed:
        all_passed = False
    
    # Test search with filters
    search_params = {'category': 'Furniture', 'limit': 10}
    response, data = make_request('GET', f"{base_url}/inventory/products", search_params, headers)
    passed = response is not None and response.status_code == 200
    log_test_result('Search Products with Filters', passed, response)
    if not passed:
        all_passed = False
    
    # Test delivery requirements endpoint
    delivery_req_data = {'skus': ['TEST001', 'HEAVY001']}
    response, data = make_request('POST', f"{base_url}/inventory/delivery-requirements", delivery_req_data, headers)
    passed = response is not None and response.status_code in [200, 207]  # 207 for partial success
    log_test_result('Get Delivery Requirements', passed, response)
    if not passed:
        all_passed = False
    
    # Test delivery types endpoint
    response, data = make_request('GET', f"{base_url}/inventory/delivery-types", headers=headers)
    passed = response is not None and response.status_code == 200
    log_test_result('Get Delivery Types', passed, response)
    if not passed:
        all_passed = False
    
    # Test product update
    if test_sku:
        update_data = {
            'unit_price': 349.99,
            'description': 'Updated ergonomic office chair for testing'
        }
        response, data = make_request('PUT', f"{base_url}/inventory/products/{test_sku}", update_data, headers)
        passed = response is not None and response.status_code == 200
        log_test_result('Update Product', passed, response)
        if not passed:
            all_passed = False
    
    return all_passed

def test_unauthorized_access() -> bool:
    """Test unauthorized access to protected endpoints"""
    print_colored(f"\nTesting Unauthorized Access...", Colors.BLUE)
    all_passed = True
    
    # Test without token
    endpoints = [
        ('GET', f"{CONFIG['base_urls']['user']}/auth/profile", "User Profile"),
        ('GET', f"{CONFIG['base_urls']['customer']}/customers", "Customer List"),
        ('GET', f"{CONFIG['base_urls']['inventory']}/inventory/products", "Product List")
    ]
    
    for method, url, description in endpoints:
        response, data = make_request(method, url)
        passed = response is not None and response.status_code == 401
        log_test_result(f"Access {description} Without Token (should fail)", passed, response)
        if not passed:
            all_passed = False
    
    # Test with invalid token
    invalid_headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer invalid_token_here'
    }
    
    for method, url, description in endpoints:
        response, data = make_request(method, url, headers=invalid_headers)
        passed = response is not None and response.status_code == 422  # JWT decode error
        log_test_result(f"Access {description} With Invalid Token (should fail)", passed, response)
        if not passed:
            all_passed = False
    
    return all_passed

def test_user_logout() -> bool:
    """Test user logout"""
    print_colored(f"\nTesting User Logout...", Colors.BLUE)
    base_url = CONFIG['base_urls']['user']
    
    if not session_data['access_token']:
        print_colored("No access token available, skipping logout test", Colors.YELLOW)
        return False
    
    headers = get_auth_headers()
    logout_data = {}
    if session_data['session_id']:
        logout_data['session_id'] = session_data['session_id']
    
    response, data = make_request('POST', f"{base_url}/auth/logout", logout_data, headers)
    passed = response is not None and response.status_code == 200
    log_test_result('User Logout', passed, response)
    
    if passed:
        # Clear session data
        session_data['access_token'] = None
        session_data['refresh_token'] = None
        session_data['session_id'] = None
        session_data['user_data'] = None
    
    return passed

def test_edge_cases() -> bool:
    """Test various edge cases and error conditions"""
    print_colored(f"\nTesting Edge Cases...", Colors.BLUE)
    all_passed = True
    
    # Test malformed JSON
    headers = {'Content-Type': 'application/json'}
    response = None
    try:
        response = requests.post(f"{CONFIG['base_urls']['user']}/auth/login", 
                               data="invalid json", headers=headers, timeout=CONFIG['timeout'])
    except:
        pass
    
    passed = response is not None and response.status_code == 400
    log_test_result('Malformed JSON (should fail)', passed, response)
    if not passed:
        all_passed = False
    
    # Test very long input
    if session_data['access_token']:
        headers = get_auth_headers()
        long_data = {
            'customer_contact': '+6599999999',
            'customer_postal_code': '1' * 100  # Way too long
        }
        response, data = make_request('POST', f"{CONFIG['base_urls']['customer']}/customers", long_data, headers)
        passed = response is not None and response.status_code == 400
        log_test_result('Very Long Postal Code (should fail)', passed, response)
        if not passed:
            all_passed = False
    
    return all_passed

def print_test_summary() -> None:
    """Print comprehensive test summary"""
    print_separator("TEST SUMMARY", "=", 80)
    
    total = test_results['total']
    passed = test_results['passed']
    failed = test_results['failed']
    
    print_colored(f"Total Tests: {total}", Colors.BOLD)
    print_colored(f"Passed: {passed}", Colors.GREEN)
    print_colored(f"Failed: {failed}", Colors.RED if failed > 0 else Colors.GREEN)
    
    if total > 0:
        success_rate = (passed / total) * 100
        print_colored(f"Success Rate: {success_rate:.1f}%", 
                     Colors.GREEN if success_rate >= 90 else Colors.YELLOW if success_rate >= 70 else Colors.RED)
    
    if test_results['errors']:
        print_colored(f"\nERRORS ENCOUNTERED:", Colors.RED)
        for error in test_results['errors']:
            print_colored(f"  • {error}", Colors.RED)
    
    print_separator("TEST COMPLETED", "=", 80)

def check_services_running() -> bool:
    """Check if all required services are running"""
    print_colored("Checking if services are running...", Colors.BLUE)
    
    services = [
        ('UserMS', CONFIG['base_urls']['user']),
        ('CustomerMS', CONFIG['base_urls']['customer']),
        ('InventoryMS', CONFIG['base_urls']['inventory'])
    ]
    
    all_running = True
    for service_name, base_url in services:
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            if response is not None and response.status_code == 200:
                print_colored(f"  [OK] {service_name} is running", Colors.GREEN)
            else:
                print_colored(f"  [FAIL] {service_name} returned status {response.status_code}", Colors.RED)
                all_running = False
        except requests.exceptions.ConnectionError:
            print_colored(f"  [FAIL] {service_name} is not reachable", Colors.RED)
            all_running = False
        except Exception as e:
            print_colored(f"  [FAIL] {service_name} error: {str(e)}", Colors.RED)
            all_running = False
    
    if not all_running:
        print_colored("\nServices not running. Make sure to start them with:", Colors.YELLOW)
        print_colored("  docker-compose up -d", Colors.YELLOW)
        print_colored("  docker-compose ps  # Check service status", Colors.YELLOW)
    
    return all_running

def run_all_tests(args: argparse.Namespace) -> None:
    """Run all test suites"""
    print_separator(f"LEVELS LIVING API COMPREHENSIVE TESTS", "=", 80)
    print_colored(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", Colors.BLUE)
    print_colored(f"UserMS URL: {CONFIG['base_urls']['user']}", Colors.BLUE)
    print_colored(f"CustomerMS URL: {CONFIG['base_urls']['customer']}", Colors.BLUE)
    print_colored(f"InventoryMS URL: {CONFIG['base_urls']['inventory']}", Colors.BLUE)
    
    # Check if services are running
    if not check_services_running():
        if not args.force:
            print_colored("\nAborting tests. Use --force to continue anyway.", Colors.RED)
            return
        else:
            print_colored("\nForcing tests to continue...", Colors.YELLOW)
    
    try:
        # Run test suites
        test_service_health('UserMS', CONFIG['base_urls']['user'])
        test_service_health('CustomerMS', CONFIG['base_urls']['customer'])  
        test_service_health('InventoryMS', CONFIG['base_urls']['inventory'])
        
        test_user_registration()
        test_user_authentication()
        test_protected_user_endpoints()
        
        test_customer_operations()
        test_inventory_operations()
        
        test_unauthorized_access()
        test_edge_cases()
        
        test_user_logout()
        
    except KeyboardInterrupt:
        print_colored("\nTests interrupted by user", Colors.YELLOW)
    except Exception as e:
        print_colored(f"\nUnexpected error during testing: {str(e)}", Colors.RED)
        test_results['errors'].append(f"Unexpected error: {str(e)}")
    
    finally:
        print_test_summary()

def main():
    """Main function with argument parsing"""
    parser = argparse.ArgumentParser(description='Comprehensive API Testing for Levels Living Microservices')
    parser.add_argument('--force', action='store_true', 
                       help='Force tests to run even if services appear to be down')
    parser.add_argument('--timeout', type=int, default=30,
                       help='Request timeout in seconds (default: 30)')
    parser.add_argument('--retries', type=int, default=3,
                       help='Number of retry attempts for failed requests (default: 3)')
    
    args = parser.parse_args()
    
    # Update configuration
    CONFIG['timeout'] = args.timeout
    CONFIG['retry_attempts'] = args.retries
    
    run_all_tests(args)

if __name__ == "__main__":
    main()