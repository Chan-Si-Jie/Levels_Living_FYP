@echo off
REM Test runner script for all microservices (Windows version)
REM Run this from the project root directory

echo 🧪 Running tests for all microservices...

REM Test all services
set "services=UserMS CustomerMS InventoryMS DeliveryMS OrderMS NotificationMS"
set "failed_services="

for %%s in (%services%) do (
    echo.
    echo Testing %%s...

    if not exist "%%s" (
        echo ❌ %%s directory not found
        set "failed_services=%failed_services% %%s"
    ) else (
        cd %%s

        REM Check if tests directory exists
        if not exist "tests" (
            echo ⚠️  No tests directory found for %%s, skipping
        ) else (
            REM Install dependencies if requirements.txt exists
            if exist "requirements.txt" (
                echo 📦 Installing dependencies...
                pip install -r requirements.txt
            )

            REM Install pytest if not already installed
            python -m pip install pytest

            REM Run tests using python -m pytest
            python -m pytest --maxfail=1 --disable-warnings --tb=short tests
            if %errorlevel% equ 0 (
                echo ✅ %%s tests passed
            ) else (
                echo ❌ %%s tests failed
                set "failed_services=%failed_services% %%s"
            )
        )

        cd ..
    )
)

REM Summary
echo.
echo === Test Summary ===

if "%failed_services%"=="" (
    echo 🎉 All tests passed!
    exit /b 0
) else (
    echo ❌ Failed services:%failed_services%
    exit /b 1
)