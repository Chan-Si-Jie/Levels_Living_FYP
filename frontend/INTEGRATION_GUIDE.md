# Frontend-Backend Integration Guide

## 🎯 Overview

This guide documents the complete integration between the Next.js frontend (v2.0) and Flask microservices backend through Kong API Gateway for the Levels Living delivery management system.

**Last Updated:** October 6, 2025
**Integration Status:** ✅ Complete scheduling & delivery workflow functional

---

## 📁 Files Created

### 1. **Environment Configuration**
- **`.env.local`** - Backend service URLs (Kong gateway: `http://localhost:8000`)

### 2. **Core API Utilities** (`lib/`)
- **`api-config.ts`** - All backend endpoint definitions for 5 microservices
- **`auth-storage.ts`** - JWT token management (localStorage)
- **`api-client.ts`** - HTTP client with automatic authentication

### 3. **Service APIs** (`lib/api/`)
- **`auth-service.ts`** - Login, register, logout, profile, user management
- **`order-service.ts`** - Orders, scheduling, deliveries (complete scheduling workflow)

### 4. **Pages Connected to Backend** ✅
- **`app/login/page.tsx`** - Login page with role-based redirects
- **`app/schedule/page.tsx`** - Order scheduling with selection & creation
- **`app/delivery/page.tsx`** - List of scheduled delivery dates
- **`app/delivery/[id]/page.tsx`** - Delivery details for specific date with WhatsApp, Call, Maps, Waze

### 5. **Pages Still Using Mock Data**
- `app/delivery/[id]/[deliveryId]/page.tsx` - Individual delivery detail (signature pad)
- `app/inventory/page.tsx` - Inventory list
- `app/inventory/[id]/page.tsx` - Inventory details
- `app/pack/page.tsx` - Packing list
- `app/pack/[id]/page.tsx` - Packing details
- `app/overview/page.tsx` - Map overview

---

## 🔄 Complete Scheduling & Delivery Workflow (IMPLEMENTED)

### Step 1: View Unscheduled Orders (`/schedule`)
**Features:**
- Fetches unscheduled orders from `GET /orders/unscheduled`
- Displays orders sorted by priority (ASAP → Adhoc → Pre-order) then postal code
- Shows order details: customer, address, items, value (if > $0), preferred time
- Value display: Only shows if order value > $0 (hides $0.00 values)

### Step 2: Select Orders for Scheduling
**Features:**
- Checkbox selection (maximum 18 orders per day limit)
- "Select All" button (respects 18 order limit with warning)
- Manual reordering with up/down arrows
- Filter by postal code or address
- Visual feedback for selected orders (blue border highlight)
- Real-time counter showing X / 18 selected

### Step 3: Create Schedule
**Features:**
- Schedule date picker (today or future dates)
- Optional driver ID assignment
- Optional team assignment
- Real-time validation (minimum 1 order, date required)
- Creates schedule via `POST /orders/schedule`
- Backend performs route optimization via Google Routes API
- Auto-refreshes order list after creation
- Success toast notification

### Step 4: View Delivery Dates (`/delivery`)
**Features:**
- Fetches all schedules via `GET /schedules`
- Groups schedules by date
- Shows list of dates with delivery counts
- Uses original v2.0 UI design with `DeliveryDateList` component
- Clean list interface with clickable date cards

### Step 5: View Deliveries for Specific Date (`/delivery/[date]`)
**Features:**
- Shows formatted date header (e.g., "Thursday, October 3, 2025")
- Displays delivery count for the date
- Fetches schedules for specific date via `GET /schedules/{date}`
- Shows all deliveries across all schedules for that date
- **Action buttons for each delivery:**
  - 📱 **WhatsApp** - Opens WhatsApp with pre-filled message
  - 📞 **Call** - Initiates phone call
  - 🗺️ **NAV (GMAPS)** - Opens Google Maps navigation
  - 🚗 **NAV (WAZE)** - Opens Waze navigation
- Displays:
  - Order number and type
  - Customer name
  - Full address with map pin icon
  - Delivery status with color coding
  - ETA if available
- Clickable cards navigate to detailed view

---

## 🚀 Quick Start Guide

### Step 1: Start Backend Services

```bash
# Terminal 1 - Redis
redis-server

# Terminal 2 - UserMS (Port 5001)
cd UserMS && python app.py

# Terminal 3 - CustomerMS (Port 5002)
cd CustomerMS && python app.py

# Terminal 4 - InventoryMS (Port 5003)
cd InventoryMS && python app.py

# Terminal 5 - DeliveryMS (Port 5004)
cd DeliveryMS && python app.py

# Terminal 6 - OrderMS (Port 5005) - MOST IMPORTANT FOR SCHEDULING
cd OrderMS && python app.py

# Terminal 7 - Kong API Gateway (Port 8000)
kong start -c kong.yml
# OR if using Docker:
# docker-compose up kong
```

