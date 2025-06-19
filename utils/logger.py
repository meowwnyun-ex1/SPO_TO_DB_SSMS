import logging
import logging.handlers
from pathlib import Path
from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal


class NeuralLogFormatter(logging.Formatter):
    """Custom formatter สำหรับ neural logging system"""

    def __init__(self):
        super().__init__()
        self.neural_symbols = {
            "DEBUG": "◇",
            "INFO": "◉",
            "WARNING": "◈",
            "ERROR": "◆",
            "CRITICAL": "⬢",
        }

    def format(self, record):
        """Format log record with neural styling"""
        symbol = self.neural_symbols.get(record.levelname, "◯")
        timestamp = datetime.fromtimestamp(record.created).strftime("%H:%M:%S.%f")[:-3]

        # Neural log format
        neural_format = (
            f"[{timestamp}] {symbol} {record.name} " f"→ {record.getMessage()}"
        )

        # Add exception info if present
        if record.exc_info:
            neural_format += f"\n⚠️ Exception: {self.formatException(record.exc_info)}"

        return neural_format


class QuantumFileHandler(logging.handlers.RotatingFileHandler):
    """Enhanced file handler with quantum data organization"""

    def __init__(self, filename, **kwargs):
        super().__init__(filename, **kwargs)
        self.setFormatter(NeuralLogFormatter())

    def emit(self, record):
        """Emit log record with quantum timestamp"""
        # Add quantum metadata
        if not hasattr(record, "quantum_id"):
            record.quantum_id = f"Q{int(datetime.now().timestamp() * 1000)}"

        super().emit(record)


class HolographicConsoleHandler(logging.StreamHandler):
    """Console handler with holographic output styling"""

    def __init__(self):
        super().__init__()
        self.setFormatter(NeuralLogFormatter())

    def emit(self, record):
        """Emit with color coding for different levels"""
        # Color codes for terminal output
        colors = {
            "DEBUG": "\033[96m",  # Cyan
            "INFO": "\033[92m",  # Green
            "WARNING": "\033[93m",  # Yellow
            "ERROR": "\033[91m",  # Red
            "CRITICAL": "\033[95m",  # Magenta
            "RESET": "\033[0m",  # Reset
        }

        if record.levelname in colors:
            # Apply color to the formatted message
            formatted = self.format(record)
            colored_msg = f"{colors[record.levelname]}{formatted}{colors['RESET']}"

            # Temporarily replace the formatted message
            original_format = self.format
            self.format = lambda r: colored_msg
            super().emit(record)
            self.format = original_format
        else:
            super().emit(record)


class NeuraUILogHandler(QObject, logging.Handler):
    """Enhanced UI log handler with neural network styling"""

    log_signal = pyqtSignal(str, str, dict)  # message, level, metadata

    def __init__(self, callback=None):
        QObject.__init__(self)
        logging.Handler.__init__(self)

        self.callback = callback
        self.setFormatter(NeuralLogFormatter())

        # Connect signal if callback provided
        if callback:
            self.log_signal.connect(lambda msg, level, meta: callback(msg, level))

    def emit(self, record):
        """Emit log with neural metadata"""
        if self.callback:
            try:
                msg = self.format(record)
                level = record.levelname.lower()

                # Neural metadata
                metadata = {
                    "timestamp": record.created,
                    "module": record.name,
                    "function": record.funcName,
                    "line": record.lineno,
                    "neural_id": f"N{int(record.created * 1000)}",
                }

                # Enhanced level mapping
                neural_levels = {
                    "debug": "debug",
                    "info": "info",
                    "warning": "warning",
                    "error": "error",
                    "critical": "error",
                }

                ui_level = neural_levels.get(level, "info")

                # Emit neural signal
                self.log_signal.emit(msg, ui_level, metadata)

            except Exception as e:
                # Fallback logging to prevent infinite loops
                print(f"Neural log handler error: {e}")


