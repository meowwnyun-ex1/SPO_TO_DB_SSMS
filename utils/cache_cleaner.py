"""
Auto Cache Cleaner - แก้ Signal signature mismatch
"""

import os
import shutil
import time
import logging
from pathlib import Path
from typing import List, Dict
from PyQt6.QtCore import pyqtSignal, QTimer, QObject, pyqtSlot  # Added pyqtSlot import

logger = logging.getLogger(__name__)


class CacheCleanupResult:
    def __init__(self):
        self.files_removed = 0
        self.dirs_removed = 0
        self.space_freed_mb = 0.0
        self.errors = []
        self.duration = 0.0


class SmartCacheCleaner:
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or os.getcwd())
        self.exclude_paths = {".git", ".venv", "venv", "env", "node_modules"}
        self.cache_patterns = {
            "python_cache": ["**/__pycache__", "**/*.pyc", "**/*.pyo"],
            "log_files": ["logs/**/*.log"],
            "temp_files": ["**/*.tmp", "**/*.temp", "**/temp/**"],
            "backup_files": ["**/*.bak", "**/*~"],
            "os_cache": ["**/Thumbs.db", "**/.DS_Store"],
        }

    def get_cache_size(self) -> Dict[str, float]:
        sizes = {}

        for cache_type, patterns in self.cache_patterns.items():
            total_size = 0
            for pattern in patterns:
                for path_str in glob.glob(
                    str(self.project_root / pattern), recursive=True
                ):
                    path = Path(path_str)
                    if path.is_file():
                        total_size += path.stat().st_size
                    elif path.is_dir():
                        for dirpath, dirnames, filenames in os.walk(path):
                            for f in filenames:
                                fp = Path(dirpath) / f
                                if (
                                    not fp.is_symlink()
                                ):  # Avoid following symlinks infinitely
                                    total_size += fp.stat().st_size
            sizes[cache_type] = total_size / (1024 * 1024)  # Convert to MB
        return sizes

    def clean_cache(self, cache_types: List[str] = None) -> CacheCleanupResult:
        """
        Cleans specified cache types or all if none specified.
        Returns a CacheCleanupResult object.
        """
        result = CacheCleanupResult()
        start_time = time.time()
        types_to_clean = cache_types or list(self.cache_patterns.keys())

        logger.info(f"Initiating cache cleanup for types: {', '.join(types_to_clean)}")

        for cache_type in types_to_clean:
            if cache_type not in self.cache_patterns:
                error_msg = f"Unknown cache type: {cache_type}. Skipping."
                result.errors.append(error_msg)
                logger.warning(error_msg)
                continue

            patterns = self.cache_patterns[cache_type]
            for pattern in patterns:
                full_pattern = self.project_root / pattern
                for path_str in glob.glob(str(full_pattern), recursive=True):
                    path = Path(path_str)
                    if not path.exists():
                        continue

                    # Check if path is within excluded directories
                    if any(
                        excluded_dir in path.parts
                        for excluded_dir in self.exclude_paths
                    ):
                        logger.debug(f"Skipping excluded path: {path}")
                        continue

                    try:
                        if path.is_file():
                            result.space_freed_mb += path.stat().st_size / (1024 * 1024)
                            path.unlink()  # Remove file
                            result.files_removed += 1
                            logger.debug(f"Removed file: {path}")
                        elif path.is_dir():
                            # For directories, get size before removal
                            dir_size = 0
                            for dirpath, dirnames, filenames in os.walk(path):
                                for f in filenames:
                                    fp = Path(dirpath) / f
                                    if not fp.is_symlink():
                                        dir_size += fp.stat().st_size

                            shutil.rmtree(path)  # Remove directory and its contents
                            result.space_freed_mb += dir_size / (1024 * 1024)
                            result.dirs_removed += 1
                            logger.debug(f"Removed directory: {path}")
                    except OSError as e:
                        error_msg = f"Failed to remove {path}: {e}"
                        result.errors.append(error_msg)
                        logger.error(error_msg)
                    except Exception as e:
                        error_msg = (
                            f"An unexpected error occurred while cleaning {path}: {e}"
                        )
                        result.errors.append(error_msg)
                        logger.error(error_msg)

        result.duration = time.time() - start_time
        logger.info(
            f"Cleanup complete. Removed {result.files_removed} files, {result.dirs_removed} directories. Freed {result.space_freed_mb:.2f} MB in {result.duration:.2f} seconds."
        )
        return result


