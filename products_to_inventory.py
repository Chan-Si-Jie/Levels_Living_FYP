#!/usr/bin/env python3
"""
Shopify Products JSON to Inventory Table Import Script
Converts Shopify product catalog into your Levels Living inventory database
"""

import json
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

def categorize_product(title, tags, vendor):
    """
    Determine category and subcategory from product info
    """
    title_lower = title.lower()
    tags_lower = tags.lower() if tags else ""

    # Category mapping logic
    if "mattress" in title_lower or "mattress" in tags_lower:
        return "Bedroom", "Mattresses"
    elif "bed" in title_lower and "frame" in title_lower:
        return "Bedroom", "Bed Frames"
    elif "sofa" in title_lower or "couch" in title_lower:
        return "Living Room", "Sofas"
    elif "chair" in title_lower:
        return "Living Room", "Chairs"
    elif "table" in title_lower:
        if "dining" in title_lower:
            return "Dining Room", "Dining Tables"
        else:
            return "Living Room", "Tables"
    elif "cabinet" in title_lower or "storage" in title_lower:
        return "Storage", "Cabinets"
    elif "wardrobe" in title_lower or "closet" in title_lower:
        return "Bedroom", "Wardrobes"
    elif "desk" in title_lower:
        return "Office", "Desks"
    else:
        return "General", "Miscellaneous"

def determine_delivery_type(weight, dimensions, title, tags):
    """
    Determine delivery type based on product characteristics
    """
    title_lower = title.lower()
    weight_kg = weight / 1000 if weight else 0  # Convert grams to kg

    # Heavy items (over 50kg)
    if weight_kg > 50:
        return "heavy_item"

    # Large items (mattresses, large furniture)
    if any(keyword in title_lower for keyword in ["mattress", "sofa", "wardrobe", "dining table"]):
        return "large_item"

    # Fragile items
    if any(keyword in title_lower for keyword in ["glass", "mirror", "ceramic"]):
        return "fragile"

    # Assembly required items
    if any(keyword in title_lower for keyword in ["cabinet", "desk", "table", "bed frame"]):
        return "assembly_required"

    # Default to standard
    return "standard"

def requires_assembly(title, description):
    """
    Determine if item requires assembly
    """
    content = f"{title or ''} {description or ''}".lower()
    assembly_keywords = ["assembly", "assemble", "self-assembled", "diy", "requires assembly"]
    return any(keyword in content for keyword in assembly_keywords)

def requires_special_handling(title, tags, weight):
    """
    Determine if special handling is required
    """
    title_lower = title.lower()
    weight_kg = weight / 1000 if weight else 0

    special_keywords = ["fragile", "glass", "mirror", "antique", "premium"]
    if any(keyword in title_lower for keyword in special_keywords):
        return True

    # Heavy items need special handling
    if weight_kg > 50:
        return True

    return False

def extract_dimensions(description, title):
    """
    Extract dimensions from product description
    """
    content = f"{title or ''} {description or ''}"

    # Look for dimension patterns like "3' x 6'3", "91.44 x 190.5cm", etc.
    dimension_patterns = [
        r"(\d+\.?\d*)\s*['\"]?\s*x\s*(\d+\.?\d*)\s*['\"]?\s*(?:x\s*(\d+\.?\d*))?\s*(?:cm|inch|inches|ft|feet)?",
        r"(\d+\.?\d*)\s*cm\s*x\s*(\d+\.?\d*)\s*cm(?:\s*x\s*(\d+\.?\d*)\s*cm)?",
        r"(\d+)\s*x\s*(\d+)(?:\s*x\s*(\d+))?\s*(?:cm|mm|inch)"
    ]

    for pattern in dimension_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            dims = matches[0]
            dimensions = {
                "length": float(dims[0]) if dims[0] else None,
                "width": float(dims[1]) if dims[1] else None,
                "height": float(dims[2]) if dims[2] and dims[2] else None,
                "unit": "cm"  # Default unit
            }
            return dimensions

    return None

