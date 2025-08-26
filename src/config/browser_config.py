"""Browser configuration management using Pydantic for validation."""

import os
import json
from typing import Optional, Dict, Any, List
from pathlib import Path
from pydantic import BaseModel, Field, validator
from dotenv import load_dotenv

from ..types import (
    BrowserType, ViewportConfig, ProxyConfig, MobileEmulation, 
    AuthenticationConfig, BrowserCapabilities, WaitStrategy
)


class BrowserConfig(BaseModel):
    """Complete browser configuration with validation."""
    
    # Basic browser settings
    browser_type: BrowserType = Field(default=BrowserType.CHROME, description="Browser type to use")
    headless: bool = Field(default=True, description="Run browser in headless mode")
    window_size: tuple[int, int] = Field(default=(1920, 1080), description="Browser window size")
    
    # Timeouts and waits
    implicit_wait: float = Field(default=10.0, ge=0, le=60, description="Implicit wait timeout in seconds")
    page_load_timeout: float = Field(default=30.0, ge=5, le=120, description="Page load timeout in seconds")
    script_timeout: float = Field(default=30.0, ge=5, le=120, description="Script execution timeout in seconds")
    
    # Wait strategy
    wait_strategy: WaitStrategy = Field(default=WaitStrategy.NORMAL, description="Page load wait strategy")
    
    # Advanced settings
    proxy: Optional[ProxyConfig] = Field(default=None, description="Proxy configuration")
    mobile_emulation: Optional[MobileEmulation] = Field(default=None, description="Mobile device emulation")
    viewport: Optional[ViewportConfig] = Field(default=None, description="Custom viewport configuration")
    
    # Authentication
    authentication: Optional[AuthenticationConfig] = Field(default=None, description="Authentication configuration")
    
    # Browser capabilities
    capabilities: BrowserCapabilities = Field(default_factory=BrowserCapabilities, description="Browser capabilities")
    
    # Custom arguments and preferences
    browser_args: List[str] = Field(default_factory=list, description="Additional browser arguments")
    prefs: Dict[str, Any] = Field(default_factory=dict, description="Browser preferences")
    
    # User agent
    user_agent: Optional[str] = Field(default=None, description="Custom user agent string")
    
    # Downloads and file handling
    download_directory: Optional[Path] = Field(default=None, description="Default download directory")
    
    # Security settings
    ignore_certificate_errors: bool = Field(default=False, description="Ignore SSL certificate errors")
    disable_web_security: bool = Field(default=False, description="Disable web security (use with caution)")
    
    # Performance settings
    disable_images: bool = Field(default=False, description="Disable image loading for faster browsing")
    disable_javascript: bool = Field(default=False, description="Disable JavaScript execution")
    disable_css: bool = Field(default=False, description="Disable CSS loading")
    
    # Extension settings
    extensions: List[str] = Field(default_factory=list, description="Browser extensions to load")
    
    class Config:
        use_enum_values = False  # Keep enum objects, don't convert to values
        arbitrary_types_allowed = True
    
    @validator('window_size')
    def validate_window_size(cls, v):
        """Validate window size dimensions."""
        width, height = v
        if width < 320 or width > 3840:
            raise ValueError("Window width must be between 320 and 3840 pixels")
        if height < 240 or height > 2160:
            raise ValueError("Window height must be between 240 and 2160 pixels")
        return v
    
    @validator('download_directory')
    def validate_download_directory(cls, v):
        """Ensure download directory exists."""
        if v is not None:
            path = Path(v)
            path.mkdir(parents=True, exist_ok=True)
        return v
    
    @validator('extensions')
    def validate_extensions(cls, v):
        """Validate extension paths exist."""
        for ext_path in v:
            if not Path(ext_path).exists():
                raise ValueError(f"Extension path does not exist: {ext_path}")
        return v


