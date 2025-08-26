"""
Example usage of Browser Controller component.

This example demonstrates the main features and capabilities of the Browser Controller
for web automation tasks in the LAM (Large Action Model) system.
"""

import asyncio
from pathlib import Path
from browser_controller import BrowserController, BrowserConfig, BrowserType


async def basic_usage_example():
    """Basic usage example with automatic session management."""
    
    # Create configuration
    config = BrowserConfig(
        browser_type=BrowserType.CHROME,
        headless=False,  # Set to True for headless mode
        window_size=(1920, 1080),
        implicit_wait=10.0,
        page_load_timeout=30.0
    )
    
    # Initialize browser controller
    controller = BrowserController(config)
    
    try:
        # Using context manager for automatic cleanup
        async with controller:
            print("Browser launched successfully!")
            
            # Navigate to a website
            result = await controller.navigate_to("https://example.com")
            print(f"Navigation result: {result}")
            
            # Get page information
            page_info = await controller.get_page_info()
            print(f"Page title: {page_info.title}")
            print(f"Page URL: {page_info.url}")
            
            # Take screenshot
            screenshot_path = "example_screenshot.png"
            await controller.take_screenshot(screenshot_path)
            print(f"Screenshot saved to: {screenshot_path}")
            
    except Exception as e:
        print(f"Error: {e}")


async def session_management_example():
    """Example using explicit session management for multiple operations."""
    
    config = BrowserConfig(
        browser_type=BrowserType.CHROME,
        headless=True,
        implicit_wait=10.0
    )
    
    controller = BrowserController(config)
    
    try:
        # Manual session management
        async with controller.new_session() as session:
            print(f"Session created: {session.session_id}")
            
            # Navigate to multiple pages in same session
            await session.navigate_to("https://httpbin.org/")
            print(f"Current URL: {await session.get_current_url()}")
            
            # Find and interact with elements
            try:
                # Look for a link or button (example)
                element = await session.find_element(("css_selector", "a[href*='get']"))
                if element:
                    await session.click_element(("css_selector", "a[href*='get']"))
                    print("Clicked on GET endpoint link")
                    
                    # Wait for page to load and get new URL
                    await asyncio.sleep(2)
                    new_url = await session.get_current_url()
                    print(f"New URL after click: {new_url}")
                    
            except Exception as e:
                print(f"Element interaction failed: {e}")
            
            # Get final page info
            final_info = await session.get_page_info()
            print(f"Final page title: {final_info.title}")
            
    except Exception as e:
        print(f"Session error: {e}")
    
    finally:
        await controller.close()


async def form_interaction_example():
    """Example of form interaction and text input."""
    
    config = BrowserConfig(
        browser_type=BrowserType.CHROME,
        headless=False,
        window_size=(1280, 720)
    )
    
    controller = BrowserController(config)
    
    try:
        async with controller.new_session() as session:
            # Navigate to a form page
            await session.navigate_to("https://httpbin.org/forms/post")
            
            # Fill out form fields
            await session.type_text(("name", "custname"), "Test Customer")
            await session.type_text(("name", "custtel"), "123-456-7890")
            await session.type_text(("name", "custemail"), "test@example.com")
            
            # Select from dropdown
            await session.select_dropdown(("name", "size"), "medium")
            
            # Check boxes and radio buttons
            await session.click_element(("name", "topping"), multiple=True)  # pizza toppings
            
            print("Form filled successfully!")
            
            # Take screenshot of filled form
            await controller.take_screenshot("filled_form.png")
            
            # Submit form (optional)
            # await session.click_element(("xpath", "//input[@type='submit']"))
            
    except Exception as e:
        print(f"Form interaction error: {e}")
    
    finally:
        await controller.close()


async def wait_strategies_example():
    """Example demonstrating different wait strategies."""
    
    config = BrowserConfig(
        browser_type=BrowserType.CHROME,
        headless=True,
        implicit_wait=5.0
    )
    
    controller = BrowserController(config)
    
    try:
        async with controller.new_session() as session:
            await session.navigate_to("https://httpbin.org/delay/3")
            
            # Wait for specific element to appear
            element = await session.wait_for_element(("tag_name", "body"), timeout=10.0)
            if element:
                print("Page loaded and body element found")
            
            # Wait for element to be clickable
            try:
                clickable_element = await session.wait_for_element_clickable(
                    ("css_selector", "a"), timeout=5.0
                )
                print("Found clickable element")
            except Exception as e:
                print(f"No clickable elements found: {e}")
            
            # Custom wait condition
            def page_contains_json(driver):
                return "json" in driver.page_source.lower()
            
            await session.wait_for_custom_condition(page_contains_json, timeout=10.0)
            print("Page contains JSON content")
            
    except Exception as e:
        print(f"Wait strategies error: {e}")
    
    finally:
        await controller.close()


