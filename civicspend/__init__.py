"""CivicSpend: Public Spending Transparency Platform

Detect meaningful changes in public spending using robust statistics + ML.
"""

__version__ = "0.1.0-dev"
__author__ = "Your Name"
__license__ = "MIT"

# Core components
from civicspend.config import config
from civicspend.logging import logger, setup_logging
from civicspend.exceptions import (
    CivicSpendError,
    DatabaseError,
    APIError,
    ValidationError,
    ConfigurationError,
    ModelError,
    InsufficientDataError,
)

__all__ = [
    "__version__",
    "config",
    "logger",
    "setup_logging",
    "CivicSpendError",
    "DatabaseError",
    "APIError",
    "ValidationError",
    "ConfigurationError",
    "ModelError",
    "InsufficientDataError",
]
