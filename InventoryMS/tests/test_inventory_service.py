# InventoryMS/tests/test_inventory_service.py
import pytest
import json


def test_health_check(client, mock_db):
    """Test health check endpoint"""
    # Mock successful database connection
    mock_db.fetchone.return_value = {"count": 1}
    
    response = client.get('/health')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert data['service'] == 'inventory-service'


def test_create_product_unauthorized(client, mock_db):
    """Test creating product without authentication should fail"""
    # Don't use auth_token fixture - this should test unauthorized access
    product_data = {
        "sku": "TEST-001",
        "item_name": "Test Product",
        "delivery_type": "standard"
    }
    
    response = client.post(
        '/inventory/products',
        data=json.dumps(product_data),
        content_type='application/json'
    )
    
    # Without auth_token, JWT verification should fail
    assert response.status_code == 401


def test_create_product_authorized(client, mock_db, auth_token):
    """Test creating product with valid authentication"""
    product_data = {
        "sku": "TEST-001",
        "item_name": "Test Product",
        "delivery_type": "standard",
        "category": "Furniture",
        "unit_price": 299.99,
        "weight_per_unit": 10.5,
        "volume_per_unit": 0.5
    }
    
    created_product = {
        "sku": "TEST-001",
        "item_name": "Test Product",
        "delivery_type": "standard",
        "category": "Furniture",
        "unit_price": 299.99,
        "weight_per_unit": 10.5,
        "volume_per_unit": 0.5,
        "dimensions": {},
        "image_urls": [],
        "product_tags": [],
        "is_active": True
    }
    
    # Mock the database operations
    # First call checks if SKU exists (should return None)
    # Second call returns the created product
    mock_db.fetchone.side_effect = [None, created_product]
    mock_db.rowcount = 1
    
    response = client.post(
        '/inventory/products',
        data=json.dumps(product_data),
        content_type='application/json'
    )
    
    assert response.status_code == 201
    data = response.get_json()
    assert data['message'] == 'Product created successfully'
    assert data['product']['sku'] == 'TEST-001'
    assert data['product']['item_name'] == 'Test Product'


def test_get_product_not_found(client, mock_db, auth_token):
    """Test getting non-existent product returns 404"""
    # Mock database to return None (product not found)
    mock_db.fetchone.return_value = None
    
    response = client.get('/inventory/products/NONEXISTENT')
    
    assert response.status_code == 404
    data = response.get_json()
    assert data['error'] == 'Product not found'


def test_get_product_success(client, mock_db, auth_token):
    """Test getting existing product"""
    product = {
        "sku": "TEST-001",
        "item_name": "Test Product",
        "variant": "Standard",
        "category": "Furniture",
        "delivery_type": "standard",
        "unit_price": 299.99,
        "dimensions": json.dumps({"length": 100, "width": 50, "height": 75}),
        "image_urls": json.dumps(["http://example.com/image.jpg"]),
        "product_tags": json.dumps(["furniture", "living room"]),
        "is_active": True
    }
    
    # Mock database to return the product
    mock_db.fetchone.return_value = product
    
    response = client.get('/inventory/products/TEST-001')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['sku'] == 'TEST-001'
    assert data['item_name'] == 'Test Product'
    # Verify JSON fields are parsed
    assert isinstance(data['dimensions'], dict)
    assert isinstance(data['image_urls'], list)
    assert isinstance(data['product_tags'], list)


def test_search_products(client, mock_db, auth_token):
    """Test searching products with filters"""
    products = [
        {
            "sku": "TEST-001",
            "item_name": "Test Product 1",
            "category": "Furniture",
            "delivery_type": "standard",
            "unit_price": 299.99,
            "dimensions": json.dumps({}),
            "image_urls": json.dumps([]),
            "product_tags": json.dumps([]),
            "is_active": True
        },
        {
            "sku": "TEST-002",
            "item_name": "Test Product 2",
            "category": "Furniture",
            "delivery_type": "express",
            "unit_price": 399.99,
            "dimensions": json.dumps({}),
            "image_urls": json.dumps([]),
            "product_tags": json.dumps([]),
            "is_active": True
        }
    ]
    
    # Mock database to return products and count
    mock_db.fetchall.return_value = products
    mock_db.fetchone.side_effect = [{"total": 2}]
    
    response = client.get('/inventory/products?category=Furniture&limit=10&offset=0')
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'products' in data
    assert 'pagination' in data
    assert len(data['products']) == 2
    assert data['pagination']['total'] == 2
    assert data['products'][0]['sku'] == 'TEST-001'