class ConfigManager:
    """Configuration manager for Browser Controller."""
    
    def __init__(self, config_file: Optional[str] = None, load_env: bool = True):
        """Initialize configuration manager.
        
        Args:
            config_file: Path to JSON configuration file
            load_env: Whether to load environment variables
        """
        self.config_file = config_file
        self.config: BrowserConfig = self._load_config(load_env)
    
    def _load_config(self, load_env: bool) -> BrowserConfig:
        """Load configuration from multiple sources."""
        # Load environment variables
        if load_env:
            load_dotenv()
        
        # Start with default config
        config_dict = {}
        
        # Load from file if specified
        if self.config_file and Path(self.config_file).exists():
            with open(self.config_file, 'r') as f:
                file_config = json.load(f)
                config_dict.update(file_config)
        
        # Override with environment variables
        env_config = self._load_from_environment()
        config_dict.update(env_config)
        
        # Create and validate config
        return BrowserConfig(**config_dict)
    
    def _load_from_environment(self) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        env_config = {}
        
        # Browser type
        if browser_type := os.getenv('BROWSER_TYPE'):
            env_config['browser_type'] = browser_type
        
        # Headless mode
        if headless := os.getenv('BROWSER_HEADLESS'):
            env_config['headless'] = headless.lower() == 'true'
        
        # Window size
        if window_width := os.getenv('BROWSER_WIDTH'):
            width = int(window_width)
            height = int(os.getenv('BROWSER_HEIGHT', 1080))
            env_config['window_size'] = (width, height)
        
        # Timeouts
        if implicit_wait := os.getenv('BROWSER_IMPLICIT_WAIT'):
            env_config['implicit_wait'] = float(implicit_wait)
        
        if page_load_timeout := os.getenv('BROWSER_PAGE_LOAD_TIMEOUT'):
            env_config['page_load_timeout'] = float(page_load_timeout)
        
        # Proxy settings
        if proxy_server := os.getenv('BROWSER_PROXY_SERVER'):
            proxy_config = {
                'server': proxy_server,
                'port': int(os.getenv('BROWSER_PROXY_PORT', 8080))
            }
            if proxy_user := os.getenv('BROWSER_PROXY_USERNAME'):
                proxy_config['username'] = proxy_user
            if proxy_pass := os.getenv('BROWSER_PROXY_PASSWORD'):
                proxy_config['password'] = proxy_pass
            
            env_config['proxy'] = ProxyConfig(**proxy_config)
        
        # User agent
        if user_agent := os.getenv('BROWSER_USER_AGENT'):
            env_config['user_agent'] = user_agent
        
        # Download directory
        if download_dir := os.getenv('BROWSER_DOWNLOAD_DIR'):
            env_config['download_directory'] = Path(download_dir)
        
        return env_config
    
    def get_config(self) -> BrowserConfig:
        """Get current configuration."""
        return self.config
    
    def update_config(self, **kwargs) -> None:
        """Update configuration with new values."""
        config_dict = self.config.dict()
        config_dict.update(kwargs)
        self.config = BrowserConfig(**config_dict)
    
    def save_config(self, file_path: Optional[str] = None) -> None:
        """Save configuration to file."""
        target_file = file_path or self.config_file
        if not target_file:
            raise ValueError("No configuration file path specified")
        
        config_dict = self.config.dict(exclude_unset=True)
        
        # Convert Path objects to strings for JSON serialization
        def convert_paths(obj):
            if isinstance(obj, dict):
                return {k: convert_paths(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_paths(item) for item in obj]
            elif isinstance(obj, Path):
                return str(obj)
            return obj
        
        config_dict = convert_paths(config_dict)
        
        # Ensure directory exists
        Path(target_file).parent.mkdir(parents=True, exist_ok=True)
        
        with open(target_file, 'w') as f:
            json.dump(config_dict, f, indent=2, default=str)
    
    def get_browser_options(self) -> Dict[str, Any]:
        """Get browser-specific options for driver initialization."""
        options = {
            'browser_type': self.config.browser_type,
            'headless': self.config.headless,
            'window_size': self.config.window_size,
            'browser_args': self.config.browser_args.copy(),
            'prefs': self.config.prefs.copy(),
        }
        
        # Add proxy settings
        if self.config.proxy:
            options['proxy'] = self.config.proxy
        
        # Add user agent
        if self.config.user_agent:
            options['user_agent'] = self.config.user_agent
        
        # Add mobile emulation
        if self.config.mobile_emulation:
            options['mobile_emulation'] = self.config.mobile_emulation
        
        # Add download directory
        if self.config.download_directory:
            options['download_directory'] = str(self.config.download_directory)
        
        # Add security options
        if self.config.ignore_certificate_errors:
            options['browser_args'].append('--ignore-certificate-errors')
        
        if self.config.disable_web_security:
            options['browser_args'].append('--disable-web-security')
        
        # Add performance options
        if self.config.disable_images:
            options['prefs']['profile.managed_default_content_settings.images'] = 2
        
        return options
    
    def get_wait_config(self) -> Dict[str, float]:
        """Get wait configuration for WebDriver."""
        return {
            'implicit_wait': self.config.implicit_wait,
            'page_load_timeout': self.config.page_load_timeout,
            'script_timeout': self.config.script_timeout,
        }
