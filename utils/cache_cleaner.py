"""
Auto Cache Cleaner - แก้ Signal signature mismatch
"""

import os
import shutil
import time
import logging
from pathlib import Path
from typing import List, Dict
from PyQt6.QtCore import QThread, pyqtSignal, QTimer

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
                for file_path in self.project_root.glob(pattern):
                    if self._should_skip_path(file_path):
                        continue
                    try:
                        if file_path.is_file():
                            total_size += file_path.stat().st_size
                        elif file_path.is_dir():
                            total_size += self._get_dir_size(file_path)
                    except (OSError, PermissionError):
                        continue

            sizes[cache_type] = total_size / (1024 * 1024)

        return sizes

    def clean_cache(self, cache_types: List[str] = None) -> CacheCleanupResult:
        start_time = time.time()
        result = CacheCleanupResult()

        if not cache_types:
            cache_types = list(self.cache_patterns.keys())

        logger.info(f"🧹 Starting cache cleanup for: {', '.join(cache_types)}")

        for cache_type in cache_types:
            if cache_type not in self.cache_patterns:
                continue

            patterns = self.cache_patterns[cache_type]
            for pattern in patterns:
                self._clean_pattern(pattern, result)

        result.duration = time.time() - start_time

        logger.info(
            f"✅ Cache cleanup completed: "
            f"{result.files_removed} files, {result.dirs_removed} dirs removed, "
            f"{result.space_freed_mb:.2f}MB freed in {result.duration:.2f}s"
        )

        return result

    def _clean_pattern(self, pattern: str, result: CacheCleanupResult):
        for path in self.project_root.glob(pattern):
            if self._should_skip_path(path):
                continue

            try:
                if path.is_file():
                    size = path.stat().st_size
                    path.unlink()
                    result.files_removed += 1
                    result.space_freed_mb += size / (1024 * 1024)

                elif path.is_dir() and path.name == "__pycache__":
                    size = self._get_dir_size(path)
                    shutil.rmtree(path)
                    result.dirs_removed += 1
                    result.space_freed_mb += size / (1024 * 1024)

            except (OSError, PermissionError) as e:
                error_msg = f"Cannot remove {path}: {e}"
                result.errors.append(error_msg)
                logger.warning(error_msg)

    def _should_skip_path(self, path: Path) -> bool:
        for part in path.parts:
            if part in self.exclude_paths:
                return True

        if any(part.startswith(".") and part != "__pycache__" for part in path.parts):
            return True

        return False

    def _get_dir_size(self, path: Path) -> int:
        total_size = 0
        try:
            for item in path.rglob("*"):
                if item.is_file():
                    total_size += item.stat().st_size
        except (OSError, PermissionError):
            pass
        return total_size


class AutoCacheManager(QThread):
    """แก้แล้ว: เปลี่ยน signal signature ให้ตรงกัน"""

    cleanup_completed = pyqtSignal(object)  # CacheCleanupResult
    # แก้: เปลี่ยนจาก status_update(str) เป็น log_message(str, str)
    log_message = pyqtSignal(str, str)  # message, level

    def __init__(self, project_root: str = None):
        super().__init__()
        self.cleaner = SmartCacheCleaner(project_root)
        self.auto_cleanup_enabled = True
        self.cleanup_interval_hours = 6
        self.max_cache_size_mb = 100
        self.is_running = False

        self.timer = QTimer()
        self.timer.timeout.connect(self._periodic_cleanup)

    def start_auto_cleanup(self):
        if not self.auto_cleanup_enabled:
            return

        self.is_running = True
        interval_ms = self.cleanup_interval_hours * 60 * 60 * 1000
        self.timer.start(interval_ms)

        # แก้: ใช้ log_message แทน status_update
        self.log_message.emit("🤖 Auto cache cleanup enabled", "info")
        logger.info(
            f"Auto cache cleanup started (interval: {self.cleanup_interval_hours}h)"
        )

    def stop_auto_cleanup(self):
        self.is_running = False
        self.timer.stop()
        self.log_message.emit("⏸️ Auto cache cleanup disabled", "info")
        logger.info("Auto cache cleanup stopped")

    def _periodic_cleanup(self):
        if not self.is_running:
            return

        cache_sizes = self.cleaner.get_cache_size()
        total_size = sum(cache_sizes.values())

        if total_size > self.max_cache_size_mb:
            self.log_message.emit(
                f"🧹 Auto cleanup triggered (cache: {total_size:.1f}MB)", "info"
            )
            self.force_cleanup()
        else:
            self.log_message.emit(f"✅ Cache size OK ({total_size:.1f}MB)", "info")

    def force_cleanup(self):
        if not self.isRunning():
            self.start()
        else:
            logger.warning("Cleanup already in progress")

    def run(self):
        try:
            self.log_message.emit("🧹 Running cache cleanup...", "info")
            result = self.cleaner.clean_cache()
            self.cleanup_completed.emit(result)

            if result.errors:
                self.log_message.emit(
                    f"⚠️ Cleanup completed with {len(result.errors)} errors", "warning"
                )
            else:
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


class CacheMonitorWidget:
    def __init__(self, auto_manager: AutoCacheManager):
        self.auto_manager = auto_manager
        self.setup_connections()

    def setup_connections(self):
        self.auto_manager.cleanup_completed.connect(self._on_cleanup_completed)
        self.auto_manager.log_message.connect(self._on_log_message)

    def _on_cleanup_completed(self, result: CacheCleanupResult):
        message = (
            f"Cache cleanup completed:\n"
            f"• Files removed: {result.files_removed}\n"
            f"• Directories removed: {result.dirs_removed}\n"
            f"• Space freed: {result.space_freed_mb:.2f}MB\n"
            f"• Duration: {result.duration:.2f}s"
        )

        if result.errors:
            message += f"\n• Errors: {len(result.errors)}"

        logger.info(message)

    def _on_log_message(self, message: str, level: str):
        logger.info(f"[{level.upper()}] {message}")


# Quick access functions
def cleanup_python_cache(project_root: str = None) -> CacheCleanupResult:
    cleaner = SmartCacheCleaner(project_root)
    return cleaner.clean_cache(["python_cache"])


def cleanup_all_cache(project_root: str = None) -> CacheCleanupResult:
    cleaner = SmartCacheCleaner(project_root)
    return cleaner.clean_cache()


def get_cache_info(project_root: str = None) -> Dict:
    cleaner = SmartCacheCleaner(project_root)
    sizes = cleaner.get_cache_size()

    return {
        "total_size_mb": sum(sizes.values()),
        "breakdown": sizes,
        "project_root": str(cleaner.project_root),
    }