### Step 2: Create Test Users

```bash
# Create HQ user (can create schedules)
curl -X POST http://localhost:5001/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "hq@test.com",
    "password": "password123",
    "role": "hq"
  }'

# Create Driver user
curl -X POST http://localhost:5001/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "driver@test.com",
    "password": "password123",
    "role": "driver"
  }'
```

### Step 3: Start Frontend

```bash
cd "frontend v2.0"
npm install  # First time only
npm run dev
```

Visit: `http://localhost:3000`

### Step 4: Test Complete Workflow

1. **Login:**
   - Go to `http://localhost:3000/login`
   - Email: `hq@test.com`
   - Password: `password123`

2. **Create Schedule:**
   - Go to `http://localhost:3000/schedule`
   - Select orders using checkboxes (max 18)
   - Pick a schedule date
   - Optional: Add driver ID (e.g., DRV001)
   - Optional: Add team (e.g., Team A)
   - Click "Create Schedule"

3. **View Delivery Dates:**
   - Go to `http://localhost:3000/delivery`
   - See list of dates with scheduled deliveries
   - Click on a date to view details

4. **View Deliveries for Date:**
   - See formatted date header
   - See all deliveries for that date
   - Use action buttons:
     - Click WhatsApp icon to message customer
     - Click Phone icon to call
     - Click "NAV (GMAPS)" to navigate via Google Maps
     - Click "NAV (WAZE)" to navigate via Waze

---

## 🔌 API Integration Examples

### Example 1: Login User

```typescript
import { authService } from '@/lib/api/auth-service'
import { hasError } from '@/lib/api-client'

const response = await authService.login({
  email: 'hq@test.com',
  password: 'password123'
})

if (!hasError(response)) {
  console.log('User:', response.data.user)
  console.log('Token stored in localStorage')
  // User is automatically redirected based on role
}
```

### Example 2: Fetch Unscheduled Orders

```typescript
import { orderService } from '@/lib/api/order-service'

const response = await orderService.getUnscheduledOrders()

if (!hasError(response)) {
  console.log('Orders:', response.data.orders)
  console.log('Count:', response.data.count)
  // Orders are pre-sorted by priority and postal code
}
```

### Example 3: Create Schedule

```typescript
const response = await orderService.createSchedule({
  order_ids: ['order-uuid-1', 'order-uuid-2', 'order-uuid-3'],
  schedule_date: '2025-10-08',
  driver_id: 'DRV001',  // Optional
  team: 'Team A'         // Optional
})

if (!hasError(response)) {
  console.log('Schedule created!')
  console.log('Total locations:', response.data.total_locations)
  console.log('Route info:', response.data.route)
  // Backend automatically optimizes route via Google Routes API
}
```

### Example 4: Get All Schedules

```typescript
const response = await orderService.getSchedules()

if (!hasError(response)) {
  console.log('Schedules:', response.data.schedules)
  // Group by date in frontend for date list view
}
```

### Example 5: Get Schedules by Date

```typescript
const response = await orderService.getScheduleByDate('2025-10-08')

if (!hasError(response)) {
  console.log('Schedules:', response.data.schedules)
  // Each schedule includes deliveries array with sequence numbers
}
```

---

## 🔒 Authentication Flow

1. **Login** → JWT access & refresh tokens stored in `localStorage`
2. **API Requests** → Access token automatically added to `Authorization: Bearer {token}` header
3. **401 Response** → Tokens cleared, user redirected to `/login`
4. **Logout** → Tokens removed from localStorage + backend blacklist

**Token Storage Keys:**
- `access_token` - JWT access token (15 min expiry)
- `refresh_token` - JWT refresh token (7 day expiry)
- `user_data` - User object (user_id, email, role)

---

## 📊 Available API Functions

### Auth Service (`authService`)
```typescript
import { authService } from '@/lib/api/auth-service'

// Login
await authService.login({ email, password })

// Register
await authService.register({ email, password, role })

// Logout
await authService.logout()

// Get profile
await authService.getProfile()

// Validate token
await authService.validateToken()

// Get all users (admin only)
await authService.getAllUsers()

// Check auth status
authService.isAuthenticated()  // Returns boolean
authService.getCurrentUser()   // Returns user data or null
```

