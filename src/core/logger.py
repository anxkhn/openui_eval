"""Comprehensive logging system for the benchmark framework."""

import gzip
import json
import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from rich.console import Console
from rich.logging import RichHandler


class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging."""

    def format(self, record):
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        # Add extra fields if present
        if hasattr(record, "model_name"):
            log_entry["model_name"] = record.model_name
        if hasattr(record, "task_name"):
            log_entry["task_name"] = record.task_name
        if hasattr(record, "iteration"):
            log_entry["iteration"] = record.iteration
        if hasattr(record, "duration"):
            log_entry["duration"] = record.duration
        if hasattr(record, "memory_usage"):
            log_entry["memory_usage"] = record.memory_usage
        if hasattr(record, "image_attached"):
            log_entry["image_attached"] = record.image_attached
        if hasattr(record, "file_attached"):
            log_entry["file_attached"] = record.file_attached
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry, ensure_ascii=False)


class CompressedRotatingFileHandler(logging.handlers.RotatingFileHandler):
    """Rotating file handler that compresses old log files."""

    def doRollover(self):
        """Override to compress the rotated file."""
        super().doRollover()
        # Compress the rotated file
        rotated_file = f"{self.baseFilename}.1"
        if os.path.exists(rotated_file):
            compressed_file = f"{rotated_file}.gz"
            with open(rotated_file, "rb") as f_in:
                with gzip.open(compressed_file, "wb") as f_out:
                    f_out.writelines(f_in)
            os.remove(rotated_file)


class Logger:
    """Centralized logging system for the benchmark framework."""

    def __init__(
        self,
        name: str = "benchmark",
        log_dir: str = "logs",
        level: str = "INFO",
        enable_compression: bool = True,
    ):
        self.name = name
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.enable_compression = enable_compression
        # Create console for rich output
        self.console = Console()
        # Setup logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        # Clear existing handlers
        self.logger.handlers.clear()
        # Setup handlers
        self._setup_console_handler()
        self._setup_file_handlers()
        # Track API calls and operations
        self.api_calls = []
        self.operations = []

    def _setup_console_handler(self):
        """Setup rich console handler for beautiful terminal output."""
        console_handler = RichHandler(
            console=self.console,
            show_time=True,
            show_path=False,
            markup=True,
            rich_tracebacks=True,
        )
        console_handler.setLevel(logging.INFO)
        console_format = "%(message)s"
        console_handler.setFormatter(logging.Formatter(console_format))
        self.logger.addHandler(console_handler)

    def _setup_file_handlers(self):
        """Setup file handlers for different log types."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Main log file (structured JSON)
        main_log_file = self.log_dir / f"benchmark_{timestamp}.jsonl"
        if self.enable_compression:
            main_handler = CompressedRotatingFileHandler(
                main_log_file, maxBytes=50 * 1024 * 1024, backupCount=5  # 50MB files
            )
        else:
            main_handler = logging.handlers.RotatingFileHandler(
                main_log_file, maxBytes=50 * 1024 * 1024, backupCount=5
            )
        main_handler.setLevel(logging.DEBUG)
        main_handler.setFormatter(StructuredFormatter())
        self.logger.addHandler(main_handler)
        # Error log file
        error_log_file = self.log_dir / f"errors_{timestamp}.log"
        error_handler = logging.FileHandler(error_log_file)
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        self.logger.addHandler(error_handler)
        # API calls log file
        api_log_file = self.log_dir / f"api_calls_{timestamp}.jsonl"
        self.api_log_handler = logging.FileHandler(api_log_file)
        self.api_log_handler.setFormatter(StructuredFormatter())

    def info(self, message: str, **kwargs):
        """Log info message with optional structured data."""
        self.logger.info(message, extra=kwargs)

    def debug(self, message: str, **kwargs):
        """Log debug message with optional structured data."""
        self.logger.debug(message, extra=kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message with optional structured data."""
        self.logger.warning(message, extra=kwargs)

    def error(self, message: str, **kwargs):
        """Log error message with optional structured data."""
        self.logger.error(message, extra=kwargs)

    def critical(self, message: str, **kwargs):
        """Log critical message with optional structured data."""
        self.logger.critical(message, extra=kwargs)

    def log_model_operation(
        self,
        operation: str,
        model_name: str,
        duration: Optional[float] = None,
        **kwargs,
    ):
        """Log model-specific operations."""
        extra = {"model_name": model_name, "operation": operation, **kwargs}
        if duration is not None:
            extra["duration"] = duration
        self.info(f"Model operation: {operation} for {model_name}", **extra)

    def log_task_operation(
        self, operation: str, task_name: str, iteration: Optional[int] = None, **kwargs
    ):
        """Log task-specific operations."""
        extra = {"task_name": task_name, "operation": operation, **kwargs}
        if iteration is not None:
            extra["iteration"] = iteration
        self.info(f"Task operation: {operation} for {task_name}", **extra)

    def log_api_call(
        self,
        model_name: str,
        prompt: str,
        response: str,
        duration: float,
        image_attached: bool = False,
        file_attached: bool = False,
        **kwargs,
    ):
        """Log API calls to Ollama with detailed information."""
        api_call = {
            "timestamp": datetime.now().isoformat(),
            "model_name": model_name,
            "prompt_length": len(prompt),
            "response_length": len(response),
            "duration": duration,
            "image_attached": image_attached,
            "file_attached": file_attached,
            **kwargs,
        }
        # Store in memory for analysis
        self.api_calls.append(api_call)
        # Log to file
        api_logger = logging.getLogger(f"{self.name}.api")
        api_logger.addHandler(self.api_log_handler)
        api_logger.info("API call", extra=api_call)
        # Log to main logger with summary
        self.info(
            f"API call to {model_name} - Duration: {duration:.2f}s, "
            f"Image: {image_attached}, File: {file_attached}",
            model_name=model_name,
            duration=duration,
            image_attached=image_attached,
            file_attached=file_attached,
        )

    def log_memory_usage(self, operation: str, memory_mb: float, **kwargs):
        """Log memory usage information."""
        self.info(
            f"Memory usage during {operation}: {memory_mb:.1f} MB",
            operation=operation,
            memory_usage=memory_mb,
            **kwargs,
        )

    def log_rendering_operation(
        self, url: str, screenshot_path: str, duration: float, success: bool, **kwargs
    ):
        """Log web rendering operations."""
        self.info(
            f"Rendered {'successfully' if success else 'failed'}: {url} -> {screenshot_path}",
            operation="rendering",
            url=url,
            screenshot_path=screenshot_path,
            duration=duration,
            success=success,
            **kwargs,
        )

    def log_evaluation_result(
        self,
        model_name: str,
        task_name: str,
        iteration: int,
        scores: Dict[str, float],
        **kwargs,
    ):
        """Log evaluation results."""
        avg_score = sum(scores.values()) / len(scores) if scores else 0
        self.info(
            f"Evaluation by {model_name} for {task_name} (iter {iteration}): "
            f"Average score: {avg_score:.2f}",
            model_name=model_name,
            task_name=task_name,
            iteration=iteration,
            scores=scores,
            average_score=avg_score,
            **kwargs,
        )

    def log_pipeline_progress(self, stage: str, progress: float, **kwargs):
        """Log pipeline progress."""
        self.info(
            f"Pipeline progress - {stage}: {progress:.1f}%",
            stage=stage,
            progress=progress,
            **kwargs,
        )

    def log_system_info(self, info: Dict[str, Any]):
        """Log system information at startup."""
        self.info("System information", **info)

    def get_api_call_stats(self) -> Dict[str, Any]:
        """Get statistics about API calls."""
        if not self.api_calls:
            return {}
        total_calls = len(self.api_calls)
        total_duration = sum(call["duration"] for call in self.api_calls)
        avg_duration = total_duration / total_calls
        model_stats = {}
        for call in self.api_calls:
            model = call["model_name"]
            if model not in model_stats:
                model_stats[model] = {"calls": 0, "total_duration": 0}
            model_stats[model]["calls"] += 1
            model_stats[model]["total_duration"] += call["duration"]
        for model in model_stats:
            model_stats[model]["avg_duration"] = (
                model_stats[model]["total_duration"] /
                model_stats[model]["calls"]
            )
        return {
            "total_calls": total_calls,
            "total_duration": total_duration,
            "average_duration": avg_duration,
            "model_stats": model_stats,
            "calls_with_images": sum(
                1 for call in self.api_calls if call.get("image_attached")
            ),
            "calls_with_files": sum(
                1 for call in self.api_calls if call.get("file_attached")
            ),
        }

    def save_summary_report(self, output_path: str):
        """Save a summary report of all logged operations."""
        summary = {
            "timestamp": datetime.now().isoformat(),
            "api_call_stats": self.get_api_call_stats(),
            "total_operations": len(self.operations),
            "log_files": [
                str(handler.baseFilename)
                for handler in self.logger.handlers
                if hasattr(handler, "baseFilename")
            ],
        }
        with open(output_path, "w") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        self.info(f"Summary report saved to {output_path}")


# Global logger instance
_global_logger: Optional[Logger] = None


def get_logger(name: str = "benchmark") -> Logger:
    """Get or create global logger instance."""
    global _global_logger
    if _global_logger is None:
        _global_logger = Logger(name)
    return _global_logger


def setup_logger(
    name: str = "benchmark",
    log_dir: str = "logs",
    level: str = "INFO",
    enable_compression: bool = True,
) -> Logger:
    """Setup and return a new logger instance."""
    global _global_logger
    _global_logger = Logger(name, log_dir, level, enable_compression)
    return _global_logger
