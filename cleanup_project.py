#!/usr/bin/env python3
"""
Project Cleanup Script - แก้แล้ว
"""

import os
import shutil
import glob
from pathlib import Path


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

    log_patterns = ["logs/**/*.log", "*.log"]

    for pattern in log_patterns:
        for log_file in glob.glob(pattern, recursive=True):
            try:
                # แก้: ไม่ลบ log ที่กำลังใช้งาน
                if not _is_file_in_use(log_file):
                    os.remove(log_file)
                    print(f"   ✅ Removed log: {log_file}")
                else:
                    print(f"   ⏭️ Skipped (in use): {log_file}")
            except Exception as e:
                print(f"   ❌ Failed to remove {log_file}: {e}")


def cleanup_temp_files():
    """ล้างไฟล์ temporary"""
    print("🧹 Cleaning temporary files...")

    temp_patterns = ["**/*.tmp", "**/*.temp", "**/*~", "**/*.bak"]

    for pattern in temp_patterns:
        for temp_file in glob.glob(pattern, recursive=True):
            try:
                if os.path.isfile(temp_file):
                    os.remove(temp_file)
                    print(f"   ✅ Removed temp: {temp_file}")
            except Exception as e:
                print(f"   ❌ Failed to remove {temp_file}: {e}")


def _is_file_in_use(file_path):
    """ตรวจสอบว่าไฟล์กำลังถูกใช้งานหรือไม่"""
    try:
        # พยายามเปิดไฟล์ในโหมด exclusive
        with open(file_path, "r+b"):
            return False
    except (OSError, IOError):
        return True


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

    required_dirs = [
        "logs",
        "logs/neural",
        "logs/quantum",
        "data",
        "assets",
        "ui/widgets",
        "utils",
    ]

    for dir_path in required_dirs:
        try:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            print(f"   ✅ Directory ready: {dir_path}")
        except Exception as e:
            print(f"   ❌ Failed to create {dir_path}: {e}")


def check_dependencies():
    """ตรวจสอบ dependencies"""
    print("📦 Checking dependencies...")

    try:
        # ใช้ importlib.metadata แทน pkg_resources (Python 3.8+)
        try:
            from importlib.metadata import distributions

            installed_packages = {
                dist.metadata["name"].lower().replace("-", "_")
                for dist in distributions()
            }
        except ImportError:
            # Fallback สำหรับ Python เก่า
            try:
                import pkg_resources

                installed_packages = {
                    pkg.key.replace("-", "_") for pkg in pkg_resources.working_set
                }
            except ImportError:
                print(
                    "   ⚠️ Cannot check dependencies - missing importlib.metadata and pkg_resources"
                )
                return

        if os.path.exists("requirements.txt"):
            with open("requirements.txt", "r") as f:
                requirements = f.read().splitlines()

            missing_packages = []
            found_packages = []

            for req in requirements:
                if req and not req.startswith("#"):
                    # แยกชื่อ package จาก version specifier
                    pkg_name = (
                        req.split(">=")[0]
                        .split("==")[0]
                        .split("<")[0]
                        .split(">")[0]
                        .strip()
                        .lower()
                        .replace("-", "_")
                    )

                    if pkg_name in installed_packages:
                        found_packages.append(pkg_name)
                        print(f"   ✅ {pkg_name}")
                    else:
                        missing_packages.append(pkg_name)
                        print(f"   ❌ Missing: {pkg_name}")

            print(
                f"\n   📊 Summary: {len(found_packages)} found, {len(missing_packages)} missing"
            )

            if missing_packages:
                print(
                    f"   💡 To install missing packages: pip install {' '.join(missing_packages)}"
                )
        else:
            print("   ⚠️ requirements.txt not found")

    except Exception as e:
        print(f"   ⚠️ Could not check dependencies: {e}")


def create_init_files():
    """สร้างไฟล์ __init__.py ที่ขาดหายไป"""
    print("📄 Creating missing __init__.py files...")

    directories = [
        "ui",
        "ui/components",
        "ui/widgets",
        "ui/styles",
        "controller",
        "connectors",
        "utils",
    ]

    for directory in directories:
        if os.path.exists(directory):
            init_file = os.path.join(directory, "__init__.py")
            if not os.path.exists(init_file):
                try:
                    with open(init_file, "w") as f:
                        f.write(f"# {directory}/__init__.py\n")
                    print(f"   ✅ Created: {init_file}")
                except Exception as e:
                    print(f"   ❌ Failed to create {init_file}: {e}")


def main():
    """Main cleanup function"""
    print("🚀 Starting project cleanup...")
    print("=" * 50)

    # Basic cleanup
    cleanup_pycache()
    print()

    cleanup_pyc_files()
    print()

    cleanup_logs()
    print()

    cleanup_temp_files()
    print()

    # Check and create required files/directories
    check_config_files()
    print()

    create_missing_directories()
    print()

    create_init_files()
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
