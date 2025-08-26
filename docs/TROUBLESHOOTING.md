# Troubleshooting Guide

Common issues and solutions for the Browser Controller.

## 🚨 Common Issues

### Browser Launch Issues

#### Issue: Browser fails to launch
```
BrowserLaunchError: Failed to launch browser
```

**Solutions:**
1. **Check browser installation**
   ```bash
   # Verify Chrome is installed
   google-chrome --version
   # or
   "C:\Program Files\Google\Chrome\Application\chrome.exe" --version
   ```

2. **Try different browser**
   ```python
   # If Chrome fails, try Firefox
   config = BrowserConfig(browser_type=BrowserType.FIREFOX)
   ```

3. **Check WebDriver compatibility**
   ```bash
   pip install --upgrade webdriver-manager selenium
   ```

4. **System permissions**
   ```python
   config = BrowserConfig(
       browser_options={
           "no_sandbox": True,  # For Linux systems
           "disable_dev_shm_usage": True
       }
   )
   ```

#### Issue: WebDriver version mismatch
```
SessionNotCreatedException: This version of ChromeDriver only supports Chrome version X
```

**Solution:**
```bash
# Update webdriver-manager to get latest drivers
pip install --upgrade webdriver-manager
```

### Element Interaction Issues

#### Issue: Element not found
```python
element = await session.find_element("button.submit")
# Returns None
```

**Solutions:**
1. **Use explicit waits**
   ```python
   # Wait for element to appear
   element = await session.wait_for_element("button.submit", timeout=30)
   ```

2. **Check selector accuracy**
   ```python
   # Use browser dev tools to verify selector
   # Try different selector strategies
   element = await session.find_element("//button[contains(@class, 'submit')]")  # XPath
   element = await session.find_element("input[type='submit']")  # CSS
   ```

3. **Wait for page load**
   ```python
   await session.navigate_to("https://example.com")
   # Wait for page to fully load
   await session.wait_for_element("body", timeout=30)
   ```

#### Issue: Element not clickable
```python
success = await session.click_element("button")
# Returns False
```

**Solutions:**
1. **Wait for element to be clickable**
   ```python
   from selenium.webdriver.support import expected_conditions as EC
   element = await session.wait_for_condition(
       EC.element_to_be_clickable(("css selector", "button")),
       timeout=30
   )
   ```

2. **Scroll element into view**
   ```python
   element = await session.find_element("button")
   if element:
       await session.execute_script(
           "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
           element
       )
       await asyncio.sleep(1)
       await session.click_element("button")
   ```

3. **Check for overlays**
   ```python
   # Close any modal or overlay first
   modal_close = await session.find_element(".modal-close, .overlay-close")
   if modal_close:
       await session.click_element(".modal-close")
   ```

### Page Load Issues

#### Issue: Page load timeout
```
TimeoutException: Page load timeout
```

**Solutions:**
1. **Increase timeout**
   ```python
   config = BrowserConfig(
       page_load_timeout=60,  # Increase from default 30
       implicit_wait=20
   )
   ```

2. **Handle slow loading sites**
   ```python
   try:
       await session.navigate_to("https://slow-site.com", timeout=60)
   except Exception as e:
       print(f"Page load timeout: {e}")
       # Continue with partial load
   ```

#### Issue: Dynamic content not loaded
```python
element = await session.find_element(".dynamic-content")
# Returns None even though element exists
```

**Solutions:**
1. **Wait for specific content**
   ```python
   # Wait for AJAX content
   element = await session.wait_for_element(".dynamic-content", timeout=30)
   
   # Wait for text to appear
   from selenium.webdriver.support import expected_conditions as EC
   await session.wait_for_condition(
       EC.text_to_be_present_in_element(("css selector", ".status"), "Ready"),
       timeout=30
   )
   ```

2. **Handle loading indicators**
   ```python
   # Wait for loading spinner to disappear
   await session.wait_for_element_to_disappear(".loading-spinner", timeout=30)
   ```

### Session Management Issues

#### Issue: Too many sessions
```
SessionError: Maximum sessions reached
```