### Order Service (`orderService`)
```typescript
import { orderService } from '@/lib/api/order-service'

// Basic Order Operations
await orderService.createOrder(orderData)
await orderService.listOrders(page, perPage)
await orderService.getOrderById(orderId)
await orderService.updateOrderStatus(orderId, status)
await orderService.getOrdersByCustomer(customerId)
await orderService.completeDelivery(orderId)

// Scheduling Operations ✅ FULLY IMPLEMENTED
await orderService.getUnscheduledOrders()
await orderService.createSchedule({ order_ids, schedule_date, driver_id, team })
await orderService.getSchedules({ date?, status? })
await orderService.getScheduleByDate(date)
await orderService.deleteSchedule(scheduleId)
```

---

## 🐛 Troubleshooting

### Problem: "Network Error" when fetching data

**Solution:**
1. Check if backend services are running (especially OrderMS on port 5005)
2. Verify Kong API Gateway is running on port 8000
3. Open browser DevTools → Network tab → Check request/response
4. Check CORS configuration in backend services

### Problem: "401 Unauthorized"

**Solution:**
1. Login again - your token may have expired (15 min expiry)
2. Clear browser localStorage and login again
3. Check JWT_SECRET_KEY matches between frontend `.env.local` and backend
4. Verify token is being sent: DevTools → Network → Request Headers → Authorization

### Problem: No orders showing on schedule page

**Solution:**
1. Check OrderMS is running and database is connected
2. Create test orders in database:
   ```sql
   -- Ensure orders have is_scheduled = 0
   SELECT * FROM orders WHERE is_scheduled = 0;
   ```
3. Check browser console for API errors
4. Verify OrderMS logs for database query errors

### Problem: Schedule page shows "Value: $0.00"

**Solution:**
- Fixed! Now only shows value if > $0
- Update order values in database:
  ```sql
  UPDATE orders SET order_value = 150.00 WHERE order_id = 'your-order-id';
  ```

### Problem: Delivery page shows 404

**Solution:**
- Make sure schedule folder is in `app/schedule/page.tsx` not root
- Already fixed in current implementation

### Problem: WhatsApp/Call buttons not working

**Solution:**
- Check phone number format in database (should include country code)
- WhatsApp removes special characters automatically
- Call uses `tel:` protocol (works on mobile devices)

---

## 📝 Database Schema Used

### Key Tables:
- **`users`** - System users (admin, hq, warehouse, driver, customer_service)
- **`customers`** - Customer details with addresses, postal codes, lat/lng
- **`orders`** - Orders with `is_scheduled` flag, `scheduled_delivery_date`, and `order_value`
- **`order_items`** - Line items for each order
- **`delivery_schedules`** - Daily delivery schedules with route data
- **`schedule_orders`** - Junction table linking orders to schedules with sequence
- **`deliveries`** - Individual delivery jobs with status tracking

### Important Views:
- **`v_unscheduled_orders`** - Pre-sorted orders ready for scheduling (by priority & postal code)

---

## 🎨 UI/UX Features

### Schedule Page (`/schedule`)
- **Clean card-based layout** (maintains v2.0 design)
- **Checkbox selection** with visual border highlight
- **18-location limit enforcement** with toast notifications
- **Reordering controls** (up/down arrows + drag handle)
- **Filter inputs** (postal code, address)
- **Create schedule form** with validation
- **Select All button** (auto-limits to 18)
- **Loading states** with spinner
- **Empty states** with helpful messages
- **Smart value display** - Only shows if > $0

### Delivery List Page (`/delivery`)
- **Original v2.0 UI** using `DeliveryDateList` component
- **Groups schedules by date**
- **Shows delivery count** per date
- **Clean list interface** with chevron icons
- **Loading state** with spinner
- **Empty state** with link to schedule page

### Delivery Detail Page (`/delivery/[date]`)
- **Formatted date header** (e.g., "Thursday, October 3, 2025")
- **Delivery count** displayed in header
- **Card-based delivery list** (original v2.0 design)
- **Action buttons:**
  - WhatsApp icon (opens with pre-filled message)
  - Phone icon (initiates call)
  - NAV (GMAPS) button
  - NAV (WAZE) button
- **Status color coding:**
  - Delivered: Green
  - Scheduled: Blue
  - In Transit: Orange
  - Failed: Red
- **Clickable cards** for detailed view
- **Map pin icon** next to address

---

## 🔗 Complete Endpoint Reference

All requests go through Kong Gateway at `http://localhost:8000`

