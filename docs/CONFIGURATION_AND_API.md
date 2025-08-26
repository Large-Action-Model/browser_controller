## 🔧 Configuration Guide

### Environment Variables

Create a `.env` file in your project root:

```env
# Browser settings
BROWSER_TYPE=chrome
HEADLESS=true
WINDOW_WIDTH=1280
WINDOW_HEIGHT=720

# Timeouts
PAGE_LOAD_TIMEOUT=30
IMPLICIT_WAIT=10

# Logging
LOG_LEVEL=INFO
LOG_ROTATION=10MB
LOG_RETENTION=30

# Proxy (optional)
HTTP_PROXY=http://proxy:8080
HTTPS_PROXY=https://proxy:8080
```

### Configuration File

Create `browser_config.json`:

```json
{
    "browser_type": "chrome",
    "headless": true,
    "window_size": [1280, 720],
    "page_load_timeout": 30,
    "implicit_wait": 10,
    "browser_options": {
        "disable_images": false,
        "disable_javascript": false,
        "user_agent": "LAM-Browser-Controller/1.0"
    },
    "proxy_settings": {
        "http": "http://proxy:8080",
        "https": "https://proxy:8080"
    }
}
```

### Programmatic Configuration

```python
from src.config.browser_config import BrowserConfig
from src.types.browser_types import BrowserType

# Basic configuration
config = BrowserConfig(
    browser_type=BrowserType.CHROME,
    headless=True,
    window_size=(1920, 1080)
)

# Advanced configuration
config = BrowserConfig(
    browser_type=BrowserType.CHROME,
    headless=False,  # Show browser window
    window_size=(1920, 1080),
    page_load_timeout=45,
    implicit_wait=15,
    browser_options={
        "disable_images": True,  # Faster loading
        "disable_javascript": False,
        "user_agent": "LAM-Browser-Controller/1.0"
    },
    proxy_settings={
        "http": "http://proxy:8080",
        "https": "https://proxy:8080"
    }
)
```

## 📖 API Reference

### BrowserController

The main controller class for managing browser instances and sessions.

#### Initialization

```python
# With config object
controller = BrowserController(config=browser_config)

# With config file
controller = BrowserController(config_file="config.json")

# With default configuration
controller = BrowserController()
```

#### Session Management

```python
# Create a session
session = await controller.create_session()

# Create session with custom config
session = await controller.create_session({
    "window_size": (1920, 1080),
    "user_agent": "Custom Agent"
})

# Get session by ID
session = controller.get_session(session_id)

# Close specific session
await controller.close_session(session_id)

# Get all active sessions
session_ids = controller.get_active_sessions()

# Get session count
count = controller.get_session_count()
```

#### Browser Control

```python
# Launch browser manually (usually done automatically)
await controller.launch()

# Close browser
await controller.close()

# Check if browser is running
is_running = controller.is_launched()

# Get browser information
info = await controller.get_browser_info()
```

### BrowserSession

Individual browser session for page interaction.

#### Navigation

```python
# Navigate to URL
result = await session.navigate_to("https://example.com")

# Navigate with custom timeout
result = await session.navigate_to("https://slow-site.com", timeout=60)

# Get current URL
url = await session.get_current_url()

# Get page title
title = await session.get_title()

# Browser history
await session.go_back()
await session.go_forward()
await session.refresh()
```

#### Element Interaction

```python
# Find single element
element = await session.find_element("css-selector")
element = await session.find_element("//xpath")

# Find multiple elements
elements = await session.find_elements(".class-name")

# Click element
success = await session.click_element("button#submit")

# Type text
success = await session.type_text("input[name='username']", "john_doe")

# Clear and type
success = await session.type_text("input", "new text", clear_first=True)

# Get element text
text = await session.get_element_text("h1")

# Get element attribute
value = await session.get_element_attribute("input", "value")

# Check if element is visible/enabled
visible = await session.is_element_visible("div.modal")
enabled = await session.is_element_enabled("button")
```

#### Waiting Strategies

```python
# Wait for element to appear
element = await session.wait_for_element("div.dynamic", timeout=30)

# Wait for element to be clickable
element = await session.wait_for_clickable("button", timeout=10)

# Wait for element to disappear
await session.wait_for_element_to_disappear("div.loading", timeout=30)

# Custom wait condition
from selenium.webdriver.support import expected_conditions as EC
element = await session.wait_for_condition(
    EC.text_to_be_present_in_element(("h1",), "Success"),
    timeout=20
)
```

