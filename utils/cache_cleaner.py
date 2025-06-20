# utils/cache_cleaner.py - Fixed Cache Cleaner
import os
import shutil
import time
import logging
import glob
from pathlib import Path
from typing import List, Dict
from PyQt6.QtCore import pyqtSignal, QTimer, QObject, pyqtSlot

from utils.config_manager import ConfigManager

logger = logging.getLogger(__name__)


class CacheCleanupResult:
    """Results from cache cleanup operation"""

    def __init__(self):
        self.files_removed = 0
        self.dirs_removed = 0
        self.space_freed_mb = 0.0
        self.errors = []
        self.duration = 0.0
        self.cache_types_cleaned = []


class SmartCacheCleaner:
    """Intelligent cache cleaner with configurable patterns"""

    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or os.getcwd())
        self.exclude_paths = {
            ".git",
            ".venv",
            "venv",
            "env",
            "node_modules",
            ".idea",
            "__pycache__",
        }
        self.cache_patterns = {
            "python_cache": ["**/__pycache__", "**/*.pyc", "**/*.pyo"],
            "log_files": ["logs/**/*.log", "*.log"],
            "temp_files": ["**/*.tmp", "**/*.temp", "**/temp/**", "**/.tmp*"],
            "backup_files": ["**/*.bak", "**/*~", "**/*.backup"],
            "os_cache": ["**/Thumbs.db", "**/.DS_Store", "**/desktop.ini"],
            "qt_cache": ["**/.qmlc", "**/*.qmlc"],
        }

    def get_cache_size(self) -> Dict[str, float]:
        """Calculate cache sizes by type in MB"""
        sizes = {}

        for cache_type, patterns in self.cache_patterns.items():
            total_size = 0
            try:
                for pattern in patterns:
                    pattern_path = str(self.project_root / pattern)
                    for file_path in glob.glob(pattern_path, recursive=True):
                        path = Path(file_path)

                        # Skip if in excluded directory
                        if any(
                            excluded in path.parts for excluded in self.exclude_paths
                        ):
                            continue

                        try:
                            if path.is_file() and not path.is_symlink():
                                total_size += path.stat().st_size
                            elif path.is_dir() and not path.is_symlink():
                                for dirpath, dirnames, filenames in os.walk(path):
                                    for filename in filenames:
                                        file_path = Path(dirpath) / filename
                                        if not file_path.is_symlink():
                                            total_size += file_path.stat().st_size
                        except (OSError, PermissionError):
                            continue  # Skip files we can't access

            except Exception as e:
                logger.debug(f"Error calculating size for {cache_type}: {e}")

            sizes[cache_type] = total_size / (1024 * 1024)  # Convert to MB

        return sizes

    def clean_cache(self, cache_types: List[str] = None) -> CacheCleanupResult:
        """Clean specified cache types or all if none specified"""
        result = CacheCleanupResult()
        start_time = time.time()

        types_to_clean = cache_types or list(self.cache_patterns.keys())
        result.cache_types_cleaned = types_to_clean

        logger.info(f"Starting cache cleanup for types: {', '.join(types_to_clean)}")

        for cache_type in types_to_clean:
            if cache_type not in self.cache_patterns:
                error_msg = f"Unknown cache type: {cache_type}"
                result.errors.append(error_msg)
                logger.warning(error_msg)
                continue

            patterns = self.cache_patterns[cache_type]
            logger.debug(f"Cleaning {cache_type} with patterns: {patterns}")

            for pattern in patterns:
                pattern_path = str(self.project_root / pattern)

                try:
                    for file_path in glob.glob(pattern_path, recursive=True):
                        path = Path(file_path)

                        # Skip if doesn't exist or is symlink
                        if not path.exists() or path.is_symlink():
                            continue

                        # Skip if in excluded directory
                        if any(
                            excluded in path.parts for excluded in self.exclude_paths
                        ):
                            logger.debug(f"Skipping excluded path: {path}")
                            continue

                        try:
                            if path.is_file():
                                file_size = path.stat().st_size
                                path.unlink()
                                result.files_removed += 1
                                result.space_freed_mb += file_size / (1024 * 1024)
                                logger.debug(f"Removed file: {path}")

                            elif path.is_dir():
                                # Calculate directory size before removal
                                dir_size = 0
                                try:
                                    for dirpath, dirnames, filenames in os.walk(path):
                                        for filename in filenames:
                                            file_path = Path(dirpath) / filename
                                            if not file_path.is_symlink():
                                                dir_size += file_path.stat().st_size
                                except (OSError, PermissionError):
                                    pass

                                shutil.rmtree(path)
                                result.dirs_removed += 1
                                result.space_freed_mb += dir_size / (1024 * 1024)
                                logger.debug(f"Removed directory: {path}")

                        except PermissionError as e:
                            error_msg = f"Permission denied: {path}"
                            result.errors.append(error_msg)
                            logger.warning(error_msg)
                        except OSError as e:
                            error_msg = f"OS error removing {path}: {e}"
                            result.errors.append(error_msg)
                            logger.warning(error_msg)
                        except Exception as e:
                            error_msg = f"Unexpected error removing {path}: {e}"
                            result.errors.append(error_msg)
                            logger.error(error_msg)

                except Exception as e:
                    error_msg = f"Error processing pattern {pattern}: {e}"
                    result.errors.append(error_msg)
                    logger.error(error_msg)

        result.duration = time.time() - start_time

        logger.info(
            f"Cache cleanup completed: {result.files_removed} files, "
            f"{result.dirs_removed} directories removed. "
            f"Freed {result.space_freed_mb:.2f} MB in {result.duration:.2f} seconds. "
            f"Errors: {len(result.errors)}"
        )

        return result


