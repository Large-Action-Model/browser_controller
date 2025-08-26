#!/usr/bin/env python3
"""
Real Browser Automation Test for Browser Controller

This test demonstrates actual browser automation capabilities:
- Opening a browser
- Navigating to websites
- Interacting with page elements
- Taking screenshots
- Proper cleanup

Prerequisites:
- Internet connection
- Browser drivers (handled automatically by webdriver-manager)
"""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.browser_controller import BrowserController
from src.config.browser_config import BrowserConfig
from src.types.browser_types import BrowserType


async def test_basic_navigation():
    """Test basic browser navigation and page interaction"""
    print("🌐 Testing basic navigation and interaction...")
    
    # Create configuration for headless testing
    config = BrowserConfig(
        browser_type=BrowserType.CHROME,
        headless=True,  # Run in headless mode for CI/automated testing
        window_size=(1280, 720),
        page_load_timeout=30,
        implicit_wait=10
    )
    
    async with BrowserController(config) as controller:
        # Create a session
        session = await controller.create_session()
        
        try:
            # Navigate to a simple test page
            await session.navigate_to("https://httpbin.org/html")
            print("✓ Successfully navigated to test page")
            
            # Try to find an element
            title_element = await session.find_element("h1")
            if title_element:
                print("✓ Found title element on page")
            
            # Take a screenshot
            screenshot_path = "test_screenshot.png"
            success = await session.take_screenshot(screenshot_path)
            if success and os.path.exists(screenshot_path):
                print(f"✓ Screenshot saved to {screenshot_path}")
                # Clean up screenshot
                os.remove(screenshot_path)
            
        except Exception as e:
            print(f"❌ Error during navigation test: {e}")
            return False
        
        finally:
            await controller.close_session(session.session_id)
    
    return True


async def test_form_interaction():
    """Test form interaction capabilities"""
    print("📝 Testing form interaction...")
    
    config = BrowserConfig(
        browser_type=BrowserType.CHROME,
        headless=True,
        window_size=(1280, 720)
    )
    
    async with BrowserController(config) as controller:
        session = await controller.create_session()
        
        try:
            # Navigate to httpbin forms page
            await session.navigate_to("https://httpbin.org/forms/post")
            print("✓ Navigated to forms test page")
            
            # Try to interact with form elements
            # Find input field by name
            custname_input = await session.find_element("input[name='custname']")
            if custname_input:
                await session.type_text("input[name='custname']", "Test User")
                print("✓ Successfully typed in form field")
            
            # Find and interact with radio button
            size_radio = await session.find_element("input[value='medium']")
            if size_radio:
                await session.click_element("input[value='medium']")
                print("✓ Successfully clicked radio button")
            
        except Exception as e:
            print(f"❌ Error during form interaction test: {e}")
            return False
        
        finally:
            await controller.close_session(session.session_id)
    
    return True


async def test_multiple_sessions():
    """Test managing multiple browser sessions"""
    print("🔄 Testing multiple sessions...")
    
    config = BrowserConfig(
        browser_type=BrowserType.CHROME,
        headless=True,
        window_size=(1280, 720)
    )
    
    async with BrowserController(config) as controller:
        sessions = []
        
        try:
            # Create multiple sessions
            for i in range(3):
                session = await controller.create_session()
                sessions.append(session)
                await session.navigate_to("https://httpbin.org/html")
            
            print(f"✓ Successfully created and navigated {len(sessions)} sessions")
            
            # Verify all sessions are active
            active_sessions = controller.get_active_sessions()
            if len(active_sessions) == 3:
                print("✓ All sessions are properly tracked")
            
        except Exception as e:
            print(f"❌ Error during multiple sessions test: {e}")
            return False
        
        finally:
            # Clean up all sessions
            for session in sessions:
                await controller.close_session(session.session_id)
    
    return True


async def test_error_handling():
    """Test error handling and recovery"""
    print("⚠️  Testing error handling...")
    
    config = BrowserConfig(
        browser_type=BrowserType.CHROME,
        headless=True,
        page_load_timeout=5  # Short timeout to test timeout handling
    )
    
    async with BrowserController(config) as controller:
        session = await controller.create_session()
        
        try:
            # Test invalid URL handling
            try:
                await session.navigate_to("http://this-domain-should-not-exist-12345.com")
                print("❌ Should have failed on invalid URL")
                return False
            except Exception:
                print("✓ Properly handled invalid URL")
            
            # Test element not found handling
            await session.navigate_to("https://httpbin.org/html")
            element = await session.find_element("non-existent-element")
            if element is None:
                print("✓ Properly handled element not found")
            
        except Exception as e:
            print(f"❌ Unexpected error during error handling test: {e}")
            return False
        
        finally:
            await controller.close_session(session.session_id)
    
    return True


async def main():
    """Run all browser automation tests"""
    print("=" * 60)
    print("Browser Controller - Real Browser Automation Tests")
    print("=" * 60)
    print()
    
    tests = [
        ("Basic Navigation", test_basic_navigation),
        ("Form Interaction", test_form_interaction),
        ("Multiple Sessions", test_multiple_sessions),
        ("Error Handling", test_error_handling)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"--- Running {test_name} Test ---")
        try:
            success = await test_func()
            if success:
                print(f"✓ {test_name} test PASSED")
                passed += 1
            else:
                print(f"❌ {test_name} test FAILED")
                failed += 1
        except Exception as e:
            print(f"❌ {test_name} test FAILED with exception: {e}")
            failed += 1
        print()
    
    print("=" * 60)
    print(f"Test Results: {passed} PASSED, {failed} FAILED")
    
    if failed == 0:
        print("🎉 All browser automation tests passed!")
        print()
        print("Your Browser Controller is ready for:")
        print("• Web scraping and data extraction")
        print("• Automated testing and form submission")
        print("• UI interaction and screenshot capture")
        print("• Integration with other LAM components")
    else:
        print("❌ Some tests failed. Check your setup:")
        print("• Internet connection")
        print("• Browser installation (Chrome recommended)")
        print("• Firewall/antivirus settings")
    
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    # Run the tests
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
