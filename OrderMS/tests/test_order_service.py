# OrderMS/tests/test_order_service.py
import pytest
import json
import os
from datetime import datetime
from app import orchestrator


def test_health_check(client, mock_db):
    """Test health check endpoint"""
    # Mock successful database connection
    mock_db.fetchone.return_value = {"count": 1}
    
    response = client.get('/health')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['service'] == 'order-service'
    assert data['status'] == 'ok'


def test_create_order_unauthorized(client, mock_db, mock_service_clients):
    """Test creating order without authentication should fail"""
    order_data = {
        "customer_id": "test-customer-123",
        "items": [
            {"sku": "TEST-001", "quantity": 2}
        ]
    }
    
    response = client.post(
        '/create_order',
        data=json.dumps(order_data),
        content_type='application/json'
    )
    
    # Without auth_token, JWT verification should fail
    assert response.status_code == 401


def test_create_order_missing_customer_id(client, mock_db, auth_token, mock_service_clients):
    """Test creating order without customer_id returns 400"""
    order_data = {
        "items": [
            {"sku": "TEST-001", "quantity": 2}
        ]
    }
    
    response = client.post(
        '/create_order',
        data=json.dumps(order_data),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'customer_id is required' in data['error']


def test_create_order_missing_items(client, mock_db, auth_token, mock_service_clients):
    """Test creating order without items returns 400"""
    order_data = {
        "customer_id": "test-customer-123"
    }
    
    response = client.post(
        '/create_order',
        data=json.dumps(order_data),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'items are required' in data['error']


def test_create_order_success(client, mock_db, auth_token, mock_service_clients):
    """Test successful order creation"""
    order_data = {
        "customer_id": "test-customer-123",
        "items": [
            {"sku": "TEST-001", "quantity": 2}
        ],
        "special_instructions": "Handle with care"
    }
    
    # Mock customer service response
    customer_data = {
        "customer_id": "test-customer-123",
        "customer_name": "Test Customer",
        "customer_contact": "12345678"
    }
    
    # Mock inventory service response for each SKU lookup
    # validate_order_items calls inventory_service.get(f"/inventory/{sku}")
    inventory_item = {
        "sku": "TEST-001",
        "item_name": "Test Product",
        "variant": "Standard",
        "unit_price": 299.99,
        "delivery_type": "standard",
        "is_active": True,
        "special_handling_required": False,
        "assembly_required": False
    }
    
    # Configure mock service responses
    mock_service_clients.json.side_effect = [
        customer_data,  # Customer validation
        inventory_item  # Inventory validation for TEST-001
    ]
    
    # Mock database operations
    mock_db.rowcount = 1
    
    response = client.post(
        '/create_order',
        data=json.dumps(order_data),
        content_type='application/json'
    )
    
    assert response.status_code == 201
    data = response.get_json()
    assert 'order_id' in data
    assert 'order_no' in data
    assert data['status'] == 'validated'  # Order is auto-validated after creation


def test_create_order_empty_body(client, auth_token):
    """Test create order with empty JSON body"""
    # Test with empty JSON object - empty dict {} is falsy in Python
    response = client.post(
        '/create_order',
        json={}  # Empty JSON object
    )
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    # Empty dict {} is falsy, so "not data" check catches it
    assert 'Request body required' in data['error']


def test_create_order_orchestrator_error(client, mock_db, auth_token, mock_service_clients):
    """Test create order when orchestrator returns an error"""
    order_data = {
        "customer_id": "invalid-customer",
        "items": [{"sku": "TEST-001", "quantity": 2}]
    }
    
    # Mock customer service to return None (customer not found)
    mock_service_clients.json.return_value = None
    
    response = client.post(
        '/create_order',
        data=json.dumps(order_data),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data


def test_create_order_customer_not_found(client, mock_db, auth_token, mock_service_clients):
    """Test create order when customer does not exist"""
    order_data = {
        "customer_id": "nonexistent-customer",
        "items": [{"sku": "TEST-001", "quantity": 2}]
    }
    
    # Mock customer service to return None
    mock_service_clients.json.return_value = None
    
    response = client.post(
        '/create_order',
        data=json.dumps(order_data),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert 'Customer not found' in data['error']


def test_create_order_empty_items_list(client, mock_db, auth_token, mock_service_clients):
    """Test create order with empty items list"""
    order_data = {
        "customer_id": "test-customer-123",
        "items": []  # Empty items list
    }
    
    # Mock customer service
    mock_service_clients.json.return_value = {
        "customer_id": "test-customer-123",
        "customer_name": "Test Customer"
    }
    
    response = client.post(
        '/create_order',
        data=json.dumps(order_data),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    # Empty list is caught at endpoint level with "items are required"
    assert 'items are required' in data['error']


def test_create_order_sku_not_found(client, mock_db, auth_token, mock_service_clients):
    """Test create order when SKU is not found in inventory"""
    order_data = {
        "customer_id": "test-customer-123",
        "items": [{"sku": "INVALID-SKU", "quantity": 2}]
    }
    
    # Mock customer service response
    customer_data = {
        "customer_id": "test-customer-123",
        "customer_name": "Test Customer"
    }
    
    # Mock inventory service to return None (SKU not found)
    mock_service_clients.json.side_effect = [
        customer_data,  # Customer validation
        None  # Inventory lookup returns None
    ]
    
    response = client.post(
        '/create_order',
        data=json.dumps(order_data),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert 'not found in inventory' in data['error']


def test_create_order_inactive_product(client, mock_db, auth_token, mock_service_clients):
    """Test create order when product is inactive"""
    order_data = {
        "customer_id": "test-customer-123",
        "items": [{"sku": "INACTIVE-001", "quantity": 2}]
    }
    
    # Mock customer service
    customer_data = {
        "customer_id": "test-customer-123",
        "customer_name": "Test Customer"
    }
    
    # Mock inventory service with inactive product
    inventory_item = {
        "sku": "INACTIVE-001",
        "item_name": "Inactive Product",
        "is_active": False  # Product is not active
    }
    
    mock_service_clients.json.side_effect = [
        customer_data,
        inventory_item
    ]
    
    response = client.post(
        '/create_order',
        data=json.dumps(order_data),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert 'not active' in data['error']


def test_create_order_with_delivery_address(client, mock_db, auth_token, mock_service_clients):
    """Test create order when customer has delivery address (triggers delivery creation)"""
    order_data = {
        "customer_id": "test-customer-123",
        "items": [{"sku": "TEST-001", "quantity": 2}]
    }
    
    # Mock customer with lat/lng
    customer_data = {
        "customer_id": "test-customer-123",
        "customer_name": "Test Customer",
        "latitude": 1.3521,
        "longitude": 103.8198
    }
    
    # Mock inventory
    inventory_item = {
        "sku": "TEST-001",
        "item_name": "Test Product",
        "variant": "Standard",
        "unit_price": 299.99,
        "delivery_type": "standard",
        "is_active": True,
        "special_handling_required": False,
        "assembly_required": False
    }
    
    # Mock delivery service response
    delivery_response = {
        "jobId": "delivery-job-123",
        "status": "created"
    }
    
    mock_service_clients.json.side_effect = [
        customer_data,
        inventory_item,
        delivery_response  # Delivery creation response
    ]
    
    mock_db.rowcount = 1
    
    response = client.post(
        '/create_order',
        data=json.dumps(order_data),
        content_type='application/json'
    )
    
    assert response.status_code == 201
    data = response.get_json()
    assert 'order_id' in data
    assert data['delivery_job_id'] == 'delivery-job-123'


def test_create_order_without_delivery_address(client, mock_db, auth_token, mock_service_clients):
    """Test create order when customer has no delivery address"""
    order_data = {
        "customer_id": "test-customer-123",
        "items": [{"sku": "TEST-001", "quantity": 2}]
    }
    
    # Mock customer WITHOUT lat/lng
    customer_data = {
        "customer_id": "test-customer-123",
        "customer_name": "Test Customer"
        # No latitude/longitude
    }
    
    # Mock inventory
    inventory_item = {
        "sku": "TEST-001",
        "item_name": "Test Product",
        "variant": "Standard",
        "unit_price": 299.99,
        "delivery_type": "standard",
        "is_active": True,
        "special_handling_required": False,
        "assembly_required": False
    }
    
    mock_service_clients.json.side_effect = [
        customer_data,
        inventory_item
        # No delivery service call
    ]
    
    mock_db.rowcount = 1
    
    response = client.post(
        '/create_order',
        data=json.dumps(order_data),
        content_type='application/json'
    )
    
    assert response.status_code == 201
    data = response.get_json()
    assert 'order_id' in data
    assert data.get('delivery_job_id') is None  # No delivery created


def test_create_order_delivery_creation_fails(client, mock_db, auth_token, mock_service_clients):
    """Test create order when delivery creation fails (should still succeed)"""
    order_data = {
        "customer_id": "test-customer-123",
        "items": [{"sku": "TEST-001", "quantity": 2}]
    }
    
    # Mock customer with lat/lng
    customer_data = {
        "customer_id": "test-customer-123",
        "customer_name": "Test Customer",
        "latitude": 1.3521,
        "longitude": 103.8198
    }
    
    # Mock inventory
    inventory_item = {
        "sku": "TEST-001",
        "item_name": "Test Product",
        "variant": "Standard",
        "unit_price": 299.99,
        "delivery_type": "standard",
        "is_active": True,
        "special_handling_required": False,
        "assembly_required": False
    }
    
    # Mock delivery service to return None (failure)
    mock_service_clients.json.side_effect = [
        customer_data,
        inventory_item,
        None  # Delivery creation fails
    ]
    
    mock_db.rowcount = 1
    
    response = client.post(
        '/create_order',
        data=json.dumps(order_data),
        content_type='application/json'
    )
    
    # Order should still be created successfully
    assert response.status_code == 201
    data = response.get_json()
    assert 'order_id' in data
    assert data.get('delivery_job_id') is None  # No delivery ID since it failed


def test_list_orders(client, mock_db, auth_token):
    """Test listing orders with pagination"""
    orders = [
        {
            "order_id": "order-1",
            "order_no": "ORD-001",
            "customer_id": "customer-1",
            "customer_name": "Customer 1",
            "customer_contact": "12345678",
            "status": "received",
            "order_value": 599.98,
            "item_count": 2,
            "created_at": datetime.now()
        },
        {
            "order_id": "order-2",
            "order_no": "ORD-002",
            "customer_id": "customer-2",
            "customer_name": "Customer 2",
            "customer_contact": "87654321",
            "status": "processing",
            "order_value": 299.99,
            "item_count": 1,
            "created_at": datetime.now()
        }
    ]
    
    # Mock database responses
    mock_db.fetchall.return_value = orders
    mock_db.fetchone.return_value = {"total": 2}
    
    response = client.get('/orders?page=1&per_page=10')
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'orders' in data
    assert 'total' in data
    assert data['page'] == 1
    assert data['per_page'] == 10
    assert len(data['orders']) == 2


def test_get_order_not_found(client, mock_db, auth_token):
    """Test getting non-existent order returns 404"""
    # Mock database to return None (order not found)
    mock_db.fetchone.return_value = None
    
    response = client.get('/orders/nonexistent-order-id')
    
    assert response.status_code == 404
    data = response.get_json()
    assert data['error'] == 'Order not found'


def test_get_order_success(client, mock_db, auth_token):
    """Test getting existing order details"""
    order = {
        "order_id": "test-order-123",
        "order_no": "ORD-001",
        "customer_id": "customer-123",
        "status": "received",
        "order_value": 599.98,
        "order_date": datetime.now().date(),
        "note": "Test order",
        "created_at": datetime.now(),
        "updated_at": datetime.now()
    }
    
    items = [
        {
            "item_id": "item-1",
            "sku": "TEST-001",
            "item_name": "Test Product",
            "variant": "Standard",
            "quantity": 2,
            "unit_price": 299.99
        }
    ]
    
    # Mock database responses
    # First call for order, second for items, third for delivery
    mock_db.fetchone.side_effect = [order, None]
    mock_db.fetchall.return_value = items
    
    response = client.get('/orders/test-order-123')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['order']['order_id'] == 'test-order-123'
    assert 'items' in data
    assert len(data['items']) == 1


def test_update_order_status_missing_status(client, mock_db, auth_token):
    """Test updating order status without status field returns 400"""
    response = client.put(
        '/orders/test-order-123/status',
        data=json.dumps({}),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'status is required' in data['error']


def test_update_order_status_invalid_status(client, mock_db, auth_token):
    """Test updating order with invalid status returns 400"""
    response = client.put(
        '/orders/test-order-123/status',
        data=json.dumps({"status": "invalid_status"}),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'Invalid status' in data['error']


def test_update_order_status_success(client, mock_db, auth_token):
    """Test successful order status update"""
    # Mock database to return existing order
    mock_db.fetchone.return_value = {
        "order_id": "test-order-123",
        "status": "received"
    }
    mock_db.rowcount = 1
    
    response = client.put(
        '/orders/test-order-123/status',
        data=json.dumps({"status": "processing"}),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Order status updated successfully'


def test_get_customer_orders(client, mock_db, auth_token):
    """Test getting all orders for a specific customer"""
    customer_orders = [
        {
            "order_id": "order-1",
            "order_no": "ORD-001",
            "customer_id": "customer-123",
            "status": "delivered",
            "order_value": 599.98,
            "item_count": 2,
            "created_at": datetime.now()
        },
        {
            "order_id": "order-2",
            "order_no": "ORD-002",
            "customer_id": "customer-123",
            "status": "processing",
            "order_value": 299.99,
            "item_count": 1,
            "created_at": datetime.now()
        }
    ]
    
    mock_db.fetchall.return_value = customer_orders
    
    response = client.get('/orders/customer/customer-123')
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'orders' in data
    assert len(data['orders']) == 2
    assert data['orders'][0]['customer_id'] == 'customer-123'


def test_get_unscheduled_orders(client, mock_db, auth_token):
    """Test getting unscheduled orders"""
    # Create datetime-safe objects
    from datetime import datetime
    now_str = datetime.now().isoformat()
    
    unscheduled_orders = [
        {
            "order_id": "order-1",
            "order_no": "ORD-001",
            "customer_name": "Customer 1",
            "customer_postal_code": "123456",
            "status": "ready_for_delivery",
            "item_count": 2,
            "order_date": now_str,
            "created_at": now_str,
            "updated_at": now_str
        }
    ]
    
    order_items = [
        {
            "item_id": "item-1",
            "sku": "TEST-001",
            "item_name": "Test Product",
            "variant": "Standard",
            "quantity": 2,
            "unit_price": 299.99,
            "total_price": 599.98
        }
    ]
    
    # First fetchall returns orders, second fetchall returns items for the order
    mock_db.fetchall.side_effect = [unscheduled_orders, order_items]
    
    response = client.get('/orders/unscheduled')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'orders' in data
    assert data['count'] == 1


def test_get_order_tracking_public(client, mock_db):
    """Test public order tracking endpoint (no auth required)"""
    order = {
        "order_id": "test-order-123",
        "order_no": "ORD-001",
        "status": "out_for_delivery",
        "order_date": datetime.now().date()
    }
    
    items = [{"item_id": "item-1", "sku": "TEST-001"}]
    
    # Mock database responses
    mock_db.fetchone.side_effect = [order, None]  # order, then delivery (None)
    mock_db.fetchall.return_value = items
    
    response = client.get('/orders/test-order-123/tracking')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['order_id'] == 'test-order-123'
    assert data['order_no'] == 'ORD-001'
    assert data['status'] == 'out_for_delivery'
    assert 'items_count' in data


def test_update_order_type_success(client, mock_db, auth_token):
    """Test updating order type successfully"""
    mock_db.rowcount = 1
    
    response = client.patch(
        '/orders/test-order-123/order-type',
        data=json.dumps({"order_type": "asap"}),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Order type updated successfully'


def test_update_order_type_invalid(client, mock_db, auth_token):
    """Test updating order with invalid order type"""
    response = client.patch(
        '/orders/test-order-123/order-type',
        data=json.dumps({"order_type": "invalid_type"}),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'Invalid order_type' in data['error']


def test_create_schedule_no_orders(client, mock_db, auth_token):
    """Test creating schedule without orders returns 400"""
    response = client.post(
        '/orders/schedule',
        data=json.dumps({
            "order_ids": [],
            "schedule_date": "2025-10-01"
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'No orders selected' in data['error']


def test_create_schedule_no_date(client, mock_db, auth_token):
    """Test creating schedule without date returns 400"""
    response = client.post(
        '/orders/schedule',
        data=json.dumps({
            "order_ids": ["order-1", "order-2"]
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'Schedule date is required' in data['error']


def test_create_schedule_too_many_orders(client, mock_db, auth_token):
    """Test creating schedule with more than 18 orders returns 400"""
    order_ids = [f"order-{i}" for i in range(1, 20)]  # 19 orders
    
    response = client.post(
        '/orders/schedule',
        data=json.dumps({
            "order_ids": order_ids,
            "schedule_date": "2025-10-01"
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'Cannot schedule more than 18 locations' in data['error']


def test_create_schedule_db_connection_failed(client, mocker, auth_token):
    """Test creating schedule when database connection fails"""
    mocker.patch('app.get_db_connection', return_value=None)
    
    response = client.post(
        '/orders/schedule',
        data=json.dumps({
            "order_ids": ["order-1", "order-2"],
            "schedule_date": "2025-10-01"
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 500
    data = response.get_json()
    assert 'Database connection failed' in data['error']


def test_create_schedule_orders_not_found(client, mock_db, auth_token):
    """Test creating schedule when some orders don't exist"""
    # Mock empty result - no orders found
    mock_db.fetchall.return_value = []
    
    response = client.post(
        '/orders/schedule',
        data=json.dumps({
            "order_ids": ["nonexistent-1", "nonexistent-2"],
            "schedule_date": "2025-10-01"
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'not found or already scheduled' in data['error']


def test_create_schedule_success_without_route_optimization(client, mock_db, mocker, auth_token):
    """Test successful schedule creation without route optimization"""
    # Mock order data
    mock_orders = [
        {
            'order_id': 'order-1',
            'order_no': 'ORD-001',
            'order_type': 'standard',
            'preferred_delivery_time': None,
            'customer_id': 'cust-1',
            'customer_name': 'John Doe',
            'customer_postal_code': '123456',
            'latitude': 1.3521,
            'longitude': 103.8198,
            'customer_street': '123 Main St',
            'customer_unit': '#01-01'
        },
        {
            'order_id': 'order-2',
            'order_no': 'ORD-002',
            'order_type': 'express',
            'preferred_delivery_time': None,
            'customer_id': 'cust-2',
            'customer_name': 'Jane Smith',
            'customer_postal_code': '123457',
            'latitude': 1.3522,
            'longitude': 103.8199,
            'customer_street': '124 Main St',
            'customer_unit': '#02-02'
        }
    ]
    
    mock_db.fetchall.return_value = mock_orders
    mock_db.rowcount = 2
    
    # Mock ServiceClient post to return None (route optimization fails)
    mock_service_client = mocker.patch('app.ServiceClient')
    mock_instance = mock_service_client.return_value
    mock_instance.post.return_value = None
    
    response = client.post(
        '/orders/schedule',
        data=json.dumps({
            "order_ids": ["order-1", "order-2"],
            "schedule_date": "2025-10-01",
            "driver_id": "DRV001",
            "team": "Team A"
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 201
    data = response.get_json()
    assert data['success'] is True
    assert data['total_locations'] == 2
    assert data['schedule_date'] == '2025-10-01'
    assert len(data['orders']) == 2


def test_create_schedule_success_with_route_optimization(client, mock_db, mocker, auth_token):
    """Test successful schedule creation with route optimization"""
    # Mock order data
    mock_orders = [
        {
            'order_id': 'order-1',
            'order_no': 'ORD-001',
            'order_type': 'standard',
            'preferred_delivery_time': None,
            'customer_id': 'cust-1',
            'customer_name': 'John Doe',
            'customer_postal_code': '123456',
            'latitude': 1.3521,
            'longitude': 103.8198,
            'customer_street': '123 Main St',
            'customer_unit': '#01-01'
        }
    ]
    
    mock_db.fetchall.return_value = mock_orders
    mock_db.rowcount = 1
    
    # Mock ServiceClient post to return successful route optimization
    mock_service_client = mocker.patch('app.ServiceClient')
    mock_instance = mock_service_client.return_value
    mock_instance.post.return_value = {
        'success': True,
        'route': {
            'polyline': 'encoded_polyline_data',
            'distance_meters': 5000,
            'duration_seconds': 900,
            'estimated_end_time': '10:00:00'
        }
    }
    
    response = client.post(
        '/orders/schedule',
        data=json.dumps({
            "order_ids": ["order-1"],
            "schedule_date": "2025-10-01"
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 201
    data = response.get_json()
    assert data['success'] is True
    assert 'route' in data
    assert data['route']['distance_meters'] == 5000


def test_create_schedule_exception_handling(client, mock_db, mocker, auth_token):
    """Test create_schedule handles exceptions properly"""
    # Mock fetchall to raise an exception during order retrieval
    mock_db.fetchall.side_effect = Exception("Database error")
    
    response = client.post(
        '/orders/schedule',
        data=json.dumps({
            "order_ids": ["order-1"],
            "schedule_date": "2025-10-01"
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 500
    data = response.get_json()
    assert 'error' in data


def test_update_delivery_preferences(client, mock_db, auth_token):
    """Test updating delivery preferences"""
    mock_db.rowcount = 1
    
    response = client.patch(
        '/orders/test-order-123/delivery-preferences',
        data=json.dumps({
            "remarks": "Please call before delivery",
            "preferred_delivery_date": "2025-10-20",
            "preferred_delivery_time": "14:00:00"
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'successfully' in data['message']


def test_update_delivery_preferences_no_data(client, mock_db, auth_token):
    """Test updating delivery preferences with valid remark"""
    mock_db.rowcount = 1
    
    response = client.patch(
        '/orders/test-order-123/delivery-preferences',
        data=json.dumps({"remarks": "Test remark"}),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True


def test_get_customer_orders_v2(client, mock_db, auth_token):
    """Test getting all orders for a customer"""
    mock_db.fetchall.return_value = [
        {
            'order_id': 'order-1',
            'order_no': 'ORD-001',
            'customer_id': 'customer-123',
            'status': 'validated',
            'item_count': 3
        },
        {
            'order_id': 'order-2',
            'order_no': 'ORD-002',
            'customer_id': 'customer-123',
            'status': 'delivered',
            'item_count': 2
        }
    ]
    
    response = client.get('/orders/customer/customer-123')
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'orders' in data
    assert len(data['orders']) == 2


def test_get_order_tracking_v2(client, mock_db):
    """Test getting order tracking information (public endpoint)"""
    mock_db.fetchone.return_value = {
        'order_id': 'test-order-123',
        'order_no': 'ORD-20251019-ABC123',
        'status': 'out_for_delivery',
        'order_date': datetime(2025, 10, 19).date(),
        'customer_name': 'John Doe'
    }
    mock_db.fetchall.return_value = [
        {'item_id': 'item-1', 'sku': 'TEST-001', 'quantity': 2}
    ]
    
    response = client.get('/orders/test-order-123/tracking')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['order_id'] == 'test-order-123'
    assert data['status'] == 'out_for_delivery'
    assert data['items_count'] == 1


def test_get_unscheduled_orders_v2(client, mock_db, auth_token):
    """Test getting unscheduled orders"""
    mock_db.fetchall.side_effect = [
        # First call: get unscheduled orders
        [
            {
                'order_id': 'order-1',
                'order_no': 'ORD-001',
                'order_type': 'asap',
                'customer_name': 'Customer A',
                'customer_postal_code': '123456'
            }
        ],
        # Second call: get items for order-1
        [
            {'item_id': 'item-1', 'sku': 'TEST-001', 'quantity': 2}
        ]
    ]
    
    response = client.get('/orders/unscheduled')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['count'] == 1
    assert len(data['orders']) == 1
    assert data['orders'][0]['order_id'] == 'order-1'


def test_get_all_schedules(client, mock_db, auth_token):
    """Test getting all delivery schedules"""
    mock_db.fetchall.return_value = [
        {
            'schedule_id': 'schedule-1',
            'schedule_date': datetime(2025, 10, 20).date(),
            'driver_id': 'DRV001',
            'team': 'Team A',
            'total_locations': 5,
            'status': 'confirmed',
            'order_count': 5,
            'delivered_count': 0,
            'start_time': None,
            'estimated_end_time': None,
            'created_at': datetime(2025, 10, 19)
        }
    ]
    
    response = client.get('/schedules')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['count'] == 1
    assert len(data['schedules']) == 1


def test_get_schedule_by_date(client, mock_db, auth_token):
    """Test getting schedules for a specific date"""
    mock_db.fetchall.side_effect = [
        # First call: get deliveries from view
        [{
            'schedule_id': 'schedule-1',
            'schedule_date': datetime(2025, 10, 20).date(),
            'driver_id': 'DRV001',
            'driver_name': 'Driver A',
            'driver_contact': '12345678',
            'team': 'Team A',
            'total_locations': 3,
            'max_locations': 18,
            'remaining_capacity': 15,
            'schedule_status': 'confirmed',
            'start_time': None,
            'estimated_end_time': None,
            'route_polyline': None,
            'order_id': 'order-1',
            'sequence_number': 1,
            'order_no': 'ORD-001',
            'shopify_order_id': None,
            'order_type': 'asap',
            'customer_name': 'Customer A',
            'customer_contact': '87654321',
            'customer_postal_code': '123456',
            'customer_street': 'Street 1',
            'customer_unit': '#01-01',
            'housing_type': 'HDB',
            'total_items': 2,
            'estimated_arrival_time': None,
            'actual_arrival_time': None,
            'delivery_status': 'scheduled',
            'requires_warehouse_return': 0,
            'latitude': 1.3521,
            'longitude': 103.8198
        }],
        # Second call: get order items
        [
            {'item_name': 'Product A', 'variant': 'Red', 'quantity': 2}
        ]
    ]
    
    response = client.get('/schedules/2025-10-20')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True


def test_mark_delivery_complete(client, mock_db, auth_token):
    """Test marking a delivery as complete"""
    # Mock order exists
    mock_db.fetchone.return_value = {
        'order_id': 'test-order-123',
        'order_no': 'ORD-001',
        'is_scheduled': 1
    }
    mock_db.rowcount = 1
    
    response = client.patch(
        '/orders/test-order-123/complete',
        data=json.dumps({
            "signature": "base64_signature_data",
            "delivered_at": "2025-10-19T14:30:00"
        }),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True


def test_delete_schedule(client, mock_db, auth_token):
    """Test deleting a schedule"""
    mock_db.fetchone.return_value = {'schedule_id': 'schedule-1', 'status': 'draft'}
    mock_db.fetchall.return_value = []
    mock_db.rowcount = 1
    
    response = client.delete('/schedules/schedule-1')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True


def test_unschedule_order(client, mock_db, auth_token):
    """Test unscheduling an order"""
    mock_db.fetchone.side_effect = [
        # First call: get order details
        {
            'order_id': 'order-1',
            'order_no': 'ORD-001',
            'is_scheduled': 1,
            'scheduled_delivery_date': datetime(2025, 10, 20).date()
        },
        # Second call: get schedule_id
        {'schedule_id': 'schedule-1'},
        # Third call: count remaining orders in schedule
        {'count': 1}
    ]
    mock_db.rowcount = 1
    
    response = client.patch('/orders/order-1/unschedule')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True


def test_reset_delivered_orders(client, mock_db, auth_token):
    """Test resetting delivered orders back to validated"""
    mock_db.fetchone.return_value = {'count': 5}
    mock_db.rowcount = 5
    
    response = client.post(
        '/orders/reset-delivered',
        data=json.dumps({}),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['orders_reset'] == 5


# ============================================
# EXCEPTION HANDLER TESTS
# ============================================

def test_list_orders_database_error(client, mock_db, auth_token):
    """Test list orders when database query fails"""
    # Make the cursor execute raise an exception
    mock_db.execute.side_effect = Exception("Database query failed")
    
    response = client.get('/orders?page=1&per_page=10')
    
    assert response.status_code == 500
    data = response.get_json()
    assert 'error' in data


def test_get_customer_orders_exception(client, mock_db, auth_token):
    """Test get customer orders when an exception occurs"""
    # Make fetchall raise an exception
    mock_db.fetchall.side_effect = Exception("Connection lost")
    
    response = client.get('/orders/customer/customer-123')
    
    assert response.status_code == 500
    data = response.get_json()
    assert 'error' in data


def test_update_order_type_exception(client, mock_db, auth_token):
    """Test update order type when database update fails"""
    from mysql.connector import Error
    mock_db.execute.side_effect = Error("Database error")
    
    response = client.patch(
        '/orders/test-order-123/order-type',
        data=json.dumps({"order_type": "asap"}),
        content_type='application/json'
    )
    
    assert response.status_code == 500
    data = response.get_json()
    assert 'error' in data


def test_update_delivery_preferences_exception(client, mock_db, auth_token):
    """Test update delivery preferences when an exception occurs"""
    from mysql.connector import Error
    mock_db.execute.side_effect = Error("Update failed")
    
    response = client.patch(
        '/orders/test-order-123/delivery-preferences',
        data=json.dumps({"remarks": "Test"}),
        content_type='application/json'
    )
    
    assert response.status_code == 500
    data = response.get_json()
    assert 'error' in data


def test_get_unscheduled_orders_exception(client, mock_db, auth_token):
    """Test get unscheduled orders when database query fails"""
    mock_db.fetchall.side_effect = Exception("Query failed")
    
    response = client.get('/orders/unscheduled')
    
    assert response.status_code == 500
    data = response.get_json()
    assert 'error' in data


def test_get_all_schedules_exception(client, mock_db, auth_token):
    """Test get all schedules when an exception occurs"""
    mock_db.fetchall.side_effect = Exception("Database connection lost")
    
    response = client.get('/schedules')
    
    assert response.status_code == 500
    data = response.get_json()
    assert 'error' in data


def test_get_schedule_by_date_exception(client, mock_db, auth_token):
    """Test get schedule by date when an exception occurs"""
    mock_db.fetchall.side_effect = Exception("Query execution failed")
    
    response = client.get('/schedules/2025-10-20')
    
    assert response.status_code == 500
    data = response.get_json()
    assert 'error' in data


def test_delete_schedule_exception(client, mock_db, auth_token):
    """Test delete schedule when an exception occurs"""
    mock_db.fetchone.return_value = {'schedule_id': 'schedule-1', 'status': 'draft'}
    mock_db.fetchall.side_effect = Exception("Delete operation failed")
    
    response = client.delete('/schedules/schedule-1')
    
    assert response.status_code == 500
    data = response.get_json()
    assert 'error' in data


def test_unschedule_order_exception(client, mock_db, auth_token):
    """Test unschedule order when an exception occurs"""
    mock_db.fetchone.side_effect = Exception("Database error")
    
    response = client.patch('/orders/order-1/unschedule')
    
    assert response.status_code == 500
    data = response.get_json()
    assert 'error' in data


def test_reset_delivered_orders_exception(client, mock_db, auth_token):
    """Test reset delivered orders when an exception occurs"""
    mock_db.fetchone.side_effect = Exception("Reset operation failed")
    
    response = client.post(
        '/orders/reset-delivered',
        data=json.dumps({}),
        content_type='application/json'
    )
    
    assert response.status_code == 500
    data = response.get_json()
    assert 'error' in data


# Tests for initiate_delivery endpoint
def test_initiate_delivery_success(client, mock_db, auth_token, mock_service_clients):
    """Test successful delivery initiation"""
    # Mock get_order_details - order exists and is ready
    mock_db.fetchone.side_effect = [
        # First call: get order
        {
            'order_id': 'test-order-123',
            'order_no': 'ORD-001',
            'status': 'validated',
            'latitude': 1.3521,
            'longitude': 103.8198
        },
        # Second call: check delivery exists (returns None - no delivery yet)
        None
    ]
    
    # Mock delivery service response
    mock_service_clients.json.return_value = {
        'delivery_id': 'delivery-123',
        'status': 'pending'
    }
    
    response = client.post(f'/orders/test-order-123/deliver')
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'message' in data
    assert 'successfully' in data['message'].lower()


def test_initiate_delivery_order_not_found(client, mock_db, auth_token):
    """Test initiate delivery when order doesn't exist"""
    # Mock get_order_details returns None
    mock_db.fetchone.return_value = None
    
    response = client.post(f'/orders/nonexistent-order/deliver')
    
    assert response.status_code == 404
    data = response.get_json()
    assert 'error' in data
    assert 'not found' in data['error'].lower()


def test_initiate_delivery_order_not_ready(client, mock_db, auth_token):
    """Test initiate delivery when order status is not ready"""
    # Mock order with invalid status
    mock_db.fetchone.return_value = {
        'order_id': 'test-order-123',
        'order_no': 'ORD-001',
        'status': 'received',  # Not ready for delivery
        'latitude': 1.3521,
        'longitude': 103.8198
    }
    
    response = client.post(f'/orders/test-order-123/deliver')
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert 'not ready' in data['error'].lower()


def test_initiate_delivery_creation_failed(client, mock_db, auth_token, mock_service_clients):
    """Test initiate delivery when delivery service fails"""
    # Mock order details
    mock_db.fetchone.side_effect = [
        {
            'order_id': 'test-order-123',
            'order_no': 'ORD-001',
            'status': 'validated',
            'latitude': 1.3521,
            'longitude': 103.8198
        },
        None  # No existing delivery
    ]
    
    # Mock delivery service failure
    mock_service_clients.json.return_value = None
    
    response = client.post(f'/orders/test-order-123/deliver')
    
    assert response.status_code == 500
    data = response.get_json()
    assert 'error' in data
    assert 'failed' in data['error'].lower()


def test_initiate_delivery_already_has_delivery(client, mock_db, auth_token, mocker):
    """Test initiate delivery when order already has a delivery"""
    # Mock get_order_details to return order with existing delivery
    mock_order_details = {
        'order': {
            'order_id': 'test-order-123',
            'order_no': 'ORD-001',
            'status': 'validated',
            'latitude': 1.3521,
            'longitude': 103.8198
        },
        'items': [],
        'delivery': {
            'delivery_id': 'existing-delivery-123',
            'status': 'pending'
        }
    }
    
    # Patch the orchestrator's get_order_details method
    mocker.patch.object(orchestrator, 'get_order_details', return_value=mock_order_details)
    
    # Mock update_order_status to succeed
    mocker.patch.object(orchestrator, 'update_order_status', return_value=None)
    
    response = client.post(f'/orders/test-order-123/deliver')
    
    # Should succeed as it skips delivery creation and just updates status
    assert response.status_code == 200
    data = response.get_json()
    assert 'message' in data


def test_initiate_delivery_exception(client, mock_db, auth_token, mocker):
    """Test initiate delivery when an exception occurs"""
    # Mock get_order_details to raise an exception
    mocker.patch.object(
        orchestrator,
        'get_order_details',
        side_effect=Exception("Database error")
    )
    
    response = client.post(f'/orders/test-order-123/deliver')
    
    assert response.status_code == 500
    data = response.get_json()
    assert 'error' in data


# ============================================
# Service Client Methods Tests
# ============================================

def test_service_client_post_success(mocker):
    """Test ServiceClient post method success"""
    from app import ServiceClient
    
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"success": True, "data": "test"}
    
    # Mock the _make_request method directly
    mocker.patch.object(ServiceClient, '_make_request', return_value={"success": True, "data": "test"})
    
    client = ServiceClient("http://test-service", "TestService")
    result = client.post("/endpoint", json={"key": "value"})
    
    assert result == {"success": True, "data": "test"}


def test_service_client_post_failure(mocker):
    """Test ServiceClient post method when request fails"""
    from app import ServiceClient
    
    # Mock _make_request to return None (failure case)
    mocker.patch.object(ServiceClient, '_make_request', return_value=None)
    
    client = ServiceClient("http://test-service", "TestService")
    result = client.post("/endpoint", json={"key": "value"})
    
    assert result is None


def test_service_client_put_success(mocker):
    """Test ServiceClient put method success"""
    from app import ServiceClient
    
    # Mock the _make_request method directly
    mocker.patch.object(ServiceClient, '_make_request', return_value={"updated": True})
    
    client = ServiceClient("http://test-service", "TestService")
    result = client.put("/endpoint/123", json={"status": "active"})
    
    assert result == {"updated": True}


def test_service_client_patch_success(mocker):
    """Test ServiceClient patch method success"""
    from app import ServiceClient
    
    # Mock the _make_request method directly
    mocker.patch.object(ServiceClient, '_make_request', return_value={"patched": True})
    
    client = ServiceClient("http://test-service", "TestService")
    result = client.patch("/endpoint/456", json={"field": "value"})
    
    assert result == {"patched": True}


# ============================================
# Additional Coverage Tests for Business Logic
# ============================================

def test_get_order_with_delivery_info(client, mock_db, auth_token, mocker):
    """Test get_order_details with delivery information fetch"""
    # Mock database responses
    order_data = {
        'order_id': 'test-order-123',
        'order_no': 'ORD-20250101-ABC123',
        'customer_id': 'customer-456',
        'status': 'out_for_delivery',
        'order_date': datetime.now().date(),
        'order_value': 299.99,
        'customer_name': 'Test Customer',
        'customer_contact': '12345678',
        'customer_street': '123 Test St',
        'customer_unit': '#01-01',
        'customer_postal_code': '123456',
        'latitude': 1.3521,
        'longitude': 103.8198
    }
    
    order_items = [
        {
            'item_id': 'item-1',
            'order_id': 'test-order-123',
            'sku': 'TEST-001',
            'item_name': 'Test Product',
            'variant': 'Standard',
            'quantity': 2,
            'unit_price': 149.99
        }
    ]
    
    delivery_info = {
        'delivery_id': 'delivery-789',
        'status': 'in_transit',
        'tracking_number': 'TRK-001'
    }
    
    # Mock database calls
    mock_db.fetchone.return_value = order_data
    mock_db.fetchall.return_value = order_items
    
    # Mock delivery service call
    from app import delivery_service
    mocker.patch.object(delivery_service, 'get', return_value=delivery_info)
    
    response = client.get('/orders/test-order-123')
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'order' in data
    assert 'items' in data
    assert 'delivery' in data
    assert data['delivery'] == delivery_info


def test_list_orders_db_connection_failed(client, auth_token, mocker):
    """Test list_orders when database connection fails"""
    # Mock get_db_connection to return None
    mocker.patch('app.get_db_connection', return_value=None)
    
    response = client.get('/orders')
    
    assert response.status_code == 500
    data = response.get_json()
    assert 'Database connection failed' in data['error']


def test_update_order_status_invalid_status_validation(client, mock_db, auth_token):
    """Test update_order_status with invalid status"""
    order_data = {
        "status": "invalid_status_that_doesnt_exist"
    }
    
    response = client.put(
        '/orders/test-order-123/status',
        data=json.dumps(order_data),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'Invalid status' in data['error']


def test_update_order_status_update_failure(client, mock_db, auth_token, mocker):
    """Test update_order_status when update operation fails"""
    order_data = {
        "status": "delivered"
    }
    
    # Mock orchestrator.update_order_status to return False (failure)
    mocker.patch.object(orchestrator, 'update_order_status', return_value=False)
    
    response = client.put(
        '/orders/test-order-123/status',
        data=json.dumps(order_data),
        content_type='application/json'
    )
    
    assert response.status_code == 500
    data = response.get_json()
    assert 'Failed to update order status' in data['error']


def test_get_schedule_by_date_db_connection_failed(client, auth_token, mocker):
    """Test get_schedule_by_date when database connection fails"""
    # Mock get_db_connection to return None
    mocker.patch('app.get_db_connection', return_value=None)
    
    response = client.get('/schedules/2025-10-01')
    
    assert response.status_code == 500
    data = response.get_json()
    assert 'Database connection failed' in data['error']


def test_delete_schedule_db_connection_failed(client, auth_token, mocker):
    """Test delete_schedule when database connection fails"""
    # Mock get_db_connection to return None
    mocker.patch('app.get_db_connection', return_value=None)
    
    response = client.delete('/schedules/test-schedule-123')
    
    assert response.status_code == 500
    data = response.get_json()
    assert 'Database connection failed' in data['error']


def test_delete_schedule_not_found(client, mock_db, auth_token):
    """Test delete_schedule when schedule doesn't exist"""
    # Mock database to return None (schedule not found)
    mock_db.fetchone.return_value = None
    
    response = client.delete('/schedules/nonexistent-schedule-id')
    
    assert response.status_code == 404
    data = response.get_json()
    assert 'Schedule not found' in data['error']


def test_unschedule_order_db_connection_failed(client, auth_token, mocker):
    """Test unschedule_order when database connection fails"""
    # Mock get_db_connection to return None
    mocker.patch('app.get_db_connection', return_value=None)
    
    response = client.patch('/orders/test-order-123/unschedule')
    
    assert response.status_code == 500
    data = response.get_json()
    assert 'Database connection failed' in data['error']


def test_unschedule_order_not_found(client, mock_db, auth_token):
    """Test unschedule_order when order doesn't exist"""
    # Mock database to return None (order not found)
    mock_db.fetchone.return_value = None
    
    response = client.patch('/orders/nonexistent-order-id/unschedule')
    
    assert response.status_code == 404
    data = response.get_json()
    assert 'Order not found' in data['error']


def test_unschedule_order_not_scheduled(client, mock_db, auth_token):
    """Test unschedule_order when order is not scheduled"""
    # Mock order that is not scheduled
    order_data = {
        'order_id': 'test-order-123',
        'order_no': 'ORD-001',
        'is_scheduled': 0,
        'scheduled_delivery_date': None
    }
    
    mock_db.fetchone.return_value = order_data
    
    response = client.patch('/orders/test-order-123/unschedule')
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'Order is not scheduled' in data['error']


def test_unschedule_order_success(client, mock_db, auth_token):
    """Test successful order unscheduling"""
    # Mock scheduled order
    order_data = {
        'order_id': 'test-order-123',
        'order_no': 'ORD-20250101-ABC123',
        'is_scheduled': 1,
        'scheduled_delivery_date': '2025-10-01'
    }
    
    schedule_data = {
        'schedule_id': 'schedule-456'
    }
    
    count_data = {
        'count': 0  # Last order in schedule
    }
    
    # Mock database calls in sequence
    mock_db.fetchone.side_effect = [order_data, schedule_data, count_data]
    
    response = client.patch('/orders/test-order-123/unschedule')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'Order unscheduled successfully' in data['message']


def test_unschedule_order_with_remaining_orders(client, mock_db, auth_token):
    """Test unscheduling order when other orders remain in schedule"""
    # Mock scheduled order
    order_data = {
        'order_id': 'test-order-123',
        'order_no': 'ORD-20250101-ABC123',
        'is_scheduled': 1,
        'scheduled_delivery_date': '2025-10-01'
    }
    
    schedule_data = {
        'schedule_id': 'schedule-456'
    }
    
    count_data = {
        'count': 2  # Other orders still in schedule
    }
    
    # Mock database calls in sequence
    mock_db.fetchone.side_effect = [order_data, schedule_data, count_data]
    
    response = client.patch('/orders/test-order-123/unschedule')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True


def test_mark_delivery_complete_db_connection_failed(client, auth_token, mocker):
    """Test mark_delivery_complete when database connection fails"""
    # Mock get_db_connection to return None
    mocker.patch('app.get_db_connection', return_value=None)
    
    response = client.patch('/orders/test-order-123/complete')
    
    assert response.status_code == 500
    data = response.get_json()
    assert 'Database connection failed' in data['error']


def test_mark_delivery_complete_order_not_found(client, mock_db, auth_token):
    """Test mark_delivery_complete when order doesn't exist"""
    # Mock database to return None (order not found)
    mock_db.fetchone.return_value = None
    
    response = client.patch('/orders/nonexistent-order-id/complete')
    
    assert response.status_code == 404
    data = response.get_json()
    assert 'Order not found' in data['error']


def test_mark_delivery_complete_success(client, mock_db, auth_token):
    """Test successful delivery completion"""
    order_data = {
        'order_id': 'test-order-123',
        'order_no': 'ORD-20250101-ABC123',
        'status': 'out_for_delivery'
    }
    
    mock_db.fetchone.return_value = order_data
    
    response = client.patch('/orders/test-order-123/complete')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'Delivery marked as complete' in data['message']


def test_reset_delivered_orders_db_connection_failed(client, auth_token, mocker):
    """Test reset_delivered_orders when database connection fails"""
    # Mock get_db_connection to return None
    mocker.patch('app.get_db_connection', return_value=None)
    
    response = client.post('/orders/reset-delivered')
    
    assert response.status_code == 500
    data = response.get_json()
    assert 'Database connection failed' in data['error']


def test_reset_delivered_orders_success(client, mock_db, auth_token):
    """Test successful reset of delivered orders"""
    count_data = {
        'count': 5
    }
    
    mock_db.fetchone.return_value = count_data
    
    response = client.post('/orders/reset-delivered')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert data['orders_reset'] == 5


def test_get_order_tracking_public_endpoint(client, mock_db):
    """Test public order tracking endpoint (no auth required)"""
    order_data = {
        'order_id': 'test-order-123',
        'order_no': 'ORD-20250101-ABC123',
        'status': 'out_for_delivery',
        'order_date': datetime.now().date(),
        'customer_name': 'Test Customer'
    }
    
    order_items = [
        {'item_id': 'item-1', 'sku': 'TEST-001', 'quantity': 2}
    ]
    
    # Mock database calls
    mock_db.fetchone.return_value = order_data
    mock_db.fetchall.return_value = order_items
    
    response = client.get('/orders/test-order-123/tracking')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['order_id'] == 'test-order-123'
    assert data['order_no'] == 'ORD-20250101-ABC123'
    assert data['status'] == 'out_for_delivery'
    assert data['items_count'] == 1


def test_get_order_tracking_not_found(client, mock_db):
    """Test order tracking when order doesn't exist"""
    # Mock database to return None
    mock_db.fetchone.return_value = None
    
    response = client.get('/orders/nonexistent-order/tracking')
    
    assert response.status_code == 404
    data = response.get_json()
    assert 'Order not found' in data['error']


def test_list_orders_exception_handling(client, mock_db, auth_token):
    """Test list_orders exception handling"""
    # Mock database to raise an exception
    mock_db.fetchall.side_effect = Exception("Database error")
    
    response = client.get('/orders')
    
    assert response.status_code == 500
    data = response.get_json()
    assert 'Internal server error' in data['error']


def test_get_customer_orders_exception(client, mock_db, auth_token):
    """Test get_customer_orders exception handling"""
    # Mock database to raise an exception
    mock_db.fetchall.side_effect = Exception("Database error")
    
    response = client.get('/orders/customer/test-customer-123')
    
    assert response.status_code == 500
    data = response.get_json()
    assert 'Internal server error' in data['error']


def test_update_order_type_missing_order_type(client, mock_db, auth_token):
    """Test update_order_type without order_type field"""
    response = client.patch(
        '/orders/test-order-123/order-type',
        data=json.dumps({}),
        content_type='application/json',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'order_type is required' in data['error']


def test_update_order_type_invalid_type(client, mock_db, auth_token):
    """Test update_order_type with invalid order_type"""
    response = client.patch(
        '/orders/test-order-123/order-type',
        data=json.dumps({"order_type": "invalid_type"}),
        content_type='application/json',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'Invalid order_type' in data['error']


def test_update_order_type_db_connection_failed(client, mocker, auth_token):
    """Test update_order_type when database connection fails"""
    mocker.patch('app.get_db_connection', return_value=None)
    
    response = client.patch(
        '/orders/test-order-123/order-type',
        data=json.dumps({"order_type": "pre_order"}),
        content_type='application/json',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 500
    data = response.get_json()
    assert 'Database connection failed' in data['error']


def test_update_order_type_order_not_found(client, mock_db, auth_token):
    """Test update_order_type when order doesn't exist"""
    mock_db.rowcount = 0
    
    response = client.patch(
        '/orders/nonexistent-order/order-type',
        data=json.dumps({"order_type": "pre_order"}),
        content_type='application/json',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 404
    data = response.get_json()
    assert 'Order not found' in data['error']


def test_update_order_details_no_body(client, mock_db, auth_token):
    """Test update_order_details without request body"""
    response = client.patch(
        '/orders/test-order-123/delivery-preferences',
        data=None,
        content_type='application/json',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 400
    data = response.get_json()
    if data:  # Only check error message if JSON response exists
        assert 'Request body is required' in data.get('error', '')


def test_update_order_details_db_connection_failed(client, mocker, auth_token):
    """Test update_order_details when database connection fails"""
    mocker.patch('app.get_db_connection', return_value=None)
    
    response = client.patch(
        '/orders/test-order-123/delivery-preferences',
        data=json.dumps({"remarks": "Test remarks"}),
        content_type='application/json',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 500
    data = response.get_json()
    assert 'Database connection failed' in data['error']


def test_update_order_details_no_fields_to_update(client, mock_db, auth_token):
    """Test update_order_details when no valid fields provided"""
    response = client.patch(
        '/orders/test-order-123/delivery-preferences',
        data=json.dumps({"invalid_field": "value"}),
        content_type='application/json',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'No fields to update' in data['error']


def test_update_order_details_order_not_found(client, mock_db, auth_token):
    """Test update_order_details when order doesn't exist"""
    mock_db.rowcount = 0
    
    response = client.patch(
        '/orders/nonexistent-order/delivery-preferences',
        data=json.dumps({"remarks": "Test remarks"}),
        content_type='application/json',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 404
    data = response.get_json()
    assert 'Order not found' in data['error']


def test_orchestrator_create_order_exception(client, mock_db, auth_token, mocker, mock_service_clients, requests_mock):
    """Test OrderOrchestrator.create_order exception handling"""
    # Mock inventory_service and customer_service to pass validation
    mocker.patch('app.customer_service.get', return_value={
        "customer_id": "test-customer-123", "name": "Test"
    })
    mocker.patch('app.inventory_service.get', return_value={
        "sku": "TEST-001", "quantity": 100, "is_active": True, "item_name": "Test",
        "unit_price": 10.0, "delivery_type": "standard", "variant": "test"
    })
    
    # Mock the global orchestrator's db connection to fail
    mock_connection = mocker.Mock()
    mock_cursor = mocker.Mock()
    mock_cursor.execute.side_effect = Exception("Database error")
    mock_connection.cursor.return_value = mock_cursor
    
    # Patch the orchestrator instance's db
    from app import orchestrator
    orchestrator.db = mock_connection
    
    order_data = {
        "customer_id": "test-customer-123",
        "items": [{"sku": "TEST-001", "quantity": 2}]
    }
    
    response = client.post(
        '/create_order',
        data=json.dumps(order_data),
        content_type='application/json',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 500
    data = response.get_json()
    assert 'error' in data


def test_orchestrator_get_order_details_exception(mocker, mock_db):
    """Test OrderOrchestrator.get_order_details exception handling"""
    from app import OrderOrchestrator
    
    # Mock get_db_connection to return mock_db
    mock_connection = mocker.Mock()
    mock_connection.cursor.side_effect = Exception("Database error")
    mocker.patch('app.get_db_connection', return_value=mock_connection)
    
    # Create orchestrator instance (no parameters)
    orch = OrderOrchestrator()
    
    result = orch.get_order_details("test-order-123")
    
    assert result is None


def test_validate_order_items_with_empty_sku_futures(mocker, mock_db):
    """Test validate_order_items when ThreadPoolExecutor returns no results"""
    from app import validate_order_items
    from concurrent.futures import Future
    
    # Mock inventory_service.get to return None (not found)
    mocker.patch('app.inventory_service.get', return_value=None)
    
    items = [{"sku": "INVALID-001", "quantity": 1}]
    
    valid, message, enriched = validate_order_items(items)
    
    assert not valid
    assert "not found in inventory" in message or "not active" in message or "invalid" in message.lower()


def test_orchestrator_create_order_general_exception(mocker, mock_db, requests_mock):
    """Test OrderOrchestrator.create_order general exception (lines 286-288)"""
    from app import OrderOrchestrator
    
    # Mock customer and inventory services to pass validation
    requests_mock.get('http://localhost:5002/customers/test-customer-123', json={
        "customer_id": "test-customer-123", "name": "Test"
    })
    requests_mock.get('http://localhost:5001/inventory/TEST-001', json={
        "sku": "TEST-001", "quantity": 100, "is_active": True, "item_name": "Test", 
        "unit_price": 10.0
    })
    
    # Mock get_db_connection to return a connection that will fail
    mock_connection = mocker.Mock()
    mock_cursor = mocker.Mock()
    mock_cursor.execute.side_effect = Exception("Database query failed")
    mock_connection.cursor.return_value = mock_cursor
    mocker.patch('app.get_db_connection', return_value=mock_connection)
    
    orch = OrderOrchestrator()
    
    result = orch.create_order(
        customer_id="test-customer-123",
        items=[{"sku": "TEST-001", "quantity": 1, "name": "Test", "unit_price": 10.0}],
        special_instructions="Handle with care"
    )
    
    assert "error" in result
    assert result["status"] == 500


def test_orchestrator_get_order_details_general_exception(mocker, mock_db):
    """Test OrderOrchestrator.get_order_details exception in try block (lines 331-333)"""
    from app import OrderOrchestrator
    
    # Mock get_db_connection to return a connection that will fail
    mock_connection = mocker.Mock()
    mock_cursor = mocker.Mock()
    mock_cursor.fetchone.side_effect = Exception("Query execution failed")
    mock_connection.cursor.return_value = mock_cursor
    mocker.patch('app.get_db_connection', return_value=mock_connection)
    
    orch = OrderOrchestrator()
    
    result = orch.get_order_details("test-order-123")
    
    assert result is None


def test_orchestrator_update_order_status_exception(mocker, mock_db):
    """Test OrderOrchestrator.update_order_status exception (lines 343-345)"""
    from app import OrderOrchestrator
    
    # Mock get_db_connection to return a connection that will fail
    mock_connection = mocker.Mock()
    mock_cursor = mocker.Mock()
    mock_cursor.execute.side_effect = Exception("Update failed")
    mock_connection.cursor.return_value = mock_cursor
    mocker.patch('app.get_db_connection', return_value=mock_connection)
    
    orch = OrderOrchestrator()
    
    result = orch.update_order_status("test-order-123", "completed")
    
    assert result is False


def test_validate_order_items_no_valid_products(mocker):
    """Test validate_order_items when inventory returns no valid products (line 163)"""
    from app import validate_order_items
    
    # Mock requests.get to return 404 for all products
    mock_response = mocker.Mock()
    mock_response.status_code = 404
    mock_response.json.return_value = {"error": "Product not found"}
    mocker.patch('requests.get', return_value=mock_response)
    
    items = [{"sku": "NONEXISTENT-001", "quantity": 1}]
    
    valid, message, enriched = validate_order_items(items)
    
    assert not valid
    assert len(enriched) == 0


def test_get_order_details_with_order_no_none(mocker, mock_db):
    """Test get_order_details when order_no is None (line 320 FALSE branch)"""
    from app import OrderOrchestrator
    
    # Mock get_db_connection to return mock connection
    mock_connection = mocker.Mock()
    mock_cursor = mocker.Mock()
    mock_cursor.fetchone.return_value = {
        "order_id": "test-123",
        "customer_id": "cust-123",
        "order_no": None,  # This triggers the FALSE branch
        "status": "pending",
        "total_value": 100.0,
        "created_at": "2025-10-24T10:00:00"
    }
    mock_cursor.fetchall.return_value = []
    mock_connection.cursor.return_value = mock_cursor
    mocker.patch('app.get_db_connection', return_value=mock_connection)
    
    orch = OrderOrchestrator()
    
    result = orch.get_order_details("test-123")
    
    assert result is not None
    assert result["delivery"] is None  # Should be None when order_no is None


def test_initiate_delivery_order_no_present(mocker, mock_db, mock_service_clients):
    """Test initiate_delivery when order already has order_no (line 371 FALSE branch)"""
    from app import OrderOrchestrator
    
    # Mock get_db_connection
    mocker.patch('app.get_db_connection', return_value=mock_db)
    
    orch = OrderOrchestrator()
    
    # Mock get_order_details to return order with existing order_no and valid status
    mocker.patch.object(orch, 'get_order_details', return_value={
        "order": {
            "order_id": "test-123",
            "order_no": "ORD-12345",  # Already has order_no
            "customer_id": "cust-123",
            "status": "validated",  # Valid status for delivery
            "latitude": 1.35,
            "longitude": 103.82
        },
        "items": [],
        "delivery": {"delivery_id": "del-123"}  # Already has delivery
    })
    
    mocker.patch.object(orch, 'update_order_status', return_value=True)
    
    result = orch.initiate_delivery("test-123")
    
    # Should succeed even though order_no already exists
    assert result["status"] == 200


def test_update_order_type_success_coverage(client, mock_db, auth_token):
    """Test update_order_type success path to ensure all branches covered"""
    mock_db.rowcount = 1
    
    response = client.patch(
        '/orders/test-order-123/order-type',
        data=json.dumps({"order_type": "asap"}),
        content_type='application/json',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 200


def test_update_delivery_preferences_success(client, mock_db, auth_token):
    """Test update delivery preferences with all fields"""
    mock_db.rowcount = 1
    
    response = client.patch(
        '/orders/test-order-123/delivery-preferences',
        data=json.dumps({
            "remarks": "Handle with care",
            "preferred_delivery_date": "2025-10-30",
            "preferred_delivery_time": "14:00:00"
        }),
        content_type='application/json',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 200


def test_update_delivery_preferences_partial_fields(client, mock_db, auth_token):
    """Test update delivery preferences with only some fields"""
    mock_db.rowcount = 1
    
    response = client.patch(
        '/orders/test-order-123/delivery-preferences',
        data=json.dumps({"remarks": "New remarks only"}),
        content_type='application/json',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 200


def test_update_delivery_preferences_with_null_time(client, mock_db, auth_token):
    """Test update with preferred_delivery_time as None/null"""
    mock_db.rowcount = 1
    
    response = client.patch(
        '/orders/test-order-123/delivery-preferences',
        data=json.dumps({
            "preferred_delivery_date": "2025-10-30",
            "preferred_delivery_time": None
        }),
        content_type='application/json',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 200


def test_get_unscheduled_orders_db_connection_failed(client, mocker, auth_token):
    """Test get_unscheduled_orders when database connection fails (line 696)"""
    mocker.patch('app.get_db_connection', return_value=None)
    
    response = client.get(
        '/orders/unscheduled',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 500
    data = response.get_json()
    assert 'Database connection failed' in data['error']


def test_get_delivery_schedules_db_connection_failed(client, mocker, auth_token):
    """Test get_all_schedules when database connection fails (line 934)"""
    mocker.patch('app.get_db_connection', return_value=None)
    
    response = client.get(
        '/schedules',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 500
    data = response.get_json()
    assert 'Database connection failed' in data['error']


def test_get_delivery_schedules_with_date_filter(client, mock_db, auth_token):
    """Test get_all_schedules with date filter (line 965)"""
    mock_db.fetchall.return_value = []
    
    response = client.get(
        '/schedules?date=2025-10-30',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 200


def test_get_delivery_schedules_with_status_filter(client, mock_db, auth_token):
    """Test get_all_schedules with status filter (line 969)"""
    mock_db.fetchall.return_value = []
    
    response = client.get(
        '/schedules?status=confirmed',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 200


def test_get_delivery_schedules_with_both_filters(client, mock_db, auth_token):
    """Test get_all_schedules with both date and status filters (line 973)"""
    mock_db.fetchall.return_value = []
    
    response = client.get(
        '/schedules?date=2025-10-30&status=confirmed',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 200


def test_get_delivery_schedules_with_datetime_fields(client, mock_db, auth_token):
    """Test get_delivery_schedules with datetime conversions (lines 991-997)"""
    from datetime import datetime, date, timedelta
    
    # Return schedules with various datetime fields
    mock_db.fetchall.return_value = [
        {
            'schedule_id': 'sch-123',
            'schedule_date': date(2025, 10, 30),  # date object - line 991-992
            'start_time': timedelta(hours=9),  # timedelta - line 993-994
            'estimated_end_time': timedelta(hours=17),  # timedelta - line 995-996
            'created_at': datetime(2025, 10, 24, 10, 0, 0),  # datetime - line 997-998
            'order_count': 5,
            'status': 'confirmed'
        }
    ]
    
    response = client.get(
        '/schedules',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert len(data['schedules']) == 1


def test_get_delivery_schedules_with_missing_datetime_fields(client, mock_db, auth_token):
    """Test get_all_schedules when datetime fields are None"""
    mock_db.fetchall.return_value = [
        {
            'schedule_id': 'sch-123',
            'schedule_date': None,  # Tests the .get() check
            'start_time': None,
            'estimated_end_time': None,
            'created_at': None,
            'order_count': 5,
            'status': 'draft'
        }
    ]
    
    response = client.get(
        '/schedules',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 200


def test_get_schedule_details_with_multiple_deliveries(client, mocker, auth_token):
    """Test get_schedule_by_date groups deliveries correctly (line 1038)"""
    from datetime import date, timedelta
    
    # Mock get_db_connection
    mock_connection = mocker.Mock()
    mock_cursor = mocker.Mock()
    mock_items_cursor = mocker.Mock()
    
    # Mock deliveries from same schedule
    mock_cursor.fetchall.return_value = [
        {
            'schedule_id': 'sch-123',
            'schedule_date': date(2025, 10, 30),
            'driver_id': 'drv-1',
            'driver_name': 'John Doe',
            'driver_contact': '12345678',
            'team': 'A',
            'total_locations': 5,
            'max_locations': 10,
            'remaining_capacity': 5,
            'schedule_status': 'in_progress',
            'start_time': timedelta(hours=9),
            'estimated_end_time': timedelta(hours=17),
            'route_polyline': 'encoded_polyline',
            'delivery_id': 'del-1',
            'order_id': 'ord-1',
            'sequence_number': 1,
            'order_no': 'ORD-001',
            'shopify_order_id': None,
            'order_type': 'standard',
            'customer_name': 'Test Customer',
            'customer_contact': '12345678',
            'customer_postal_code': '123456',
            'customer_street': '123 Test St',
            'customer_unit': '#01-01',
            'housing_type': 'HDB',
            'total_items': 1,
            'estimated_arrival_time': None,
            'actual_arrival_time': None,
            'delivery_status': 'pending',
            'requires_warehouse_return': False,
            'latitude': 1.35,
            'longitude': 103.82
        }
    ]
    
    # Mock order items query
    mock_items_cursor.fetchall.return_value = []
    
    # Make cursor() return different mocks for different calls
    call_count = [0]
    def cursor_side_effect(*args, **kwargs):
        call_count[0] += 1
        if call_count[0] == 1:
            return mock_cursor
        else:
            return mock_items_cursor
    
    mock_connection.cursor.side_effect = cursor_side_effect
    mock_connection.close.return_value = None
    mock_cursor.close.return_value = None
    mock_items_cursor.close.return_value = None
    mock_items_cursor.execute.return_value = None
    
    mocker.patch('app.get_db_connection', return_value=mock_connection)
    
    response = client.get(
        '/schedules/2025-10-30',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'schedules' in data
    # schedules should be a list
    assert isinstance(data['schedules'], list)
    assert len(data['schedules']) >= 1
    # Verify the grouping worked - should have deliveries array
    assert 'deliveries' in data['schedules'][0]


def test_orchestrator_create_order_exception_deep(mocker, requests_mock):
    """Test OrderOrchestrator.create_order exception at cursor.execute (lines 286-288)"""
    from app import OrderOrchestrator
    import mysql.connector
    
    # Mock customer service to pass validation
    requests_mock.get('http://localhost:5002/customers/cust-123', json={
        "customer_id": "cust-123",
        "name": "Test Customer"
    })
    
    # Mock inventory service to pass validation
    requests_mock.get('http://localhost:5001/inventory/TEST-001', json={
        "sku": "TEST-001",
        "quantity": 100
    })
    
    # Mock get_db_connection to return a mock database
    mock_db = mocker.Mock()
    mock_cursor = mocker.Mock()
    
    # Make execute raise exception to trigger lines 286-288
    mock_cursor.execute.side_effect = mysql.connector.Error("Query failed")
    mock_db.cursor.return_value = mock_cursor
    
    mocker.patch('app.get_db_connection', return_value=mock_db)
    
    orch = OrderOrchestrator()
    
    result = orch.create_order(
        customer_id="cust-123",
        items=[{"sku": "TEST-001", "quantity": 1, "name": "Test", "unit_price": 10.0}],
        special_instructions="Handle with care"
    )
    
    assert "error" in result
    assert result["status"] == 500


def test_orchestrator_get_order_details_exception_deep(mocker):
    """Test OrderOrchestrator.get_order_details exception at fetchone (lines 331-333)"""
    from app import OrderOrchestrator
    
    mock_db = mocker.Mock()
    mock_cursor = mocker.Mock()
    
    # Make fetchone raise exception to trigger lines 331-333
    mock_cursor.fetchone.side_effect = Exception("Fetch failed")
    mock_db.cursor.return_value = mock_cursor
    
    mocker.patch('app.get_db_connection', return_value=mock_db)
    
    orch = OrderOrchestrator()
    
    result = orch.get_order_details("order-123")
    
    assert result is None


def test_orchestrator_update_order_status_exception_deep(mocker):
    """Test OrderOrchestrator.update_order_status exception at execute (lines 343-345)"""
    from app import OrderOrchestrator
    
    mock_db = mocker.Mock()
    mock_cursor = mocker.Mock()
    
    # Make execute raise exception to trigger lines 343-345
    mock_cursor.execute.side_effect = Exception("Update failed")
    mock_db.cursor.return_value = mock_cursor
    
    mocker.patch('app.get_db_connection', return_value=mock_db)
    
    orch = OrderOrchestrator()
    
    result = orch.update_order_status("order-123", "completed")
    
    assert result is False


def test_validate_order_items_empty_results(mocker):
    """Test validate_order_items when no valid products found (line 163)"""
    from app import validate_order_items
    
    # Mock requests to return non-OK status for all requests
    mock_response = mocker.Mock()
    mock_response.status_code = 404
    mock_response.ok = False
    mocker.patch('requests.get', return_value=mock_response)
    
    items = [{"sku": "INVALID-001", "quantity": 1}]
    
    valid, message, enriched = validate_order_items(items)
    
    # Should fail validation when no products found
    assert not valid
    assert len(enriched) == 0


def test_update_delivery_preferences_no_valid_fields(client, mocker, auth_token):
    """Test update_delivery_preferences with no valid update fields (lines 588-590)"""
    # Mock get_db_connection to return a valid connection
    mock_connection = mocker.Mock()
    mock_cursor = mocker.Mock()
    mock_connection.cursor.return_value = mock_cursor
    mocker.patch('app.get_db_connection', return_value=mock_connection)
    
    # Send data with keys that aren't recognized (not remarks, preferred_delivery_date, or preferred_delivery_time)
    response = client.patch(
        '/orders/test-order-123/delivery-preferences',
        json={"invalid_field": "some value", "another_invalid": "data"},
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'No fields to update' in data['error']
    
    # Verify cursor.close() and connection.close() were called (lines 588-589)
    mock_cursor.close.assert_called_once()
    mock_connection.close.assert_called_once()


def test_get_delivery_schedules_with_conditions(client, mock_db, auth_token):
    """Test get_all_schedules with WHERE conditions (lines 965-973)"""
    from datetime import date, timedelta
    
    # Mock with data that triggers the conditional branches
    mock_db.fetchall.return_value = [
        {
            'schedule_id': 'sch-1',
            'schedule_date': date(2025, 10, 30),
            'start_time': timedelta(hours=9),
            'estimated_end_time': timedelta(hours=17),
            'created_at': None,
            'order_count': 3,
            'status': 'confirmed'
        }
    ]
    
    # Test with date filter (triggers line 965-966)
    response = client.get(
        '/schedules?date=2025-10-30',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert response.status_code == 200
    
    # Test with status filter (triggers line 969-970)
    response = client.get(
        '/schedules?status=confirmed',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert response.status_code == 200
    
    # Test with both filters (triggers line 973)
    response = client.get(
        '/schedules?date=2025-10-30&status=confirmed',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    assert response.status_code == 200


def test_get_delivery_schedules_datetime_conversions(client, mock_db, auth_token):
    """Test datetime conversions in schedules (lines 991-997)"""
    from datetime import date, timedelta, datetime
    
    mock_db.fetchall.return_value = [
        {
            'schedule_id': 'sch-1',
            'schedule_date': date(2025, 10, 30),  # Line 991-992
            'start_time': timedelta(hours=9, minutes=30),  # Line 993-994
            'estimated_end_time': timedelta(hours=17, minutes=45),  # Line 995-996
            'created_at': datetime(2025, 10, 24, 10, 30, 0),  # Line 997
            'order_count': 5,
            'status': 'in_progress'
        }
    ]
    
    response = client.get(
        '/schedules',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 200
    data = response.get_json()
    schedules = data['schedules']
    assert len(schedules) == 1
    # Verify all datetime fields were converted to strings
    assert isinstance(schedules[0]['schedule_date'], str)
    assert isinstance(schedules[0]['start_time'], str)
    assert isinstance(schedules[0]['estimated_end_time'], str)


def test_mark_delivery_complete_exception(client, mocker, auth_token):
    """Test mark_delivery_complete exception handling (lines 1164-1166)"""
    # Mock get_db_connection to raise exception
    mocker.patch('app.get_db_connection', side_effect=Exception("DB Error"))
    
    response = client.patch(
        '/orders/test-order-123/complete',
        data='{}',
        content_type='application/json',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 500
    data = response.get_json()
    assert 'error' in data


def test_get_unscheduled_orders_db_failure(client, mocker, auth_token):
    """Test get_unscheduled_orders with DB connection failure (line 696)"""
    mocker.patch('app.get_db_connection', return_value=None)
    
    response = client.get(
        '/orders/unscheduled',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 500
    data = response.get_json()
    assert 'Database connection failed' in data['error']


def test_get_delivery_schedules_db_failure(client, mocker, auth_token):
    """Test get_all_schedules with DB connection failure (line 934)"""
    mocker.patch('app.get_db_connection', return_value=None)
    
    response = client.get(
        '/schedules',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 500
    data = response.get_json()
    assert 'Database connection failed' in data['error']


def test_schedule_details_conditional_datetime_checks(client, mock_db, auth_token):
    """Test schedule details with conditional datetime checks (lines 994, 996)"""
    from datetime import date
    
    # Return schedule with None start_time and estimated_end_time to test conditional checks
    mock_db.fetchall.return_value = [
        {
            'schedule_id': 'sch-1',
            'schedule_date': date(2025, 10, 30),
            'driver_id': 'drv-1',
            'team': 'A',
            'total_locations': 3,
            'status': 'confirmed',
            'start_time': None,  # Test None case (line 994)
            'estimated_end_time': None,  # Test None case (line 996)
            'total_distance_meters': 1000,
            'total_duration_seconds': 3600,
            'created_at': None,
            'order_count': 2,
            'delivered_count': 0
        }
    ]
    
    response = client.get(
        '/schedules',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 200
    data = response.get_json()
    schedules = data['schedules']
    assert len(schedules) == 1
    # Verify None values are not converted (lines 994, 996 conditional checks prevent conversion)
    assert schedules[0]['start_time'] is None
    assert schedules[0]['estimated_end_time'] is None


def test_error_handler_500(client):
    """Test internal error handler (line 1367)"""
    # This is difficult to trigger directly, but we can test it exists
    from app import app as flask_app
    
    # Get the error handler
    error_handler = flask_app.error_handler_spec[None][500]
    assert error_handler is not None


def test_update_order_type_missing_body(client, mock_db, auth_token):
    """Test update order type with missing body (line 515)"""
    response = client.patch(
        '/orders/ORD-001/order-type',
        json={},
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert 'order_type is required' in data['error']


def test_update_order_type_invalid_type(client, mock_db, auth_token):
    """Test update order type with invalid type (line 525)"""
    response = client.patch(
        '/orders/ORD-001/order-type',
        json={'order_type': 'invalid_type'},
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert 'Invalid order_type' in data['error']


def test_update_order_type_not_found(client, mock_db, auth_token):
    """Test update order type when order not found (line 538-540)"""
    mock_cursor = mock_db.cursor.return_value
    mock_cursor.rowcount = 0
    
    response = client.patch(
        '/orders/ORD-999/order-type',
        json={'order_type': 'asap'},
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 404
    data = response.get_json()
    assert data['error'] == 'Order not found'


def test_update_order_type_db_error(client, mocker, auth_token):
    """Test update order type with database error (line 562)"""
    from mysql.connector import Error
    
    mocker.patch('app.get_db_connection', side_effect=Error("DB connection failed"))
    
    response = client.patch(
        '/orders/ORD-001/order-type',
        json={'order_type': 'asap'},
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 500
    data = response.get_json()
    assert 'error' in data


def test_update_delivery_preferences_no_body(client, mock_db, auth_token):
    """Test update delivery preferences with no body (line 567)"""
    response = client.patch(
        '/orders/ORD-001/delivery-preferences',
        json={},
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 400
    data = response.get_json()
    # Empty dict triggers "No fields to update" not "Request body is required"
    assert 'error' in data


def test_update_delivery_preferences_no_fields(client, mock_db, auth_token):
    """Test update delivery preferences with no valid fields (line 588-590)"""
    response = client.patch(
        '/orders/ORD-001/delivery-preferences',
        json={'invalid_field': 'value'},
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 400
    data = response.get_json()
    assert data['error'] == 'No fields to update'


def test_update_delivery_preferences_order_not_found(client, mock_db, auth_token):
    """Test update delivery preferences when order not found (line 603-605)"""
    mock_cursor = mock_db.cursor.return_value
    mock_cursor.rowcount = 0
    
    response = client.patch(
        '/orders/ORD-999/delivery-preferences',
        json={'remarks': 'Test remark'},
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 404
    data = response.get_json()
    assert data['error'] == 'Order not found'


def test_list_orders_db_connection_failed(client, mocker, auth_token):
    """Test list orders with database connection failure (line 696)"""
    mocker.patch('app.get_db_connection', return_value=None)
    
    response = client.get(
        '/orders',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 500
    data = response.get_json()
    assert data['error'] == 'Database connection failed'


def test_get_delivery_schedules_no_filters(client, mock_db, auth_token):
    """Test get delivery schedules without filters (line 973)"""
    mock_cursor = mock_db.cursor.return_value
    mock_cursor.fetchall.return_value = []
    
    response = client.get(
        '/schedules',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'schedules' in data


def test_get_delivery_schedules_date_filter_only(client, mock_db, auth_token):
    """Test get delivery schedules with date filter only (line 965-966)"""
    mock_cursor = mock_db.cursor.return_value
    mock_cursor.fetchall.return_value = []
    
    response = client.get(
        '/schedules?date=2025-10-24',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'schedules' in data


def test_get_delivery_schedules_status_filter_only(client, mock_db, auth_token):
    """Test get delivery schedules with status filter only (line 969-970)"""
    mock_cursor = mock_db.cursor.return_value
    mock_cursor.fetchall.return_value = []
    
    response = client.get(
        '/schedules?status=pending',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'schedules' in data


def test_get_schedule_details_schedule_date_conversion(client, mock_db, auth_token):
    """Test get schedule details with schedule_date conversion (line 994)"""
    from datetime import date
    
    mock_cursor = mock_db.cursor.return_value
    mock_cursor.fetchall.return_value = [{
        'schedule_id': 'SCH-001',
        'schedule_date': date(2025, 10, 24),
        'status': 'pending',
        'order_id': 'ORD-001',
        'order_no': 'ON-001',
        'customer_name': 'Test Customer',
        'delivery_address': '123 Test St',
        'customer_id': 'CUST-001',
        'contact_no': '12345678',
        'housing_type': 'HDB',
        'shopify_order_id': 'SH-001',
        'latitude': 1.3521,
        'longitude': 103.8198
    }]
    
    response = client.get(
        '/schedules/2025-10-24',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'schedules' in data


def test_get_schedule_details_start_time_conversion(client, mock_db, auth_token):
    """Test get schedule details with start_time conversion (line 996)"""
    from datetime import date, time
    
    mock_cursor = mock_db.cursor.return_value
    mock_cursor.fetchall.return_value = [{
        'schedule_id': 'SCH-001',
        'schedule_date': date(2025, 10, 24),
        'start_time': time(10, 0, 0),
        'status': 'pending',
        'order_id': 'ORD-001',
        'order_no': 'ON-001',
        'customer_name': 'Test Customer',
        'delivery_address': '123 Test St',
        'customer_id': 'CUST-001',
        'contact_no': '12345678',
        'housing_type': 'HDB',
        'shopify_order_id': 'SH-001',
        'latitude': 1.3521,
        'longitude': 103.8198
    }]
    
    response = client.get(
        '/schedules/2025-10-24',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'schedules' in data


def test_404_error_handler(client):
    """Test 404 error handler (line 1363)"""
    response = client.get('/non-existent-endpoint')
    
    assert response.status_code == 404
    data = response.get_json()
    assert data['error'] == 'Endpoint not found'


def test_validate_order_items_empty_list():
    """Test validate_order_items with empty list (line 163)"""
    from app import validate_order_items

    is_valid, error_msg, enriched = validate_order_items([])

    assert is_valid is False
    assert error_msg == "Order must contain at least one item"
    assert enriched == []


def test_orchestrator_create_order_base_exception(mocker, requests_mock):
    """Test OrderOrchestrator create_order with base Exception (lines 286-288)"""
    from app import OrderOrchestrator, get_db_connection
    
    # Mock get_db_connection to return a mock connection
    mock_connection = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    mocker.patch('app.get_db_connection', return_value=mock_connection)
    
    # Mock customer service
    requests_mock.get('http://customer:5001/customers/CUST-001', json={
        'customer_id': 'CUST-001',
        'customer_name': 'Test Customer'
    })
    
    # Mock inventory service
    requests_mock.get('http://inventory:5002/products/SKU-001', json={
        'sku': 'SKU-001',
        'product_name': 'Test Product',
        'unit_price': 10.0,
        'status': 'active'
    })
    
    # Make cursor.execute raise a base Exception
    mock_cursor.execute.side_effect = Exception("Database error")
    
    orchestrator = OrderOrchestrator()
    
    result = orchestrator.create_order(
        customer_id='CUST-001',
        items=[{'sku': 'SKU-001', 'quantity': 1}],
        special_instructions='Test instructions'
    )
    
    assert result['error'] == 'Internal server error'
    assert result['status'] == 500


def test_orchestrator_get_order_details_base_exception(mocker):
    """Test OrderOrchestrator get_order_details with base Exception (lines 331-333)"""
    from app import OrderOrchestrator
    
    # Mock get_db_connection to return a mock connection
    mock_connection = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    mocker.patch('app.get_db_connection', return_value=mock_connection)
    
    # Make cursor.execute raise a base Exception
    mock_cursor.execute.side_effect = Exception("Database error")
    
    orchestrator = OrderOrchestrator()
    
    result = orchestrator.get_order_details('ORD-001')
    
    assert result is None


def test_orchestrator_update_order_status_base_exception(mocker):
    """Test OrderOrchestrator update_order_status with base Exception (lines 343-345)"""
    from app import OrderOrchestrator
    
    # Mock get_db_connection to return a mock connection
    mock_connection = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    mocker.patch('app.get_db_connection', return_value=mock_connection)
    
    # Make cursor.execute raise a base Exception
    mock_cursor.execute.side_effect = Exception("Database error")
    
    orchestrator = OrderOrchestrator()
    
    result = orchestrator.update_order_status('ORD-001', 'validated')
    
    assert result is False

def test_orchestrator_create_order_exception_direct(mocker, requests_mock):
    """Directly test OrderOrchestrator.create_order catching exceptions (lines 286-288)"""
    from app import OrderOrchestrator

    # Patch get_db_connection to return a mock connection before instantiation
    mock_connection = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    mocker.patch('app.get_db_connection', return_value=mock_connection)

    # Mock customer and inventory services to allow orchestration to proceed to DB
    requests_mock.get('http://customer:5001/customers/CUST-001', json={
        'customer_id': 'CUST-001', 'customer_name': 'Test Customer'
    })
    requests_mock.get('http://inventory:5002/products/SKU-001', json={
        'sku': 'SKU-001', 'product_name': 'Test Product', 'unit_price': 10.0, 'status': 'active'
    })

    # Make cursor.execute raise an exception to hit the orchestrator's except
    mock_cursor.execute.side_effect = Exception("DB insert failed")

    orchestrator = OrderOrchestrator()

    result = orchestrator.create_order(
        customer_id='CUST-001',
        items=[{'sku': 'SKU-001', 'quantity': 1}],
        special_instructions='Test'
    )

    assert isinstance(result, dict)
    assert result.get('error') == 'Internal server error'


def test_orchestrator_get_order_details_exception_direct(mocker):
    """Directly test OrderOrchestrator.get_order_details catching exceptions (lines 331-333)"""
    from app import OrderOrchestrator

    mock_connection = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    mocker.patch('app.get_db_connection', return_value=mock_connection)

    # Make cursor.execute raise an exception
    mock_cursor.execute.side_effect = Exception("DB select failed")

    orchestrator = OrderOrchestrator()

    result = orchestrator.get_order_details('ORD-001')

    assert result is None


def test_orchestrator_update_order_status_exception_direct(mocker):
    """Directly test OrderOrchestrator.update_order_status catching exceptions (lines 343-345)"""
    from app import OrderOrchestrator

    mock_connection = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    mocker.patch('app.get_db_connection', return_value=mock_connection)

    mock_cursor.execute.side_effect = Exception("DB update failed")

    orchestrator = OrderOrchestrator()

    result = orchestrator.update_order_status('ORD-001', 'validated')

    assert result is False


def test_500_error_handler_by_raising(client, mocker, auth_token):
    """Trigger the 500 error handler by calling it directly."""
    from app import internal_error
    from werkzeug.exceptions import InternalServerError
    
    # Call the 500 error handler directly to cover line 1367
    response, status_code = internal_error(InternalServerError())
    
    assert status_code == 500
    data = response.get_json()
    assert data == {"error": "Internal server error"}


def test_update_delivery_preferences_no_valid_fields(client, mock_db, auth_token):
    """Test update delivery preferences with no valid fields (lines 588-590)"""
    mock_db.rowcount = 1
    
    # Send request with an invalid field name (not remarks, preferred_delivery_date, or preferred_delivery_time)
    response = client.patch(
        '/orders/ORD-001/delivery-preferences',
        json={'invalid_field': 'Test', 'another_invalid': 'Value'},
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 400
    data = response.get_json()
    assert data['error'] == 'No fields to update'

def test_update_delivery_preferences_order_not_found(client, mock_db, auth_token):
    """Test update delivery preferences when order not found (lines 603-605)"""
    # Ensure the mocked DB connection's cursor reports zero rows affected
    mock_db.rowcount = 0

    response = client.patch(
        '/orders/ORD-NONEXISTENT/delivery-preferences',
        json={'remarks': 'Test'},
        headers={'Authorization': f'Bearer {auth_token}'}
    )

    assert response.status_code == 404
    data = response.get_json()
    assert data['error'] == 'Order not found'

def test_update_delivery_preferences_order_not_found(client, mock_db, auth_token):
    """Test update delivery preferences when order not found (lines 603-605)"""
    mock_db.rowcount = 0  # Simulate no rows updated (order not found)
    
    response = client.patch(
        '/orders/ORD-NONEXISTENT/delivery-preferences',
        json={'remarks': 'Test'},
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 404
    data = response.get_json()
    assert data['error'] == 'Order not found'


def test_get_delivery_schedules_no_conditions(client, mock_db, auth_token):
    """Test get delivery schedules with no filters (line 973)"""
    mock_cursor = mock_db.cursor.return_value
    mock_cursor.fetchall.return_value = []
    
    response = client.get(
        '/schedules',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'schedules' in data


def test_get_delivery_schedules_only_date(client, mock_db, auth_token):
    """Test get delivery schedules with only date filter (lines 965-966)"""
    mock_cursor = mock_db.cursor.return_value
    mock_cursor.fetchall.return_value = []
    
    response = client.get(
        '/schedules?date=2025-10-24',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 200


def test_get_delivery_schedules_only_status(client, mock_db, auth_token):
    """Test get delivery schedules with only status filter (lines 969-970)"""
    mock_cursor = mock_db.cursor.return_value
    mock_cursor.fetchall.return_value = []
    
    response = client.get(
        '/schedules?status=pending',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 200


def test_get_schedule_details_with_schedule_date_object(client, mock_db, auth_token):
    """Test get schedule details with schedule_date as date object (line 994)"""
    from datetime import date
    
    mock_cursor = mock_db.cursor.return_value
    mock_cursor.fetchall.return_value = [{
        'schedule_id': 'SCH-001',
        'schedule_date': date(2025, 10, 24),
        'status': 'pending',
        'order_id': 'ORD-001',
        'order_no': 'ON-001',
        'customer_name': 'Test',
        'delivery_address': '123 Test',
        'customer_id': 'C-001',
        'contact_no': '12345678',
        'housing_type': 'HDB',
        'shopify_order_id': 'SH-001',
        'latitude': 1.3521,
        'longitude': 103.8198
    }]
    
    response = client.get(
        '/schedules/2025-10-24',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 200


def test_get_schedule_details_with_start_time_object(client, mock_db, auth_token):
    """Test get schedule details with start_time as time object (line 996)"""
    from datetime import date, time
    
    mock_cursor = mock_db.cursor.return_value
    mock_cursor.fetchall.return_value = [{
        'schedule_id': 'SCH-001',
        'schedule_date': date(2025, 10, 24),
        'start_time': time(10, 30, 0),
        'status': 'pending',
        'order_id': 'ORD-001',
        'order_no': 'ON-001',
        'customer_name': 'Test',
        'delivery_address': '123 Test',
        'customer_id': 'C-001',
        'contact_no': '12345678',
        'housing_type': 'HDB',
        'shopify_order_id': 'SH-001',
        'latitude': 1.3521,
        'longitude': 103.8198
    }]
    
    response = client.get(
        '/schedules/2025-10-24',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 200


def test_list_orders_db_connection_failure(client, mocker, auth_token):
    """Test list orders when DB connection fails (line 934)"""
    mocker.patch('app.get_db_connection', return_value=None)
    
    response = client.get(
        '/orders',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 500
    data = response.get_json()
    assert data['error'] == 'Database connection failed'


def test_mark_delivery_complete_with_exception(client, mocker, auth_token):
    """Test mark delivery complete with exception (lines 1164-1166)"""
    # Mock get_db_connection to return a connection
    mock_connection = mocker.MagicMock()
    mock_cursor = mocker.MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    mocker.patch('app.get_db_connection', return_value=mock_connection)
    
    # Make fetchone raise an exception
    mock_cursor.fetchone.side_effect = Exception("Database error")
    
    response = client.patch(
        '/orders/ORD-001/complete',
        headers={'Authorization': f'Bearer {auth_token}'}
    )
    
    assert response.status_code == 500
    data = response.get_json()
    assert 'error' in data


# ============================================
# START SERVER FUNCTION TESTS
# ============================================

def test_start_server_function(mocker):
    """
    Test the start_server() function to cover lines 1371-1373.
    """
    from app import app, start_server
    
    # Mock app.run to prevent actual server startup
    mock_run = mocker.patch.object(app, 'run')
    
    # Set environment variables
    mocker.patch.dict(os.environ, {'SERVICE_PORT': '5599', 'FLASK_ENV': 'development'})
    
    # Call start_server - this covers the function body (lines 1371-1373)
    start_server()
    
    # Verify app.run was called with correct parameters
    mock_run.assert_called_once_with(host="0.0.0.0", port=5599, debug=True)


def test_start_server_with_defaults(mocker):
    """
    Test start_server() with default environment values.
    """
    from app import app, start_server
    
    # Mock app.run
    mock_run = mocker.patch.object(app, 'run')
    
    # Clear SERVICE_PORT and FLASK_ENV to test defaults
    env_copy = os.environ.copy()
    if 'SERVICE_PORT' in env_copy:
        del env_copy['SERVICE_PORT']
    if 'FLASK_ENV' in env_copy:
        del env_copy['FLASK_ENV']
    mocker.patch.dict(os.environ, env_copy, clear=True)
    
    # Call start_server
    start_server()
    
    # Verify app.run was called with defaults (port 5005, debug=False)
    mock_run.assert_called_once_with(host="0.0.0.0", port=5005, debug=False)


# ============================================
# BRANCH COVERAGE TESTS (Lines 371, 1038, 1071)
# ============================================

def test_get_schedule_by_date_with_null_variant(client, mock_db, auth_token):
    """Test get_schedule_by_date with item that has null variant (line 1071 FALSE branch)"""
    mock_db.fetchall.side_effect = [
        # First call: get deliveries from view
        [{
            'schedule_id': 'schedule-1',
            'schedule_date': datetime(2025, 10, 20).date(),
            'driver_id': 'DRV001',
            'driver_name': 'Driver A',
            'driver_contact': '12345678',
            'team': 'Team A',
            'total_locations': 1,
            'max_locations': 18,
            'remaining_capacity': 17,
            'schedule_status': 'confirmed',
            'start_time': None,
            'estimated_end_time': None,
            'route_polyline': None,
            'order_id': 'order-1',
            'sequence_number': 1,
            'order_no': 'ORD-001',
            'shopify_order_id': None,
            'order_type': 'asap',
            'customer_name': 'Customer A',
            'customer_contact': '87654321',
            'customer_postal_code': '123456',
            'customer_street': 'Street 1',
            'customer_unit': '#01-01',
            'housing_type': 'HDB',
            'total_items': 1,
            'estimated_arrival_time': None,
            'actual_arrival_time': None,
            'delivery_status': 'scheduled',
            'requires_warehouse_return': 0,
            'latitude': 1.3521,
            'longitude': 103.8198
        }],
        # Second call: get order items with NULL variant
        [
            {'item_name': 'Product A', 'variant': None, 'quantity': 2}
        ]
    ]
    
    response = client.get('/schedules/2025-10-20')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert len(data['schedules']) == 1
    # Verify item format without variant
    items = data['schedules'][0]['deliveries'][0]['items']
    assert len(items) == 1
    assert items[0] == "2x Product A"  # No variant in parentheses


def test_get_schedule_by_date_multiple_schedules(client, mock_db, auth_token):
    """Test get_schedule_by_date with multiple deliveries in same schedule (line 1038 FALSE branch)"""
    mock_db.fetchall.side_effect = [
        # First call: get deliveries from view - 2 deliveries in same schedule
        [
            {
                'schedule_id': 'schedule-1',
                'schedule_date': datetime(2025, 10, 20).date(),
                'driver_id': 'DRV001',
                'driver_name': 'Driver A',
                'driver_contact': '12345678',
                'team': 'Team A',
                'total_locations': 2,
                'max_locations': 18,
                'remaining_capacity': 16,
                'schedule_status': 'confirmed',
                'start_time': None,
                'estimated_end_time': None,
                'route_polyline': None,
                'order_id': 'order-1',
                'sequence_number': 1,
                'order_no': 'ORD-001',
                'shopify_order_id': None,
                'order_type': 'asap',
                'customer_name': 'Customer A',
                'customer_contact': '87654321',
                'customer_postal_code': '123456',
                'customer_street': 'Street 1',
                'customer_unit': '#01-01',
                'housing_type': 'HDB',
                'total_items': 1,
                'estimated_arrival_time': None,
                'actual_arrival_time': None,
                'delivery_status': 'scheduled',
                'requires_warehouse_return': 0,
                'latitude': 1.3521,
                'longitude': 103.8198
            },
            {
                'schedule_id': 'schedule-1',  # Same schedule_id - tests FALSE branch
                'schedule_date': datetime(2025, 10, 20).date(),
                'driver_id': 'DRV001',
                'driver_name': 'Driver A',
                'driver_contact': '12345678',
                'team': 'Team A',
                'total_locations': 2,
                'max_locations': 18,
                'remaining_capacity': 16,
                'schedule_status': 'confirmed',
                'start_time': None,
                'estimated_end_time': None,
                'route_polyline': None,
                'order_id': 'order-2',
                'sequence_number': 2,
                'order_no': 'ORD-002',
                'shopify_order_id': None,
                'order_type': 'asap',
                'customer_name': 'Customer B',
                'customer_contact': '87654322',
                'customer_postal_code': '123457',
                'customer_street': 'Street 2',
                'customer_unit': '#02-02',
                'housing_type': 'Condo',
                'total_items': 1,
                'estimated_arrival_time': None,
                'actual_arrival_time': None,
                'delivery_status': 'scheduled',
                'requires_warehouse_return': 0,
                'latitude': 1.3522,
                'longitude': 103.8199
            }
        ],
        # Second call: items for order-1
        [{'item_name': 'Product A', 'variant': 'Red', 'quantity': 1}],
        # Third call: items for order-2
        [{'item_name': 'Product B', 'variant': 'Blue', 'quantity': 1}]
    ]
    
    response = client.get('/schedules/2025-10-20')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert len(data['schedules']) == 1  # One schedule
    assert len(data['schedules'][0]['deliveries']) == 2  # Two deliveries in same schedule


def test_initiate_delivery_with_existing_delivery_response(client, mock_db, auth_token, mocker):
    """Test initiate_delivery when delivery already exists (line 371 FALSE branch)"""
    from app import orchestrator
    
    # Mock get_order_details to return order with existing delivery
    mock_order_details = {
        'order': {
            'order_id': 'order-1',
            'order_no': 'ORD-001',
            'status': 'validated',
            'latitude': 1.3521,
            'longitude': 103.8198
        },
        'items': [],
        'delivery': {  # Existing delivery - line 371 should be FALSE
            'jobId': 'existing-job-123',
            'status': 'pending'
        }
    }
    
    mocker.patch.object(orchestrator, 'get_order_details', return_value=mock_order_details)
    mocker.patch.object(orchestrator, 'update_order_status', return_value=True)
    
    response = client.post('/orders/order-1/deliver')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == "Delivery initiated successfully"


def test_initiate_delivery_service_post_fails(mocker):
    """Test initiate_delivery when delivery_service.post returns None (line 371-372 TRUE branch)"""
    from app import orchestrator, delivery_service
    
    # Mock the database cursor to return order details
    mock_cursor = mocker.MagicMock()
    mock_cursor.fetchone.return_value = {
        'order_id': 'order-1',
        'order_no': 'ORD-001',
        'status': 'validated',
        'latitude': 1.3521,
        'longitude': 103.8198,
        'customer_name': 'Test Customer',
        'customer_contact': '12345678',
        'customer_street': 'Test Street',
        'customer_unit': '#01-01',
        'customer_postal_code': '123456'
    }
    mock_cursor.fetchall.return_value = []  # No order items
    
    mock_connection = mocker.MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    
    # Replace orchestrator's db connection
    orchestrator.db = mock_connection
    
    # Mock delivery_service.get to return None (no existing delivery)
    mocker.patch.object(delivery_service, 'get', return_value=None)
    
    # Mock delivery_service.post to return None (simulating failure) - THIS IS THE CRITICAL PATH
    mocker.patch.object(delivery_service, 'post', return_value=None)
    
    # Mock update_order_status to avoid DB issues
    mocker.patch.object(orchestrator, 'update_order_status', return_value=True)
    
    # Call the orchestrator method directly
    result = orchestrator.initiate_delivery('order-1')
    
    # Should return error because delivery_response is None (line 372)
    assert result['error'] == "Failed to create delivery"
    assert result['status'] == 500
    
    # Verify that delivery_service.post was actually called
    delivery_service.post.assert_called_once()
    
    # Verify that update_order_status was NOT called (because we returned early)
    orchestrator.update_order_status.assert_not_called()


def test_initiate_delivery_endpoint_post_fails(client, mocker, auth_token):
    """Test /deliver endpoint when delivery_service.post returns None (line 371-372 via endpoint)"""
    from app import orchestrator, delivery_service
    
    # Mock get_order_details to return proper order structure
    mock_order_details = {
        'order': {
            'order_id': 'order-1',
            'order_no': 'ORD-001',
            'status': 'validated',
            'latitude': 1.3521,
            'longitude': 103.8198
        },
        'items': [],
        'delivery': None  # No existing delivery - will try to create one
    }
    
    mocker.patch.object(orchestrator, 'get_order_details', return_value=mock_order_details)
    mocker.patch.object(delivery_service, 'post', return_value=None)  # POST fails
    
    response = client.post('/orders/order-1/deliver')
    
    # Should get 500 error because delivery creation failed
    assert response.status_code == 500
    data = response.get_json()
    assert data['error'] == "Failed to create delivery"


def test_initiate_delivery_post_succeeds(mocker):
    """Test initiate_delivery when delivery_service.post succeeds (line 371 FALSE branch->375)"""
    from app import orchestrator, delivery_service
    
    # Mock the database cursor to return order details
    mock_cursor = mocker.MagicMock()
    mock_cursor.fetchone.return_value = {
        'order_id': 'order-1',
        'order_no': 'ORD-001',
        'status': 'validated',
        'latitude': 1.3521,
        'longitude': 103.8198,
        'customer_name': 'Test Customer',
        'customer_contact': '12345678',
        'customer_street': 'Test Street',
        'customer_unit': '#01-01',
        'customer_postal_code': '123456'
    }
    mock_cursor.fetchall.return_value = []  # No order items
    
    mock_connection = mocker.MagicMock()
    mock_connection.cursor.return_value = mock_cursor
    
    # Replace orchestrator's db connection
    orchestrator.db = mock_connection
    
    # Mock delivery_service.get to return None (no existing delivery)
    mocker.patch.object(delivery_service, 'get', return_value=None)
    
    # Mock delivery_service.post to return SUCCESS (not None) - FALSE branch
    mock_delivery_response = {'jobId': 'job-123', 'status': 'created'}
    mocker.patch.object(delivery_service, 'post', return_value=mock_delivery_response)
    
    # Mock update_order_status to succeed
    mocker.patch.object(orchestrator, 'update_order_status', return_value=True)
    
    # Call the orchestrator method directly
    result = orchestrator.initiate_delivery('order-1')
    
    # Should succeed because delivery_response is NOT None (skips if block, goes to line 375)
    assert result['message'] == "Delivery initiated successfully"
    assert result['status'] == 200
    
    # Verify that delivery_service.post was called
    delivery_service.post.assert_called_once()
    
    # Verify that update_order_status WAS called (because we didn't return early)
    orchestrator.update_order_status.assert_called_once_with('order-1', 'out_for_delivery')


def test_unschedule_order_no_schedule_id(client, mock_db, auth_token):
    """Test unscheduling order when schedule_id is None (line 1274 FALSE branch->1284)"""
    # Mock scheduled order
    order_data = {
        'order_id': 'test-order-123',
        'order_no': 'ORD-20250101-ABC123',
        'is_scheduled': 1,
        'scheduled_delivery_date': '2025-10-01'
    }
    
    # Mock database calls in sequence
    mock_db.fetchone.side_effect = [
        order_data,  # First call: get order details
        None,  # Second call: get schedule_id - returns None (no schedule_orders entry)
        # Third call would be count query, but it's skipped because schedule_id is None
    ]
    
    response = client.patch('/orders/test-order-123/unschedule')
    
    # Should succeed even though schedule_id is None (skips the if block at line 1274)
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'Order unscheduled successfully' in data['message']

