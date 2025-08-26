"""
Browser Controller Package

A robust browser automation component for Large Action Model (LAM) systems.
Provides high-level interfaces for web browser interaction, session management,
and intelligent waiting strategies.
"""

from .core.browser_controller import BrowserController
from .config.browser_config import BrowserConfig, ConfigManager
from .types import (
    BrowserType, WaitStrategy, ElementLocatorType,
    ProxyConfig, ViewportConfig, MobileEmulation, 
    AuthenticationConfig, BrowserCapabilities,
    SessionMetadata, NavigationResult, ElementInfo, PageInfo,
    ElementLocator, Coordinates, WindowSize
)
from .utils import (
    BrowserLogger, get_logger, set_log_level,
    BrowserControllerError, BrowserLaunchError, SessionError,
    NavigationError, ElementNotFoundError, ElementInteractionError,
    TimeoutError, AuthenticationError, ConfigurationError
)

# Package metadata
__version__ = "1.0.0"
__author__ = "LAM Project"
__description__ = "Browser Controller component for Large Action Model web automation"
__license__ = "MIT"

# Main exports
__all__ = [
    # Main classes
    "BrowserController",
    "BrowserConfig", 
    "ConfigManager",
    
    # Types and enums
    "BrowserType",
    "WaitStrategy", 
    "ElementLocatorType",
    
    # Configuration classes
    "ProxyConfig",
    "ViewportConfig", 
    "MobileEmulation",
    "AuthenticationConfig",
    "BrowserCapabilities",
    
    # Data classes
    "SessionMetadata",
    "NavigationResult",
    "ElementInfo", 
    "PageInfo",
    
    # Type aliases
    "ElementLocator",
    "Coordinates",
    "WindowSize",
    
    # Utilities
    "BrowserLogger",
    "get_logger",
    "set_log_level",
    
    # Exceptions
    "BrowserControllerError",
    "BrowserLaunchError", 
    "SessionError",
    "NavigationError",
    "ElementNotFoundError",
    "ElementInteractionError", 
    "TimeoutError",
    "AuthenticationError",
    "ConfigurationError",
    
    # Package info
    "__version__",
    "__author__", 
    "__description__",
    "__license__",
]


# Convenience function for quick setup
def create_browser_controller(
    browser_type: str = "chrome",
    headless: bool = True, 
    window_size: tuple = (1920, 1080),
    **kwargs
) -> BrowserController:
    """
    Create a BrowserController with common configuration.
    
    Args:
        browser_type: Browser type ("chrome", "firefox", "edge")
        headless: Run in headless mode
        window_size: Browser window size as (width, height)
        **kwargs: Additional configuration options
        
    Returns:
        Configured BrowserController instance
        
    Example:
        >>> controller = create_browser_controller("chrome", headless=False)
        >>> async with controller as browser:
        ...     await browser.navigate_to("https://example.com")
    """
    config = BrowserConfig(
        browser_type=BrowserType(browser_type.lower()),
        headless=headless,
        window_size=window_size,
        **kwargs
    )
    return BrowserController(config)


# Package-level logger
logger = get_logger("BrowserController")

# Log package initialization
logger.info(f"Browser Controller v{__version__} initialized")


# Version check and compatibility warnings
import sys
import warnings

if sys.version_info < (3, 9):
    warnings.warn(
        "Browser Controller requires Python 3.9 or higher. "
        f"Current version: {sys.version_info.major}.{sys.version_info.minor}",
        UserWarning,
        stacklevel=2
    )

# Check for required dependencies
try:
    import selenium
    logger.debug(f"Selenium version: {selenium.__version__}")
except ImportError:
    logger.error("Selenium not found. Please install with: pip install selenium")

try:
    import webdriver_manager
    logger.debug("WebDriver Manager available")
except ImportError:
    logger.warning("WebDriver Manager not found. Manual driver management required.")

try:
    import pydantic
    logger.debug(f"Pydantic version: {pydantic.__version__}")
except ImportError:
    logger.error("Pydantic not found. Please install with: pip install pydantic")

# Export commonly used constants
SUPPORTED_BROWSERS = [browser.value for browser in BrowserType]
DEFAULT_TIMEOUTS = {
    "implicit_wait": 10.0,
    "page_load_timeout": 30.0, 
    "script_timeout": 30.0,
}
DEFAULT_WINDOW_SIZES = {
    "desktop": (1920, 1080),
    "laptop": (1366, 768),
    "tablet": (768, 1024),
    "mobile": (375, 667),
}

logger.debug(f"Supported browsers: {SUPPORTED_BROWSERS}")
