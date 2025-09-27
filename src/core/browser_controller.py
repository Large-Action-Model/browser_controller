"""
Main Browser Controller class that orchestrates browser automation.

This is the primary interface for the Browser Controller component of the LAM system.
It handles browser lifecycle, session management, and provides high-level automation methods.
"""

import asyncio
import time
import uuid
from typing import Optional, Dict, Any, List, Union, AsyncContextManager
from contextlib import asynccontextmanager
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import WebDriverException

from ..config.browser_config import BrowserConfig, ConfigManager
from ..session.browser_session import BrowserSession
from ..session.session_manager import SessionManager
from ..core.browser_factory import BrowserFactory
from ..utils import get_logger, BrowserControllerError, BrowserLaunchError, SessionError
from ..types import (
    BrowserType, SessionMetadata, NavigationResult, PageInfo, 
    ElementLocator, Coordinates, WindowSize
)


class BrowserController:
    """
    Main Browser Controller class providing high-level browser automation interface.
    
    This class is responsible for:
    - Browser lifecycle management (launch, close)  
    - Session creation and management
    - High-level navigation and interaction methods
    - Resource cleanup and error handling
    - Integration with other LAM components
    """
    
    def __init__(self, config: Optional[BrowserConfig] = None, config_file: Optional[str] = None):
        """
        Initialize Browser Controller.
        
        Args:
            config: Browser configuration object
            config_file: Path to configuration file
        """
        # Initialize configuration
        if config:
            self.config = config
        else:
            config_manager = ConfigManager(config_file)
            self.config = config_manager.get_config()
        
        # Initialize components
        self.logger = get_logger("BrowserController")
        self.browser_factory = BrowserFactory(self.config)
        self.session_manager = SessionManager()
        
        # Browser state
        self._driver: Optional[WebDriver] = None
        self._is_launched = False
        self._sessions: Dict[str, BrowserSession] = {}
        
        self.logger.info("Browser Controller initialized", {
            "browser_type": self.config.browser_type.value if hasattr(self.config.browser_type, 'value') else str(self.config.browser_type),
            "headless": self.config.headless,
            "window_size": self.config.window_size
        })
    
    async def launch(self) -> None:
        """Launch browser instance."""
        if self._is_launched:
            self.logger.warning("Browser already launched")
            return
        
        try:
            self.logger.info("Launching browser", {"browser_type": self.config.browser_type.value if hasattr(self.config.browser_type, 'value') else str(self.config.browser_type)})
            start_time = time.time()
            
            # Create browser driver
            self._driver = await asyncio.get_event_loop().run_in_executor(
                None, self.browser_factory.create_driver
            )
            
            # Configure timeouts
            self._driver.implicitly_wait(self.config.implicit_wait)
            self._driver.set_page_load_timeout(self.config.page_load_timeout)
            self._driver.set_script_timeout(self.config.script_timeout)
            
            # Set window size if not headless
            if not self.config.headless:
                self._driver.set_window_size(*self.config.window_size)
            
            self._is_launched = True
            launch_time = time.time() - start_time
            
            self.logger.info("Browser launched successfully", {
                "launch_time": launch_time,
                "session_id": self._driver.session_id
            })
            
        except Exception as e:
            self.logger.error("Failed to launch browser", exception=e)
            raise BrowserLaunchError(
                f"Failed to launch {self.config.browser_type.value if hasattr(self.config.browser_type, 'value') else str(self.config.browser_type)} browser: {str(e)}",
                browser_type=str(self.config.browser_type),
                context={"config": self.config.dict()}
            ) from e
    
    async def close(self) -> None:
        """Close browser and cleanup resources."""
        if not self._is_launched:
            return
        
        try:
            self.logger.info("Closing browser")
            
            # Close all sessions first
            await self._close_all_sessions()
            
            # Quit browser driver
            if self._driver:
                await asyncio.get_event_loop().run_in_executor(None, self._driver.quit)
                self._driver = None
            
            self._is_launched = False
            self.logger.info("Browser closed successfully")
            
        except Exception as e:
            self.logger.error("Error closing browser", exception=e)
            raise BrowserControllerError(
                f"Error closing browser: {str(e)}",
                context={"browser_type": str(self.config.browser_type)}
            ) from e
    
    async def _close_all_sessions(self) -> None:
        """Close all active sessions."""
        for session_id, session in self._sessions.items():
            try:
                await session.close()
            except Exception as e:
                self.logger.warning(f"Error closing session {session_id}", exception=e)
        
        self._sessions.clear()
    
    @asynccontextmanager
    async def new_session(self, session_config: Optional[Dict[str, Any]] = None):
        """
        Create a new browser session with automatic cleanup.
        
        Args:
            session_config: Optional session-specific configuration
            
        Returns:
            Browser session context manager
            
        Usage:
            async with controller.new_session() as session:
                await session.navigate_to("https://example.com")
                title = await session.get_title()
        """
        if not self._is_launched:
            await self.launch()
        
        session_id = str(uuid.uuid4())
        
        try:
            # Create session
            session = BrowserSession(
                driver=self._driver,
                session_id=session_id,
                config=self.config,
                session_config=session_config or {}
            )
            
            # Register session
            self._sessions[session_id] = session
            await self.session_manager.register_session(session)
            
            self.logger.log_session_event("session_created", session_id, {
                "total_sessions": len(self._sessions)
            })
            
            yield session
            
        except Exception as e:
            self.logger.error(f"Session error: {str(e)}", exception=e)
            raise SessionError(
                f"Session {session_id} error: {str(e)}",
                session_id=session_id
            ) from e
        
        finally:
            # Cleanup session
            if session_id in self._sessions:
                try:
                    await self._sessions[session_id].close()
                    del self._sessions[session_id]
                    await self.session_manager.unregister_session(session_id)
                    
                    self.logger.log_session_event("session_closed", session_id, {
                        "remaining_sessions": len(self._sessions)
                    })
                except Exception as e:
                    self.logger.warning(f"Error cleaning up session {session_id}", exception=e)
    
    # Convenience methods that delegate to session
    async def navigate_to(self, url: str, wait_for_load: bool = True, timeout: Optional[float] = None) -> NavigationResult:
        """
        Navigate to URL using a temporary session.
        
        Args:
            url: Target URL
            wait_for_load: Whether to wait for page load completion
            timeout: Navigation timeout
            
        Returns:
            Navigation result
        """
        async with self.new_session() as session:
            return await session.navigate_to(url, wait_for_load, timeout)
    
    async def get_page_info(self) -> PageInfo:
        """Get current page information using a temporary session."""
        async with self.new_session() as session:
            return await session.get_page_info()
    
    async def get_dom(self) -> str:
        """
        Get the complete DOM (HTML source) of the current page.
        
        Returns:
            Complete HTML source code as string for DOM analyzer component
        """
        if not self._is_launched:
            await self.launch()
        
        try:
            dom_source = await asyncio.get_event_loop().run_in_executor(
                None, lambda: self._driver.page_source
            )
            
            self.logger.info("DOM retrieved", {
                "dom_size": len(dom_source),
                "current_url": self._driver.current_url
            })
            
            return dom_source
            
        except Exception as e:
            self.logger.error("Error retrieving DOM", exception=e)
            raise BrowserControllerError(f"Failed to retrieve DOM: {str(e)}") from e
    
    async def find_element(self, locator: ElementLocator, timeout: Optional[float] = None):
        """Find element using a temporary session."""
        async with self.new_session() as session:
            return await session.find_element(locator, timeout)
    
    async def click_element(self, locator: ElementLocator, timeout: Optional[float] = None) -> bool:
        """Click element using a temporary session."""
        async with self.new_session() as session:
            return await session.click_element(locator, timeout)
    
    async def type_text(self, locator: ElementLocator, text: str, clear_first: bool = True, timeout: Optional[float] = None) -> bool:
        """Type text into element using a temporary session."""
        async with self.new_session() as session:
            return await session.type_text(locator, text, clear_first, timeout)
    
    async def wait_for_element(self, locator: ElementLocator, timeout: Optional[float] = None):
        """Wait for element using a temporary session.""" 
        async with self.new_session() as session:
            return await session.wait_for_element(locator, timeout)
    
    # Browser management methods
    def is_launched(self) -> bool:
        """Check if browser is launched."""
        return self._is_launched
    
    def get_active_sessions(self) -> List[str]:
        """Get list of active session IDs."""
        return list(self._sessions.keys())
    
    def get_session_count(self) -> int:
        """Get number of active sessions."""
        return len(self._sessions)
    
    def get_session(self, session_id: str) -> Optional[BrowserSession]:
        """Get session by ID."""
        return self._sessions.get(session_id)
    
    async def create_session(self, session_config: Optional[Dict[str, Any]] = None) -> BrowserSession:
        """
        Create a new browser session.
        
        Args:
            session_config: Optional session-specific configuration
            
        Returns:
            BrowserSession instance
        """
        if not self._is_launched:
            await self.launch()
        
        session_id = str(uuid.uuid4())
        
        try:
            # Create session
            session = BrowserSession(
                driver=self._driver,
                session_id=session_id,
                config=self.config,
                session_config=session_config or {}
            )
            
            # Register session
            self._sessions[session_id] = session
            await self.session_manager.register_session(session)
            
            self.logger.log_session_event("session_created", session_id, {
                "total_sessions": len(self._sessions)
            })
            
            return session
            
        except Exception as e:
            self.logger.error(f"Session error: {str(e)}", exception=e)
            raise SessionError(
                f"Session {session_id} error: {str(e)}",
                session_id=session_id
            ) from e
    
    async def close_session(self, session_id: str) -> bool:
        """
        Close a browser session.
        
        Args:
            session_id: ID of session to close
            
        Returns:
            True if session was closed successfully
        """
        if session_id not in self._sessions:
            return False
        
        try:
            await self._sessions[session_id].close()
            del self._sessions[session_id]
            await self.session_manager.unregister_session(session_id)
            
            self.logger.log_session_event("session_closed", session_id, {
                "remaining_sessions": len(self._sessions)
            })
            
            return True
            
        except Exception as e:
            self.logger.warning(f"Error closing session {session_id}", exception=e)
            return False
    
    async def get_browser_info(self) -> Dict[str, Any]:
        """Get browser information and capabilities."""
        if not self._is_launched:
            await self.launch()
        
        try:
            capabilities = self._driver.capabilities
            return {
                "browser_name": capabilities.get("browserName"),
                "browser_version": capabilities.get("browserVersion"),
                "platform": capabilities.get("platformName"), 
                "driver_version": capabilities.get("version"),
                "session_id": self._driver.session_id,
                "current_url": self._driver.current_url,
                "window_handles": self._driver.window_handles,
                "page_source_length": len(self._driver.page_source),
            }
        except Exception as e:
            self.logger.error("Error getting browser info", exception=e)
            return {}
    
    async def take_screenshot(self, file_path: Optional[str] = None) -> Union[str, bytes]:
        """
        Take screenshot of current page.
        
        Args:
            file_path: Optional path to save screenshot
            
        Returns:
            Screenshot as bytes or file path if saved
        """
        if not self._is_launched:
            await self.launch()
        
        try:
            screenshot_data = self._driver.get_screenshot_as_png()
            
            if file_path:
                with open(file_path, 'wb') as f:
                    f.write(screenshot_data)
                self.logger.info("Screenshot saved", {"file_path": file_path})
                return file_path
            else:
                return screenshot_data
                
        except Exception as e:
            self.logger.error("Error taking screenshot", exception=e)
            raise BrowserControllerError(f"Failed to take screenshot: {str(e)}") from e
    
    def __enter__(self):
        """Synchronous context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Synchronous context manager exit."""
        if self._is_launched:
            # Run cleanup in event loop
            try:
                loop = asyncio.get_event_loop()
                loop.run_until_complete(self.close())
            except RuntimeError:
                # Create new event loop if none exists
                asyncio.run(self.close())
    
    async def __aenter__(self):
        """Asynchronous context manager entry."""
        await self.launch()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Asynchronous context manager exit."""
        await self.close()
    
    def __del__(self):
        """Destructor to ensure cleanup."""
        if self._is_launched:
            try:
                # Attempt emergency cleanup
                if self._driver:
                    self._driver.quit()
            except:
                pass