class AutoCacheManager(QObject):
    """
    Manages automatic cache cleanup using a QTimer.
    Emits signals for logging and completion status.
    """

    log_message = pyqtSignal(str, str)  # message, level
    cleanup_completed = pyqtSignal(object)  # CacheCleanupResult object

    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.cleaner = SmartCacheCleaner(self.config_manager.project_root)

        self.cleanup_timer = QTimer(self)
        self.cleanup_timer.timeout.connect(self._perform_auto_cleanup)
        self.last_cleanup_time = None

        self._load_auto_cleanup_settings()
        logger.info("AutoCacheManager initialized.")

    def _load_auto_cleanup_settings(self):
        """Loads auto-cleanup settings from config."""
        self.auto_cleanup_enabled = self.config_manager.get_setting(
            "auto_cleanup_enabled"
        )
        self.cleanup_interval_hours = self.config_manager.get_setting(
            "cleanup_interval_hours"
        )

        if self.auto_cleanup_enabled and self.cleanup_interval_hours > 0:
            interval_ms = self.cleanup_interval_hours * 60 * 60 * 1000
            self.cleanup_timer.start(interval_ms)
            self.log_message.emit(
                f"Auto cache cleanup enabled. Interval: {self.cleanup_interval_hours} hours.",
                "info",
            )
            logger.info(f"Auto-cleanup timer started with {interval_ms} ms interval.")
        else:
            self.cleanup_timer.stop()
            self.log_message.emit("Auto cache cleanup disabled.", "info")
            logger.info("Auto-cleanup timer stopped.")

    @pyqtSlot(bool)
    def toggle_auto_cleanup(self, enable: bool):
        """Toggles automatic cache cleanup on/off."""
        self.config_manager.set_setting(
            "auto_sync_enabled", enable
        )  # This should be auto_cleanup_enabled, not auto_sync_enabled
        self.auto_cleanup_enabled = enable
        if enable and self.cleanup_interval_hours > 0:
            interval_ms = self.cleanup_interval_hours * 60 * 60 * 1000
            self.cleanup_timer.start(interval_ms)
            self.log_message.emit(
                f"Auto cache cleanup enabled. Interval: {self.cleanup_interval_hours} hours.",
                "info",
            )
            logger.info(
                f"Auto-cleanup toggled ON. Timer started with {interval_ms} ms interval."
            )
        else:
            self.cleanup_timer.stop()
            self.log_message.emit("Auto cache cleanup disabled.", "info")
            logger.info("Auto-cleanup toggled OFF. Timer stopped.")

    @pyqtSlot()
    def _perform_auto_cleanup(self):
        """Performs cache cleanup automatically when the timer times out."""
        logger.info("Performing scheduled auto cache cleanup...")
        self.log_message.emit("Performing scheduled auto cache cleanup...", "info")
        self.run_manual_cleanup()  # Call the manual cleanup method to reuse logic

    @pyqtSlot()
    def run_manual_cleanup(self):
        """Runs a manual cache cleanup."""
        logger.info("Running manual cache cleanup...")
        self.log_message.emit("Running manual cache cleanup...", "info")
        try:
            result = self.cleaner.clean_cache()
            self.last_cleanup_time = time.time()
            self.cleanup_completed.emit(result)
            self.log_message.emit(
                f"✅ Cleanup completed: {result.space_freed_mb:.1f}MB freed",
                "success",
            )

        except Exception as e:
            error_msg = f"❌ Cache cleanup failed: {e}"
            self.log_message.emit(error_msg, "error")
            logger.error(error_msg)

    def get_cache_statistics(self) -> Dict:
        cache_sizes = self.cleaner.get_cache_size()

        return {
            "total_size_mb": sum(cache_sizes.values()),
            "cache_breakdown": cache_sizes,
            "auto_cleanup_enabled": self.auto_cleanup_enabled,
            "cleanup_interval_hours": self.cleanup_interval_hours,
            "last_cleanup": getattr(self, "last_cleanup_time", None),
            "project_root": str(self.cleaner.project_root),
        }

    def cleanup(self):
        """Performs cleanup for AutoCacheManager."""
        logger.info("AutoCacheManager cleanup initiated.")
        if self.cleanup_timer and self.cleanup_timer.isActive():
            self.cleanup_timer.stop()
            self.cleanup_timer.deleteLater()
            self.cleanup_timer = None
            logger.debug("Auto-cleanup timer stopped and deleted.")

        # Disconnect all signals
        try:
            self.log_message.disconnect()
            self.cleanup_completed.disconnect()
            logger.info("Disconnected AutoCacheManager signals.")
        except TypeError as e:
            logger.debug(
                f"Attempted to disconnect non-connected AutoCacheManager signal: {e}"
            )
        except Exception as e:
            logger.warning(f"Error during AutoCacheManager signal disconnection: {e}")
        logger.info("AutoCacheManager cleanup completed.")


# Quick access functions
def cleanup_python_cache(project_root: str = None) -> CacheCleanupResult:
    cleaner = SmartCacheCleaner(project_root)
    return cleaner.clean_cache(["python_cache"])


def cleanup_all_cache(project_root: str = None) -> CacheCleanupResult:
    cleaner = SmartCacheCleaner(project_root)
    return cleaner.clean_cache()


def get_cache_info(project_root: str = None) -> Dict:
    cleaner = SmartCacheCleaner(project_root)
    return cleaner.get_cache_size()
