#!/usr/bin/env python3
"""
Cross-platform test runner for all microservices
Run this from the project root directory
"""

import os
import sys
import subprocess
import platform

def run_command(cmd, cwd=None):
    """Run a command and return (success, output, error)"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def run_service_tests(service_name, service_dir):
    """Run tests for a specific service"""
    print(f"\n🧪 Testing {service_name}...")

    if not os.path.exists(service_dir):
        print(f"❌ {service_dir} directory not found")
        return False

    os.chdir(service_dir)

    # Check if tests directory exists
    if not os.path.exists("tests"):
        print(f"⚠️  No tests directory found for {service_name}, skipping")
        os.chdir("..")
        return True

    # Install dependencies if requirements.txt exists
    if os.path.exists("requirements.txt"):
        print("📦 Installing dependencies...")
        success, _, error = run_command("pip install -r requirements.txt")
        if not success:
            print(f"❌ Failed to install dependencies: {error}")
            os.chdir("..")
            return False

    # Install pytest
    success, _, error = run_command("python -m pip install pytest")
    if not success:
        print(f"❌ Failed to install pytest: {error}")
        os.chdir("..")
        return False

    # Run tests
    success, output, error = run_command("python -m pytest --maxfail=1 --disable-warnings --tb=short tests")

    os.chdir("..")

    if success:
        print(f"✅ {service_name} tests passed")
        return True
    else:
        print(f"❌ {service_name} tests failed")
        if output:
            print(f"Output: {output}")
        if error:
            print(f"Error: {error}")
        return False

def main():
    """Main test runner function"""
    print("🧪 Running tests for all microservices...")

    # Define services to test
    services = [
        ("UserMS", "UserMS"),
        ("CustomerMS", "CustomerMS"),
        ("InventoryMS", "InventoryMS"),
        ("DeliveryMS", "DeliveryMS"),
        ("OrderMS", "OrderMS"),
        ("NotificationMS", "NotificationMS"),
    ]

    failed_services = []

    # Change to project root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    for service_name, service_dir in services:
        if not run_service_tests(service_name, service_dir):
            failed_services.append(service_name)

    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)

    if not failed_services:
        print("🎉 All tests passed!")
        return 0
    else:
        print(f"❌ Failed services: {', '.join(failed_services)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())