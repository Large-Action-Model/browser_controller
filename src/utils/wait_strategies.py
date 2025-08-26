"""Wait strategies for dynamic content loading."""

import time
import asyncio
from typing import Callable, Any, Optional, Union
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from ..types import ElementLocatorType, ElementLocator
from ..utils.exceptions import TimeoutError as BrowserTimeoutError, ElementNotFoundError


class WaitStrategies:
    """Collection of wait strategies for browser automation."""
    
    def __init__(self, driver: WebDriver, default_timeout: float = 30.0):
        self.driver = driver
        self.default_timeout = default_timeout
        self.wait = WebDriverWait(driver, default_timeout)
    
    def _convert_locator(self, locator: ElementLocator) -> tuple:
        """Convert our locator format to Selenium By format."""
        if isinstance(locator, tuple):
            locator_type, locator_value = locator
            by_mapping = {
                ElementLocatorType.ID: By.ID,
                ElementLocatorType.NAME: By.NAME,
                ElementLocatorType.CLASS_NAME: By.CLASS_NAME,
                ElementLocatorType.TAG_NAME: By.TAG_NAME,
                ElementLocatorType.CSS_SELECTOR: By.CSS_SELECTOR,
                ElementLocatorType.XPATH: By.XPATH,
                ElementLocatorType.LINK_TEXT: By.LINK_TEXT,
                ElementLocatorType.PARTIAL_LINK_TEXT: By.PARTIAL_LINK_TEXT,
            }
            return by_mapping[locator_type], locator_value
        elif isinstance(locator, dict):
            # Assume it's a CSS selector if dict format
            return By.CSS_SELECTOR, list(locator.values())[0]
        else:
            # Assume it's a CSS selector string
            return By.CSS_SELECTOR, str(locator)
    
    def wait_for_element_present(self, locator: ElementLocator, timeout: Optional[float] = None) -> WebElement:
        """Wait for element to be present in DOM."""
        timeout = timeout or self.default_timeout
        by, value = self._convert_locator(locator)
        
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.presence_of_element_located((by, value)))
            return element
        except TimeoutException as e:
            raise BrowserTimeoutError(
                f"Element not found within {timeout} seconds",
                timeout_duration=timeout,
                context={"locator": locator, "by": by.name, "value": value}
            ) from e
    
    def wait_for_element_visible(self, locator: ElementLocator, timeout: Optional[float] = None) -> WebElement:
        """Wait for element to be visible."""
        timeout = timeout or self.default_timeout
        by, value = self._convert_locator(locator)
        
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.visibility_of_element_located((by, value)))
            return element
        except TimeoutException as e:
            raise BrowserTimeoutError(
                f"Element not visible within {timeout} seconds",
                timeout_duration=timeout,
                context={"locator": locator, "by": by.name, "value": value}
            ) from e
    
    def wait_for_element_clickable(self, locator: ElementLocator, timeout: Optional[float] = None) -> WebElement:
        """Wait for element to be clickable."""
        timeout = timeout or self.default_timeout
        by, value = self._convert_locator(locator)
        
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.element_to_be_clickable((by, value)))
            return element
        except TimeoutException as e:
            raise BrowserTimeoutError(
                f"Element not clickable within {timeout} seconds",
                timeout_duration=timeout,
                context={"locator": locator, "by": by.name, "value": value}
            ) from e
    
    def wait_for_elements(self, locator: ElementLocator, min_count: int = 1, timeout: Optional[float] = None) -> list:
        """Wait for multiple elements to be present."""
        timeout = timeout or self.default_timeout
        by, value = self._convert_locator(locator)
        
        try:
            wait = WebDriverWait(self.driver, timeout)
            elements = wait.until(lambda driver: driver.find_elements(by, value))
            if len(elements) < min_count:
                raise ElementNotFoundError(
                    f"Expected at least {min_count} elements, found {len(elements)}",
                    locator=str(locator)
                )
            return elements
        except TimeoutException as e:
            raise BrowserTimeoutError(
                f"Elements not found within {timeout} seconds",
                timeout_duration=timeout,
                context={"locator": locator, "min_count": min_count}
            ) from e
    
    def wait_for_text_in_element(self, locator: ElementLocator, text: str, timeout: Optional[float] = None) -> WebElement:
        """Wait for specific text to appear in element."""
        timeout = timeout or self.default_timeout
        by, value = self._convert_locator(locator)
        
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.text_to_be_present_in_element((by, value), text))
            return self.driver.find_element(by, value)
        except TimeoutException as e:
            raise BrowserTimeoutError(
                f"Text '{text}' not found in element within {timeout} seconds",
                timeout_duration=timeout,
                context={"locator": locator, "expected_text": text}
            ) from e
    
    def wait_for_url_contains(self, url_fragment: str, timeout: Optional[float] = None) -> str:
        """Wait for URL to contain specific fragment."""
        timeout = timeout or self.default_timeout
        
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.url_contains(url_fragment))
            return self.driver.current_url
        except TimeoutException as e:
            raise BrowserTimeoutError(
                f"URL did not contain '{url_fragment}' within {timeout} seconds",
                timeout_duration=timeout,
                context={"url_fragment": url_fragment, "current_url": self.driver.current_url}
            ) from e
    
    def wait_for_page_title(self, title: str, timeout: Optional[float] = None) -> str:
        """Wait for page title to match."""
        timeout = timeout or self.default_timeout
        
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.title_is(title))
            return self.driver.title
        except TimeoutException as e:
            raise BrowserTimeoutError(
                f"Page title did not match '{title}' within {timeout} seconds",
                timeout_duration=timeout,
                context={"expected_title": title, "current_title": self.driver.title}
            ) from e
    
    def wait_for_custom_condition(self, condition: Callable, timeout: Optional[float] = None, poll_frequency: float = 0.5) -> Any:
        """Wait for custom condition to be met."""
        timeout = timeout or self.default_timeout
        
        try:
            wait = WebDriverWait(self.driver, timeout, poll_frequency)
            return wait.until(condition)
        except TimeoutException as e:
            raise BrowserTimeoutError(
                f"Custom condition not met within {timeout} seconds",
                timeout_duration=timeout,
                context={"condition": str(condition)}
            ) from e
    
    def wait_for_ajax_complete(self, timeout: Optional[float] = None) -> bool:
        """Wait for AJAX requests to complete (jQuery required on page)."""
        timeout = timeout or self.default_timeout
        
        def ajax_complete(driver):
            try:
                return driver.execute_script("return jQuery.active == 0")
            except:
                # jQuery not available, assume AJAX is complete
                return True
        
        try:
            wait = WebDriverWait(self.driver, timeout)
            return wait.until(ajax_complete)
        except TimeoutException as e:
            raise BrowserTimeoutError(
                f"AJAX requests did not complete within {timeout} seconds",
                timeout_duration=timeout
            ) from e
    
    def wait_for_dom_ready(self, timeout: Optional[float] = None) -> bool:
        """Wait for DOM to be ready."""
        timeout = timeout or self.default_timeout
        
        def dom_ready(driver):
            return driver.execute_script("return document.readyState") == "complete"
        
        try:
            wait = WebDriverWait(self.driver, timeout)
            return wait.until(dom_ready)
        except TimeoutException as e:
            raise BrowserTimeoutError(
                f"DOM not ready within {timeout} seconds",
                timeout_duration=timeout
            ) from e
    
    async def async_wait_for_condition(self, condition: Callable, timeout: Optional[float] = None, poll_interval: float = 0.1) -> Any:
        """Asynchronously wait for a condition to be met."""
        timeout = timeout or self.default_timeout
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                result = condition()
                if result:
                    return result
            except Exception:
                pass
            
            await asyncio.sleep(poll_interval)
        
        raise BrowserTimeoutError(
            f"Async condition not met within {timeout} seconds",
            timeout_duration=timeout
        )
    
    def smart_wait(self, locator: ElementLocator, timeout: Optional[float] = None) -> WebElement:
        """Smart wait that tries multiple strategies."""
        timeout = timeout or self.default_timeout
        
        # Try clickable first (most restrictive)
        try:
            return self.wait_for_element_clickable(locator, timeout=timeout/3)
        except BrowserTimeoutError:
            pass
        
        # Try visible next
        try:
            return self.wait_for_element_visible(locator, timeout=timeout/3)
        except BrowserTimeoutError:
            pass
        
        # Finally try just present
        return self.wait_for_element_present(locator, timeout=timeout/3)
