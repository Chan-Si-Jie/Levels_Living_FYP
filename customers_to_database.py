#!/usr/bin/env python3
"""
Shopify Customer JSON to Database Import Script
Transforms Shopify customer data into your Levels Living database format
"""

import json
import uuid
import mysql.connector
from datetime import datetime
from decimal import Decimal
import os
import re

# Database configuration
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'database': os.environ.get('DB_NAME', 'levels_living_db_new'),
    'user': os.environ.get('DB_USER', 'levels_user'),
    'password': os.environ.get('DB_PASSWORD', 'levels_password'),
    'port': int(os.environ.get('DB_PORT', 3306))
}

def determine_housing_type(address_info):
    """
    Determine housing type from address information
    Returns: 'HDB', 'Condo', 'Landed', 'Commercial'
    """
    address_text = f"{address_info.get('address1', '')} {address_info.get('address2', '')}".lower()

    # HDB indicators
    hdb_keywords = ['blk', 'block', 'hdb', 'avenue', 'ave', 'street', 'st', 'road', 'rd', 'drive', 'dr']
    if any(keyword in address_text for keyword in hdb_keywords):
        # Check for unit format like "05-365" which is typical HDB format
        if re.search(r'\d{2}-\d{3}', address_info.get('address2', '')):
            return 'HDB'

    # Condo indicators
    condo_keywords = ['condo', 'condominium', 'residences', 'suites', 'towers', 'heights']
    if any(keyword in address_text for keyword in condo_keywords):
        return 'Condo'

    # Commercial indicators
    commercial_keywords = ['office', 'building', 'tower', 'plaza', 'centre', 'center', 'complex']
    if any(keyword in address_text for keyword in commercial_keywords):
        return 'Commercial'

    # Default to HDB for Singapore addresses
    return 'HDB'

def geocode_singapore_address(address_info):
    """
    Simple geocoding for Singapore addresses using postal codes
    This is a simplified version - in production you'd use a proper geocoding service
    """
    postal_code = address_info.get('zip', '')

    # Simplified mapping based on Singapore postal sectors
    # In production, you'd use Google Maps Geocoding API or Singapore's OneMap API
    postal_mappings = {
        # Central area
        '0': (1.2966, 103.8558),  # Marina Bay area
        '1': (1.3048, 103.8318),  # Raffles Place area
        '2': (1.3200, 103.8434),  # Chinatown area

        # North
        '5': (1.3691, 103.8454),  # Ang Mo Kio area (like your sample)
        '6': (1.4304, 103.8333),  # Yishun area
        '7': (1.4184, 103.8235),  # Woodlands area

        # East
        '4': (1.3162, 103.9058),  # Bedok area
        '3': (1.3138, 103.9648),  # Tampines area

        # West
        '6': (1.3375, 103.7047),  # Jurong area
        '2': (1.3519, 103.7442),  # Bukit Batok area
    }

    if postal_code and len(postal_code) >= 2:
        sector = postal_code[0]  # First digit indicates sector
        if sector in postal_mappings:
            return postal_mappings[sector]

    # Default Singapore coordinates if no mapping found
    return (1.3521, 103.8198)

def parse_communication_preferences(shopify_customer):
    """
    Parse communication preferences from Shopify customer data
    """
    email_consent = shopify_customer.get('email_marketing_consent')
    sms_consent = shopify_customer.get('sms_marketing_consent', {})

    preferences = {
        'email': email_consent is not None and email_consent.get('state') == 'subscribed',
        'sms': sms_consent.get('state') == 'subscribed',
        'phone': True,  # Default to allowing phone calls
        'preferred_time': 'business_hours',  # Default preference
        'language': 'en'  # Default to English
    }

    return preferences

def determine_delivery_preferences(shopify_customer):
    """
    Create delivery preferences based on customer data
    """
    preferences = {
        'delivery_time': 'business_hours',  # Default
        'special_instructions': shopify_customer.get('note', '') or None,
        'contact_method': 'phone',  # Primary contact method
        'delivery_window': 'standard',  # 3-7 days
        'requires_appointment': True  # Singapore deliveries typically need appointment
    }

    return preferences

