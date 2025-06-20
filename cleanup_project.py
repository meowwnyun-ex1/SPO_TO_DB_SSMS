#!/usr/bin/env python3
"""
Project Cleanup Script - แก้แล้ว
"""

import os
import shutil
import glob
from pathlib import Path
import logging
import importlib.util  # Added for robust dependency checking

# Configure basic logging for the script itself
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def cleanup_pycache():
    """ล้าง __pycache__ ทั้งหมด"""
    logger.info("🧹 Cleaning __pycache__ directories...")

    for root, dirs, files in os.walk("."):
        if "__pycache__" in dirs:
            cache_path = os.path.join(root, "__pycache__")
            try:
                shutil.rmtree(cache_path)
                logger.info(f"   ✅ Removed: {cache_path}")
            except OSError as e:
                logger.error(f"   ❌ Failed to remove {cache_path}: {e}")
            except Exception as e:
                logger.error(f"   ❌ Unexpected error removing {cache_path}: {e}")


def cleanup_pyc_files():
    """ล้างไฟล์ .pyc ทั้งหมด"""
    logger.info("🧹 Cleaning .pyc files...")

    pyc_files = glob.glob("**/*.pyc", recursive=True)
    for pyc_file in pyc_files:
        try:
            os.remove(pyc_file)
            logger.info(f"   ✅ Removed: {pyc_file}")
        except OSError as e:
            logger.error(f"   ❌ Failed to remove {pyc_file}: {e}")
        except Exception as e:
            logger.error(f"   ❌ Unexpected error removing {pyc_file}: {e}")


def cleanup_logs():
    """ล้างไฟล์ log เก่า"""
    logger.info("🧹 Cleaning old log files...")

    log_patterns = ["logs/**/*.log", "*.log"]
    cleaned_count = 0
    for pattern in log_patterns:
        for log_file in glob.glob(pattern, recursive=True):
            if Path(log_file).parent.name == "logs" or Path(log_file).name.endswith(
                ".log"
            ):  # Ensure it's explicitly a log file
                try:
                    os.remove(log_file)
                    logger.info(f"   ✅ Removed: {log_file}")
                    cleaned_count += 1
                except OSError as e:
                    logger.error(f"   ❌ Failed to remove {log_file}: {e}")
                except Exception as e:
                    logger.error(f"   ❌ Unexpected error removing {log_file}: {e}")
    if cleaned_count == 0:
        logger.info("   No log files found to clean.")


def cleanup_temp_files():
    """ล้างไฟล์ temp เก่า"""
    logger.info("🧹 Cleaning temporary files...")

    temp_patterns = [
        "**/*.tmp",
        "**/*.temp",
        "**/temp/**",
        "~*.xlsx",
        "~*.docx",
        "*.bak",
        "*~",
    ]
    cleaned_count = 0
    for pattern in temp_patterns:
        for temp_file in glob.glob(pattern, recursive=True):
            try:
                if Path(
                    temp_file
                ).is_file():  # Ensure it's a file, not a directory matching "temp/**"
                    os.remove(temp_file)
                    logger.info(f"   ✅ Removed: {temp_file}")
                    cleaned_count += 1
            except OSError as e:
                logger.error(f"   ❌ Failed to remove {temp_file}: {e}")
            except Exception as e:
                logger.error(f"   ❌ Unexpected error removing {temp_file}: {e}")
    if cleaned_count == 0:
        logger.info("   No temporary files found to clean.")


def check_config_files():
    """ตรวจสอบว่า config files ที่จำเป็นมีอยู่หรือไม่"""
    logger.info("⚙️ Checking essential configuration files...")
    required_configs = ["config.json", ".env"]
    found_all = True
    for config_file in required_configs:
        if not os.path.exists(config_file):
            logger.warning(f"   ⚠️ Missing: {config_file}. Consider creating one.")
            found_all = False
        else:
            logger.info(f"   ✅ Found: {config_file}")
    if found_all:
        logger.info("   All essential configuration files are present.")


def create_missing_directories():
    """สร้าง directories ที่จำเป็นถ้าไม่มี"""
    logger.info("📁 Creating missing essential directories...")
    directories = [
        "logs",
        "resources/images",
        "resources/audio",
        "config",
        "data",
        "reports",
    ]  # Added reports, data
    for directory in directories:
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
                logger.info(f"   ✅ Created: {directory}")
            except OSError as e:
                logger.error(f"   ❌ Failed to create {directory}: {e}")
            except Exception as e:
                logger.error(f"   ❌ Unexpected error creating {directory}: {e}")
        else:
            logger.info(f"   ☑️ Exists: {directory}")


def create_init_files():
    """สร้าง __init__.py files ใน package directories"""
    logger.info("📦 Creating missing __init__.py files...")
    # These paths are relative to the project root
    directories = [
        "controller",
        "connectors",
        "ui",
        "ui/components",
        "ui/styles",
        "ui/widgets",
        "utils",
    ]

    for directory in directories:
        # Ensure the directory actually exists before creating __init__.py
        full_dir_path = Path(os.getcwd()) / directory
        if full_dir_path.exists() and full_dir_path.is_dir():
            init_file = full_dir_path / "__init__.py"
            if not init_file.exists():
                try:
                    with open(init_file, "w") as f:
                        f.write(f"# {directory}/__init__.py\n")
                    logger.info(f"   ✅ Created: {init_file}")
                except OSError as e:
                    logger.error(f"   ❌ Failed to create {init_file}: {e}")
                except Exception as e:
                    logger.error(f"   ❌ Unexpected error creating {init_file}: {e}")
            else:
                logger.info(f"   ☑️ Exists: {init_file}")
        else:
            logger.debug(
                f"   Directory does not exist, skipping __init__.py: {directory}"
            )


def check_dependencies():
    """ตรวจสอบว่า dependencies ที่จำเป็นติดตั้งอยู่หรือไม่"""
    logger.info("➕ Checking Python dependencies...")
    # List of key packages to check (use the actual module name for importlib check)
    required_packages = {
        "PyQt6": "PyQt6",
        "pandas": "pandas",
        "requests": "requests",
        "sqlalchemy": "sqlalchemy",
        "python-dotenv": "dotenv",  # The actual module imported by python-dotenv is 'dotenv'
        "pyodbc": "pyodbc",
        "openpyxl": "openpyxl",
        "xlrd": "xlrd",
    }
    missing_packages = []

    for pkg_name, module_name in required_packages.items():
        if importlib.util.find_spec(module_name) is None:
            missing_packages.append(pkg_name)
            logger.warning(f"   ⚠️ Missing: {pkg_name} (module: {module_name})")
        else:
            logger.info(f"   ✅ Found: {pkg_name}")

    if missing_packages:
        logger.warning(
            f"   Some dependencies are missing. Please install them using pip:\n   pip install {' '.join(missing_packages)}"
        )
        return False
    else:
        logger.info("   All essential Python dependencies are installed.")
        return True


def main():
    """Main cleanup function"""
    logger.info("🚀 Starting project cleanup...")
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
    logger.info("✅ Project cleanup finished.")


if __name__ == "__main__":
    main()