class AutoCacheManager(QObject):
    """
    Manages automatic cache cleanup with configurable schedules.
    """

    log_message = pyqtSignal(str, str)  # message, level
    cleanup_completed = pyqtSignal(object)  # CacheCleanupResult

    def __init__(self, config_manager: ConfigManager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.config = config_manager.get_config()

        # Initialize cleaner with project root
        project_root = getattr(config_manager, "project_root", None) or os.getcwd()
        self.cleaner = SmartCacheCleaner(project_root)

        # Setup auto-cleanup timer
        self.cleanup_timer = QTimer(self)
        self.cleanup_timer.timeout.connect(self._perform_auto_cleanup)
        self.last_cleanup_time = None

        self._load_auto_cleanup_settings()
        logger.info("AutoCacheManager initialized")

    def _load_auto_cleanup_settings(self):
        """Load auto-cleanup settings from configuration"""
        try:
            self.auto_cleanup_enabled = self.config.auto_cache_cleanup_enabled
            self.cleanup_interval_hours = self.config.cache_cleanup_interval_hours

            if self.auto_cleanup_enabled and self.cleanup_interval_hours > 0:
                interval_ms = (
                    self.cleanup_interval_hours * 60 * 60 * 1000
                )  # Convert to milliseconds
                self.cleanup_timer.start(interval_ms)
                self.log_message.emit(
                    f"Auto cache cleanup enabled. Interval: {self.cleanup_interval_hours} hours",
                    "info",
                )
                logger.info(
                    f"Auto-cleanup timer started with {interval_ms} ms interval"
                )
            else:
                self.cleanup_timer.stop()
                self.log_message.emit("Auto cache cleanup disabled", "info")
                logger.info("Auto-cleanup timer stopped")

        except Exception as e:
            logger.error(f"Error loading auto-cleanup settings: {e}")
            self.cleanup_timer.stop()

    @pyqtSlot(bool)
    def toggle_auto_cleanup(self, enable: bool):
        """Toggle automatic cache cleanup on/off"""
        try:
            self.config_manager.update_setting("auto_cache_cleanup_enabled", enable)
            self.auto_cleanup_enabled = enable

            if enable and self.cleanup_interval_hours > 0:
                interval_ms = self.cleanup_interval_hours * 60 * 60 * 1000
                self.cleanup_timer.start(interval_ms)
                self.log_message.emit(
                    f"Auto cache cleanup enabled. Interval: {self.cleanup_interval_hours} hours",
                    "info",
                )
                logger.info(
                    f"Auto-cleanup toggled ON. Timer started with {interval_ms} ms interval"
                )
            else:
                self.cleanup_timer.stop()
                self.log_message.emit("Auto cache cleanup disabled", "info")
                logger.info("Auto-cleanup toggled OFF")

        except Exception as e:
            logger.error(f"Error toggling auto-cleanup: {e}")
            self.log_message.emit(f"Error toggling auto-cleanup: {e}", "error")

    @pyqtSlot()
    def _perform_auto_cleanup(self):
        """Perform automatic cache cleanup when timer triggers"""
        logger.info("Performing scheduled auto cache cleanup")
        self.log_message.emit("Performing scheduled auto cache cleanup...", "info")
        self.run_manual_cleanup()

    @pyqtSlot()
    def run_manual_cleanup(self):
        """Run manual cache cleanup"""
        logger.info("Running manual cache cleanup")
        self.log_message.emit("Starting manual cache cleanup...", "info")

        try:
            # Run cleanup in background to avoid blocking UI
            result = self.cleaner.clean_cache()
            self.last_cleanup_time = time.time()

            # Emit completion signal
            self.cleanup_completed.emit(result)

            # Log results
            if result.errors:
                self.log_message.emit(
                    f"⚠️ Cleanup completed with {len(result.errors)} errors. "
                    f"Freed {result.space_freed_mb:.1f}MB",
                    "warning",
                )
            else:
                self.log_message.emit(
                    f"✅ Cleanup completed successfully. Freed {result.space_freed_mb:.1f}MB",
                    "success",
                )

        except Exception as e:
            error_msg = f"Cache cleanup failed: {e}"
            self.log_message.emit(f"❌ {error_msg}", "error")
            logger.error(error_msg, exc_info=True)

    def get_cache_statistics(self) -> Dict:
        """Get current cache statistics"""
        try:
            cache_sizes = self.cleaner.get_cache_size()

            stats = {
                "total_size_mb": sum(cache_sizes.values()),
                "cache_breakdown": cache_sizes,
                "auto_cleanup_enabled": self.auto_cleanup_enabled,
                "cleanup_interval_hours": self.cleanup_interval_hours,
                "last_cleanup": self.last_cleanup_time,
                "project_root": str(self.cleaner.project_root),
                "cache_types": list(self.cleaner.cache_patterns.keys()),
            }

            return stats

        except Exception as e:
            logger.error(f"Error getting cache statistics: {e}")
            return {
                "total_size_mb": 0,
                "cache_breakdown": {},
                "auto_cleanup_enabled": False,
                "cleanup_interval_hours": 24,
                "last_cleanup": None,
                "project_root": str(self.cleaner.project_root),
                "error": str(e),
            }

    def cleanup(self):
        """Perform cleanup for AutoCacheManager"""
        logger.info("AutoCacheManager cleanup initiated")

        try:
            # Stop timer
            if self.cleanup_timer and self.cleanup_timer.isActive():
                self.cleanup_timer.stop()
                self.cleanup_timer.deleteLater()
                self.cleanup_timer = None
                logger.debug("Auto-cleanup timer stopped and deleted")

            # Disconnect signals
            try:
                self.log_message.disconnect()
                self.cleanup_completed.disconnect()
                logger.info("AutoCacheManager signals disconnected")
            except (TypeError, RuntimeError):
                pass  # Signals already disconnected

        except Exception as e:
            logger.error(f"Error during AutoCacheManager cleanup: {e}")

        logger.info("AutoCacheManager cleanup completed")


# Convenience functions for direct usage
def cleanup_python_cache(project_root: str = None) -> CacheCleanupResult:
    """Quick cleanup of Python cache files"""
    cleaner = SmartCacheCleaner(project_root)
    return cleaner.clean_cache(["python_cache"])


def cleanup_all_cache(project_root: str = None) -> CacheCleanupResult:
    """Clean all cache types"""
    cleaner = SmartCacheCleaner(project_root)
    return cleaner.clean_cache()


def get_cache_info(project_root: str = None) -> Dict:
    """Get cache size information"""
    cleaner = SmartCacheCleaner(project_root)
    return cleaner.get_cache_size()