def parse_shopify_customer(shopify_customer):
    """
    Transform a Shopify customer into database format
    """
    # Get default address (primary delivery address)
    default_address = shopify_customer.get('default_address', {})
    if not default_address and shopify_customer.get('addresses'):
        # Use first address if no default specified
        default_address = shopify_customer['addresses'][0]

    # Clean and format address components
    street = default_address.get('address1', '').strip()
    unit = default_address.get('address2', '').strip()
    postal_code = default_address.get('zip', '').strip()[:6]  # Limit to 6 chars

    # Get contact information
    phone = shopify_customer.get('phone', '').strip()
    if not phone and default_address.get('phone'):
        phone = default_address.get('phone', '').strip()

    # Determine housing type
    housing_type = determine_housing_type(default_address)

    # Get coordinates
    latitude, longitude = geocode_singapore_address(default_address)

    # Parse preferences
    communication_prefs = parse_communication_preferences(shopify_customer)
    delivery_prefs = determine_delivery_preferences(shopify_customer)

    # Build customer record
    customer_data = {
        'customer_id': str(uuid.uuid4()),  # Generate new UUID
        'shopify_customer_id': str(shopify_customer.get('id', '')),  # Store Shopify ID for reference
        'customer_contact': phone[:20] if phone else None,  # Limit to VARCHAR(20)
        'customer_street': street[:200] if street else None,  # Limit to VARCHAR(200)
        'customer_unit': unit[:20] if unit else None,  # Limit to VARCHAR(20)
        'customer_postal_code': postal_code,
        'housing_type': housing_type,
        'delivery_preferences': delivery_prefs,
        'communication_preferences': communication_prefs,
        'latitude': Decimal(str(latitude)),
        'longitude': Decimal(str(longitude)),
        'is_active': shopify_customer.get('state') != 'disabled',
        'created_at': datetime.now(),
        'updated_at': datetime.now()
    }

    return customer_data

def import_customer(customer_data, connection):
    """
    Import a single customer into the database
    """
    cursor = connection.cursor()

    try:
        # Check if customer already exists by phone number
        if customer_data['customer_contact']:
            cursor.execute("SELECT customer_id FROM customers WHERE customer_contact = %s",
                          (customer_data['customer_contact'],))
            if cursor.fetchone():
                print(f"Customer with phone {customer_data['customer_contact']} already exists, skipping...")
                return False

        # Insert customer
        query = """
            INSERT INTO customers (
                customer_id, customer_contact, customer_street, customer_unit,
                customer_postal_code, housing_type, delivery_preferences,
                communication_preferences, latitude, longitude, is_active,
                created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(query, (
            customer_data['customer_id'],
            customer_data['customer_contact'],
            customer_data['customer_street'],
            customer_data['customer_unit'],
            customer_data['customer_postal_code'],
            customer_data['housing_type'],
            json.dumps(customer_data['delivery_preferences']),
            json.dumps(customer_data['communication_preferences']),
            customer_data['latitude'],
            customer_data['longitude'],
            customer_data['is_active'],
            customer_data['created_at'],
            customer_data['updated_at']
        ))

        connection.commit()
        print(f"Successfully imported customer: {customer_data['customer_contact']} - {customer_data['customer_street']}")
        return True

    except Exception as e:
        connection.rollback()
        print(f"Error importing customer {customer_data.get('customer_contact', 'Unknown')}: {e}")
        return False
    finally:
        cursor.close()

def main():
    """
    Main function to import customers from JSON file
    """
    # Load the Shopify customer JSON
    with open('customer_sample.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Connect to database
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        print("Connected to database successfully")

        # Process each customer
        customers = data.get('customers', [])
        successful_imports = 0

        for customer in customers:
            print(f"\nProcessing customer: {customer.get('first_name', '')} {customer.get('last_name', '')}")

            # Parse customer data
            customer_data = parse_shopify_customer(customer)

            # Import to database
            if import_customer(customer_data, connection):
                successful_imports += 1

        print(f"\n=== Import Summary ===")
        print(f"Total customers processed: {len(customers)}")
        print(f"Successfully imported: {successful_imports}")
        print(f"Failed imports: {len(customers) - successful_imports}")

    except mysql.connector.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if connection and connection.is_connected():
            connection.close()

if __name__ == "__main__":
    main()