**Solutions:**
1. **Close unused sessions**
   ```python
   # Get and close old sessions
   active_sessions = controller.get_active_sessions()
   for session_id in active_sessions[:-5]:  # Keep only last 5
       await controller.close_session(session_id)
   ```

2. **Use session context managers**
   ```python
   # Automatically cleaned up
   async with controller.new_session() as session:
       await session.navigate_to("https://example.com")
       # Session auto-closed when block exits
   ```

#### Issue: Memory usage growing
**Solutions:**
1. **Monitor session count**
   ```python
   print(f"Active sessions: {controller.get_session_count()}")
   if controller.get_session_count() > 10:
       # Close some sessions
       pass
   ```

2. **Use headless mode**
   ```python
   config = BrowserConfig(headless=True)  # Uses less memory
   ```

### Configuration Issues

#### Issue: Invalid configuration
```
ValidationError: Invalid browser configuration
```

**Solutions:**
1. **Check configuration values**
   ```python
   # Valid browser types
   config = BrowserConfig(
       browser_type=BrowserType.CHROME,  # Use enum
       headless=True,  # Boolean not string
       window_size=(1280, 720),  # Tuple not list
   )
   ```

2. **Validate configuration**
   ```python
   try:
       config = BrowserConfig(**config_dict)
   except ValidationError as e:
       print(f"Configuration error: {e}")
   ```

#### Issue: Environment variables not loaded
```python
config = BrowserConfig()  # Uses defaults instead of .env
```

**Solutions:**
1. **Load environment explicitly**
   ```python
   from dotenv import load_dotenv
   load_dotenv()  # Load .env file
   
   config = BrowserConfig()  # Now uses env vars
   ```

2. **Check .env file location**
   ```bash
   # .env should be in project root
   ls -la .env
   ```

### Logging Issues

#### Issue: Logs not appearing
**Solutions:**
1. **Set log level**
   ```python
   import os
   os.environ["LOG_LEVEL"] = "DEBUG"
   
   # Or configure directly
   from src.utils.logger import configure_logging
   configure_logging(level="DEBUG")
   ```

2. **Check log file location**
   ```python
   # Logs are saved to logs/ directory
   ls -la logs/
   ```

#### Issue: Too many log files
**Solutions:**
1. **Configure rotation**
   ```python
   configure_logging(
       file_rotation="10 MB",
       retention="7 days"
   )
   ```

## 🔧 Debugging Techniques

### Enable Debug Mode
```python
import os
os.environ["LOG_LEVEL"] = "DEBUG"

from src.utils.logger import get_logger
logger = get_logger("Debug")

# Log everything
logger.debug("Starting automation")
```

### Take Screenshots at Each Step
```python
async def debug_automation():
    async with BrowserController(config) as controller:
        session = await controller.create_session()
        
        try:
            await session.navigate_to("https://example.com")
            await session.take_screenshot("01_loaded.png")
            
            await session.click_element("button")
            await session.take_screenshot("02_clicked.png")
            
        finally:
            await controller.close_session(session.session_id)
```

### Check Element States
```python
async def check_element_state(session, selector):
    element = await session.find_element(selector)
    if element:
        visible = await session.is_element_visible(selector)
        enabled = await session.is_element_enabled(selector)
        text = await session.get_element_text(selector)
        
        print(f"Element {selector}:")
        print(f"  Visible: {visible}")
        print(f"  Enabled: {enabled}")
        print(f"  Text: {text}")
    else:
        print(f"Element not found: {selector}")
```

### Monitor Network Activity
```python
# Enable logging of network requests (Chrome only)
config = BrowserConfig(
    browser_options={
        "enable_logging": True,
        "log_level": "INFO"
    }
)
```

## 🚀 Performance Issues

### Slow Page Loading
**Solutions:**
1. **Disable images**
   ```python
   config = BrowserConfig(
       browser_options={"disable_images": True}
   )
   ```

2. **Use mobile viewport**
   ```python
   config = BrowserConfig(
       window_size=(390, 844),  # Mobile size
       browser_options={"mobile_emulation": {"deviceName": "iPhone X"}}
   )
   ```