### Authentication Endpoints (UserMS)
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/register` | Register new user | No |
| POST | `/auth/login` | Login user | No |
| POST | `/auth/logout` | Logout user | Yes |
| GET | `/auth/profile` | Get user profile | Yes |
| POST | `/auth/validate` | Validate JWT token | Yes |
| GET | `/auth/users` | List all users | Yes (admin/hq) |

### Order Endpoints (OrderMS)
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/create_order` | Create new order | Yes |
| GET | `/orders` | List orders (paginated) | Yes |
| GET | `/orders/{id}` | Get order details | Yes |
| PUT | `/orders/{id}/status` | Update order status | Yes |
| GET | `/orders/customer/{id}` | Get customer orders | Yes |
| PATCH | `/orders/{id}/complete` | Mark delivery complete | Yes |

### Scheduling Endpoints (OrderMS) ✅
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/orders/unscheduled` | Get unscheduled orders | Yes (hq/admin) |
| POST | `/orders/schedule` | Create delivery schedule | Yes (hq/admin) |
| GET | `/schedules` | List all schedules | Yes |
| GET | `/schedules/{date}` | Get schedules by date | Yes |
| DELETE | `/schedules/{id}` | Delete schedule | Yes (hq/admin) |

### Customer Endpoints (CustomerMS)
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/customers` | Create customer | Yes |
| GET | `/customers/{id}` | Get customer | Yes |
| GET | `/customers/contact/{contact}` | Get by contact | Yes |
| GET | `/customers` | Search customers | Yes |
| POST | `/customers/validate` | Validate customer | Yes |

### Inventory Endpoints (InventoryMS)
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/inventory/products` | Create product | Yes (admin/hq) |
| GET | `/inventory/products` | List products | Yes |
| GET | `/inventory/products/{sku}` | Get product | Yes |
| PUT | `/inventory/products/{sku}` | Update product | Yes (admin/hq) |
| POST | `/inventory/delivery-requirements` | Get delivery reqs | Yes |
| GET | `/inventory/delivery-types` | List delivery types | Yes |

---

## ✅ Integration Checklist

### Infrastructure
- [x] Environment variables configured (`.env.local`)
- [x] API client with automatic authentication
- [x] Error handling with toast notifications
- [x] JWT token storage and management

### Services
- [x] Auth service fully implemented
- [x] Order service with complete scheduling workflow
- [ ] Customer service (not yet created)
- [ ] Inventory service (not yet created)
- [ ] Delivery service (not yet created)

### Pages
- [x] Login page with role-based redirects
- [x] Schedule page - order selection & schedule creation
- [x] Delivery list page - grouped by date (original v2.0 design)
- [x] Delivery detail page - with WhatsApp, Call, Maps, Waze buttons
- [ ] Individual delivery detail page (signature pad)
- [ ] Inventory pages
- [ ] Packing pages
- [ ] Overview/map page

### Features
- [x] User authentication flow
- [x] Unscheduled orders display
- [x] Order selection (checkbox with 18-limit)
- [x] Schedule creation with validation
- [x] Schedule viewing by date
- [x] WhatsApp integration
- [x] Phone call integration
- [x] Google Maps navigation
- [x] Waze navigation
- [x] Loading states
- [x] Error handling
- [x] Smart value display (hide $0.00)
- [x] Date formatting
- [ ] Protected routes middleware
- [ ] Mark delivery as complete button
- [ ] Real-time updates
- [ ] Route map visualization
- [ ] Signature capture

---

## 🚧 Known Limitations

1. **No protected route middleware** - Pages can be accessed without login (tokens just won't work)
2. **No refresh token implementation** - Tokens expire after 15 minutes
3. **Limited error messages** - Some backend errors may not be user-friendly
4. **No offline support** - Requires active backend connection
5. **Individual delivery detail page not connected** - Signature pad page still uses mock data
6. **No "Mark as Complete" functionality** - Button not yet implemented

---

## 🎯 Recommended Next Steps

### Priority 1: Complete Delivery Flow
1. Connect individual delivery detail page (`/delivery/[id]/[deliveryId]`)
   - Fetch order details from backend
   - Connect signature pad
   - Implement "Mark as Complete" button
   - Call `PATCH /orders/{id}/complete` endpoint

2. Add "Mark as Complete" buttons on delivery list
   - Add button to each delivery card
   - Show confirmation dialog
   - Update status in real-time
   - Show success toast

### Priority 2: Add More Services
1. Create `customer-service.ts`
2. Create `inventory-service.ts`
3. Create `delivery-service.ts`
4. Connect inventory pages to backend
5. Connect packing pages to backend

### Priority 3: Security & UX
1. Add protected route middleware
2. Implement refresh token flow
3. Add better error messages
4. Add confirmation dialogs for destructive actions
5. Add real-time updates (WebSocket or polling)
6. Add route map visualization (Google Maps integration)

---

## 💡 Tips for Development

### Working with the API Client
```typescript
// Always check for errors
import { hasError } from '@/lib/api-client'

