# OrderMS/tests/test_order_service.py
import pytest
import json
from datetime import datetime


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