async def mobile_emulation_example():
    """Example using mobile device emulation."""
    
    config = BrowserConfig(
        browser_type=BrowserType.CHROME,
        headless=False,
        mobile_emulation={
            "device_name": "iPhone 12 Pro"
        }
    )
    
    controller = BrowserController(config)
    
    try:
        async with controller.new_session() as session:
            await session.navigate_to("https://whatismyviewport.com/")
            
            # Get viewport information
            viewport_info = await session.execute_script(
                "return {width: window.innerWidth, height: window.innerHeight};"
            )
            print(f"Mobile viewport: {viewport_info}")
            
            # Take mobile screenshot
            await controller.take_screenshot("mobile_viewport.png")
            
    except Exception as e:
        print(f"Mobile emulation error: {e}")
    
    finally:
        await controller.close()


async def error_handling_example():
    """Example demonstrating error handling and recovery."""
    
    config = BrowserConfig(
        browser_type=BrowserType.CHROME,
        headless=True,
        page_load_timeout=5.0  # Short timeout to demonstrate error handling
    )
    
    controller = BrowserController(config)
    
    try:
        async with controller.new_session() as session:
            # Try to navigate to non-existent domain
            try:
                await session.navigate_to("https://this-domain-does-not-exist-12345.com")
            except Exception as nav_error:
                print(f"Navigation failed as expected: {nav_error}")
            
            # Try to find non-existent element
            try:
                await session.find_element(("id", "non-existent-element"), timeout=2.0)
            except Exception as elem_error:
                print(f"Element not found as expected: {elem_error}")
            
            # Successful navigation after errors
            result = await session.navigate_to("https://httpbin.org/")
            print(f"Recovery successful: {result.success}")
            
    except Exception as e:
        print(f"Session error: {e}")
    
    finally:
        await controller.close()


def configuration_file_example():
    """Example using configuration file."""
    
    # Create configuration file
    config_data = {
        "browser_type": "chrome",
        "headless": True,
        "window_size": [1920, 1080],
        "implicit_wait": 10.0,
        "page_load_timeout": 30.0,
        "user_agent": "LAM-Browser-Controller/1.0",
        "disable_images": True,
        "browser_args": ["--disable-logging", "--disable-gpu"]
    }
    
    import json
    config_file = "browser_config.json"
    with open(config_file, 'w') as f:
        json.dump(config_data, f, indent=2)
    
    # Use configuration file
    controller = BrowserController(config_file=config_file)
    
    print(f"Controller created with config from {config_file}")
    print(f"Browser type: {controller.config.browser_type}")
    print(f"Headless mode: {controller.config.headless}")
    
    # Clean up
    Path(config_file).unlink(missing_ok=True)


async def main():
    """Run all examples."""
    
    print("=" * 60)
    print("Browser Controller Examples")
    print("=" * 60)
    
    examples = [
        ("Basic Usage", basic_usage_example),
        ("Session Management", session_management_example), 
        ("Form Interaction", form_interaction_example),
        ("Wait Strategies", wait_strategies_example),
        ("Mobile Emulation", mobile_emulation_example),
        ("Error Handling", error_handling_example),
    ]
    
    for name, example_func in examples:
        print(f"\n--- Running {name} Example ---")
        try:
            await example_func()
            print(f"✓ {name} example completed successfully")
        except Exception as e:
            print(f"✗ {name} example failed: {e}")
        
        # Small delay between examples
        await asyncio.sleep(1)
    
    print(f"\n--- Running Configuration File Example ---")
    try:
        configuration_file_example()
        print("✓ Configuration file example completed successfully")
    except Exception as e:
        print(f"✗ Configuration file example failed: {e}")
    
    print("\n" + "=" * 60)
    print("All examples completed!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