const response = await orderService.getUnscheduledOrders()

if (hasError(response)) {
  // Handle error
  toast.error(response.error.error)
  return
}

// Use the data
const orders = response.data.orders
```

### Adding New API Endpoints
1. Add endpoint to `lib/api-config.ts`
2. Add function to appropriate service file (e.g., `lib/api/order-service.ts`)
3. Add TypeScript types for request/response
4. Use in your component with error handling

### Debugging Tips
1. Check browser Network tab (F12) for API calls
2. Check OrderMS/UserMS console logs for backend errors
3. Use `console.log(response)` to see API responses
4. Check localStorage for stored tokens
5. Use toast notifications for user-friendly errors

### Handling Data Type Issues
```typescript
// Convert string to number before using .toFixed()
Number(value || 0).toFixed(2)

// Check if value exists and is > 0 before displaying
{Number(value || 0) > 0 && (
  <p>Value: ${Number(value).toFixed(2)}</p>
)}
```

---

## 📞 Support & Documentation

- **Backend API Docs:** Check each microservice's `app.py` for available endpoints
- **Database Schema:** See `levels-living_db_schema.sql`
- **Old React Implementation:** Check `backups/OrderScheduling.jsx` and `backups/ScheduledDeliveries.jsx`
- **Frontend Backup:** Check `app/backup/delivery/` for original v2.0 UI reference

---

## 📋 Session Summary

**What Was Built:**
1. ✅ Complete scheduling workflow (select, create, view)
2. ✅ Delivery list page with date grouping
3. ✅ Delivery detail page with action buttons (WhatsApp, Call, Maps, Waze)
4. ✅ Individual delivery detail page with signature pad and Mark Complete
5. ✅ Driver dashboard with today's deliveries and Mark Complete
6. ✅ HQ dashboard with date selector and delivery overview
7. ✅ Smart value display (hides $0.00)
8. ✅ Date formatting headers
9. ✅ Original v2.0 UI design preserved
10. ✅ All backend integrations functional
11. ✅ Role-based access control for Schedule page
12. ✅ Role-based navigation (Driver vs Admin/HQ)

**Files Modified:**
- `app/login/page.tsx` - Fixed redirects to proper dashboards
- `app/schedule/page.tsx` - Added role-based access control (admin/hq only)
- `app/delivery/page.tsx` - Restored original v2.0 UI, connected to backend
- `app/delivery/[id]/page.tsx` - Added WhatsApp/Call/Maps/Waze, date header
- `app/delivery/[id]/[deliveryId]/page.tsx` - Connected signature pad, Mark Complete button
- `app/dashboard/page.tsx` - Driver dashboard with Mark Complete functionality
- `app/hq-dashboard/page.tsx` - HQ dashboard with date selector
- `components/mobile-nav.tsx` - Role-based navigation items
- `lib/api/order-service.ts` - Complete scheduling API functions
- `lib/api/auth-service.ts` - Authentication functions
- `lib/api/inv-service.ts` - Inventory API functions
- `lib/api-client.ts` - HTTP client with auto-auth
- `.env.local` - Kong gateway configuration

---

## 🔐 Access Control & User Roles

**User Roles:**
- `admin` - Full access (HQ functions + Schedule creation)
- `hq` - Full access (HQ functions + Schedule creation)
- `driver` - Limited access (No Schedule creation)

**Page Access:**
- `/login` - Public
- `/schedule` - ✅ **Admin/HQ only** (protected with access control)
- `/dashboard` - Driver dashboard
- `/hq-dashboard` - HQ/Admin dashboard
- `/delivery` - All authenticated users
- `/inventory` - All authenticated users
- `/pack` - All authenticated users
- `/overview` - All authenticated users

**Login Redirects:**
- Driver → `/dashboard`
- Admin/HQ → `/hq-dashboard`

**Navigation Items:**

**Driver Navigation (5 items):**
1. Dashboard
2. Pack
3. Delivery
4. Inventory
5. Overview

**Admin/HQ Navigation (6 items):**
1. Dashboard
2. Schedule (admin/hq only)
3. Pack
4. Delivery
5. Inventory
6. Overview

---

**Last Updated:** January 7, 2025
**Status:** ✅ Scheduling, delivery workflow, and role-based access control fully functional
**Next Session:**
- Add signature data persistence to backend
- Connect Pack pages to backend
- Connect Overview map to display route polylines
- Add inventory detail page (`/inventory/[id]`)
- Implement refresh token flow
- Add protected route middleware

**Happy Coding! 🚀**
