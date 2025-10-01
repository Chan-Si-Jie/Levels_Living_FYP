// ============================================================================
// DATABASE INTEGRATION GUIDE
// ============================================================================
// This file contains dummy data for development. To integrate with a live database:
//
// 1. CREATE API ROUTES (recommended approach):
//    - Create /app/api/delivery-dates/route.ts for fetching delivery dates
//    - Create /app/api/deliveries/route.ts for fetching deliveries
//    - Create /app/api/deliveries/[id]/route.ts for individual delivery details
//
// 2. REPLACE FUNCTION CALLS:
//    Instead of:
//      const dates = deliveryDates
//    Use:
//      const dates = await fetch('/api/delivery-dates').then(r => r.json())
//
//    Instead of:
//      const deliveries = getDeliveriesForDate(dateId)
//    Use:
//      const deliveries = await fetch(`/api/deliveries?dateId=${dateId}`).then(r => r.json())
//
// 3. DATABASE SCHEMA EXAMPLE (SQL):
//    CREATE TABLE delivery_dates (
//      id VARCHAR PRIMARY KEY,
//      date VARCHAR NOT NULL,
//      count INTEGER NOT NULL,
//      is_favorite BOOLEAN DEFAULT false
//    );
//
//    CREATE TABLE deliveries (
//      id VARCHAR PRIMARY KEY,
//      order_id VARCHAR NOT NULL,
//      order_details TEXT,
//      time_slot VARCHAR,
//      customer_name VARCHAR NOT NULL,
//      address TEXT,
//      phone VARCHAR,
//      status VARCHAR CHECK (status IN ('pending', 'delivered', 'cancelled')),
//      date_id VARCHAR REFERENCES delivery_dates(id),
//      skus TEXT,
//      items TEXT,
//      variants TEXT,
//      quantities TEXT,
//      street VARCHAR,
//      unit VARCHAR,
//      postal_code VARCHAR,
//      note TEXT,
//      signature_data TEXT,
//      created_at TIMESTAMP DEFAULT NOW(),
//      updated_at TIMESTAMP DEFAULT NOW()
//    );
//
// 4. EXAMPLE API ROUTE (/app/api/deliveries/route.ts):
//    import { NextResponse } from 'next/server'
//    import { neon } from '@neondatabase/serverless'
//
//    const sql = neon(process.env.DATABASE_URL!)
//
//    export async function GET(request: Request) {
//      const { searchParams } = new URL(request.url)
//      const dateId = searchParams.get('dateId')
//
//      const deliveries = await sql`
//        SELECT * FROM deliveries
//        WHERE date_id = ${dateId}
//        ORDER BY time_slot
//      `
//
//      return NextResponse.json(deliveries)
//    }
//
// ============================================================================

export interface DeliveryDate {
  id: string
  date: string
  count: number
  isFavorite?: boolean
}

export const deliveryDates: DeliveryDate[] = [
  { id: "1", date: "30 Sep 2025", count: 34, isFavorite: false },
  { id: "2", date: "1 Oct 2025", count: 32, isFavorite: true },
  { id: "3", date: "3 Oct 2025", count: 31, isFavorite: false },
  { id: "4", date: "10 Oct 2025", count: 26, isFavorite: false },
  { id: "5", date: "15 Oct 2025", count: 2, isFavorite: false },
]

export interface Delivery {
  id: string
  orderId: string
  orderDetails: string
  timeSlot: string
  customerName: string
  address: string
  phone: string
  status: "pending" | "delivered" | "cancelled"
  dateId: string
  skus: string
  items: string
  variants: string
  quantities: string
  street: string
  unit: string
  postalCode: string
  note: string
}

