"""Browser factory for creating WebDriver instances with proper configuration."""

from typing import Dict, Any, Optional
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
from selenium.webdriver.remote.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from fake_useragent import UserAgent

from ..config.browser_config import BrowserConfig
from ..types import BrowserType, ProxyConfig, MobileEmulation
from ..utils import get_logger, BrowserLaunchError


class BrowserFactory:
    """Factory class for creating configured WebDriver instances."""
    
    def __init__(self, config: BrowserConfig):
        """Initialize browser factory with configuration."""
        self.config = config
        self.logger = get_logger("BrowserFactory")
    
    def create_driver(self) -> WebDriver:
        """Create WebDriver instance based on configuration."""
        try:
            self.logger.info("Creating browser driver", {
                "browser_type": self.config.browser_type.value if hasattr(self.config.browser_type, 'value') else str(self.config.browser_type),
                "headless": self.config.headless
            })
            
            if self.config.browser_type == BrowserType.CHROME:
                return self._create_chrome_driver()
            elif self.config.browser_type == BrowserType.FIREFOX:
                return self._create_firefox_driver()
            elif self.config.browser_type == BrowserType.EDGE:
                return self._create_edge_driver()
            else:
                raise BrowserLaunchError(
                    f"Unsupported browser type: {str(self.config.browser_type)}",
                    browser_type=str(self.config.browser_type)
                )
        
        except Exception as e:
            self.logger.error("Failed to create browser driver", exception=e)
            raise BrowserLaunchError(
                f"Failed to create {str(self.config.browser_type)} driver: {str(e)}",
                browser_type=str(self.config.browser_type),
                context={"config": self.config.dict()}
            ) from e
    
    def _create_chrome_driver(self) -> webdriver.Chrome:
        """Create Chrome WebDriver instance."""
        # Setup Chrome options
        options = ChromeOptions()
        
        # Basic options
        if self.config.headless:
            options.add_argument("--headless")
        
        # Window size
        options.add_argument(f"--window-size={self.config.window_size[0]},{self.config.window_size[1]}")
        
        # User agent
        user_agent = self.config.user_agent or self._get_random_user_agent()
        options.add_argument(f"--user-agent={user_agent}")
        
        # Security options
        if self.config.ignore_certificate_errors:
            options.add_argument("--ignore-certificate-errors")
            options.add_argument("--ignore-ssl-errors")
            options.add_argument("--ignore-certificate-errors-spki-list")
        
        if self.config.disable_web_security:
            options.add_argument("--disable-web-security")
            options.add_argument("--allow-running-insecure-content")
        
        # Performance options
        if self.config.disable_images:
            prefs = {"profile.managed_default_content_settings.images": 2}
            options.add_experimental_option("prefs", prefs)
        
        # Additional Chrome arguments
        chrome_args = [
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--disable-extensions",
            "--disable-plugins",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
            "--disable-renderer-backgrounding",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-default-apps",
        ]
        
        for arg in chrome_args + self.config.browser_args:
            options.add_argument(arg)
        
        # Mobile emulation
        if self.config.mobile_emulation:
            mobile_emulation = self._get_mobile_emulation_dict()
            options.add_experimental_option("mobileEmulation", mobile_emulation)
        
        # Proxy configuration
        if self.config.proxy:
            proxy_config = self._get_proxy_config()
            options.add_argument(f"--proxy-server={proxy_config}")
        
        # Preferences
        if self.config.prefs:
            options.add_experimental_option("prefs", self.config.prefs)
        
        # Download directory
        if self.config.download_directory:
            prefs = {
                "download.default_directory": str(self.config.download_directory),
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True
            }
            options.add_experimental_option("prefs", prefs)
        
        # Extensions
        for extension_path in self.config.extensions:
            options.add_extension(extension_path)
        
        # Setup service with driver manager
        service = ChromeService(ChromeDriverManager().install())
        
        return webdriver.Chrome(service=service, options=options)
    
    def _create_firefox_driver(self) -> webdriver.Firefox:
        """Create Firefox WebDriver instance."""
        options = FirefoxOptions()
        
        # Basic options
        if self.config.headless:
            options.add_argument("--headless")
        
        # User agent
        user_agent = self.config.user_agent or self._get_random_user_agent()
        options.set_preference("general.useragent.override", user_agent)
        
        # Window size
        options.add_argument(f"--width={self.config.window_size[0]}")
        options.add_argument(f"--height={self.config.window_size[1]}")
        
        # Security options
        if self.config.ignore_certificate_errors:
            options.set_preference("security.tls.insecure_fallback_hosts", "*")
            options.set_preference("security.tls.version.fallback-limit", 1)
        
        # Performance options
        if self.config.disable_images:
            options.set_preference("permissions.default.image", 2)
        
        if self.config.disable_javascript:
            options.set_preference("javascript.enabled", False)
        
        # Download directory
        if self.config.download_directory:
            options.set_preference("browser.download.dir", str(self.config.download_directory))
            options.set_preference("browser.download.folderList", 2)
            options.set_preference("browser.helperApps.neverAsk.saveToDisk", 
                                 "application/pdf,application/octet-stream")
        
        # Additional Firefox arguments
        for arg in self.config.browser_args:
            options.add_argument(arg)
        
        # Setup service
        service = FirefoxService(GeckoDriverManager().install())
        
        return webdriver.Firefox(service=service, options=options)
    
    def _create_edge_driver(self) -> webdriver.Edge:
        """Create Edge WebDriver instance."""
        options = EdgeOptions()
        
        # Basic options
        if self.config.headless:
            options.add_argument("--headless")
        
        # Window size
        options.add_argument(f"--window-size={self.config.window_size[0]},{self.config.window_size[1]}")
        
        # User agent
        user_agent = self.config.user_agent or self._get_random_user_agent()
        options.add_argument(f"--user-agent={user_agent}")
        
        # Similar to Chrome configuration
        edge_args = [
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--disable-extensions",
        ]
        
        for arg in edge_args + self.config.browser_args:
            options.add_argument(arg)
        
        # Setup service
        service = EdgeService(EdgeChromiumDriverManager().install())
        
        return webdriver.Edge(service=service, options=options)
    
    def _get_random_user_agent(self) -> str:
        """Generate random user agent string."""
        try:
            ua = UserAgent()
            return ua.random
        except Exception:
            # Fallback user agent
            return ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
    
    def _get_mobile_emulation_dict(self) -> Dict[str, Any]:
        """Get mobile emulation configuration dictionary."""
        if not self.config.mobile_emulation:
            return {}
        
        mobile_config = {}
        mobile_emulation = self.config.mobile_emulation
        
        if mobile_emulation.device_name:
            mobile_config["deviceName"] = mobile_emulation.device_name
        else:
            device_metrics = {}
            if mobile_emulation.width and mobile_emulation.height:
                device_metrics["width"] = mobile_emulation.width
                device_metrics["height"] = mobile_emulation.height
            
            if mobile_emulation.pixel_ratio:
                device_metrics["pixelRatio"] = mobile_emulation.pixel_ratio
            
            if device_metrics:
                mobile_config["deviceMetrics"] = device_metrics
            
            if mobile_emulation.user_agent:
                mobile_config["userAgent"] = mobile_emulation.user_agent
        
        return mobile_config
    
    def _get_proxy_config(self) -> str:
        """Get proxy configuration string."""
        if not self.config.proxy:
            return ""
        
        proxy = self.config.proxy
        proxy_string = f"{proxy.protocol}://"
        
        if proxy.username and proxy.password:
            proxy_string += f"{proxy.username}:{proxy.password}@"
        
        proxy_string += f"{proxy.server}:{proxy.port}"
        
        return proxy_string
