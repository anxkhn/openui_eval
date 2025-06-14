"""Custom exceptions for the benchmark system."""


class BenchmarkError(Exception):
    """Base exception for benchmark system errors."""

    pass


class ModelError(BenchmarkError):
    """Exception raised for model-related errors."""

    pass


class RenderingError(BenchmarkError):
    """Exception raised for rendering-related errors."""

    pass


class EvaluationError(BenchmarkError):
    """Exception raised for evaluation-related errors."""

    pass


class ConfigurationError(BenchmarkError):
    """Exception raised for configuration-related errors."""

    pass


class HTMLExtractionError(BenchmarkError):
    """Exception raised for HTML extraction errors."""

    pass


class MemoryError(BenchmarkError):
    """Exception raised for memory management errors."""

    pass