#### Screenshots

```python
# Full page screenshot
await session.take_screenshot("page.png")

# Element screenshot
await session.take_element_screenshot("div.content", "element.png")

# Screenshot to bytes (for processing)
screenshot_data = await session.take_screenshot()
```

#### Advanced Features

```python
# Execute JavaScript
result = await session.execute_script("return document.title;")

# Cookie management
await session.add_cookie({"name": "session", "value": "abc123"})
cookies = await session.get_cookies()
await session.delete_all_cookies()

# Window management
await session.set_window_size(1920, 1080)
size = await session.get_window_size()

# Form handling
await session.submit_form("form#login")
await session.select_dropdown_option("select[name='country']", "USA")
```

## 🧪 Testing

### Unit Tests

Run the comprehensive unit test suite:

```bash
python test_implementation.py
```

Expected output:
```
✓ Package Structure test PASSED
✓ Browser Controller Creation test PASSED
✓ Configuration Manager test PASSED
✓ Types and Exceptions test PASSED
✓ Logging System test PASSED

Test Results: 5 PASSED, 0 FAILED
🎉 All tests passed! Browser Controller implementation is working correctly.
```

### Integration Tests

Run real browser automation tests:

```bash
python test_browser_automation.py
```

Expected output:
```
✓ Basic Navigation test PASSED
✓ Form Interaction test PASSED
✓ Multiple Sessions test PASSED
✓ Error Handling test PASSED

Test Results: 4 PASSED, 0 FAILED
🎉 All browser automation tests passed!
```

### Custom Tests

Create your own test file:

```python
import asyncio
import pytest
from src.core.browser_controller import BrowserController
from src.config.browser_config import BrowserConfig
from src.types.browser_types import BrowserType

@pytest.mark.asyncio
async def test_custom_automation():
    config = BrowserConfig(
        browser_type=BrowserType.CHROME,
        headless=True
    )
    
    async with BrowserController(config) as controller:
        session = await controller.create_session()
        
        try:
            await session.navigate_to("https://httpbin.org/forms/post")
            
            # Your custom test logic here
            title = await session.get_title()
            assert "httpbin" in title.lower()
            
        finally:
            await controller.close_session(session.session_id)
```

## 📊 Dependencies

### Core Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| selenium | 4.35.0 | WebDriver automation |
| webdriver-manager | 4.0.2 | Automatic driver management |
| pydantic | 2.11.7 | Configuration validation |
| loguru | 0.7.3 | Advanced logging |
| python-dotenv | 1.0.1 | Environment variable loading |

### Development Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| pytest | latest | Testing framework |
| black | latest | Code formatting |
| mypy | latest | Type checking |
| isort | latest | Import sorting |

## 🚀 Performance & Optimization

### Configuration Tips

```python
# For maximum speed (headless)
config = BrowserConfig(
    browser_type=BrowserType.CHROME,
    headless=True,
    browser_options={
        "disable_images": True,
        "disable_javascript": False,  # Keep if needed for functionality
        "disable_plugins": True,
        "disable_extensions": True
    }
)

# For development (visible)
config = BrowserConfig(
    browser_type=BrowserType.CHROME,
    headless=False,
    window_size=(1920, 1080),
    page_load_timeout=30
)

# For production (robust)
config = BrowserConfig(
    browser_type=BrowserType.CHROME,
    headless=True,
    page_load_timeout=60,
    implicit_wait=20,
    browser_options={
        "disable_images": True,
        "user_agent": "Production-Bot/1.0"
    }
)
```

### Resource Management

```python
# Always use context managers
async with BrowserController(config) as controller:
    session = await controller.create_session()
    try:
        # Your automation code
        pass
    finally:
        await controller.close_session(session.session_id)

# Monitor session count
print(f"Active sessions: {controller.get_session_count()}")

# Cleanup when needed
for session_id in controller.get_active_sessions():
    await controller.close_session(session_id)
```

## 🔧 Integration with LAM Systems

### Architecture Integration

