# Browser Controller - API Reference

Complete API documentation for the Browser Controller component.

## 📚 Table of Contents

1. [Core Classes](#core-classes)
2. [Configuration](#configuration) 
3. [Type System](#type-system)
4. [Utilities](#utilities)
5. [Exceptions](#exceptions)
6. [Examples](#examples)

## Core Classes

### BrowserController

The main controller class for managing browser instances and sessions.

```python
class BrowserController:
    """
    Main Browser Controller class providing high-level browser automation interface.
    
    Handles browser lifecycle, session management, and provides integration
    with LAM (Large Action Model) systems.
    """
```

#### Constructor

```python
def __init__(
    self, 
    config: Optional[BrowserConfig] = None, 
    config_file: Optional[str] = None
) -> None
```

**Parameters:**
- `config` (BrowserConfig, optional): Browser configuration object
- `config_file` (str, optional): Path to JSON configuration file

**Examples:**
```python
# Using configuration object
config = BrowserConfig(browser_type=BrowserType.CHROME, headless=True)
controller = BrowserController(config=config)

# Using configuration file
controller = BrowserController(config_file="browser_config.json")

# Using default configuration
controller = BrowserController()
```

#### Context Manager Methods

```python
async def __aenter__(self) -> 'BrowserController'
async def __aexit__(self, exc_type, exc_val, exc_tb) -> None
```

**Usage:**
```python
async with BrowserController(config) as controller:
    # Browser automatically launched
    session = await controller.create_session()
    # ... automation code ...
    # Browser automatically closed when exiting
```

#### Browser Management

##### `launch()`
```python
async def launch(self) -> None
```
Launch the browser instance.

**Raises:**
- `BrowserLaunchError`: If browser fails to launch
- `BrowserControllerError`: General browser controller errors

**Example:**
```python
controller = BrowserController(config)
await controller.launch()
```

##### `close()`
```python
async def close(self) -> None
```
Close the browser instance and cleanup all sessions.

**Example:**
```python
await controller.close()
```

##### `is_launched()`
```python
def is_launched(self) -> bool
```
Check if browser is currently launched.

**Returns:**
- `bool`: True if browser is running, False otherwise

#### Session Management

##### `create_session()`
```python
async def create_session(
    self, 
    session_config: Optional[Dict[str, Any]] = None
) -> BrowserSession
```
Create a new browser session.

**Parameters:**
- `session_config` (dict, optional): Session-specific configuration overrides

**Returns:**
- `BrowserSession`: New browser session instance

**Raises:**
- `SessionError`: If session creation fails

**Example:**
```python
# Basic session creation
session = await controller.create_session()

# Session with custom configuration
session = await controller.create_session({
    "window_size": (1920, 1080),
    "user_agent": "Custom Agent"
})
```

##### `close_session()`
```python
async def close_session(session_id: str) -> bool
```
Close a specific browser session.

**Parameters:**
- `session_id` (str): ID of session to close

**Returns:**
- `bool`: True if session was closed successfully

**Example:**
```python
success = await controller.close_session(session.session_id)
```

##### `get_session()`
```python
def get_session(session_id: str) -> Optional[BrowserSession]
```
Get session by ID.

**Parameters:**
- `session_id` (str): Session identifier

**Returns:**
- `BrowserSession` or `None`: Session instance if found

##### `get_active_sessions()`
```python
def get_active_sessions(self) -> List[str]
```
Get list of active session IDs.

**Returns:**
- `List[str]`: List of active session identifiers

##### `get_session_count()`
```python
def get_session_count(self) -> int
```
Get number of active sessions.

**Returns:**
- `int`: Count of active sessions

#### Information Methods

##### `get_browser_info()`
```python
async def get_browser_info(self) -> Dict[str, Any]
```
Get browser information and capabilities.

**Returns:**
- `Dict[str, Any]`: Browser information including version, capabilities

**Example:**
```python
info = await controller.get_browser_info()
print(f"Browser: {info['name']} {info['version']}")
```

##### `take_screenshot()`
```python
async def take_screenshot(
    self, 
    file_path: Optional[str] = None
) -> Union[str, bytes]
```
Take screenshot of current browser state.

**Parameters:**
- `file_path` (str, optional): Path to save screenshot

**Returns:**
- `str`: File path if saved to file
- `bytes`: Screenshot data if no file path provided

---

### BrowserSession

Individual browser session for page interaction.

```python
class BrowserSession:
    """
    Represents an individual browser session with full page interaction capabilities.
    
    Provides methods for navigation, element interaction, form handling, and more.
    """
```

#### Properties

```python
@property
def session_id(self) -> str
    """Get the session identifier."""

@property 
def config(self) -> BrowserConfig
    """Get the session configuration."""
```

#### Navigation Methods

##### `navigate_to()`
```python
async def navigate_to(
    self, 
    url: str, 
    wait_for_load: bool = True, 
    timeout: Optional[float] = None
) -> NavigationResult
```
Navigate to a URL.

**Parameters:**
- `url` (str): Target URL
- `wait_for_load` (bool): Whether to wait for page load completion
- `timeout` (float, optional): Custom timeout in seconds

**Returns:**
- `NavigationResult`: Navigation result with status and timing

**Example:**
```python
result = await session.navigate_to("https://example.com")
print(f"Navigation took {result.load_time:.2f} seconds")
```

##### `get_current_url()`
```python
async def get_current_url(self) -> str
```
Get current page URL.

**Returns:**
- `str`: Current URL

##### `get_title()`
```python
async def get_title(self) -> str
```
Get current page title.

**Returns:**
- `str`: Page title

##### `go_back()`
```python
async def go_back(self) -> None
```
Navigate back in browser history.

##### `go_forward()`
```python
async def go_forward(self) -> None
```
Navigate forward in browser history.

##### `refresh()`
```python
async def refresh(self) -> None
```
Refresh current page.

#### Element Interaction

##### `find_element()`
```python
async def find_element(
    self, 
    locator: ElementLocator, 
    timeout: Optional[float] = None
) -> Optional[WebElement]
```
Find a single element on the page.

**Parameters:**
- `locator` (ElementLocator): CSS selector, XPath, or element locator
- `timeout` (float, optional): Custom timeout for element search

**Returns:**
- `WebElement` or `None`: Found element or None if not found

**Examples:**
```python
# CSS selector
element = await session.find_element("button.submit")

# XPath
element = await session.find_element("//button[contains(@class, 'submit')]")

# With timeout
element = await session.find_element("div.loading", timeout=30)
```

##### `find_elements()`
```python
async def find_elements(
    self, 
    locator: ElementLocator, 
    timeout: Optional[float] = None
) -> List[WebElement]
```
Find multiple elements on the page.

**Parameters:**
- `locator` (ElementLocator): CSS selector, XPath, or element locator
- `timeout` (float, optional): Custom timeout for element search

**Returns:**
- `List[WebElement]`: List of found elements (empty if none found)

##### `click_element()`
```python
async def click_element(
    self, 
    locator: ElementLocator, 
    timeout: Optional[float] = None
) -> bool
```
Click an element on the page.

**Parameters:**
- `locator` (ElementLocator): Element locator
- `timeout` (float, optional): Custom timeout

**Returns:**
- `bool`: True if click was successful

**Example:**
```python
success = await session.click_element("button#submit")
if success:
    print("Button clicked successfully")
```

##### `type_text()`
```python
async def type_text(
    self, 
    locator: ElementLocator, 
    text: str, 
    clear_first: bool = True, 
    timeout: Optional[float] = None
) -> bool
```
Type text into an input element.

**Parameters:**
- `locator` (ElementLocator): Element locator
- `text` (str): Text to type
- `clear_first` (bool): Whether to clear field before typing
- `timeout` (float, optional): Custom timeout

**Returns:**
- `bool`: True if typing was successful

**Example:**
```python
success = await session.type_text("input[name='username']", "john_doe")
```

##### `get_element_text()`
```python
async def get_element_text(
    self, 
    locator: ElementLocator, 
    timeout: Optional[float] = None
) -> str
```
Get text content of an element.

**Parameters:**
- `locator` (ElementLocator): Element locator
- `timeout` (float, optional): Custom timeout

**Returns:**
- `str`: Element text content

##### `get_element_attribute()`
```python
async def get_element_attribute(
    self, 
    locator: ElementLocator, 
    attribute: str, 
    timeout: Optional[float] = None
) -> Optional[str]
```
Get attribute value of an element.

**Parameters:**
- `locator` (ElementLocator): Element locator
- `attribute` (str): Attribute name
- `timeout` (float, optional): Custom timeout

**Returns:**
- `str` or `None`: Attribute value or None if not found

**Example:**
```python
value = await session.get_element_attribute("input[name='email']", "value")
```

#### Waiting Strategies

##### `wait_for_element()`
```python
async def wait_for_element(
    self, 
    locator: ElementLocator, 
    timeout: Optional[float] = None
) -> Optional[WebElement]
```
Wait for element to appear on page.

**Parameters:**
- `locator` (ElementLocator): Element locator
- `timeout` (float, optional): Maximum wait time

**Returns:**
- `WebElement` or `None`: Element if found within timeout

##### `wait_for_element_to_disappear()`
```python
async def wait_for_element_to_disappear(
    self, 
    locator: ElementLocator, 
    timeout: Optional[float] = None
) -> bool
```
Wait for element to disappear from page.

**Parameters:**
- `locator` (ElementLocator): Element locator  
- `timeout` (float, optional): Maximum wait time

**Returns:**
- `bool`: True if element disappeared within timeout

##### `wait_for_clickable()`
```python
async def wait_for_clickable(
    self, 
    locator: ElementLocator, 
    timeout: Optional[float] = None
) -> Optional[WebElement]
```
Wait for element to become clickable.

**Parameters:**
- `locator` (ElementLocator): Element locator
- `timeout` (float, optional): Maximum wait time

**Returns:**
- `WebElement` or `None`: Clickable element if found

#### Screenshots

##### `take_screenshot()`
```python
async def take_screenshot(
    self, 
    file_path: Optional[str] = None
) -> Union[str, bytes, bool]
```
Take screenshot of current page.

**Parameters:**
- `file_path` (str, optional): Path to save screenshot

**Returns:**
- `str`: File path if saved to file
- `bytes`: Screenshot data if no file path provided  
- `bool`: True if successful (for some implementations)

**Example:**
```python
# Save to file
await session.take_screenshot("page.png")

# Get as bytes
screenshot_data = await session.take_screenshot()
```

##### `take_element_screenshot()`
```python
async def take_element_screenshot(
    self, 
    locator: ElementLocator, 
    file_path: str,
    timeout: Optional[float] = None
) -> bool
```
Take screenshot of specific element.

**Parameters:**
- `locator` (ElementLocator): Element locator
- `file_path` (str): Path to save screenshot
- `timeout` (float, optional): Custom timeout

**Returns:**
- `bool`: True if screenshot was successful

#### Advanced Methods

##### `execute_script()`
```python
async def execute_script(
    self, 
    script: str, 
    *args
) -> Any
```
Execute JavaScript in browser context.

**Parameters:**
- `script` (str): JavaScript code to execute
- `args`: Arguments to pass to script

**Returns:**
- `Any`: Script return value

**Example:**
```python
title = await session.execute_script("return document.title;")
await session.execute_script("window.scrollTo(0, document.body.scrollHeight);")
```

##### `add_cookie()`
```python
async def add_cookie(self, cookie_dict: Dict[str, Any]) -> None
```
Add cookie to browser session.

**Parameters:**
- `cookie_dict` (dict): Cookie information

**Example:**
```python
await session.add_cookie({
    "name": "session_id", 
    "value": "abc123",
    "domain": "example.com"
})
```

##### `get_cookies()`
```python
async def get_cookies(self) -> List[Dict[str, Any]]
```
Get all cookies from current domain.

**Returns:**
- `List[Dict[str, Any]]`: List of cookie dictionaries

##### `delete_all_cookies()`
```python
async def delete_all_cookies(self) -> None
```
Delete all cookies from browser session.

---

## Configuration

### BrowserConfig

Pydantic-based configuration class with validation.

```python
class BrowserConfig(BaseModel):
    """
    Browser configuration with Pydantic validation.
    
    Supports environment variable loading and validation.
    """
```

#### Fields

```python
# Browser settings
browser_type: BrowserType = BrowserType.CHROME
headless: bool = True
window_size: Tuple[int, int] = (1280, 720)

# Timeouts
page_load_timeout: float = 30.0
implicit_wait: float = 10.0
script_timeout: float = 30.0

# Browser options
browser_options: Dict[str, Any] = {}

# Proxy settings
proxy_settings: Optional[Dict[str, str]] = None

# Logging
log_level: str = "INFO"
enable_logging: bool = True
```

#### Environment Variables

The following environment variables are automatically loaded:

```bash
# Browser settings
BROWSER_TYPE=chrome          # chrome, firefox, edge
HEADLESS=true               # true, false
WINDOW_WIDTH=1280           # integer
WINDOW_HEIGHT=720           # integer

# Timeouts
PAGE_LOAD_TIMEOUT=30        # float seconds
IMPLICIT_WAIT=10           # float seconds
SCRIPT_TIMEOUT=30          # float seconds

# Logging
LOG_LEVEL=INFO             # DEBUG, INFO, WARNING, ERROR
ENABLE_LOGGING=true        # true, false

# Proxy (optional)
HTTP_PROXY=http://proxy:8080
HTTPS_PROXY=https://proxy:8080
```

#### Examples

```python
# Basic configuration
config = BrowserConfig()

# Custom configuration
config = BrowserConfig(
    browser_type=BrowserType.CHROME,
    headless=False,
    window_size=(1920, 1080),
    page_load_timeout=45,
    browser_options={
        "disable_images": True,
        "user_agent": "Custom Agent"
    }
)

# With proxy
config = BrowserConfig(
    proxy_settings={
        "http": "http://proxy:8080",
        "https": "https://proxy:8080"
    }
)
```

### ConfigManager

Utility class for loading configuration from various sources.

```python
class ConfigManager:
    """Manages configuration loading from files and environment."""
```

#### Methods

##### `load_from_file()`
```python
@classmethod
def load_from_file(cls, file_path: str) -> BrowserConfig
```
Load configuration from JSON file.

##### `load_from_env()`
```python
@classmethod
def load_from_env(cls) -> BrowserConfig
```
Load configuration from environment variables.

---

## Type System

### Enums

#### BrowserType
```python
class BrowserType(str, Enum):
    CHROME = "chrome"
    FIREFOX = "firefox"
    EDGE = "edge"
    SAFARI = "safari"
```

#### ActionType
```python
class ActionType(str, Enum):
    NAVIGATE = "navigate"
    CLICK = "click"
    TYPE = "type"
    WAIT = "wait"
    SCREENSHOT = "screenshot"
```

#### WaitStrategy
```python
class WaitStrategy(str, Enum):
    PRESENCE = "presence"
    VISIBLE = "visible"
    CLICKABLE = "clickable"
    INVISIBLE = "invisible"
```

### Data Classes

#### NavigationResult
```python
@dataclass
class NavigationResult:
    url: str
    success: bool
    load_time: float
    status_code: Optional[int] = None
    error: Optional[str] = None
```

#### PageInfo
```python
@dataclass  
class PageInfo:
    url: str
    title: str
    source_length: int
    viewport_size: Tuple[int, int]
    ready_state: str
```

#### SessionMetadata
```python
@dataclass
class SessionMetadata:
    session_id: str
    created_at: datetime
    last_activity: datetime
    page_count: int
    current_url: str
```

### Type Aliases

```python
ElementLocator = Union[str, Tuple[str, str]]  # CSS selector or (strategy, locator)
Coordinates = Tuple[int, int]                 # (x, y) coordinates  
WindowSize = Tuple[int, int]                  # (width, height)
```

---

## Utilities

### Logger

#### `get_logger()`
```python
def get_logger(name: str) -> Logger
```
Get a structured logger instance.

**Parameters:**
- `name` (str): Logger name

**Returns:**
- `Logger`: Loguru logger instance

**Example:**
```python
from src.utils.logger import get_logger

logger = get_logger("MyAutomation")
logger.info("Starting automation", session_id="12345")
logger.error("Failed to find element", selector="button.submit")
```

#### `configure_logging()`
```python
def configure_logging(
    level: str = "INFO",
    file_rotation: str = "10 MB",
    retention: str = "30 days",
    format: Optional[str] = None
) -> None
```
Configure logging system.

**Parameters:**
- `level` (str): Log level (DEBUG, INFO, WARNING, ERROR)
- `file_rotation` (str): File rotation trigger
- `retention` (str): Log retention period
- `format` (str, optional): Custom log format

### Wait Strategies

#### `wait_for_condition()`
```python
async def wait_for_condition(
    session: BrowserSession,
    condition: Callable,
    timeout: float = 30,
    poll_frequency: float = 0.5
) -> Any
```
Wait for custom condition to be met.

**Parameters:**
- `session` (BrowserSession): Browser session
- `condition` (Callable): Condition function to check
- `timeout` (float): Maximum wait time
- `poll_frequency` (float): Check frequency in seconds

**Returns:**
- `Any`: Condition result when met

---

## Exceptions

### Exception Hierarchy

```
BrowserControllerError
├── BrowserLaunchError
├── BrowserCloseError
├── SessionError
│   ├── SessionCreationError
│   ├── SessionTimeoutError
│   └── SessionCleanupError
├── NavigationError
│   ├── PageLoadError
│   └── NavigationTimeoutError
└── ElementError
    ├── ElementNotFoundError
    ├── ElementNotClickableError
    └── ElementInteractionError
```

### Base Exception

```python
class BrowserControllerError(Exception):
    """Base exception for browser controller errors."""
    
    def __init__(
        self, 
        message: str, 
        session_id: Optional[str] = None,
        url: Optional[str] = None,
        **kwargs
    ):
        self.message = message
        self.session_id = session_id
        self.url = url
        self.extra_data = kwargs
        super().__init__(self.message)
```

### Specific Exceptions

#### SessionError
```python
class SessionError(BrowserControllerError):
    """Session-related errors."""
```

#### NavigationError
```python
class NavigationError(BrowserControllerError):
    """Navigation-related errors."""
```

#### ElementError
```python
class ElementError(BrowserControllerError):
    """Element interaction errors."""
    
    def __init__(
        self, 
        message: str, 
        selector: Optional[str] = None,
        **kwargs
    ):
        self.selector = selector
        super().__init__(message, **kwargs)
```

---

## Examples

### Complete API Usage Example

```python
import asyncio
from src.core.browser_controller import BrowserController
from src.config.browser_config import BrowserConfig
from src.types.browser_types import BrowserType
from src.utils.logger import get_logger

async def complete_api_example():
    """Demonstrates complete API usage"""
    
    # Configure logging
    logger = get_logger("APIExample")
    
    # Create configuration
    config = BrowserConfig(
        browser_type=BrowserType.CHROME,
        headless=True,
        window_size=(1280, 720),
        page_load_timeout=30
    )
    
    # Use browser controller
    async with BrowserController(config) as controller:
        logger.info("Browser controller initialized")
        
        # Create session
        session = await controller.create_session()
        logger.info(f"Created session: {session.session_id}")
        
        try:
            # Navigate
            result = await session.navigate_to("https://httpbin.org/forms/post")
            logger.info(f"Navigation completed in {result.load_time:.2f}s")
            
            # Interact with form
            await session.type_text("input[name='custname']", "API Test User")
            await session.type_text("input[name='custemail']", "test@api.com")
            await session.click_element("input[value='medium']")
            
            # Take screenshot
            await session.take_screenshot("form_filled.png")
            logger.info("Screenshot saved")
            
            # Submit form
            await session.click_element("input[type='submit']")
            
            # Wait for response
            await session.wait_for_element("pre", timeout=10)
            
            # Get response data
            response_text = await session.get_element_text("pre")
            logger.info(f"Form response received: {len(response_text)} characters")
            
        except Exception as e:
            logger.error(f"API example failed: {e}")
            
        finally:
            # Cleanup
            await controller.close_session(session.session_id)
            logger.info("Session closed")
    
    logger.info("API example completed")

# Run example
asyncio.run(complete_api_example())
```

This completes the comprehensive API reference documentation for the Browser Controller. All classes, methods, parameters, and examples are documented with proper types and usage patterns.
