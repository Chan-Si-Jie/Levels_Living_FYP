// DATABASE INTEGRATION GUIDE
// ==========================
// This file contains dummy data for the packing list.
// Replace these functions with actual database queries when integrating with your backend.
//
// Recommended Database Schema:
//
// CREATE TABLE packing_items (
//   id TEXT PRIMARY KEY,
//   pack_date TEXT NOT NULL,
//   sku TEXT NOT NULL,
//   quantity INTEGER NOT NULL,
//   variant TEXT NOT NULL,
//   order_no TEXT NOT NULL,
//   assembly TEXT NOT NULL,
//   item_name TEXT NOT NULL,
//   item_color TEXT,
//   is_highlighted BOOLEAN DEFAULT FALSE,
//   created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
// );
//
// API Integration Example:
//
// export async function getPackingItemsForDate(dateId: string) {
//   const response = await fetch(`/api/packing-items?date=${dateId}`)
//   return response.json()
// }

export interface PackingItem {
  id: string
  sku: string
  quantity: number
  variant: string
  orderNo: string
  assembly: string
  itemName: string
  itemColor?: string
  isHighlighted?: boolean
}

export const packingDates = [
  { id: "2024-01-15", date: "15 Jan 2024", itemCount: 15 },
  { id: "2024-01-16", date: "16 Jan 2024", itemCount: 12 },
  { id: "2024-01-17", date: "17 Jan 2024", itemCount: 8 },
]

// Dummy packing data - replace with database queries
const packingItemsData: Record<string, PackingItem[]> = {
  "2024-01-15": [
    {
      id: "1",
      sku: "SC4/WAL",
      quantity: 1,
      variant: "Assembly",
      orderNo: "12082",
      assembly: "Y",
      itemName: "Vegas Oak",
      itemColor: "green",
    },
    {
      id: "2",
      sku: "SC5",
      quantity: 1,
      variant: "Assembly",
      orderNo: "12086",
      assembly: "Y",
      itemName: "Vegas Oak",
      itemColor: "green",
    },
    {
      id: "3",
      sku: "SB8083/3065-soft close",
      quantity: 1,
      variant: "Assembly",
      orderNo: "Shaw-30ct",
      assembly: "Y",
      itemName: "SB8083",
      itemColor: "green",
    },
    {
      id: "4",
      sku: "SR5/3036",
      quantity: 1,
      variant: "Assembly",
      orderNo: "Shaw-30ct",
      assembly: "Y",
      itemName: "SR5",
      itemColor: "green",
    },
    {
      id: "5",
      sku: "SC15/WAL",
      quantity: 1,
      variant: "Assembly",
      orderNo: "12075",
      assembly: "Y",
      itemName: "Vegas Oak",
      itemColor: "green",
    },
    {
      id: "6",
      sku: "SC15/WAL",
      quantity: 1,
      variant: "Assembly",
      orderNo: "12065",
      assembly: "Y",
      itemName: "Vegas Oak",
      itemColor: "green",
    },
    {
      id: "7",
      sku: "SC4",
      quantity: 1,
      variant: "Assembly",
      orderNo: "12074",
      assembly: "Y",
      itemName: "Vegas Oak",
      itemColor: "green",
    },
    {
      id: "8",
      sku: "CU",
      quantity: 1,
      variant: "Upgrade",
      orderNo: "12054",
      assembly: "",
      itemName: "Soft Close",
      isHighlighted: true,
    },
    {
      id: "9",
      sku: "SC15(X2) - SOFTCLOSE",
      quantity: 1,
      variant: "Assembly",
      orderNo: "12054",
      assembly: "Y",
      itemName: "Vegas Oak",
      itemColor: "green",
      isHighlighted: true,
    },
    {
      id: "10",
      sku: "CU",
      quantity: 1,
      variant: "Upgrade",
      orderNo: "12071",
      assembly: "",
      itemName: "Soft Close",
      isHighlighted: true,
    },
    {
      id: "11",
      sku: "SC4(X2)/WAL",
      quantity: 1,
      variant: "Assembly",
      orderNo: "12071",
      assembly: "Y",
      itemName: "Vegas Oak",
      itemColor: "green",
      isHighlighted: true,
    },
    {
      id: "12",
      sku: "CTM11719",
      quantity: 1,
      variant: "Custom",
      orderNo: "11719",
      assembly: "Y",
      itemName: "Custom",
      itemColor: "green",
    },
    {
      id: "13",
      sku: "CTM11751",
      quantity: 1,
      variant: "Assembly",
      orderNo: "11771-P0",
      assembly: "Y",
      itemName: "Custom",
      itemColor: "green",
    },
    {
      id: "14",
      sku: "SC15/WAL",
      quantity: 1,
      variant: "Assembly",
      orderNo: "11900",
      assembly: "Y",
      itemName: "Vegas Oak",
      itemColor: "green",
    },
    {
      id: "15",
      sku: "BS-DC1232/4045WH",
      quantity: 1,
      variant: "Assembly",
      orderNo: "12069",
      assembly: "Y",
      itemName: "Evening Mist",
      itemColor: "green",
    },
    {
      id: "16",
      sku: "CTM11720",
      quantity: 1,
      variant: "Custom",
      orderNo: "11720",
      assembly: "Y",
      itemName: "Custom",
      itemColor: "green",
      isHighlighted: true,
    },
  ],
  "2024-01-16": [
    {
      id: "17",
      sku: "SC5/OAK",
      quantity: 2,
      variant: "Assembly",
      orderNo: "12090",
      assembly: "Y",
      itemName: "Oak Finish",
      itemColor: "green",
    },
    {
      id: "18",
      sku: "CU",
      quantity: 1,
      variant: "Upgrade",
      orderNo: "12091",
      assembly: "",
      itemName: "Soft Close",
      isHighlighted: true,
    },
  ],
  "2024-01-17": [
    {
      id: "19",
      sku: "SC10/WAL",
      quantity: 1,
      variant: "Assembly",
      orderNo: "12100",
      assembly: "Y",
      itemName: "Walnut",
      itemColor: "green",
    },
  ],
}

// DATABASE INTEGRATION: Replace with actual database query
// Example:
// export async function getPackingItemsForDate(dateId: string) {
//   const sql = neon(process.env.DATABASE_URL)
//   const items = await sql`
//     SELECT * FROM packing_items
//     WHERE pack_date = ${dateId}
//     ORDER BY order_no, sku
//   `
//   return items
// }
export function getPackingItemsForDate(dateId: string): PackingItem[] {
  return packingItemsData[dateId] || []
}