```python
class LAMWebAutomation:
    """Example integration with LAM system"""
    
    def __init__(self):
        self.browser_controller = None
        self.action_planner = None     # Your LAM action planner
        self.content_analyzer = None   # Your LAM content analyzer
        self.decision_engine = None    # Your LAM decision engine
    
    async def initialize(self):
        """Initialize LAM components"""
        config = BrowserConfig(
            browser_type=BrowserType.CHROME,
            headless=True,
            page_load_timeout=30
        )
        self.browser_controller = BrowserController(config)
        await self.browser_controller.launch()
    
    async def execute_web_task(self, task_description: str):
        """Execute a high-level web task using LAM components"""
        
        # 1. Plan actions using LAM
        actions = await self.action_planner.plan(task_description)
        
        # 2. Create browser session
        session = await self.browser_controller.create_session()
        
        try:
            # 3. Execute planned actions
            for action in actions:
                if action.type == "navigate":
                    result = await session.navigate_to(action.url)
                    
                elif action.type == "click":
                    success = await session.click_element(action.selector)
                    
                elif action.type == "type":
                    success = await session.type_text(action.selector, action.text)
                    
                elif action.type == "extract":
                    # Extract content for LAM analysis
                    content = await session.get_element_text(action.selector)
                    analysis = await self.content_analyzer.analyze(content)
                    
                elif action.type == "decide":
                    # Make decision based on page state
                    page_info = await session.get_page_info()
                    decision = await self.decision_engine.decide(page_info)
                    
                # Add more action types as needed
                
        finally:
            await self.browser_controller.close_session(session.session_id)
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.browser_controller:
            await self.browser_controller.close()

# Usage
async def main():
    lam_automation = LAMWebAutomation()
    await lam_automation.initialize()
    
    try:
        await lam_automation.execute_web_task(
            "Find and extract product prices from e-commerce site"
        )
    finally:
        await lam_automation.cleanup()

asyncio.run(main())
```

## 🔒 Security Considerations

### Best Practices

```python
# 1. Use browser profiles for isolation
config = BrowserConfig(
    browser_type=BrowserType.CHROME,
    browser_options={
        "user_data_dir": "/tmp/isolated_profile",
        "no_sandbox": False,  # Keep sandboxing enabled
        "disable_web_security": False  # Keep security enabled
    }
)

# 2. Handle credentials securely
import os
username = os.getenv('WEB_USERNAME')  # Never hardcode credentials
password = os.getenv('WEB_PASSWORD')

await session.type_text("input[name='username']", username)
await session.type_text("input[name='password']", password)

# 3. Use proxy for additional security
config = BrowserConfig(
    browser_type=BrowserType.CHROME,
    proxy_settings={
        "http": "http://secure-proxy:8080",
        "https": "https://secure-proxy:8080"
    }
)

# 4. Clean up sensitive data
await session.delete_all_cookies()
await session.execute_script("sessionStorage.clear(); localStorage.clear();")
```

## 📝 Logging and Monitoring

### Log Configuration

```python
from src.utils.logger import get_logger, configure_logging

# Configure logging
configure_logging(
    level="INFO",
    file_rotation="10 MB",
    retention="30 days",
    format="{time} | {level} | {name} | {message}"
)

# Use in your code
logger = get_logger("MyAutomation")
logger.info("Starting automation task", task_id="12345")
logger.error("Failed to find element", selector="button.submit", page_url="https://example.com")
```

### Log Analysis

Logs are saved to:
- `logs/browser_controller_{date}.log` (daily rotation)
- JSON format for structured analysis
- Console output for development

Example log entry:
```json
{
    "timestamp": "2025-08-23T10:39:21.349Z",
    "level": "INFO",
    "logger": "BrowserController",
    "message": "Session created",
    "session_id": "abc123",
    "total_sessions": 3,
    "browser_type": "chrome"
}
```

## 🎯 Example Use Cases

### 1. Data Extraction

```python
async def extract_product_data():
    config = BrowserConfig(browser_type=BrowserType.CHROME, headless=True)
    
    async with BrowserController(config) as controller:
        session = await controller.create_session()
        
        try:
            await session.navigate_to("https://ecommerce-site.com/products")
            
            # Extract all product names and prices
            products = await session.find_elements(".product-item")
            
            data = []
            for product in products:
                name = await session.get_element_text(f"{product} .product-name")
                price = await session.get_element_text(f"{product} .product-price")
                data.append({"name": name, "price": price})
            
            return data
            
        finally:
            await controller.close_session(session.session_id)
```

