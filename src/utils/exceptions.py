"""Custom exceptions for Browser Controller."""


class BrowserControllerError(Exception):
    """Base exception for Browser Controller errors."""
    
    def __init__(self, message: str, error_code: str = None, context: dict = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "BROWSER_CONTROLLER_ERROR"
        self.context = context or {}


class BrowserLaunchError(BrowserControllerError):
    """Raised when browser fails to launch."""
    
    def __init__(self, message: str, browser_type: str = None, context: dict = None):
        super().__init__(message, "BROWSER_LAUNCH_ERROR", context)
        self.browser_type = browser_type


class SessionError(BrowserControllerError):
    """Raised when session operation fails."""
    
    def __init__(self, message: str, session_id: str = None, context: dict = None):
        super().__init__(message, "SESSION_ERROR", context)
        self.session_id = session_id


class NavigationError(BrowserControllerError):
    """Raised when navigation fails."""
    
    def __init__(self, message: str, url: str = None, context: dict = None):
        super().__init__(message, "NAVIGATION_ERROR", context)
        self.url = url


class ElementNotFoundError(BrowserControllerError):
    """Raised when element cannot be found."""
    
    def __init__(self, message: str, locator: str = None, context: dict = None):
        super().__init__(message, "ELEMENT_NOT_FOUND", context)
        self.locator = locator


class ElementInteractionError(BrowserControllerError):
    """Raised when element interaction fails."""
    
    def __init__(self, message: str, element_info: dict = None, context: dict = None):
        super().__init__(message, "ELEMENT_INTERACTION_ERROR", context)
        self.element_info = element_info or {}


class TimeoutError(BrowserControllerError):
    """Raised when operation times out."""
    
    def __init__(self, message: str, timeout_duration: float = None, context: dict = None):
        super().__init__(message, "TIMEOUT_ERROR", context)
        self.timeout_duration = timeout_duration


class AuthenticationError(BrowserControllerError):
    """Raised when authentication fails."""
    
    def __init__(self, message: str, auth_type: str = None, context: dict = None):
        super().__init__(message, "AUTHENTICATION_ERROR", context)
        self.auth_type = auth_type


class ConfigurationError(BrowserControllerError):
    """Raised when configuration is invalid."""
    
    def __init__(self, message: str, config_key: str = None, context: dict = None):
        super().__init__(message, "CONFIGURATION_ERROR", context)
        self.config_key = config_key


class ResourceError(BrowserControllerError):
    """Raised when resource management fails."""
    
    def __init__(self, message: str, resource_type: str = None, context: dict = None):
        super().__init__(message, "RESOURCE_ERROR", context)
        self.resource_type = resource_type


class SecurityError(BrowserControllerError):
    """Raised when security-related operations fail."""
    
    def __init__(self, message: str, security_context: str = None, context: dict = None):
        super().__init__(message, "SECURITY_ERROR", context)
        self.security_context = security_context
