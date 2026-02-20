"""Custom exceptions for CivicSpend."""


class CivicSpendError(Exception):
    """Base exception for CivicSpend."""
    pass


class DatabaseError(CivicSpendError):
    """Database operation failed."""
    pass


class APIError(CivicSpendError):
    """API request failed."""
    pass


class ValidationError(CivicSpendError):
    """Data validation failed."""
    pass


class ConfigurationError(CivicSpendError):
    """Configuration error."""
    pass


class ModelError(CivicSpendError):
    """ML model error."""
    pass


class InsufficientDataError(CivicSpendError):
    """Not enough data for operation."""
    pass