### 2. Form Automation

```python
async def automate_form_submission():
    config = BrowserConfig(browser_type=BrowserType.CHROME, headless=False)
    
    async with BrowserController(config) as controller:
        session = await controller.create_session()
        
        try:
            await session.navigate_to("https://forms.example.com/contact")
            
            # Fill form fields
            await session.type_text("input[name='name']", "John Doe")
            await session.type_text("input[name='email']", "john@example.com")
            await session.type_text("textarea[name='message']", "Hello from automation!")
            
            # Select dropdown
            await session.select_dropdown_option("select[name='country']", "United States")
            
            # Submit form
            await session.click_element("button[type='submit']")
            
            # Wait for success message
            success_element = await session.wait_for_element(".success-message", timeout=10)
            
            return success_element is not None
            
        finally:
            await controller.close_session(session.session_id)
```

### 3. Testing Automation

```python
async def test_login_flow():
    config = BrowserConfig(browser_type=BrowserType.CHROME, headless=True)
    
    async with BrowserController(config) as controller:
        session = await controller.create_session()
        
        try:
            # Test invalid credentials
            await session.navigate_to("https://app.example.com/login")
            await session.type_text("input[name='username']", "invalid_user")
            await session.type_text("input[name='password']", "wrong_password")
            await session.click_element("button[type='submit']")
            
            # Verify error message appears
            error_element = await session.wait_for_element(".error-message", timeout=5)
            assert error_element is not None, "Error message should appear for invalid credentials"
            
            # Test valid credentials
            await session.type_text("input[name='username']", "valid_user", clear_first=True)
            await session.type_text("input[name='password']", "correct_password", clear_first=True)
            await session.click_element("button[type='submit']")
            
            # Verify redirect to dashboard
            await session.wait_for_element(".dashboard", timeout=10)
            current_url = await session.get_current_url()
            assert "/dashboard" in current_url, "Should redirect to dashboard after login"
            
            return True
            
        finally:
            await controller.close_session(session.session_id)
```

## 🆘 Troubleshooting

### Common Issues

1. **Browser not launching**
   ```python
   # Check if Chrome is installed
   config = BrowserConfig(browser_type=BrowserType.CHROME)
   # Try Firefox as alternative
   config = BrowserConfig(browser_type=BrowserType.FIREFOX)
   ```

2. **Element not found**
   ```python
   # Use explicit waits
   element = await session.wait_for_element("selector", timeout=30)
   
   # Check if element exists first
   element = await session.find_element("selector")
   if element:
       await session.click_element("selector")
   ```

3. **Page load timeout**
   ```python
   config = BrowserConfig(
       page_load_timeout=60,  # Increase timeout
       implicit_wait=15       # Increase implicit wait
   )
   ```

4. **Memory issues with multiple sessions**
   ```python
   # Limit concurrent sessions
   max_sessions = 3
   session_count = controller.get_session_count()
   if session_count >= max_sessions:
       # Wait or close existing sessions
       pass
   ```

### Debug Mode

Enable debug logging:

```python
from src.utils.logger import configure_logging

configure_logging(level="DEBUG")

# Or set environment variable
import os
os.environ["LOG_LEVEL"] = "DEBUG"
```

## 📚 Additional Resources

### Documentation Files
- `API_REFERENCE.md` - Complete API documentation
- `EXAMPLES.md` - More usage examples
- `TROUBLESHOOTING.md` - Detailed troubleshooting guide
- `CHANGELOG.md` - Version history and changes

### External Links
- [Selenium Documentation](https://selenium-python.readthedocs.io/)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)
- [Loguru Documentation](https://loguru.readthedocs.io/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run tests: `python test_implementation.py && python test_browser_automation.py`
5. Commit your changes: `git commit -am 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ✨ Acknowledgments

- Built for Large Action Model (LAM) web automation systems
- Designed for production-ready browser automation
- Comprehensive testing and documentation included
- Ready for integration with AI/ML components

---

**🎉 Ready for Production!** This Browser Controller is complete, tested, and ready to be integrated into your LAM system for sophisticated web automation tasks.
