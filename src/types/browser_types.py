from enum import Enum
from typing import Dict, Any, Optional, List, Union, Tuple
from dataclasses import dataclass
from dataclasses_json import dataclass_json


class BrowserType(Enum):
    """Supported browser types."""
    CHROME = "chrome"
    FIREFOX = "firefox"
    EDGE = "edge"
    SAFARI = "safari"


class WaitStrategy(Enum):
    """Waiting strategies for page loading."""
    NONE = "none"
    NORMAL = "normal"
    EAGER = "eager"
    COMPLETE = "complete"


class ElementLocatorType(Enum):
    """Element locator strategies."""
    ID = "id"
    NAME = "name"
    CLASS_NAME = "class_name"
    TAG_NAME = "tag_name"
    CSS_SELECTOR = "css_selector"
    XPATH = "xpath"
    LINK_TEXT = "link_text"
    PARTIAL_LINK_TEXT = "partial_link_text"


@dataclass_json
@dataclass
class ProxyConfig:
    """Proxy configuration."""
    server: str
    port: int
    username: Optional[str] = None
    password: Optional[str] = None
    protocol: str = "http"


@dataclass_json
@dataclass
class ViewportConfig:
    """Browser viewport configuration."""
    width: int = 1920
    height: int = 1080
    device_scale_factor: float = 1.0


@dataclass_json
@dataclass
class MobileEmulation:
    """Mobile device emulation configuration."""
    device_name: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    pixel_ratio: Optional[float] = None
    user_agent: Optional[str] = None


@dataclass_json
@dataclass
class AuthenticationConfig:
    """Authentication configuration."""
    username: str
    password: str
    auth_type: str = "basic"  # basic, digest, etc.


@dataclass_json
@dataclass
class BrowserCapabilities:
    """Browser-specific capabilities and preferences."""
    accept_ssl_certs: bool = True
    accept_insecure_certs: bool = True
    disable_images: bool = False
    disable_javascript: bool = False
    disable_css: bool = False
    disable_plugins: bool = True
    disable_notifications: bool = True
    disable_popup_blocking: bool = False
    enable_logging: bool = True
    log_level: str = "INFO"


@dataclass_json
@dataclass
class SessionMetadata:
    """Session metadata and information."""
    session_id: str
    browser_type: BrowserType
    created_at: float
    current_url: Optional[str] = None
    title: Optional[str] = None
    user_agent: Optional[str] = None
    cookies: List[Dict[str, Any]] = None
    local_storage: Dict[str, Any] = None
    session_storage: Dict[str, Any] = None

    def __post_init__(self):
        if self.cookies is None:
            self.cookies = []
        if self.local_storage is None:
            self.local_storage = {}
        if self.session_storage is None:
            self.session_storage = {}


@dataclass_json
@dataclass
class NavigationResult:
    """Result of navigation operation."""
    success: bool
    url: str
    title: str
    status_code: Optional[int] = None
    load_time: Optional[float] = None
    error_message: Optional[str] = None


@dataclass_json
@dataclass
class ElementInfo:
    """Information about a web element."""
    tag_name: str
    text: str
    attributes: Dict[str, str]
    location: Dict[str, int]
    size: Dict[str, int]
    is_displayed: bool
    is_enabled: bool
    is_selected: bool


@dataclass_json
@dataclass
class PageInfo:
    """Complete page information."""
    url: str
    title: str
    source: str
    timestamp: float
    metadata: Dict[str, Any]
    load_time: Optional[float] = None
    status_code: Optional[int] = None
    headers: Optional[Dict[str, str]] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.headers is None:
            self.headers = {}


# Type aliases for common use cases
ElementLocator = Union[
    Tuple[ElementLocatorType, str],
    Dict[str, str]
]

Coordinates = Tuple[int, int]
WindowSize = Tuple[int, int]
