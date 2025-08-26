# Browser Controller - Examples

This document provides comprehensive examples of using the Browser Controller for various web automation tasks.

## 🎯 Table of Contents

1. [Basic Operations](#basic-operations)
2. [Form Automation](#form-automation)
3. [Data Extraction](#data-extraction)
4. [Testing Scenarios](#testing-scenarios)
5. [Advanced Patterns](#advanced-patterns)
6. [Real-World Use Cases](#real-world-use-cases)

## Basic Operations

### Simple Navigation and Screenshot

```python
import asyncio
from src.core.browser_controller import BrowserController
from src.config.browser_config import BrowserConfig
from src.types.browser_types import BrowserType

async def basic_navigation():
    """Basic navigation and screenshot example"""
    config = BrowserConfig(
        browser_type=BrowserType.CHROME,
        headless=True,
        window_size=(1280, 720)
    )
    
    async with BrowserController(config) as controller:
        session = await controller.create_session()
        
        try:
            # Navigate to website
            await session.navigate_to("https://example.com")
            
            # Get page information
            title = await session.get_title()
            url = await session.get_current_url()
            
            print(f"Title: {title}")
            print(f"URL: {url}")
            
            # Take screenshot
            await session.take_screenshot("example_page.png")
            print("Screenshot saved!")
            
        finally:
            await controller.close_session(session.session_id)

asyncio.run(basic_navigation())
```

### Multiple Browser Sessions

```python
async def multiple_sessions_example():
    """Managing multiple browser sessions"""
    config = BrowserConfig(
        browser_type=BrowserType.CHROME,
        headless=True
    )
    
    async with BrowserController(config) as controller:
        # Create multiple sessions
        sessions = []
        websites = [
            "https://httpbin.org/html",
            "https://example.com",
            "https://httpbin.org/forms/post"
        ]
        
        # Launch all sessions
        for url in websites:
            session = await controller.create_session()
            await session.navigate_to(url)
            sessions.append(session)
        
        print(f"Created {len(sessions)} sessions")
        
        # Work with each session
        for i, session in enumerate(sessions):
            title = await session.get_title()
            print(f"Session {i+1}: {title}")
            
            # Take individual screenshots
            await session.take_screenshot(f"session_{i+1}.png")
        
        # Clean up all sessions
        for session in sessions:
            await controller.close_session(session.session_id)

asyncio.run(multiple_sessions_example())
```

## Form Automation

### Contact Form Submission

```python
async def contact_form_automation():
    """Automate contact form submission"""
    config = BrowserConfig(
        browser_type=BrowserType.CHROME,
        headless=False,  # Show browser for demo
        window_size=(1280, 720)
    )
    
    async with BrowserController(config) as controller:
        session = await controller.create_session()
        
        try:
            # Navigate to form
            await session.navigate_to("https://httpbin.org/forms/post")
            
            # Fill out the form
            await session.type_text("input[name='custname']", "John Doe")
            await session.type_text("input[name='custtel']", "+1-555-0123")
            await session.type_text("input[name='custemail']", "john@example.com")
            
            # Select radio button
            await session.click_element("input[value='medium']")
            
            # Select from dropdown (if available)
            # await session.select_dropdown_option("select[name='size']", "Large")
            
            # Fill textarea
            await session.type_text("textarea[name='comments']", 
                                   "This is an automated test message.")
            
            # Submit form
            await session.click_element("input[type='submit']")
            
            # Wait for response page
            await asyncio.sleep(2)
            
            # Verify submission
            current_url = await session.get_current_url()
            if "post" in current_url:
                print("✅ Form submitted successfully!")
            
            # Take screenshot of result
            await session.take_screenshot("form_result.png")
            
        finally:
            await controller.close_session(session.session_id)

asyncio.run(contact_form_automation())
```

### Login Flow Automation

```python
async def login_automation():
    """Automate login process"""
    config = BrowserConfig(
        browser_type=BrowserType.CHROME,
        headless=True
    )
    
    async with BrowserController(config) as controller:
        session = await controller.create_session()
        
        try:
            # Navigate to login page
            await session.navigate_to("https://the-internet.herokuapp.com/login")
            
            # Enter credentials
            await session.type_text("input[name='username']", "tomsmith")
            await session.type_text("input[name='password']", "SuperSecretPassword!")
            
            # Click login button
            await session.click_element("button[type='submit']")
            
            # Wait for page to load and check for success
            success_element = await session.wait_for_element(
                ".flash.success", timeout=10
            )
            
            if success_element:
                success_text = await session.get_element_text(".flash.success")
                print(f"✅ Login successful: {success_text}")
            else:
                print("❌ Login failed")
            
            # Take screenshot
            await session.take_screenshot("login_result.png")
            
        finally:
            await controller.close_session(session.session_id)

asyncio.run(login_automation())
```

## Data Extraction

### Web Scraping Example

```python
async def web_scraping_example():
    """Extract data from a website"""
    config = BrowserConfig(
        browser_type=BrowserType.CHROME,
        headless=True,
        browser_options={
            "disable_images": True  # Faster loading
        }
    )
    
    async with BrowserController(config) as controller:
        session = await controller.create_session()
        
        try:
            # Navigate to quotes website
            await session.navigate_to("http://quotes.toscrape.com/")
            
            # Extract quotes
            quotes_data = []
            
            # Find all quote containers
            quote_elements = await session.find_elements(".quote")
            
            for i, quote_element in enumerate(quote_elements[:5]):  # First 5 quotes
                # Extract text, author, and tags
                text_selector = f".quote:nth-child({i+1}) .text"
                author_selector = f".quote:nth-child({i+1}) .author"
                tags_selector = f".quote:nth-child({i+1}) .tags a"
                
                text = await session.get_element_text(text_selector)
                author = await session.get_element_text(author_selector)
                
                # Get all tags
                tag_elements = await session.find_elements(tags_selector)
                tags = []
                for tag_element in tag_elements:
                    tag_text = await session.get_element_text(tag_element)
                    tags.append(tag_text)
                
                quotes_data.append({
                    "text": text,
                    "author": author,
                    "tags": tags
                })
            
            # Print extracted data
            for i, quote in enumerate(quotes_data, 1):
                print(f"\nQuote {i}:")
                print(f"Text: {quote['text']}")
                print(f"Author: {quote['author']}")
                print(f"Tags: {', '.join(quote['tags'])}")
            
            print(f"\n✅ Extracted {len(quotes_data)} quotes")
            
        finally:
            await controller.close_session(session.session_id)

asyncio.run(web_scraping_example())
```

### Table Data Extraction

```python
async def table_extraction():
    """Extract data from HTML tables"""
    config = BrowserConfig(browser_type=BrowserType.CHROME, headless=True)
    
    async with BrowserController(config) as controller:
        session = await controller.create_session()
        
        try:
            # Navigate to page with table
            await session.navigate_to("https://the-internet.herokuapp.com/tables")
            
            # Extract table 1 data
            table_data = []
            
            # Get table headers
            header_elements = await session.find_elements("#table1 thead th")
            headers = []
            for header in header_elements:
                header_text = await session.get_element_text(header)
                headers.append(header_text)
            
            print(f"Headers: {headers}")
            
            # Get table rows
            row_elements = await session.find_elements("#table1 tbody tr")
            
            for row_element in row_elements:
                cell_elements = await session.find_elements(f"{row_element} td")
                row_data = {}
                
                for i, cell in enumerate(cell_elements):
                    if i < len(headers):
                        cell_text = await session.get_element_text(cell)
                        row_data[headers[i]] = cell_text
                
                table_data.append(row_data)
            
            # Print extracted table data
            for row in table_data:
                print(row)
            
            print(f"\n✅ Extracted {len(table_data)} rows")
            
        finally:
            await controller.close_session(session.session_id)

asyncio.run(table_extraction())
```

## Testing Scenarios

### Element Interaction Testing

```python
async def element_interaction_test():
    """Test various element interactions"""
    config = BrowserConfig(
        browser_type=BrowserType.CHROME,
        headless=False,  # Show browser for demo
        window_size=(1280, 720)
    )
    
    async with BrowserController(config) as controller:
        session = await controller.create_session()
        
        try:
            # Navigate to interactive elements page
            await session.navigate_to("https://the-internet.herokuapp.com/")
            
            # Test clicking links
            checkboxes_link = await session.find_element("a[href='/checkboxes']")
            if checkboxes_link:
                print("✅ Found checkboxes link")
                await session.click_element("a[href='/checkboxes']")
                
                # Wait for page to load
                await asyncio.sleep(2)
                
                # Test checkboxes
                checkboxes = await session.find_elements("input[type='checkbox']")
                print(f"Found {len(checkboxes)} checkboxes")
                
                # Click first checkbox
                if checkboxes:
                    await session.click_element("input[type='checkbox']:first-of-type")
                    print("✅ Clicked first checkbox")
                
                # Take screenshot
                await session.take_screenshot("checkbox_test.png")
                
                # Go back
                await session.go_back()
            
            # Test dropdown
            await session.click_element("a[href='/dropdown']")
            await asyncio.sleep(2)
            
            # Select dropdown option
            dropdown = await session.find_element("#dropdown")
            if dropdown:
                # await session.select_dropdown_option("#dropdown", "Option 1")
                print("✅ Found dropdown element")
            
            await session.take_screenshot("dropdown_test.png")
            
        finally:
            await controller.close_session(session.session_id)

asyncio.run(element_interaction_test())
```

### Error Handling Test

```python
async def error_handling_test():
    """Test error handling scenarios"""
    config = BrowserConfig(browser_type=BrowserType.CHROME, headless=True)
    
    async with BrowserController(config) as controller:
        session = await controller.create_session()
        
        try:
            print("🧪 Testing error handling scenarios...")
            
            # Test 1: Invalid URL
            try:
                await session.navigate_to("http://invalid-url-that-does-not-exist.com")
                print("❌ Should have failed on invalid URL")
            except Exception as e:
                print(f"✅ Correctly handled invalid URL: {type(e).__name__}")
            
            # Test 2: Valid site for other tests
            await session.navigate_to("https://httpbin.org/html")
            
            # Test 3: Element not found
            try:
                non_existent = await session.find_element("non-existent-selector")
                if non_existent is None:
                    print("✅ Correctly returned None for non-existent element")
            except Exception as e:
                print(f"✅ Correctly handled missing element: {type(e).__name__}")
            
            # Test 4: Click non-existent element
            try:
                success = await session.click_element("non-existent-button")
                if not success:
                    print("✅ Correctly returned False for non-existent click")
            except Exception as e:
                print(f"✅ Correctly handled click on missing element: {type(e).__name__}")
            
            # Test 5: Timeout test
            try:
                element = await session.wait_for_element("never-appears", timeout=2)
                if element is None:
                    print("✅ Correctly handled timeout")
            except Exception as e:
                print(f"✅ Correctly handled timeout: {type(e).__name__}")
            
            print("✅ All error handling tests completed")
            
        finally:
            await controller.close_session(session.session_id)

asyncio.run(error_handling_test())
```

## Advanced Patterns

### Page Object Pattern

```python
class LoginPage:
    """Page Object for login functionality"""
    
    def __init__(self, session):
        self.session = session
        self.username_field = "input[name='username']"
        self.password_field = "input[name='password']"
        self.submit_button = "button[type='submit']"
        self.success_message = ".flash.success"
        self.error_message = ".flash.error"
    
    async def navigate(self):
        """Navigate to login page"""
        await self.session.navigate_to("https://the-internet.herokuapp.com/login")
    
    async def login(self, username: str, password: str):
        """Perform login"""
        await self.session.type_text(self.username_field, username, clear_first=True)
        await self.session.type_text(self.password_field, password, clear_first=True)
        await self.session.click_element(self.submit_button)
    
    async def is_login_successful(self) -> bool:
        """Check if login was successful"""
        success_element = await self.session.find_element(self.success_message)
        return success_element is not None
    
    async def get_error_message(self) -> str:
        """Get error message if login failed"""
        error_element = await self.session.find_element(self.error_message)
        if error_element:
            return await self.session.get_element_text(self.error_message)
        return ""

async def page_object_example():
    """Example using Page Object pattern"""
    config = BrowserConfig(browser_type=BrowserType.CHROME, headless=True)
    
    async with BrowserController(config) as controller:
        session = await controller.create_session()
        
        try:
            # Create page object
            login_page = LoginPage(session)
            
            # Navigate to login page
            await login_page.navigate()
            
            # Test invalid credentials
            await login_page.login("invalid_user", "wrong_password")
            
            if not await login_page.is_login_successful():
                error_msg = await login_page.get_error_message()
                print(f"❌ Login failed as expected: {error_msg}")
            
            # Test valid credentials
            await login_page.login("tomsmith", "SuperSecretPassword!")
            
            if await login_page.is_login_successful():
                print("✅ Login successful!")
            else:
                error_msg = await login_page.get_error_message()
                print(f"❌ Login failed unexpectedly: {error_msg}")
            
        finally:
            await controller.close_session(session.session_id)

asyncio.run(page_object_example())
```

### Configuration-Driven Automation

```python
import json
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class AutomationStep:
    action: str
    selector: str = ""
    text: str = ""
    timeout: int = 30
    screenshot: str = ""

@dataclass
class AutomationConfig:
    url: str
    steps: List[AutomationStep]

async def config_driven_automation():
    """Run automation based on JSON configuration"""
    
    # Configuration (could be loaded from JSON file)
    config_data = {
        "url": "https://httpbin.org/forms/post",
        "steps": [
            {"action": "navigate", "screenshot": "01_initial.png"},
            {"action": "type", "selector": "input[name='custname']", "text": "Automated User"},
            {"action": "type", "selector": "input[name='custemail']", "text": "auto@example.com"},
            {"action": "click", "selector": "input[value='medium']"},
            {"action": "type", "selector": "textarea[name='comments']", "text": "Automated message"},
            {"action": "screenshot", "screenshot": "02_form_filled.png"},
            {"action": "click", "selector": "input[type='submit']"},
            {"action": "wait", "selector": "body", "timeout": 5},
            {"action": "screenshot", "screenshot": "03_submitted.png"}
        ]
    }
    
    # Parse configuration
    automation_config = AutomationConfig(
        url=config_data["url"],
        steps=[AutomationStep(**step) for step in config_data["steps"]]
    )
    
    # Execute automation
    browser_config = BrowserConfig(browser_type=BrowserType.CHROME, headless=True)
    
    async with BrowserController(browser_config) as controller:
        session = await controller.create_session()
        
        try:
            # Navigate to initial URL
            await session.navigate_to(automation_config.url)
            
            # Execute each step
            for i, step in enumerate(automation_config.steps, 1):
                print(f"Step {i}: {step.action}")
                
                if step.action == "navigate":
                    await session.navigate_to(step.selector or automation_config.url)
                
                elif step.action == "click":
                    success = await session.click_element(step.selector)
                    print(f"  Click {'✅' if success else '❌'}: {step.selector}")
                
                elif step.action == "type":
                    success = await session.type_text(step.selector, step.text)
                    print(f"  Type {'✅' if success else '❌'}: {step.text}")
                
                elif step.action == "wait":
                    element = await session.wait_for_element(step.selector, timeout=step.timeout)
                    print(f"  Wait {'✅' if element else '❌'}: {step.selector}")
                
                elif step.action == "screenshot":
                    await session.take_screenshot(step.screenshot)
                    print(f"  Screenshot ✅: {step.screenshot}")
                
                # Take screenshot if specified
                if step.screenshot and step.action != "screenshot":
                    await session.take_screenshot(step.screenshot)
            
            print("✅ Configuration-driven automation completed!")
            
        finally:
            await controller.close_session(session.session_id)

asyncio.run(config_driven_automation())
```

## Real-World Use Cases

### E-commerce Price Monitoring

```python
async def price_monitoring():
    """Monitor product prices on e-commerce site"""
    config = BrowserConfig(
        browser_type=BrowserType.CHROME,
        headless=True,
        browser_options={
            "disable_images": True,
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    )
    
    async with BrowserController(config) as controller:
        session = await controller.create_session()
        
        try:
            # List of products to monitor
            products = [
                {"name": "Example Product 1", "url": "https://example-store.com/product1"},
                {"name": "Example Product 2", "url": "https://example-store.com/product2"}
            ]
            
            price_data = []
            
            for product in products:
                try:
                    print(f"Checking price for: {product['name']}")
                    
                    await session.navigate_to(product['url'])
                    
                    # Extract price (selector depends on actual site)
                    price_element = await session.find_element(".price, .current-price, [data-price]")
                    
                    if price_element:
                        price_text = await session.get_element_text(price_element)
                        print(f"  Price: {price_text}")
                        
                        price_data.append({
                            "product": product['name'],
                            "price": price_text,
                            "url": product['url'],
                            "timestamp": "2025-08-23T10:00:00Z"  # Use actual timestamp
                        })
                    else:
                        print(f"  ❌ Price not found for {product['name']}")
                
                except Exception as e:
                    print(f"  ❌ Error monitoring {product['name']}: {e}")
                
                # Delay between requests
                await asyncio.sleep(2)
            
            # Save price data (to database, file, etc.)
            print(f"\n✅ Monitored {len(price_data)} products")
            for data in price_data:
                print(f"  {data['product']}: {data['price']}")
            
        finally:
            await controller.close_session(session.session_id)

# Note: This is a template - adapt URLs and selectors for actual sites
# asyncio.run(price_monitoring())
```

### Social Media Automation

```python
async def social_media_automation():
    """Automate social media posting (template)"""
    config = BrowserConfig(
        browser_type=BrowserType.CHROME,
        headless=False,  # Usually need to see for social media
        window_size=(1280, 720)
    )
    
    async with BrowserController(config) as controller:
        session = await controller.create_session()
        
        try:
            # This is a template - adapt for actual social media platforms
            print("🔒 Social media automation requires careful handling of:")
            print("  • Terms of service compliance")
            print("  • Rate limiting")
            print("  • Authentication handling")
            print("  • CAPTCHA solving")
            print("  • Proper delays between actions")
            
            # Example structure:
            # 1. Navigate to platform
            # await session.navigate_to("https://social-platform.com/login")
            
            # 2. Handle login (preferably with saved session)
            # await session.type_text("input[name='username']", username)
            # await session.type_text("input[name='password']", password)
            # await session.click_element("button[type='submit']")
            
            # 3. Navigate to posting area
            # await session.click_element(".compose-button")
            
            # 4. Create post
            # await session.type_text(".post-composer", "Automated post content")
            
            # 5. Add media if needed
            # await session.upload_file("input[type='file']", "/path/to/image.jpg")
            
            # 6. Submit post
            # await session.click_element(".submit-post")
            
            print("⚠️  Remember to implement proper error handling and respect platform limits!")
            
        finally:
            await controller.close_session(session.session_id)

# Note: This is a template only - implement carefully with platform-specific considerations
# asyncio.run(social_media_automation())
```

### Website Health Monitoring

```python
async def website_health_check():
    """Monitor website health and performance"""
    config = BrowserConfig(browser_type=BrowserType.CHROME, headless=True)
    
    async with BrowserController(config) as controller:
        session = await controller.create_session()
        
        try:
            websites = [
                "https://httpbin.org/",
                "https://example.com",
                "https://httpbin.org/delay/2"
            ]
            
            health_results = []
            
            for url in websites:
                print(f"🔍 Checking: {url}")
                
                start_time = asyncio.get_event_loop().time()
                
                try:
                    # Navigate and measure load time
                    await session.navigate_to(url)
                    load_time = asyncio.get_event_loop().time() - start_time
                    
                    # Get page info
                    title = await session.get_title()
                    current_url = await session.get_current_url()
                    
                    # Check for specific elements that indicate health
                    body_element = await session.find_element("body")
                    has_content = body_element is not None
                    
                    # Check for error indicators
                    error_indicators = await session.find_elements(
                        ".error, .404, .500, [class*='error']"
                    )
                    has_errors = len(error_indicators) > 0
                    
                    status = "✅ Healthy" if has_content and not has_errors else "⚠️  Issues detected"
                    
                    result = {
                        "url": url,
                        "status": status,
                        "load_time": round(load_time, 2),
                        "title": title,
                        "redirected": current_url != url,
                        "final_url": current_url,
                        "has_errors": has_errors
                    }
                    
                    health_results.append(result)
                    
                    print(f"  Status: {status}")
                    print(f"  Load time: {load_time:.2f}s")
                    print(f"  Title: {title}")
                    
                except Exception as e:
                    result = {
                        "url": url,
                        "status": "❌ Failed",
                        "error": str(e),
                        "load_time": None
                    }
                    health_results.append(result)
                    print(f"  Status: ❌ Failed - {e}")
                
                print()
            
            # Summary
            healthy_count = sum(1 for r in health_results if "Healthy" in r["status"])
            print(f"📊 Health Check Summary:")
            print(f"  Total sites: {len(websites)}")
            print(f"  Healthy: {healthy_count}")
            print(f"  Issues: {len(websites) - healthy_count}")
            
        finally:
            await controller.close_session(session.session_id)

asyncio.run(website_health_check())
```

## Best Practices Summary

### 1. Resource Management
```python
# Always use async context managers
async with BrowserController(config) as controller:
    session = await controller.create_session()
    try:
        # Your automation code
        pass
    finally:
        await controller.close_session(session.session_id)
```

### 2. Error Handling
```python
# Handle errors gracefully
try:
    element = await session.find_element("selector")
    if element:
        await session.click_element("selector")
except Exception as e:
    logger.error(f"Element interaction failed: {e}")
    # Implement retry logic or fallback
```

### 3. Wait Strategies
```python
# Use explicit waits instead of sleep
element = await session.wait_for_element("selector", timeout=30)

# Don't use
await asyncio.sleep(5)  # Unreliable
```

### 4. Performance
```python
# Configure for speed when appropriate
config = BrowserConfig(
    headless=True,
    browser_options={
        "disable_images": True,
        "disable_plugins": True
    }
)
```

### 5. Debugging
```python
# Enable debug logging
from src.utils.logger import configure_logging
configure_logging(level="DEBUG")

# Take screenshots for debugging
await session.take_screenshot("debug_state.png")
```

---

These examples demonstrate the flexibility and power of the Browser Controller for various web automation tasks. Adapt them to your specific use cases and requirements.
