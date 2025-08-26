"""
Browser Session class for managing individual browser sessions.

This class provides high-level methods for interacting with web pages,
including navigation, element interaction, and data extraction.
"""

import asyncio
import time
import uuid
from typing import Optional, Dict, Any, List, Union, Callable
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    WebDriverException, NoSuchElementException, TimeoutException,
    StaleElementReferenceException, ElementNotInteractableException
)

from ..config.browser_config import BrowserConfig
from ..utils import get_logger, WaitStrategies
from ..utils.exceptions import (
    SessionError, NavigationError, ElementNotFoundError, 
    ElementInteractionError, TimeoutError as BrowserTimeoutError
)
from ..types import (
    SessionMetadata, NavigationResult, ElementInfo, PageInfo,
    ElementLocator, ElementLocatorType, Coordinates, WindowSize
)


class BrowserSession:
    """
    Browser session class for managing web page interactions.
    
    This class provides high-level methods for:
    - Page navigation and loading
    - Element finding and interaction  
    - Form handling and data input
    - Page information extraction
    - Cookie and storage management
    """
    
    def __init__(
        self, 
        driver: WebDriver, 
        session_id: str, 
        config: BrowserConfig,
        session_config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize browser session.
        
        Args:
            driver: Selenium WebDriver instance
            session_id: Unique session identifier
            config: Browser configuration
            session_config: Session-specific configuration overrides
        """
        self.driver = driver
        self.session_id = session_id
        self.config = config
        self.session_config = session_config or {}
        
        # Initialize components
        self.logger = get_logger(f"BrowserSession:{session_id[:8]}")
        self.wait_strategies = WaitStrategies(driver, config.implicit_wait)
        
        # Session state
        self.created_at = time.time()
        self.is_active = True
        self._metadata: Optional[SessionMetadata] = None
        
        self.logger.info("Browser session initialized", {
            "session_id": session_id,
            "driver_session_id": driver.session_id
        })
    
    # Navigation methods
    async def navigate_to(
        self, 
        url: str, 
        wait_for_load: bool = True, 
        timeout: Optional[float] = None
    ) -> NavigationResult:
        """
        Navigate to URL.
        
        Args:
            url: Target URL
            wait_for_load: Wait for page load completion
            timeout: Navigation timeout
            
        Returns:
            Navigation result with status and timing
        """
        if not self.is_active:
            raise SessionError("Session is not active", self.session_id)
        
        start_time = time.time()
        
        try:
            self.logger.log_navigation(url, "GET")
            
            # Navigate to URL
            await asyncio.get_event_loop().run_in_executor(
                None, self.driver.get, url
            )
            
            # Wait for page load if requested
            if wait_for_load:
                await self._wait_for_page_ready(timeout)
            
            # Get final URL (may have redirected)
            final_url = self.driver.current_url
            title = self.driver.title
            load_time = time.time() - start_time
            
            result = NavigationResult(
                success=True,
                url=final_url,
                title=title,
                load_time=load_time
            )
            
            self.logger.log_navigation(final_url, "GET", load_time=load_time)
            return result
            
        except Exception as e:
            load_time = time.time() - start_time
            error_msg = str(e)
            
            self.logger.error(f"Navigation failed to {url}", {
                "error": error_msg,
                "load_time": load_time
            }, exception=e)
            
            result = NavigationResult(
                success=False,
                url=url,
                title="",
                load_time=load_time,
                error_message=error_msg
            )
            
            raise NavigationError(
                f"Failed to navigate to {url}: {error_msg}",
                url=url,
                context={"load_time": load_time}
            ) from e
    
    async def go_back(self) -> bool:
        """Navigate back in browser history."""
        try:
            await asyncio.get_event_loop().run_in_executor(None, self.driver.back)
            self.logger.info("Navigated back")
            return True
        except Exception as e:
            self.logger.error("Failed to go back", exception=e)
            return False
    
    async def go_forward(self) -> bool:
        """Navigate forward in browser history."""
        try:
            await asyncio.get_event_loop().run_in_executor(None, self.driver.forward)
            self.logger.info("Navigated forward")
            return True
        except Exception as e:
            self.logger.error("Failed to go forward", exception=e)
            return False
    
    async def refresh(self) -> bool:
        """Refresh current page."""
        try:
            await asyncio.get_event_loop().run_in_executor(None, self.driver.refresh)
            await self._wait_for_page_ready()
            self.logger.info("Page refreshed")
            return True
        except Exception as e:
            self.logger.error("Failed to refresh page", exception=e)
            return False
    
    # Element interaction methods
    async def find_element(
        self, 
        locator: ElementLocator, 
        timeout: Optional[float] = None
    ) -> Optional[WebElement]:
        """
        Find single element by locator.
        
        Args:
            locator: Element locator (type, value) tuple or string
            timeout: Wait timeout
            
        Returns:
            WebElement if found, None otherwise
        """
        try:
            element = self.wait_strategies.wait_for_element_present(locator, timeout)
            
            self.logger.debug("Element found", {
                "locator": str(locator),
                "element_tag": element.tag_name
            })
            
            return element
            
        except BrowserTimeoutError:
            self.logger.warning("Element not found", {"locator": str(locator)})
            return None
        except Exception as e:
            self.logger.error("Error finding element", {"locator": str(locator)}, exception=e)
            return None
    
    async def find_elements(
        self, 
        locator: ElementLocator, 
        min_count: int = 1,
        timeout: Optional[float] = None
    ) -> List[WebElement]:
        """
        Find multiple elements by locator.
        
        Args:
            locator: Element locator
            min_count: Minimum expected count
            timeout: Wait timeout
            
        Returns:
            List of WebElements
        """
        try:
            elements = self.wait_strategies.wait_for_elements(locator, min_count, timeout)
            
            self.logger.debug("Elements found", {
                "locator": str(locator),
                "count": len(elements)
            })
            
            return elements
            
        except (BrowserTimeoutError, ElementNotFoundError):
            self.logger.warning("Elements not found", {
                "locator": str(locator),
                "min_count": min_count
            })
            return []
    
    async def click_element(
        self, 
        locator: ElementLocator, 
        timeout: Optional[float] = None
    ) -> bool:
        """
        Click element by locator.
        
        Args:
            locator: Element locator
            timeout: Wait timeout
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Wait for element to be clickable
            element = self.wait_strategies.wait_for_element_clickable(locator, timeout)
            
            # Click element
            await asyncio.get_event_loop().run_in_executor(None, element.click)
            
            self.logger.log_element_interaction("click", {
                "locator": str(locator),
                "element_tag": element.tag_name
            })
            
            return True
            
        except BrowserTimeoutError as e:
            self.logger.error("Element not clickable", {"locator": str(locator)}, exception=e)
            return False
        except Exception as e:
            self.logger.error("Click failed", {"locator": str(locator)}, exception=e)
            raise ElementInteractionError(
                f"Failed to click element: {str(e)}",
                element_info={"locator": str(locator)},
                context={"action": "click"}
            ) from e
    
    async def type_text(
        self, 
        locator: ElementLocator, 
        text: str,
        clear_first: bool = True,
        timeout: Optional[float] = None
    ) -> bool:
        """
        Type text into element.
        
        Args:
            locator: Element locator
            text: Text to type
            clear_first: Clear existing text first
            timeout: Wait timeout
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Wait for element to be visible
            element = self.wait_strategies.wait_for_element_visible(locator, timeout)
            
            # Clear existing text if requested
            if clear_first:
                await asyncio.get_event_loop().run_in_executor(None, element.clear)
            
            # Type text
            await asyncio.get_event_loop().run_in_executor(None, element.send_keys, text)
            
            self.logger.log_element_interaction("type_text", {
                "locator": str(locator),
                "text_length": len(text),
                "clear_first": clear_first
            })
            
            return True
            
        except Exception as e:
            self.logger.error("Type text failed", {
                "locator": str(locator),
                "text": text[:50] + "..." if len(text) > 50 else text
            }, exception=e)
            
            raise ElementInteractionError(
                f"Failed to type text: {str(e)}",
                element_info={"locator": str(locator)},
                context={"action": "type_text", "text": text}
            ) from e
    
    async def select_dropdown(
        self, 
        locator: ElementLocator, 
        value: str,
        by_value: bool = True,
        timeout: Optional[float] = None
    ) -> bool:
        """
        Select option from dropdown.
        
        Args:
            locator: Dropdown element locator
            value: Value to select
            by_value: Select by value (True) or visible text (False)
            timeout: Wait timeout
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Find dropdown element
            element = self.wait_strategies.wait_for_element_visible(locator, timeout)
            select = Select(element)
            
            # Select option
            if by_value:
                await asyncio.get_event_loop().run_in_executor(
                    None, select.select_by_value, value
                )
            else:
                await asyncio.get_event_loop().run_in_executor(
                    None, select.select_by_visible_text, value
                )
            
            self.logger.log_element_interaction("select_dropdown", {
                "locator": str(locator),
                "value": value,
                "by_value": by_value
            })
            
            return True
            
        except Exception as e:
            self.logger.error("Dropdown selection failed", {
                "locator": str(locator),
                "value": value
            }, exception=e)
            return False
    
    async def get_element_text(
        self, 
        locator: ElementLocator, 
        timeout: Optional[float] = None
    ) -> Optional[str]:
        """Get text content of element."""
        try:
            element = self.wait_strategies.wait_for_element_visible(locator, timeout)
            text = element.text
            
            self.logger.debug("Element text retrieved", {
                "locator": str(locator),
                "text_length": len(text)
            })
            
            return text
        except Exception as e:
            self.logger.error("Failed to get element text", {"locator": str(locator)}, exception=e)
            return None
    
    async def get_element_attribute(
        self, 
        locator: ElementLocator, 
        attribute: str,
        timeout: Optional[float] = None
    ) -> Optional[str]:
        """Get attribute value of element."""
        try:
            element = self.wait_strategies.wait_for_element_present(locator, timeout)
            value = element.get_attribute(attribute)
            
            self.logger.debug("Element attribute retrieved", {
                "locator": str(locator),
                "attribute": attribute,
                "value": str(value)[:100] if value else None
            })
            
            return value
        except Exception as e:
            self.logger.error("Failed to get element attribute", {
                "locator": str(locator),
                "attribute": attribute
            }, exception=e)
            return None
    
    # Wait methods
    async def wait_for_element(
        self, 
        locator: ElementLocator, 
        timeout: Optional[float] = None
    ) -> Optional[WebElement]:
        """Wait for element to be present and return it."""
        return await self.find_element(locator, timeout)
    
    async def wait_for_element_clickable(
        self, 
        locator: ElementLocator, 
        timeout: Optional[float] = None
    ) -> Optional[WebElement]:
        """Wait for element to be clickable."""
        try:
            return self.wait_strategies.wait_for_element_clickable(locator, timeout)
        except BrowserTimeoutError:
            return None
    
    async def wait_for_text_in_element(
        self, 
        locator: ElementLocator, 
        text: str,
        timeout: Optional[float] = None
    ) -> bool:
        """Wait for specific text to appear in element."""
        try:
            self.wait_strategies.wait_for_text_in_element(locator, text, timeout)
            return True
        except BrowserTimeoutError:
            return False
    
    async def wait_for_url_contains(
        self, 
        url_fragment: str, 
        timeout: Optional[float] = None
    ) -> bool:
        """Wait for URL to contain specific fragment."""
        try:
            self.wait_strategies.wait_for_url_contains(url_fragment, timeout)
            return True
        except BrowserTimeoutError:
            return False
    
    async def wait_for_custom_condition(
        self, 
        condition: Callable, 
        timeout: Optional[float] = None
    ) -> Any:
        """Wait for custom condition."""
        return await self.wait_strategies.async_wait_for_condition(condition, timeout)
    
    # Page information methods
    async def get_current_url(self) -> str:
        """Get current page URL."""
        return self.driver.current_url
    
    async def get_title(self) -> str:
        """Get page title."""
        return self.driver.title
    
    async def get_page_source(self) -> str:
        """Get page HTML source."""
        return self.driver.page_source
    
    async def get_page_info(self) -> PageInfo:
        """Get comprehensive page information."""
        try:
            url = self.driver.current_url
            title = self.driver.title
            source = self.driver.page_source
            timestamp = time.time()
            
            # Additional metadata
            metadata = {
                "session_id": self.session_id,
                "user_agent": await self.execute_script("return navigator.userAgent;"),
                "viewport": await self.execute_script(
                    "return {width: window.innerWidth, height: window.innerHeight};"
                ),
                "document_ready_state": await self.execute_script("return document.readyState;"),
                "cookies_count": len(self.driver.get_cookies()),
                "local_storage_keys": await self.execute_script(
                    "return Object.keys(localStorage).length;"
                ) if await self._is_local_storage_available() else 0
            }
            
            page_info = PageInfo(
                url=url,
                title=title,
                source=source,
                timestamp=timestamp,
                metadata=metadata
            )
            
            self.logger.debug("Page info retrieved", {
                "url": url,
                "title": title[:100],
                "source_length": len(source),
                "metadata_keys": list(metadata.keys())
            })
            
            return page_info
            
        except Exception as e:
            self.logger.error("Failed to get page info", exception=e)
            raise SessionError(f"Failed to get page info: {str(e)}", self.session_id) from e
    
    # Cookie and storage methods
    async def get_cookies(self) -> List[Dict[str, Any]]:
        """Get all cookies."""
        try:
            cookies = self.driver.get_cookies()
            self.logger.debug("Cookies retrieved", {"count": len(cookies)})
            return cookies
        except Exception as e:
            self.logger.error("Failed to get cookies", exception=e)
            return []
    
    async def add_cookie(self, cookie_dict: Dict[str, Any]) -> bool:
        """Add cookie."""
        try:
            self.driver.add_cookie(cookie_dict)
            self.logger.debug("Cookie added", {"name": cookie_dict.get("name")})
            return True
        except Exception as e:
            self.logger.error("Failed to add cookie", {"cookie": cookie_dict}, exception=e)
            return False
    
    async def delete_cookie(self, name: str) -> bool:
        """Delete cookie by name."""
        try:
            self.driver.delete_cookie(name)
            self.logger.debug("Cookie deleted", {"name": name})
            return True
        except Exception as e:
            self.logger.error("Failed to delete cookie", {"name": name}, exception=e)
            return False
    
    async def clear_cookies(self) -> bool:
        """Clear all cookies."""
        try:
            self.driver.delete_all_cookies()
            self.logger.debug("All cookies cleared")
            return True
        except Exception as e:
            self.logger.error("Failed to clear cookies", exception=e)
            return False
    
    # JavaScript execution
    async def execute_script(self, script: str, *args) -> Any:
        """Execute JavaScript code."""
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None, self.driver.execute_script, script, *args
            )
            self.logger.debug("Script executed", {
                "script": script[:100] + "..." if len(script) > 100 else script
            })
            return result
        except Exception as e:
            self.logger.error("Script execution failed", {"script": script}, exception=e)
            raise SessionError(f"Script execution failed: {str(e)}", self.session_id) from e
    
    async def execute_async_script(self, script: str, *args) -> Any:
        """Execute asynchronous JavaScript code."""
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                None, self.driver.execute_async_script, script, *args
            )
            self.logger.debug("Async script executed")
            return result
        except Exception as e:
            self.logger.error("Async script execution failed", {"script": script}, exception=e)
            raise SessionError(f"Async script execution failed: {str(e)}", self.session_id) from e
    
    # Window management
    async def get_window_size(self) -> WindowSize:
        """Get current window size."""
        size = self.driver.get_window_size()
        return (size["width"], size["height"])
    
    async def set_window_size(self, width: int, height: int) -> bool:
        """Set window size."""
        try:
            self.driver.set_window_size(width, height)
            self.logger.debug("Window size set", {"width": width, "height": height})
            return True
        except Exception as e:
            self.logger.error("Failed to set window size", {"width": width, "height": height}, exception=e)
            return False
    
    # Screenshot
    async def take_screenshot(self, file_path: Optional[str] = None) -> Union[str, bytes]:
        """Take screenshot."""
        try:
            screenshot_data = await asyncio.get_event_loop().run_in_executor(
                None, self.driver.get_screenshot_as_png
            )
            
            if file_path:
                with open(file_path, 'wb') as f:
                    f.write(screenshot_data)
                self.logger.debug("Screenshot saved", {"file_path": file_path})
                return file_path
            else:
                self.logger.debug("Screenshot taken", {"size": len(screenshot_data)})
                return screenshot_data
                
        except Exception as e:
            self.logger.error("Failed to take screenshot", exception=e)
            raise SessionError(f"Failed to take screenshot: {str(e)}", self.session_id) from e
    
    # Private helper methods
    async def _wait_for_page_ready(self, timeout: Optional[float] = None) -> None:
        """Wait for page to be fully loaded."""
        timeout = timeout or self.config.page_load_timeout
        
        try:
            # Wait for DOM ready
            self.wait_strategies.wait_for_dom_ready(timeout / 3)
            
            # Wait for AJAX if jQuery is available
            try:
                self.wait_strategies.wait_for_ajax_complete(timeout / 3)
            except BrowserTimeoutError:
                # jQuery not available or AJAX not complete, continue
                pass
            
            # Additional wait for dynamic content
            await asyncio.sleep(0.5)
            
        except Exception as e:
            self.logger.warning("Page ready wait failed", exception=e)
    
    async def _is_local_storage_available(self) -> bool:
        """Check if localStorage is available."""
        try:
            result = await self.execute_script("return typeof(Storage) !== 'undefined';")
            return bool(result)
        except:
            return False
    
    # Session lifecycle
    async def close(self) -> None:
        """Close session and cleanup."""
        if not self.is_active:
            return
        
        try:
            self.logger.info("Closing session")
            self.is_active = False
            
            # Session is closed by the controller, not here
            # The WebDriver instance is shared and managed at controller level
            
        except Exception as e:
            self.logger.error("Error closing session", exception=e)
    
    def __del__(self):
        """Destructor."""
        if self.is_active:
            try:
                # Mark as inactive to prevent further use
                self.is_active = False
            except:
                pass
