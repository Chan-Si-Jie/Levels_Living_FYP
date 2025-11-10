@echo off
REM Build script that runs tests before building Docker images
REM Usage: build.bat [--no-tests] [--rebuild]

echo 🚀 Levels Living Build Script
echo ===============================
echo.

REM Parse arguments
set SKIP_TESTS=0
set REBUILD=0

if "%1"=="--no-tests" set SKIP_TESTS=1
if "%2"=="--rebuild" set REBUILD=1
if "%1"=="--rebuild" set REBUILD=1

REM Run tests first (unless skipped)
if %SKIP_TESTS%==0 (
    echo 🧪 Running tests for all microservices...
    echo.

    python run_tests.py
    if errorlevel 1 (
        echo.
        echo ❌ Tests failed! Aborting build.
        exit /b 1
    )
    echo.
    echo ✅ All tests passed!
    echo.
) else (
    echo ⚠️  Skipping tests ^(--no-tests flag used^)
    echo.
)

REM Build Docker images
echo 🐳 Building Docker images...

if %REBUILD%==1 (
    echo 🔄 Rebuilding from scratch ^(no cache^)...
    docker-compose build --no-cache
) else (
    docker-compose build
)

if errorlevel 1 (
    echo.
    echo ❌ Docker build failed!
    exit /b 1
)

echo.
echo ✅ Build completed successfully!
echo.
echo 💡 To start services: docker-compose up -d
echo 💡 To view logs: docker-compose logs -f