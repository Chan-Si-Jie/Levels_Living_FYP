#!/usr/bin/env python3
"""
Shopify Order JSON to Database Import Script
Transforms Shopify order data into your Levels Living database format
"""

import json
import uuid
import mysql.connector
from datetime import datetime
from decimal import Decimal
import os

# Database configuration
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'database': os.environ.get('DB_NAME', 'levels_living_db_new'),
    'user': os.environ.get('DB_USER', 'levels_user'),
    'password': os.environ.get('DB_PASSWORD', 'levels_password'),
    'port': int(os.environ.get('DB_PORT', 3306))
}

def parse_shopify_order(shopify_order):
    """
    Transform a single Shopify order into database format
    """
    # Extract customer information
    customer = shopify_order.get('customer', {})
    shipping_address = shopify_order.get('shipping_address', {})

    # Map Shopify fields to your database schema
    order_data = {
        # Generate UUID for internal order_id
        'order_id': str(uuid.uuid4()),

        # Map Shopify order number to order_no
        'order_no': shopify_order.get('name', '').replace('#', ''),  # Remove # from "#12054"

        # Store Shopify's internal ID
        'shopify_order_id': str(shopify_order.get('id', '')),

        # Use Shopify order number as platform ID
        'platform_order_id': str(shopify_order.get('order_number', '')),

        # Customer ID - you'll need to map this to your customers table
        'customer_id': None,  # TO BE MAPPED to your customer system

        # Order status mapping
        'status': map_shopify_status(
            shopify_order.get('financial_status'),
            shopify_order.get('fulfillment_status')
        ),

        # Parse order date
        'order_date': parse_date(shopify_order.get('created_at')),

        # Financial information
        'order_value': Decimal(shopify_order.get('total_price', '0')),
        'currency': shopify_order.get('currency', 'SGD'),

        # Additional info
        'tag': shopify_order.get('tags', ''),
        'note': shopify_order.get('note') or f"Shopify Order - {shopify_order.get('source_name', 'pos')}"
    }

    # Extract line items
    line_items = []
    for item in shopify_order.get('line_items', []):
        line_item = {
            'item_id': str(uuid.uuid4()),
            'order_id': order_data['order_id'],
            'sku': item.get('sku', ''),
            'item_name': item.get('name', ''),
            'variant': item.get('variant_title'),
            'quantity': item.get('quantity', 1),
            'unit_price': Decimal(item.get('price', '0')),
            'total_price': Decimal(str(item.get('quantity', 1))) * Decimal(item.get('price', '0')),
            'assembled': False,  # Default value
            'assembly_notes': None
        }
        line_items.append(line_item)

    # Customer data for reference
    customer_data = {
        'first_name': customer.get('first_name', ''),
        'last_name': customer.get('last_name', ''),
        'email': customer.get('email', ''),
        'phone': customer.get('phone', ''),
        'address1': shipping_address.get('address1', ''),
        'address2': shipping_address.get('address2', ''),
        'city': shipping_address.get('city', ''),
        'zip': shipping_address.get('zip', ''),
        'country': shipping_address.get('country', ''),
        'latitude': shipping_address.get('latitude'),
        'longitude': shipping_address.get('longitude')
    }

    return order_data, line_items, customer_data

def map_shopify_status(financial_status, fulfillment_status):
    """
    Map Shopify status to your internal status enum
    """
    # Your status options: 'received', 'validated', 'processing', 'in_assembly',
    # 'ready_for_delivery', 'out_for_delivery', 'delivered', 'failed', 'cancelled', 'returned'

    if financial_status == 'paid' and fulfillment_status is None:
        return 'validated'  # Paid but not yet fulfilled
    elif financial_status == 'paid' and fulfillment_status == 'fulfilled':
        return 'delivered'
    elif fulfillment_status == 'partial':
        return 'processing'
    elif financial_status == 'refunded':
        return 'returned'
    elif financial_status == 'voided':
        return 'cancelled'
    else:
        return 'received'  # Default status

