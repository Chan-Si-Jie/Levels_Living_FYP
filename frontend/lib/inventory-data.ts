// ============================================================================
// DATABASE INTEGRATION GUIDE
// ============================================================================
// This file contains dummy data for development. To integrate with a live database:
//
// 1. CREATE API ROUTES (recommended approach):
//    - Create /app/api/inventory/route.ts for fetching all inventory items
//    - Create /app/api/inventory/[id]/route.ts for individual item CRUD operations
//
// 2. REPLACE FUNCTION CALLS:
//    Instead of:
//      const items = inventoryItems
//    Use:
//      const items = await fetch('/api/inventory').then(r => r.json())
//
//    Instead of:
//      const item = inventoryItems.find(i => i.id === id)
//    Use:
//      const item = await fetch(`/api/inventory/${id}`).then(r => r.json())
//
// 3. DATABASE SCHEMA EXAMPLE (SQL):
//    CREATE TABLE inventory_items (
//      id VARCHAR PRIMARY KEY,
//      name VARCHAR NOT NULL,
//      type VARCHAR NOT NULL,
//      quantity INTEGER NOT NULL DEFAULT 0,
//      required INTEGER NOT NULL DEFAULT 0,
//      created_at TIMESTAMP DEFAULT NOW(),
//      updated_at TIMESTAMP DEFAULT NOW()
//    );
//
//    CREATE INDEX idx_inventory_type ON inventory_items(type);
//
// 4. EXAMPLE API ROUTE (/app/api/inventory/route.ts):
//    import { NextResponse } from 'next/server'
//    import { neon } from '@neondatabase/serverless'
//
//    const sql = neon(process.env.DATABASE_URL!)
//
//    export async function GET() {
//      const items = await sql`
//        SELECT * FROM inventory_items
//        ORDER BY type, name
//      `
//      return NextResponse.json(items)
//    }
//
//    export async function PUT(request: Request) {
//      const body = await request.json()
//      const { id, name, type, quantity, required } = body
//
//      await sql`
//        UPDATE inventory_items
//        SET name = ${name},
//            type = ${type},
//            quantity = ${quantity},
//            required = ${required},
//            updated_at = NOW()
//        WHERE id = ${id}
//      `
//
//      return NextResponse.json({ success: true })
//    }
//
// 5. UPDATING INVENTORY IN FORMS:
//    In your form submission (e.g., app/inventory/[id]/page.tsx):
//
//    const handleSave = async () => {
//      await fetch('/api/inventory', {
//        method: 'PUT',
//        headers: { 'Content-Type': 'application/json' },
//        body: JSON.stringify(formData)
//      })
//      router.push('/inventory')
//    }
//
// ============================================================================

// Dummy data for development purposes only - replace with live database calls as described above
// export interface InventoryItem {
//   id: string
//   name: string
//   type: string
//   quantity: number
//   required: number
// }

// export const inventoryItems: InventoryItem[] = [
//   { id: "1", name: "2/8 normal hinge", type: "Door Hinge", quantity: 0, required: 0 },
//   { id: "2", name: "5/8 normal hinge", type: "Door Hinge", quantity: 1, required: 0 },
//   { id: "3", name: "7/8 normal hinge", type: "Door Hinge", quantity: 1, required: 0 },
//   { id: "4", name: "2/8 soft close hinge", type: "Door Hinge", quantity: 0, required: 0 },
//   { id: "5", name: "5/8 soft close hinge", type: "Door Hinge", quantity: 1, required: 0 },
//   { id: "6", name: "7/8 soft close hinge", type: "Door Hinge", quantity: 0, required: 0 },
//   { id: "7", name: "Dowel", type: "Dowel", quantity: 2, required: 0 },
//   { id: "8", name: '12" normal sliders', type: "Drawer Slider", quantity: 19, required: 0 },
//   { id: "9", name: '14" normal sliders', type: "Drawer Slider", quantity: 120, required: 0 },
//   { id: "10", name: '16" normal sliders', type: "Drawer Slider", quantity: 3, required: 0 },
//   { id: "11", name: '18" normal sliders', type: "Drawer Slider", quantity: 11, required: 0 },
//   { id: "12", name: '20" normal sliders', type: "Drawer Slider", quantity: 10, required: 0 },
//   { id: "13", name: '22" normal sliders', type: "Drawer Slider", quantity: 6, required: 0 },
//   { id: "14", name: '12" ball bearing sliders', type: "Drawer Slider", quantity: 17, required: 0 },
//   { id: "15", name: '14" ball bearing sliders', type: "Drawer Slider", quantity: 8, required: 0 },
//   { id: "16", name: '16" ball bearing sliders', type: "Drawer Slider", quantity: 0, required: 0 },
// ]


export interface InventoryItem {
  id: string; // Unique identifier (SKU)
  name: string; // Item name
  type: string; // Item type
  quantity: number; // Quantity available
  required: number; // Quantity required
}

import {
  fetchInventoryItems,
  fetchInventoryItemById,
  createInventoryItem,
  updateInventoryItem,
  deleteInventoryItem,
} from "./api/inv-service";

// Fetch all inventory items
export const getAllInventoryItems = async () => {
  try {
    return await fetchInventoryItems();
  } catch (error) {
    console.error("Error fetching inventory items:", error);
    throw error;
  }
};

// Fetch a single inventory item by ID
export const getInventoryItemById = async (id: string) => {
  try {
    return await fetchInventoryItemById(id);
  } catch (error) {
    console.error(`Error fetching inventory item with ID ${id}:`, error);
    throw error;
  }
};

// Create a new inventory item. 
export const addInventoryItem = async (itemData: any) => {
  try {
    return await createInventoryItem(itemData);
  } catch (error) {
    console.error("Error creating inventory item:", error);
    throw error;
  }
};

// Update an inventory item
export const editInventoryItem = async (id: string, itemData: any) => {
  try {
    return await updateInventoryItem(id, itemData);
  } catch (error) {
    console.error(`Error updating inventory item with ID ${id}:`, error);
    throw error;
  }
};

// Delete an inventory item
export const removeInventoryItem = async (id: string) => {
  try {
    return await deleteInventoryItem(id);
  } catch (error) {
    console.error(`Error deleting inventory item with ID ${id}:`, error);
    throw error;
  }
};