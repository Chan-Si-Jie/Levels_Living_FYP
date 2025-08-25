# Levels Living - Last Mile Delivery System

A comprehensive microservices-based last mile delivery system with complete API testing interface.

## Table of Contents
- [System Architecture](#system-architecture)
- [Quick Start Guide](#quick-start-guide)
- [Testing Your APIs](#testing-your-apis)
- [Service Documentation](#service-documentation)
- [Development Setup](#development-setup)
- [Troubleshooting](#troubleshooting)

---

## System Architecture

### Microservices Overview
This project implements a microservices architecture consisting of: (So far)

1. **User Authentication Service (Port 5001)** - Handles user registration, login, JWT token management
2. **Customer Service (Port 5002)** - Manages customer information, addresses, and preferences  
3. **Inventory Service (Port 5003)** - Inventory and delivery types


4. **MySQL Database** - Primary data storage with comprehensive schema
5. **Redis** - Session management, caching, and real-time features

### Technology Stack
- **Backend**: Python 3.11, Flask, Gunicorn
- **Database**: MySQL 8.0
- **Cache**: Redis 7 Alpine
- **Containerization**: Docker & Docker Compose
- **Authentication**: JWT with role-based access control
- **Frontend**: HTML5/CSS3/JavaScript (for the time being)

---

## Quick Start Guide

### Prerequisites
- Docker and Docker Compose installed
- Git for version control
- Web browser for API testing interface

### 1. Clone and Setup
```bash
git clone <your-repository>
cd FYP_Level_Logix
```

### 2. Start All Services
```bash
# Remove any existing images for fresh start
docker rmi $(docker images -q) -f

# Start all services with fresh build
docker-compose up -d --build
```

### 3. Verify Services
Check that all services are healthy:
```bash
# Check container status
docker-compose ps

# All services should show "healthy" status
# - levels_mysql (MySQL database)
# - levels_redis (Redis cache) 
# - levels_user_auth (User Authentication Service)
# - levels_customer (Customer Service)
# - levels_inventory (Inventory Service)
```

### 4. Start API Testing Interface
```bash
# Start the web server for the testing interface
python -m http.server 8000
```

**Operating the Program:**
- **API Testing Dashboard**: http://localhost:8000/api_tester.html OR run api_tester.html from your vscode
- **Services**: Running on ports 5001-5003
- **Database**: MySQL on port 3306
- **Redis**: On port 6379

- **SQL Workbench**: See port 3306 levels_sql inside docker desktop.
  - Username: root
  - Password: rootpassword

- **Redis Commander**: http://localhost:8081

---

## Testing Your APIs

### Web-Based Testing Dashboard
Open your browser to **http://localhost:8000/api_tester.html** for a complete testing interface featuring:

#### Features:
- **User Authentication**: Register, login, logout with visual session management
- **Customer Management**: Create and search customers with full address support
- **Inventory Management**: Product creation, search, and delivery type management
- **Real-time Monitoring**: Live API response logging with JSON syntax highlighting
- **Browser Console Logging**: Detailed debugging information (Press F12 to view)
- **Service Health Monitoring**: Real-time status of all microservices

#### Quick Testing Workflow:
1. **Check Service Health** - Verify all services are online (should show green)
2. **Register a User** - Create an admin account
3. **Login** - Get authenticated (session info appears in top bar)
4. **Test Endpoints** - Use the authenticated session to test all APIs
5. **Monitor Responses** - View detailed logs in the response panel and browser console

### Python Testing Script
For automated testing:
```bash
# To automate an API tests - Created by AI (Drop and reupload in database schema if you are using this)
python api_test.py

# Expected: 39/42 tests passing (92.9% success rate)
```

### Manual Testing with cURL
Quick manual tests:

**Health Checks:**
```bash
curl http://localhost:5001/health  # User Auth Service
curl http://localhost:5002/health  # Customer Service  
curl http://localhost:5003/health  # Inventory Service
```

**User Registration:**
```bash
curl -X POST http://localhost:5001/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@levels.sg",
    "password": "securePassword123!",
    "role": "admin"
  }'
```

**User Login:**
```bash
curl -X POST http://localhost:5001/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@levels.sg", 
    "password": "securePassword123!"
  }'
```

---

## Service Documentation

### User Authentication Service (Port 5001)
**Base URL**: `http://localhost:5001`

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/health` | GET | No | Service health check |
| `/auth/register` | POST | No | Register new user |
| `/auth/login` | POST | No | User authentication |
| `/auth/logout` | POST | Yes | User logout |
| `/auth/profile` | GET | Yes | Get user profile |
| `/auth/users` | GET | Yes (Admin) | List all users |
| `/auth/validate` | POST | Yes | Validate JWT token |

**User Roles Available:**
- `admin` - Full system access
- `hq` - Headquarters operations  
- `warehouse` - Warehouse operations
- `driver` - Delivery operations
- `customer_service` - Customer support

#### Sample Registration Request:
```json
{
  "email": "user@levels.sg",
  "password": "securePassword123!",
  "role": "admin"
}
```

#### Sample Login Response:
```json
{
  "message": "Login successful",
  "access_token": "jwt-access-token",
  "refresh_token": "jwt-refresh-token",
  "session_id": "session-uuid",
  "user": {
    "user_id": "user-uuid",
    "email": "user@levels.sg",
    "role": "admin"
  }
}
```

### Customer Service (Port 5002) 
**Base URL**: `http://localhost:5002`

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/health` | GET | No | Service health check |
| `/customers` | POST | Yes (Admin/HQ/CS) | Create new customer |
| `/customers` | GET | Yes (Admin/HQ/CS) | Search customers |
| `/customers/{id}` | GET | Yes (All roles) | Get customer by ID |
| `/customers/contact/{contact}` | GET | Yes (All roles) | Get customer by contact |
| `/customers/validate` | POST | Yes (Admin/HQ/CS) | Validate customer data |

**Supported Housing Types:**
- `HDB` - Housing Development Board flats
- `Condo` - Condominium apartments
- `Landed` - Landed properties  
- `Commercial` - Commercial addresses

#### Sample Customer Creation Request:
```json
{
  "customer_contact": "+6591234567",
  "customer_street": "123 Ang Mo Kio Ave 1",
  "customer_unit": "#12-34",
  "customer_postal_code": "560123",
  "housing_type": "HDB",
  "delivery_preferences": {
    "preferred_time": "morning",
    "special_instructions": "Ring doorbell twice"
  },
  "communication_preferences": {
    "sms": true,
    "email": false
  }
}
```

### Inventory Service (Port 5003)
**Base URL**: `http://localhost:5003`

| Endpoint | Method | Auth Required | Description |
|----------|--------|---------------|-------------|
| `/health` | GET | No | Service health check |
| `/inventory/products` | POST | Yes (Admin/HQ) | Create new product |
| `/inventory/products` | GET | Yes (All roles) | Search products |
| `/inventory/products/{sku}` | GET | Yes (All roles) | Get product by SKU |
| `/inventory/products/{sku}` | PUT | Yes (Admin/HQ) | Update product |
| `/inventory/delivery-types` | GET | Yes (All roles) | Get delivery types |
| `/inventory/delivery-requirements` | POST | Yes (Admin/HQ/WH) | Get delivery requirements |

**Delivery Types Available:**
- `standard` - Regular delivery (2-4 hours)
- `express` - Priority delivery (1-2 hours)
- `heavy_item` - Heavy items requiring equipment (3-5 hours)
- `large_item` - Oversized items (4-6 hours)
- `fragile` - Fragile handling required (3-4 hours)
- `special_handling` - Special requirements (3-5 hours)
- `white_glove` - Full-service delivery (4-8 hours)
- `assembly_required` - On-site assembly (2-6 hours)
- `showroom_pickup` - Showroom collection required (Variable)

#### Sample Product Creation Request:
```json
{
  "sku": "CHAIR001",
  "item_name": "Ergonomic Office Chair",
  "category": "Furniture",
  "description": "Professional office chair with lumbar support",
  "unit_price": 299.99,
  "weight_per_unit": 15.5,
  "delivery_type": "standard",
  "dimensions": {
    "length": 60,
    "width": 60,
    "height": 110
  }
}
```

---

## Development Setup

### Project Structure
```
FYP_Level_Logix/
├── docker-compose.yml          # Service orchestration
├── database.sql               # Database schema
├── comprehensive_api_test.py   # Automated testing script
├── api_tester.html            # Web testing interface
├── UserMS/                    # User Authentication Service
│   ├── app.py                 # Main application
│   ├── requirements.txt       # Python dependencies
│   └── Dockerfile            # Container configuration
├── CustomerMS/                # Customer Service
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
└── InventoryMS/               # Inventory Service
    ├── app.py
    ├── requirements.txt
    └── Dockerfile
```

### Environment Variables
Each service uses these environment variables (configured in docker-compose.yml):

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_HOST` | mysql | Database host |
| `DB_NAME` | levels_living_db_new | Database name |
| `DB_USER` | levels_user | Database user |
| `DB_PASSWORD` | levels_password | Database password |
| `REDIS_HOST` | redis | Redis host |
| `JWT_SECRET_KEY` | (auto-generated) | JWT signing key |

If using Root to access the Database:
|----------|---------|
| `user` | root |
| `password` | rootpassword |

### Service Ports
- **User Authentication Service**: 5001
- **Customer Service**: 5002
- **Inventory Service**: 5003
- **MySQL Database**: 3306
- **Redis**: 6379
- **API Testing Interface**: 8000

### Docker Services Configuration
- **MySQL**: Persistent data storage with health checks
- **Redis**: Session management and caching
- **UserMS**: Authentication service with JWT management
- **CustomerMS**: Customer data management with geolocation
- **InventoryMS**: Product catalog and delivery requirements

### Security Features
- **JWT Authentication**: Access and refresh tokens
- **Role-Based Access Control**: Fine-grained permissions
- **Account Security**: Login attempt limiting and lockouts
- **CORS Support**: Cross-origin resource sharing enabled
- **Input Validation**: Comprehensive data validation
- **Password Hashing**: Secure bcrypt hashing

---

## Troubleshooting

### Common Issues

#### 1. Services Not Starting
```bash
# Check container status
docker-compose ps

# View service logs
docker-compose logs user-auth-service
docker-compose logs customer-service  
docker-compose logs inventory-service
```

#### 2. Database Connection Issues
```bash
# Check MySQL status
docker-compose logs mysql

# Verify database exists
docker exec -it levels_mysql mysql -u levels_user -p levels_living_db_new
```

#### 3. CORS Errors in API Tester
```bash
# Restart web server
python -m http.server 8000

# Ensure you're accessing via http://localhost:8000/api_tester.html
# Not file:// protocol
```

#### 4. Port Already in Use
```bash
# Check what's using the port (Windows)
netstat -ano | findstr :5001

# Check what's using the port (Linux/Mac)
lsof -i :5001

# Stop all services and restart
docker-compose down
docker-compose up -d
```

#### 5. Authentication Issues
- Ensure you're logged in via the web interface or have valid JWT token
- Check token expiration (15 minutes for access tokens)
- Verify user role permissions for the endpoint

### Complete System Reset
```bash
# Stop and remove everything
docker-compose down -v

# Remove all images
docker rmi $(docker images -q) -f

# Clean Docker system
docker system prune -f

# Start fresh
docker-compose up -d --build
```

### Service Health Monitoring
All services include health check endpoints:
- **User Auth**: `GET /health`
- **Customer Service**: `GET /health` 
- **Inventory Service**: `GET /health`

Each returns database and Redis connection status.

### API Response Formats

#### Success Response Structure
```json
{
  "message": "Operation successful",
  "data": {
    // Response data
  }
}
```

#### Error Response Structure
```json
{
  "error": "Error description",
  "details": "Additional error details (optional)"
}
```

---

## Error Codes

| HTTP Status | Description | Common Scenarios |
|-------------|-------------|------------------|
| 200 | OK | Successful GET, PUT requests |
| 201 | Created | Successful POST requests |
| 207 | Multi-Status | Partial success in bulk operations |
| 400 | Bad Request | Invalid request data, validation errors |
| 401 | Unauthorized | Missing or invalid JWT token |
| 403 | Forbidden | Insufficient role permissions |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Duplicate resource (e.g., existing SKU, email) |
| 423 | Locked | Account temporarily locked |
| 500 | Internal Server Error | Server-side errors |

---


## Next Steps

### Upcoming Features
1. **Order Management Service** - Complete order lifecycle
2. **Delivery Service** - Route optimization and tracking
3. **Mobile Apps** - Driver and customer applications  
4. **Notification Service** - SMS/Email communications
5. **Analytics Dashboard** - Business intelligence
6. **API Gateway** - Centralized routing and rate limiting
7. **PDF Generation** - Delivery notes and invoices

### Integration Ready
The system is designed for easy integration with:
- **E-commerce Platforms** (Shopify, WooCommerce)
- **External APIs** (Google Maps, SendGrid)
- **Mobile Applications** (React Native, Flutter)
- **Frontend Frameworks** (React, Vue.js, Next.js)

---

## Support & Documentation

- **API Testing Interface**: http://localhost:8000/api_tester.html
- **Service Endpoints**: Ports 5001-5003
- **Database Management**: Available via Docker exec
- **Console Debugging**: Press F12 in browser for detailed logs

**Last Updated**: August 25th, 2025 11:00pm with API testing interface - Mervin Tan Zhi Yong

