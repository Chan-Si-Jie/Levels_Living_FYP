#!/bin/bash

# Test runner script for all microservices (Linux/macOS version)
# Run this from the project root directory

set -e  # Exit on any error

echo "🧪 Running tests for all microservices..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to run tests for a service
run_service_tests() {
    local service_name=$1
    local service_dir=$2

    echo -e "\n${YELLOW}Testing ${service_name}...${NC}"

    if [ ! -d "${service_dir}" ]; then
        echo -e "${RED}❌ ${service_dir} directory not found${NC}"
        return 1
    fi

    cd "${service_dir}"

    # Check if tests directory exists
    if [ ! -d "tests" ]; then
        echo -e "${YELLOW}⚠️  No tests directory found for ${service_name}, skipping${NC}"
        cd ..
        return 0
    fi

    # Install dependencies if requirements.txt exists
    if [ -f "requirements.txt" ]; then
        echo "📦 Installing dependencies..."
        pip install -r requirements.txt
    fi

    # Install pytest if not already installed
    pip install pytest

    # Run tests
    if python -m pytest --maxfail=1 --disable-warnings --tb=short tests; then
        echo -e "${GREEN}✅ ${service_name} tests passed${NC}"
        cd ..
        return 0
    else
        echo -e "${RED}❌ ${service_name} tests failed${NC}"
        cd ..
        return 1
    fi
}

# Test all services
services=(
    "UserMS:UserMS"
    "CustomerMS:CustomerMS"
    "InventoryMS:InventoryMS"
    "DeliveryMS:DeliveryMS"
    "OrderMS:OrderMS"
    "NotificationMS:NotificationMS"
)

failed_services=()

for service in "${services[@]}"; do
    IFS=':' read -r service_name service_dir <<< "$service"
    if ! run_service_tests "$service_name" "$service_dir"; then
        failed_services+=("$service_name")
    fi
done

# Summary
echo -e "\n${YELLOW}=== Test Summary ===${NC}"

if [ ${#failed_services[@]} -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}❌ Failed services: ${failed_services[*]}${NC}"
    exit 1
fi