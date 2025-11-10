#!/bin/bash

# Build script that runs tests before building Docker images
# Usage: ./build.sh [--no-tests] [--rebuild]

set -e  # Exit on any error

echo "🚀 Levels Living Build Script"
echo "==============================="

# Parse arguments
SKIP_TESTS=false
REBUILD=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --no-tests)
            SKIP_TESTS=true
            shift
            ;;
        --rebuild)
            REBUILD=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--no-tests] [--rebuild]"
            exit 1
            ;;
    esac
done

# Run tests first (unless skipped)
if [ "$SKIP_TESTS" = false ]; then
    echo "🧪 Running tests for all microservices..."

    python3 run_tests.py
    echo ""
    echo "✅ All tests passed!"
else
    echo "⚠️  Skipping tests (--no-tests flag used)"
fi

# Build Docker images
echo "🐳 Building Docker images..."

if [ "$REBUILD" = true ]; then
    echo "🔄 Rebuilding from scratch (no cache)..."
    docker-compose build --no-cache
else
    docker-compose build
fi

echo ""
echo "✅ Build completed successfully!"
echo ""
echo "💡 To start services: docker-compose up -d"
echo "💡 To view logs: docker-compose logs -f"