### High Memory Usage
**Solutions:**
1. **Limit concurrent sessions**
   ```python
   MAX_SESSIONS = 5
   if controller.get_session_count() >= MAX_SESSIONS:
       await controller.close_session(oldest_session_id)
   ```

2. **Use browser restart strategy**
   ```python
   # Restart browser every N operations
   operations_count = 0
   RESTART_AFTER = 100
   
   if operations_count >= RESTART_AFTER:
       await controller.close()
       await controller.launch()
       operations_count = 0
   ```

### Slow Element Interactions
**Solutions:**
1. **Optimize waits**
   ```python
   # Use shorter, specific waits
   element = await session.wait_for_element("button", timeout=5)
   
   # Instead of long implicit wait
   config = BrowserConfig(implicit_wait=2)  # Shorter default
   ```

2. **Batch operations**
   ```python
   # Find all elements at once
   elements = await session.find_elements(".item")
   
   # Process them efficiently
   for i, element in enumerate(elements):
       text = await session.get_element_text(f".item:nth-child({i+1})")
   ```

## 🔍 Diagnostic Tools

### Health Check Script
```python
async def health_check():
    """Comprehensive health check"""
    print("🏥 Browser Controller Health Check")
    print("=" * 40)
    
    # Test 1: Basic import
    try:
        from src.core.browser_controller import BrowserController
        print("✅ Import successful")
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return
    
    # Test 2: Configuration
    try:
        from src.config.browser_config import BrowserConfig
        config = BrowserConfig()
        print("✅ Configuration successful")
    except Exception as e:
        print(f"❌ Configuration failed: {e}")
        return
    
    # Test 3: Browser launch
    try:
        async with BrowserController(config) as controller:
            print("✅ Browser launch successful")
            
            # Test 4: Session creation
            session = await controller.create_session()
            print("✅ Session creation successful")
            
            # Test 5: Navigation
            await session.navigate_to("https://httpbin.org/html")
            title = await session.get_title()
            print(f"✅ Navigation successful: {title}")
            
            await controller.close_session(session.session_id)
            print("✅ Session cleanup successful")
            
    except Exception as e:
        print(f"❌ Browser test failed: {e}")
        return
    
    print("🎉 All health checks passed!")

# Run health check
asyncio.run(health_check())
```

### Environment Check
```python
def check_environment():
    """Check system environment"""
    import sys
    import subprocess
    
    print(f"Python version: {sys.version}")
    print(f"Platform: {sys.platform}")
    
    # Check Chrome
    try:
        result = subprocess.run(
            ["google-chrome", "--version"], 
            capture_output=True, 
            text=True
        )
        print(f"Chrome: {result.stdout.strip()}")
    except:
        print("Chrome: Not found or not in PATH")
    
    # Check dependencies
    deps = ["selenium", "webdriver-manager", "pydantic", "loguru"]
    for dep in deps:
        try:
            __import__(dep)
            print(f"✅ {dep}: Installed")
        except ImportError:
            print(f"❌ {dep}: Missing")

check_environment()
```

## 📞 Getting Help

### Enable Verbose Logging
```python
import os
os.environ["LOG_LEVEL"] = "DEBUG"

# Run your automation
# Check logs/ directory for detailed logs
```

### Collect System Information
```bash
# System info
uname -a  # Linux/Mac
systeminfo  # Windows

# Python info
python --version
pip list | grep -E "(selenium|webdriver|pydantic|loguru)"

# Browser info
google-chrome --version
firefox --version
```

### Create Minimal Reproduction
```python
async def minimal_repro():
    """Minimal code that reproduces the issue"""
    config = BrowserConfig(browser_type=BrowserType.CHROME, headless=True)
    
    async with BrowserController(config) as controller:
        session = await controller.create_session()
        
        try:
            # Minimal steps to reproduce issue
            await session.navigate_to("https://httpbin.org/html")
            element = await session.find_element("h1")
            print(f"Found element: {element is not None}")
            
        finally:
            await controller.close_session(session.session_id)

asyncio.run(minimal_repro())
```

---

If you encounter issues not covered here, check the logs first, then create a minimal reproduction case to help with diagnosis.
