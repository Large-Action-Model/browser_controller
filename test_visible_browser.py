#!/usr/bin/env python3
"""
Visible Browser Test - Shows browser window and demonstrates screenshot location

This test runs with headless=False so you can see the browser in action.
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


async def visible_browser_test():
    """Test with visible browser window"""
    print("🌐 Testing with VISIBLE browser...")
    print("📍 Current working directory:", os.getcwd())
    print()
    
    # Create configuration for VISIBLE browser
    config = BrowserConfig(
        browser_type=BrowserType.CHROME,
        headless=False,  # Show the browser window!
        window_size=(1280, 720),
        page_load_timeout=30,
        implicit_wait=10
    )
    
    async with BrowserController(config) as controller:
        # Create a session
        session = await controller.create_session()
        
        try:
            print("✓ Browser window should be visible now!")
            
            # Navigate to a test page
            print("📂 Navigating to test page...")
            await session.navigate_to("https://httpbin.org/html")
            
            # Wait a bit so you can see the page
            print("⏳ Waiting 3 seconds so you can see the page...")
            await asyncio.sleep(3)
            
            # Try to find an element
            title_element = await session.find_element("h1")
            if title_element:
                print("✓ Found title element on page")
            
            # Take a screenshot and show exactly where it's saved
            screenshot_filename = "visible_test_screenshot.png"
            screenshot_path = os.path.abspath(screenshot_filename)
            
            print(f"📸 Taking screenshot...")
            print(f"📍 Screenshot will be saved to: {screenshot_path}")
            
            success = await session.take_screenshot(screenshot_filename)
            
            if success and os.path.exists(screenshot_filename):
                file_size = os.path.getsize(screenshot_filename)
                print(f"✅ Screenshot saved successfully!")
                print(f"📁 File location: {screenshot_path}")
                print(f"📏 File size: {file_size:,} bytes")
                
                # Show directory contents to confirm
                print(f"📂 Current directory contents:")
                for item in os.listdir("."):
                    if item.endswith(('.png', '.jpg', '.jpeg')):
                        print(f"   🖼️  {item}")
            else:
                print("❌ Screenshot failed")
            
            print("⏳ Waiting 5 more seconds before closing...")
            await asyncio.sleep(5)
            
        except Exception as e:
            print(f"❌ Error: {e}")
        
        finally:
            print("🔒 Closing browser session...")
            await controller.close_session(session.session_id)
    
    print("✅ Test completed!")


async def screenshot_location_test():
    """Test different screenshot locations"""
    print("\n" + "="*60)
    print("📸 Screenshot Location Test")
    print("="*60)
    
    config = BrowserConfig(
        browser_type=BrowserType.CHROME,
        headless=True,  # Keep headless for this test
        window_size=(1280, 720)
    )
    
    async with BrowserController(config) as controller:
        session = await controller.create_session()
        
        try:
            await session.navigate_to("https://httpbin.org/html")
            
            # Test different screenshot paths
            test_cases = [
                "screenshot1.png",  # Current directory
                "screenshots/screenshot2.png",  # Subdirectory
                os.path.join(os.getcwd(), "screenshot3.png"),  # Absolute path
            ]
            
            for i, screenshot_path in enumerate(test_cases, 1):
                print(f"\n📸 Test {i}: {screenshot_path}")
                
                # Create directory if needed
                screenshot_dir = os.path.dirname(screenshot_path)
                if screenshot_dir and not os.path.exists(screenshot_dir):
                    os.makedirs(screenshot_dir)
                    print(f"📁 Created directory: {screenshot_dir}")
                
                # Take screenshot
                success = await session.take_screenshot(screenshot_path)
                
                if success and os.path.exists(screenshot_path):
                    abs_path = os.path.abspath(screenshot_path)
                    file_size = os.path.getsize(screenshot_path)
                    print(f"✅ Screenshot saved!")
                    print(f"📍 Absolute path: {abs_path}")
                    print(f"📏 File size: {file_size:,} bytes")
                else:
                    print(f"❌ Screenshot failed: {screenshot_path}")
        
        finally:
            await controller.close_session(session.session_id)


async def main():
    """Run both tests"""
    print("🚀 Browser Visibility and Screenshot Location Tests")
    print("="*60)
    
    try:
        # Test 1: Visible browser
        await visible_browser_test()
        
        # Test 2: Screenshot locations
        await screenshot_location_test()
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    return True


if __name__ == "__main__":
    # Run the tests
    success = asyncio.run(main())
    print("\n" + "="*60)
    if success:
        print("🎉 All tests completed successfully!")
        print("\nKey Points:")
        print("• Set headless=False to see the browser window")
        print("• Screenshots are saved to the current working directory by default")
        print("• You can specify absolute or relative paths for screenshots")
        print("• Check the file paths printed above to find your screenshots")
    else:
        print("❌ Some tests failed")
    print("="*60)
    
    sys.exit(0 if success else 1)