class QuantumLogManager:
    """Advanced log management with quantum organization"""

    def __init__(self, log_dir="logs", app_name="neural_matrix"):
        self.log_dir = Path(log_dir)
        self.app_name = app_name
        self.handlers = {}
        self.setup_quantum_structure()

    def setup_quantum_structure(self):
        """Setup quantum log directory structure"""
        # Create quantum log directories
        directories = [
            self.log_dir,
            self.log_dir / "neural",
            self.log_dir / "quantum",
            self.log_dir / "archive",
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def create_neural_handler(self, name, level=logging.INFO):
        """Create specialized neural log handler"""
        log_file = self.log_dir / "neural" / f"{name}.log"

        handler = QuantumFileHandler(
            log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"  # 10MB
        )
        handler.setLevel(level)

        self.handlers[name] = handler
        return handler

    def create_quantum_handler(self, name, level=logging.DEBUG):
        """Create quantum debug handler"""
        log_file = self.log_dir / "quantum" / f"{name}_quantum.log"

        handler = QuantumFileHandler(
            log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8"  # 5MB
        )
        handler.setLevel(level)

        return handler

    def get_log_statistics(self):
        """Get neural log statistics"""
        stats = {"total_logs": 0, "by_level": {}, "by_module": {}, "disk_usage": 0}

        # Calculate disk usage
        for log_file in self.log_dir.rglob("*.log"):
            stats["disk_usage"] += log_file.stat().st_size

        return stats


def setup_neural_logging(log_level="INFO", log_dir="logs", enable_quantum=True):
    """Setup comprehensive neural logging system"""

    # Initialize quantum log manager
    quantum_manager = QuantumLogManager(log_dir)

    # Configure log level
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Capture all levels

    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # === Core Neural Handlers ===

    # 1. Main neural log
    main_handler = quantum_manager.create_neural_handler("neural_matrix", numeric_level)
    root_logger.addHandler(main_handler)

    # 2. Error-specific handler
    error_handler = quantum_manager.create_neural_handler("errors", logging.ERROR)
    root_logger.addHandler(error_handler)

    # 3. Holographic console handler
    console_handler = HolographicConsoleHandler()
    console_handler.setLevel(numeric_level)
    root_logger.addHandler(console_handler)

    # === Quantum Debug Handlers ===
    if enable_quantum:
        # Quantum sync operations
        sync_handler = quantum_manager.create_quantum_handler("sync_operations")
        sync_logger = logging.getLogger("core.sync_engine")
        sync_logger.addHandler(sync_handler)

        # Quantum connections
        conn_handler = quantum_manager.create_quantum_handler("connections")
        conn_logger = logging.getLogger("core.connection_manager")
        conn_logger.addHandler(conn_handler)

        # Quantum UI events
        ui_handler = quantum_manager.create_quantum_handler("ui_events")
        ui_logger = logging.getLogger("ui")
        ui_logger.addHandler(ui_handler)

    # === Performance Logging ===
    perf_handler = quantum_manager.create_neural_handler("performance", logging.WARNING)
    perf_logger = logging.getLogger("performance")
    perf_logger.addHandler(perf_handler)

    # Log neural initialization
    logger = logging.getLogger(__name__)
    logger.info("◉ Neural logging system initialized")
    logger.info(f"◦ Log level: {log_level}")
    logger.info(f"◦ Quantum directory: {quantum_manager.log_dir.absolute()}")
    logger.info(f"◦ Quantum mode: {'enabled' if enable_quantum else 'disabled'}")

    return quantum_manager


def get_neural_logger(name):
    """Get specialized neural logger"""
    logger = logging.getLogger(name)

    # Add neural context
    class NeuralLoggerAdapter(logging.LoggerAdapter):
        def process(self, msg, kwargs):
            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
            return f"[{timestamp}] {msg}", kwargs

    return NeuralLoggerAdapter(logger, {})


class PerformanceLogger:
    """Specialized performance logging for neural operations"""

    def __init__(self, operation_name):
        self.operation_name = operation_name
        self.logger = logging.getLogger("performance")
        self.start_time = None

    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.info(f"◈ Starting: {self.operation_name}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now() - self.start_time).total_seconds()

        if exc_type:
            self.logger.error(
                f"◆ Failed: {self.operation_name} ({duration:.3f}s) - {exc_val}"
            )
        else:
            self.logger.info(f"◎ Completed: {self.operation_name} ({duration:.3f}s)")


class NeuralDebugger:
    """Advanced debugging utilities for neural operations"""

    @staticmethod
    def log_function_entry(func):
        """Decorator for logging function entry/exit"""

        def wrapper(*args, **kwargs):
            logger = get_neural_logger(func.__module__)
            logger.info(f"◉ Entering: {func.__name__}")

            try:
                result = func(*args, **kwargs)
                logger.info(f"◎ Exiting: {func.__name__}")
                return result
            except Exception as e:
                logger.error(f"◆ Exception in {func.__name__}: {e}")
                raise

        return wrapper

    @staticmethod
    def log_data_flow(data, stage_name):
        """Log data transformation stages"""
        logger = get_neural_logger("data_flow")

        if hasattr(data, "__len__"):
            logger.info(f"◦ {stage_name}: {len(data)} items")
        else:
            logger.info(f"◦ {stage_name}: {type(data).__name__}")


# Backward compatibility
UILogHandler = NeuraUILogHandler
setup_logging = setup_neural_logging
