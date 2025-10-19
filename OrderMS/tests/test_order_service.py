# OrderMS/tests/test_order_service.py
import pytest
import json
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