export const deliveries: Delivery[] = [
  {
    id: "1",
    orderId: "12045",
    orderDetails: "CU , SC5(X2) : Soft Close Hinge Upgrade , Vegas Oak 1.2m Wide 1.62m High Shoe Cabinet",
    timeSlot: "10 AM - 1 PM",
    customerName: "Kelly Ang",
    address: "102 Gerald Drive, 01-79, Singapore 798593",
    phone: "+6594245287",
    status: "delivered",
    dateId: "2",
    skus: "CU , SC5(X2)",
    items: "Soft Close Hinge Upgrade , Vegas Oak 1.2m Wide 1.62m High Shoe Cabinet",
    variants: "Upgrade , Assembly",
    quantities: "1 , 1",
    street: "102 Gerald Drive",
    unit: "01-79",
    postalCode: "798593",
    note: "Please sign below to confirm inspection and receipt of the items in the above packing list, and that they are in good condition. Hereafter, the recipient is responsible for the item and the condition it is in. Any new issue highlighted will be reviewed on a case-to-case basis and any decision made will be at the discretion of the company.",
  },
  {
    id: "2",
    orderId: "12045",
    orderDetails: "CU , SC5(X2) : Soft Close Hinge Upgrade , Vegas Oak 1.2m Wide 1.62m High Shoe Cabinet",
    timeSlot: "10 AM - 1 PM",
    customerName: "Kelly Ang",
    address: "102 Gerald Drive, 01-79, Singapore 798593",
    phone: "+6594245287",
    status: "delivered",
    dateId: "2",
    skus: "CU , SC5(X2)",
    items: "Soft Close Hinge Upgrade , Vegas Oak 1.2m Wide 1.62m High Shoe Cabinet",
    variants: "Upgrade , Assembly",
    quantities: "1 , 1",
    street: "102 Gerald Drive",
    unit: "01-79",
    postalCode: "798593",
    note: "Please sign below to confirm inspection and receipt of the items in the above packing list, and that they are in good condition. Hereafter, the recipient is responsible for the item and the condition it is in. Any new issue highlighted will be reviewed on a case-to-case basis and any decision made will be at the discretion of the company.",
  },
  {
    id: "3",
    orderId: "12041",
    orderDetails: "KI-SB1204/3045-add holes caps , CU : Osaka 1.2m Maple XL Shoe Cabinet , Soft Close Hinge Upgrade",
    timeSlot: "2 PM - 5 PM",
    customerName: "John Tan",
    address: "45 Orchard Road, #12-34, Singapore 238874",
    phone: "+6598765432",
    status: "pending",
    dateId: "2",
    skus: "KI-SB1204/3045 , CU",
    items: "Add holes caps , Osaka 1.2m Maple XL Shoe Cabinet , Soft Close Hinge Upgrade",
    variants: "Standard , Assembly",
    quantities: "2 , 1",
    street: "45 Orchard Road",
    unit: "#12-34",
    postalCode: "238874",
    note: "Please sign below to confirm inspection and receipt of the items in the above packing list, and that they are in good condition. Hereafter, the recipient is responsible for the item and the condition it is in. Any new issue highlighted will be reviewed on a case-to-case basis and any decision made will be at the discretion of the company.",
  },
  {
    id: "4",
    orderId: "12050",
    orderDetails: "CU : Modern Walnut 1.5m Wide TV Console with Storage",
    timeSlot: "9 AM - 12 PM",
    customerName: "Sarah Lim",
    address: "88 Marine Parade, #05-12, Singapore 449269",
    phone: "+6587654321",
    status: "pending",
    dateId: "1",
    skus: "CU",
    items: "Modern Walnut 1.5m Wide TV Console with Storage",
    variants: "Assembly",
    quantities: "1",
    street: "88 Marine Parade",
    unit: "#05-12",
    postalCode: "449269",
    note: "Please sign below to confirm inspection and receipt of the items in the above packing list, and that they are in good condition. Hereafter, the recipient is responsible for the item and the condition it is in. Any new issue highlighted will be reviewed on a case-to-case basis and any decision made will be at the discretion of the company.",
  },
]

// DATABASE INTEGRATION: Replace these functions with API calls
export function getDeliveriesForDate(dateId: string): Delivery[] {
  return deliveries.filter((delivery) => delivery.dateId === dateId)
}

export function getDeliveryById(id: string): Delivery | undefined {
  return deliveries.find((delivery) => delivery.id === id)
}