def process_shopify_variant(product, variant):
    """
    Convert a Shopify product variant to inventory record
    """
    # Use variant SKU if available, otherwise generate one
    sku = (variant.get('sku') or '').strip()
    if not sku:
        sku = f"PROD_{product['id']}_VAR_{variant['id']}"

    # Build item name
    item_name = product.get('title', '')
    variant_title = (variant.get('title') or '').strip()
    if variant_title and variant_title != 'Default Title':
        item_name = f"{product['title']} - {variant_title}"

    # Get category info
    category, subcategory = categorize_product(
        product['title'],
        product.get('tags', ''),
        product.get('vendor', '')
    )

    # Extract dimensions from description
    dimensions = extract_dimensions(
        product.get('body_html', ''),
        product['title']
    )

    # Determine delivery characteristics
    weight = variant.get('grams', 0)
    delivery_type = determine_delivery_type(
        weight, dimensions, product['title'], product.get('tags', '')
    )

    # Build inventory record
    inventory_item = {
        'sku': sku,
        'item_name': item_name[:200],  # Truncate to fit VARCHAR(200)
        'variant': variant_title if variant_title != 'Default Title' else None,
        'category': category,
        'subcategory': subcategory,
        'description': clean_html_description(product.get('body_html', '')),
        'unit_price': Decimal(variant.get('price', '0')),
        'weight_per_unit': Decimal(str(weight / 1000)) if weight else None,  # Convert to kg
        'volume_per_unit': None,  # Not available in Shopify data
        'dimensions': json.dumps(dimensions) if dimensions else None,
        'delivery_type': delivery_type,
        'special_handling_required': requires_special_handling(
            product['title'], product.get('tags', ''), weight
        ),
        'assembly_required': requires_assembly(
            product['title'], product.get('body_html', '')
        ),
        'showroom_item': product.get('status') == 'active',
        'handling_instructions': None,  # To be filled manually if needed
        'storage_location': None,  # To be filled manually
        'supplier': product.get('vendor', ''),
        'supplier_sku': variant.get('barcode', ''),
        'image_urls': json.dumps([img.get('src') for img in product.get('images', [])]),
        'product_tags': json.dumps(product.get('tags', '').split(',') if product.get('tags') else []),
        'is_active': product.get('status') == 'active' and variant.get('inventory_quantity', 0) >= 0
    }

    return inventory_item

def clean_html_description(html_content):
    """
    Clean HTML from product description
    """
    if not html_content:
        return None

    # Remove HTML tags
    import re
    clean_text = re.sub(r'<[^>]+>', '', html_content)

    # Decode HTML entities
    import html
    clean_text = html.unescape(clean_text)

    # Clean up whitespace
    clean_text = re.sub(r'\s+', ' ', clean_text).strip() if clean_text else ''

    # Truncate if too long
    return clean_text[:1000] if clean_text else None

def import_inventory_item(inventory_item, connection):
    """
    Import a single inventory item into the database
    """
    cursor = connection.cursor()

    try:
        # Check if SKU already exists
        cursor.execute("SELECT sku FROM inventory WHERE sku = %s", (inventory_item['sku'],))
        if cursor.fetchone():
            print(f"SKU {inventory_item['sku']} already exists, skipping...")
            return False

        # Insert inventory item
        query = """
            INSERT INTO inventory (
                sku, item_name, variant, category, subcategory, description,
                unit_price, weight_per_unit, volume_per_unit, dimensions,
                delivery_type, special_handling_required, assembly_required,
                showroom_item, handling_instructions, storage_location,
                supplier, supplier_sku, image_urls, product_tags, is_active,
                created_at, updated_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s
            )
        """

        cursor.execute(query, (
            inventory_item['sku'],
            inventory_item['item_name'],
            inventory_item['variant'],
            inventory_item['category'],
            inventory_item['subcategory'],
            inventory_item['description'],
            inventory_item['unit_price'],
            inventory_item['weight_per_unit'],
            inventory_item['volume_per_unit'],
            inventory_item['dimensions'],
            inventory_item['delivery_type'],
            inventory_item['special_handling_required'],
            inventory_item['assembly_required'],
            inventory_item['showroom_item'],
            inventory_item['handling_instructions'],
            inventory_item['storage_location'],
            inventory_item['supplier'],
            inventory_item['supplier_sku'],
            inventory_item['image_urls'],
            inventory_item['product_tags'],
            inventory_item['is_active'],
            datetime.now(),
            datetime.now()
        ))

        connection.commit()
        print(f"Successfully imported SKU: {inventory_item['sku']} - {inventory_item['item_name']}")
        return True

    except Exception as e:
        connection.rollback()
        print(f"Error importing SKU {inventory_item['sku']}: {e}")
        return False
    finally:
        cursor.close()

def main():
    """
    Main function to convert products.json to inventory table
    """
    # Load Shopify products JSON
    with open('products.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Connect to database
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        print("Connected to database successfully")

        products = data.get('products', [])
        total_variants = 0
        successful_imports = 0

        for product in products:
            print(f"\nProcessing product: {product.get('title', 'Unknown')}")

            # Process each variant as a separate inventory item
            for variant in product.get('variants', []):
                total_variants += 1
                inventory_item = process_shopify_variant(product, variant)

                if import_inventory_item(inventory_item, connection):
                    successful_imports += 1

        print(f"\n=== Import Summary ===")
        print(f"Total products processed: {len(products)}")
        print(f"Total variants processed: {total_variants}")
        print(f"Successfully imported: {successful_imports}")
        print(f"Failed imports: {total_variants - successful_imports}")

    except mysql.connector.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if connection and connection.is_connected():
            connection.close()

if __name__ == "__main__":
    main()