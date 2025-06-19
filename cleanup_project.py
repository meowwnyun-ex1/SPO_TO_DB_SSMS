#!/usr/bin/env python3
"""
Project Cleanup Script - สคริปต์ทำความสะอาดโปรเจค
รันสคริปต์นี้เพื่อทำความสะอาดโปรเจคก่อนใช้งาน
"""

import os
import shutil
import glob
from utils.cache_cleaner import cleanup_all_cache, get_cache_info
from utils.error_handling import init_error_handling


def cleanup_pycache():
    """ล้าง __pycache__ ทั้งหมด"""
    print("🧹 Cleaning __pycache__ directories...")

    for root, dirs, files in os.walk("."):
        if "__pycache__" in dirs:
            cache_path = os.path.join(root, "__pycache__")
            try:
                shutil.rmtree(cache_path)
                print(f"   ✅ Removed: {cache_path}")
            except Exception as e:
                print(f"   ❌ Failed to remove {cache_path}: {e}")


def cleanup_pyc_files():
    """ล้างไฟล์ .pyc ทั้งหมด"""
    print("🧹 Cleaning .pyc files...")

    pyc_files = glob.glob("**/*.pyc", recursive=True)
    for pyc_file in pyc_files:
        try:
            os.remove(pyc_file)
            print(f"   ✅ Removed: {pyc_file}")
        except Exception as e:
            print(f"   ❌ Failed to remove {pyc_file}: {e}")


def cleanup_logs():
    """ล้างไฟล์ log เก่า"""
    print("🧹 Cleaning old log files...")

    log_patterns = ["logs/**/*.log", "*.log", "logs/neural/*.log", "logs/quantum/*.log"]

    for pattern in log_patterns:
        for log_file in glob.glob(pattern, recursive=True):
            try:
                os.remove(log_file)
                print(f"   ✅ Removed log: {log_file}")
            except Exception as e:
                print(f"   ❌ Failed to remove {log_file}: {e}")


def cleanup_temp_files():
    """ล้างไฟล์ temporary"""
    print("🧹 Cleaning temporary files...")

    temp_patterns = ["**/*.tmp", "**/*.temp", "**/temp/**/*", "**/*~", "**/*.bak"]

    for pattern in temp_patterns:
        for temp_file in glob.glob(pattern, recursive=True):
            try:
                if os.path.isfile(temp_file):
                    os.remove(temp_file)
                    print(f"   ✅ Removed temp: {temp_file}")
            except Exception as e:
                print(f"   ❌ Failed to remove {temp_file}: {e}")


def check_config_files():
    """ตรวจสอบไฟล์ config"""
    print("⚙️ Checking configuration files...")

    config_files = ["config.json", ".env"]

    for config_file in config_files:
        if os.path.exists(config_file):
            print(f"   ✅ Found: {config_file}")
        else:
            print(f"   ⚠️ Missing: {config_file}")


def create_missing_directories():
    """สร้างโฟลเดอร์ที่ขาดหายไป"""
    print("📁 Creating missing directories...")

    required_dirs = ["logs", "logs/neural", "logs/quantum", "data", "assets"]

    for dir_path in required_dirs:
        try:
            os.makedirs(dir_path, exist_ok=True)
            print(f"   ✅ Directory ready: {dir_path}")
        except Exception as e:
            print(f"   ❌ Failed to create {dir_path}: {e}")


def check_dependencies():
    """ตรวจสอบ dependencies"""
    print("📦 Checking dependencies...")

    try:
        import pkg_resources

        with open("requirements.txt", "r") as f:
            requirements = f.read().splitlines()

        installed = [pkg.key for pkg in pkg_resources.working_set]

        for req in requirements:
            if req and not req.startswith("#"):
                pkg_name = req.split(">=")[0].split("==")[0].lower()
                if pkg_name in installed:
                    print(f"   ✅ {pkg_name}")
                else:
                    print(f"   ❌ Missing: {pkg_name}")

    except Exception as e:
        print(f"   ⚠️ Could not check dependencies: {e}")


def show_cache_stats():
    """แสดงสถิติแคช"""
    print("📊 Cache Statistics...")

    try:
        cache_info = get_cache_info()
        print(f"   Total cache size: {cache_info['total_size_mb']:.2f} MB")
        print(f"   Project root: {cache_info['project_root']}")

        for cache_type, size in cache_info["breakdown"].items():
            if size > 0:
                print(f"   - {cache_type}: {size:.2f} MB")

    except Exception as e:
        print(f"   ⚠️ Could not get cache stats: {e}")


def main():
    """Main cleanup function"""
    print("🚀 Starting project cleanup...")
    print("=" * 50)

    # Initialize error handling
    init_error_handling()

    # Show current cache stats
    show_cache_stats()
    print()

    # Cleanup operations
    cleanup_pycache()
    print()

    cleanup_pyc_files()
    print()

    cleanup_logs()
    print()

    cleanup_temp_files()
    print()

    # Use the new cache cleaner
    print("🧹 Running advanced cache cleanup...")
    try:
        result = cleanup_all_cache()
        print(f"   ✅ Advanced cleanup: {result.space_freed_mb:.2f}MB freed")
        if result.errors:
            print(f"   ⚠️ {len(result.errors)} errors occurred")
    except Exception as e:
        print(f"   ❌ Advanced cleanup failed: {e}")
    print()

    # Check and create required files/directories
    check_config_files()
    print()

    create_missing_directories()
    print()

    check_dependencies()
    print()

    print("=" * 50)
    print("✅ Project cleanup completed!")
    print()
    print("📋 Next steps:")
    print("   1. Run: python main.py")
    print("   2. Configure SharePoint settings")
    print("   3. Configure Database settings")
    print("   4. Test connections")
    print("   5. Run your first sync")


if __name__ == "__main__":
    main()
