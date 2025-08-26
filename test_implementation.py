"""
Simple test to verify Browser Controller implementation works correctly.
"""

import asyncio
import sys
import traceback
from pathlib import Path

# Add current directory to path for testing
sys.path.insert(0, str(Path(__file__).parent))

try:
    from browser_controller import (
        BrowserController, BrowserConfig, BrowserType,
        create_browser_controller
    )
    print("✓ Successfully imported Browser Controller components")
except ImportError as e:
    print(f"✗ Import error: {e}")
    traceback.print_exc()
    sys.exit(1)


async def test_browser_controller_creation():
    """Test basic browser controller creation without launching browser."""
    try:
        # Test configuration creation
        config = BrowserConfig(
            browser_type=BrowserType.CHROME,
            headless=True,
            window_size=(1280, 720),
            implicit_wait=10.0
        )
        print("✓ BrowserConfig created successfully")
        
        # Test controller creation
        controller = BrowserController(config)
        print("✓ BrowserController created successfully")
        
        # Test convenience function
        controller2 = create_browser_controller("chrome", headless=True)
        print("✓ create_browser_controller works")
        
        # Test configuration validation
        print(f"Debug: browser_type is {type(controller.config.browser_type)}: {controller.config.browser_type}")
        print(f"Debug: BrowserType.CHROME is {type(BrowserType.CHROME)}: {BrowserType.CHROME}")
        
        # Handle both enum and string comparison
        if hasattr(controller.config.browser_type, 'value'):
            assert controller.config.browser_type == BrowserType.CHROME
        else:
            assert controller.config.browser_type == BrowserType.CHROME.value
            
        assert controller.config.headless == True
        assert controller.config.window_size == (1280, 720)
        print("✓ Configuration validation works")
        
        return True
        
    except Exception as e:
        print(f"✗ Browser Controller creation test failed: {e}")
        traceback.print_exc()
        return False


async def test_config_manager():
    """Test configuration management."""
    try:
        from src.config import ConfigManager
        
        # Test default config loading
        config_manager = ConfigManager()
        config = config_manager.get_config()
        
        print(f"✓ Default config loaded: {config.browser_type.value}")
        
        # Test config updates
        config_manager.update_config(headless=False, window_size=(1920, 1080))
        updated_config = config_manager.get_config()
        
        assert updated_config.headless == False
        assert updated_config.window_size == (1920, 1080)
        print("✓ Configuration updates work")
        
        return True
        
    except Exception as e:
        print(f"✗ Config Manager test failed: {e}")
        traceback.print_exc()
        return False


async def test_types_and_exceptions():
    """Test type definitions and custom exceptions."""
    try:
        from src.types import (
            BrowserType, ElementLocatorType, ViewportConfig,
            NavigationResult, PageInfo
        )
        from src.utils.exceptions import (
            BrowserControllerError, SessionError, NavigationError
        )
        
        # Test enum values
        assert BrowserType.CHROME.value == "chrome"
        assert ElementLocatorType.CSS_SELECTOR.value == "css_selector"
        print("✓ Enum types work correctly")
        
        # Test dataclass creation
        viewport = ViewportConfig(width=1920, height=1080)
        assert viewport.width == 1920
        print("✓ Configuration dataclasses work")
        
        # Test exception hierarchy
        try:
            raise SessionError("Test error", "test-session-123")
        except BrowserControllerError as e:
            assert e.session_id == "test-session-123"
            print("✓ Exception hierarchy works")
        
        return True
        
    except Exception as e:
        print(f"✗ Types and exceptions test failed: {e}")
        traceback.print_exc()
        return False


async def test_logging():
    """Test logging functionality."""
    try:
        from src.utils import get_logger, BrowserLogger
        
        # Test logger creation
        logger = get_logger("TestComponent")
        logger.info("Test log message")
        print("✓ Logger creation and basic logging works")
        
        # Test child logger
        child_logger = logger.create_child_logger("SubComponent")
        child_logger.debug("Child logger message")
        print("✓ Child logger creation works")
        
        return True
        
    except Exception as e:
        print(f"✗ Logging test failed: {e}")
        traceback.print_exc()
        return False


def test_package_structure():
    """Test package structure and imports."""
    try:
        # Test all main imports
        from browser_controller import (
            BrowserController, BrowserConfig, BrowserType,
            ProxyConfig, ViewportConfig, MobileEmulation,
            SessionMetadata, NavigationResult, PageInfo,
            BrowserControllerError, SessionError,
            get_logger, __version__
        )
        
        print(f"✓ Package imports successful, version: {__version__}")
        
        # Test internal module imports
        from src.core import BrowserController as CoreController
        from src.config import ConfigManager
        from src.utils import WaitStrategies
        from src.types import ElementLocatorType
        
        print("✓ Internal module imports successful")
        
        return True
        
    except Exception as e:
        print(f"✗ Package structure test failed: {e}")
        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("=" * 60)
    print("Browser Controller Implementation Test")
    print("=" * 60)
    
    tests = [
        ("Package Structure", test_package_structure),
        ("Browser Controller Creation", test_browser_controller_creation),
        ("Configuration Manager", test_config_manager),
        ("Types and Exceptions", test_types_and_exceptions), 
        ("Logging System", test_logging),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        print(f"\n--- Running {test_name} Test ---")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                print(f"✓ {test_name} test PASSED")
                passed += 1
            else:
                print(f"✗ {test_name} test FAILED")
                failed += 1
        except Exception as e:
            print(f"✗ {test_name} test FAILED with exception: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed} PASSED, {failed} FAILED")
    
    if failed == 0:
        print("🎉 All tests passed! Browser Controller implementation is working correctly.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run browser automation tests (requires browser drivers)")
        print("3. Integrate with other LAM components")
    else:
        print(f"⚠️  {failed} test(s) failed. Please review the errors above.")
    
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