def parse_date(date_string):
    """
    Parse Shopify date format to database date
    """
    if not date_string:
        return datetime.now().date()

    try:
        # Shopify format: "2025-09-22T20:02:55+08:00"
        dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
        return dt.date()
    except:
        return datetime.now().date()

def find_or_create_customer(customer_data, cursor):
    """
    Find existing customer or create new one
    Returns customer_id
    """
    # Check if customer exists by phone or email
    phone = (customer_data.get('phone') or '').strip()
    email = (customer_data.get('email') or '').strip()

    if phone:
        cursor.execute("SELECT customer_id FROM customers WHERE customer_contact = %s", (phone,))
        result = cursor.fetchone()
        if result:
            return result[0]

    if email:
        cursor.execute("SELECT customer_id FROM customers WHERE customer_email = %s", (email,))
        result = cursor.fetchone()
        if result:
            return result[0]

    # Create new customer
    customer_id = str(uuid.uuid4())
    customer_query = """
        INSERT INTO customers (
            customer_id, customer_name, customer_email, customer_contact,
            customer_street, customer_unit, customer_postal_code,
            latitude, longitude, created_at, updated_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    full_name = f"{customer_data.get('first_name') or ''} {customer_data.get('last_name') or ''}".strip()

    cursor.execute(customer_query, (
        customer_id,
        full_name or 'Unknown Customer',
        email or None,
        phone or None,
        customer_data.get('address1', ''),
        customer_data.get('address2', ''),
        customer_data.get('zip', ''),
        customer_data.get('latitude'),
        customer_data.get('longitude'),
        datetime.now(),
        datetime.now()
    ))

    return customer_id

def import_shopify_order(shopify_order, connection):
    """
    Import a single Shopify order into the database
    """
    cursor = connection.cursor()

    try:
        # Parse the order
        order_data, line_items, customer_data = parse_shopify_order(shopify_order)

        # Find or create customer
        customer_id = find_or_create_customer(customer_data, cursor)
        order_data['customer_id'] = customer_id

        # Check if order already exists
        cursor.execute("SELECT order_id FROM orders WHERE shopify_order_id = %s",
                      (order_data['shopify_order_id'],))
        if cursor.fetchone():
            print(f"Order {order_data['order_no']} already exists, skipping...")
            return False

        # Insert order
        order_query = """
            INSERT INTO orders (
                order_id, order_no, shopify_order_id, platform_order_id,
                customer_id, status, order_date, order_value, currency,
                tag, note, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(order_query, (
            order_data['order_id'],
            order_data['order_no'],
            order_data['shopify_order_id'],
            order_data['platform_order_id'],
            order_data['customer_id'],
            order_data['status'],
            order_data['order_date'],
            order_data['order_value'],
            order_data['currency'],
            order_data['tag'],
            order_data['note'],
            datetime.now(),
            datetime.now()
        ))

        # Insert order items
        item_query = """
            INSERT INTO order_items (
                item_id, order_id, sku, item_name, variant,
                quantity, unit_price, total_price, assembled,
                assembly_notes, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        for item in line_items:
            cursor.execute(item_query, (
                item['item_id'],
                item['order_id'],
                item['sku'],
                item['item_name'],
                item['variant'],
                item['quantity'],
                item['unit_price'],
                item['total_price'],
                item['assembled'],
                item['assembly_notes'],
                datetime.now()
            ))

        connection.commit()
        print(f"Successfully imported order {order_data['order_no']}")
        return True

    except Exception as e:
        connection.rollback()
        print(f"Error importing order: {e}")
        return False
    finally:
        cursor.close()

def main():
    """
    Main function to import orders from JSON file
    """
    # Load the Shopify order JSON
    with open('order_sample.json', 'r') as f:
        data = json.load(f)

    # Connect to database
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        print("Connected to database successfully")

        # Process each order
        orders = data.get('orders', [])
        successful_imports = 0

        for order in orders:
            if import_shopify_order(order, connection):
                successful_imports += 1

        print(f"\nImport completed: {successful_imports}/{len(orders)} orders imported successfully")

    except mysql.connector.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if connection and connection.is_connected():
            connection.close()

if __name__ == "__main__":
    main()