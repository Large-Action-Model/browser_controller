"""
Browser Controller Package

A robust browser automation component for Large Action Model (LAM) systems.
Provides high-level interfaces for web browser interaction, session management,
and intelligent waiting strategies.
"""

# Import all main components
from src.core.browser_controller import BrowserController
from src.config.browser_config import BrowserConfig, ConfigManager
from src.types import (
    BrowserType, WaitStrategy, ElementLocatorType,
    ProxyConfig, ViewportConfig, MobileEmulation, 
    AuthenticationConfig, BrowserCapabilities,
    SessionMetadata, NavigationResult, ElementInfo, PageInfo,
    ElementLocator, Coordinates, WindowSize
)
from src.utils import (
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