def test_update_product_success(client, mock_db, auth_token):
    """Test updating product successfully"""
    existing_product = {
        "sku": "TEST-001",
        "item_name": "Test Product",
        "delivery_type": "standard",
        "unit_price": 299.99,
        "dimensions": json.dumps({}),
        "image_urls": json.dumps([]),
        "product_tags": json.dumps([]),
        "is_active": True
    }
    
    updated_product = {
        "sku": "TEST-001",
        "item_name": "Updated Product",
        "delivery_type": "express",
        "unit_price": 349.99,
        "dimensions": json.dumps({}),
        "image_urls": json.dumps([]),
        "product_tags": json.dumps([]),
        "is_active": True
    }
    
    update_data = {
        "item_name": "Updated Product",
        "delivery_type": "express",
        "unit_price": 349.99
    }
    
    # Mock database operations
    # First call checks if product exists
    # Second call returns updated product
    mock_db.fetchone.side_effect = [existing_product, updated_product]
    mock_db.rowcount = 1
    
    response = client.put(
        '/inventory/products/TEST-001',
        data=json.dumps(update_data),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'Product updated successfully'
    assert data['product']['item_name'] == 'Updated Product'
    assert data['product']['unit_price'] == 349.99


def test_get_delivery_types(client, mock_db, auth_token):
    """Test getting delivery types"""
    # Note: This endpoint returns hardcoded delivery types, not from database
    response = client.get('/inventory/delivery-types')
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'delivery_types' in data
    
    # Verify the response contains expected delivery types
    delivery_types = data['delivery_types']
    assert 'standard' in delivery_types
    assert 'express' in delivery_types
    assert 'heavy_item' in delivery_types
    assert 'fragile' in delivery_types
    
    # Verify structure of delivery type objects
    assert 'name' in delivery_types['standard']
    assert 'description' in delivery_types['standard']
    assert 'estimated_time' in delivery_types['standard']
    assert 'requirements' in delivery_types['standard']


def test_get_delivery_requirements(client, mock_db, auth_token):
    """Test getting delivery requirements for multiple SKUs"""
    request_data = {
        "skus": ["TEST-001", "TEST-002"]
    }
    
    product_1 = {
        "sku": "TEST-001",
        "item_name": "Test Product 1",
        "variant": "Standard",
        "delivery_type": "standard",
        "weight_per_unit": 10.5,
        "volume_per_unit": 0.5,
        "special_handling_required": False,
        "assembly_required": False,
        "showroom_item": False,
        "handling_instructions": None
    }
    
    product_2 = {
        "sku": "TEST-002",
        "item_name": "Test Product 2",
        "variant": "Premium",
        "delivery_type": "express",
        "weight_per_unit": 5.0,
        "volume_per_unit": 0.3,
        "special_handling_required": True,
        "assembly_required": True,
        "showroom_item": False,
        "handling_instructions": "Handle with care"
    }
    
    # Mock database to return products for each SKU lookup
    # The function calls execute_query once per SKU
    mock_db.fetchone.side_effect = [product_1, product_2]
    
    response = client.post(
        '/inventory/delivery-requirements',
        data=json.dumps(request_data),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'delivery_requirements' in data
    assert len(data['delivery_requirements']) == 2
    assert data['delivery_requirements'][0]['sku'] == 'TEST-001'
    assert data['delivery_requirements'][1]['sku'] == 'TEST-002'
    assert 'delivery_complexity' in data['delivery_requirements'][0]
    assert 'estimated_delivery_time' in data['delivery_requirements'][0]
