"""
DOM Test Example - Test the get_dom() method

This example demonstrates how to use the BrowserController's get_dom() method
to retrieve complete HTML source for DOM analysis components.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.browser_controller import BrowserController
from src.config.browser_config import BrowserConfig
from src.types.browser_types import BrowserType


async def test_dom_retrieval():
    """Test DOM retrieval from different websites."""
    
    # Create browser configuration
    config = BrowserConfig(
        browser_type=BrowserType.CHROME,
        headless=False,  # Set to False to see browser in action
        window_size=(1200, 800),
        implicit_wait=10,
        page_load_timeout=30
    )
    
    # Initialize browser controller
    controller = BrowserController(config=config)
    
    try:
        print("🚀 Starting DOM test...")
        
        # Launch browser
        await controller.launch()
        print("✅ Browser launched successfully")
        
        # Test websites with different DOM structures
        test_urls = [
            "https://httpbin.org/html",  # Simple HTML page
            "https://example.com",       # Basic example page
            "https://www.google.com"     # Complex modern page
        ]
        
        for i, url in enumerate(test_urls, 1):
            print(f"\n📄 Test {i}: Navigating to {url}")
            
            try:
                # Navigate to website
                result = await controller.navigate_to(url)
                print(f"   ✅ Navigation successful: {result.success}")
                print(f"   📍 Final URL: {result.url}")
                if result.load_time:
                    print(f"   ⏱️  Load time: {result.load_time:.2f}s")
                
                # Get DOM
                print("   🔍 Retrieving DOM...")
                dom_html = await controller.get_dom()
                
                # Analyze DOM
                dom_size = len(dom_html)
                line_count = dom_html.count('\n')
                
                # Count basic elements
                tag_counts = {
                    'div': dom_html.lower().count('<div'),
                    'span': dom_html.lower().count('<span'),
                    'p': dom_html.lower().count('<p>'),
                    'a': dom_html.lower().count('<a'),
                    'img': dom_html.lower().count('<img'),
                    'script': dom_html.lower().count('<script'),
                    'style': dom_html.lower().count('<style')
                }
                
                print(f"   📊 DOM Analysis:")
                print(f"      Size: {dom_size:,} characters")
                print(f"      Lines: {line_count:,}")
                print(f"      Elements found:")
                for tag, count in tag_counts.items():
                    if count > 0:
                        print(f"        - {tag}: {count}")
                
                # Show DOM preview (first 200 chars)
                preview = dom_html[:200].replace('\n', ' ').strip()
                if len(dom_html) > 200:
                    preview += "..."
                print(f"   📝 DOM Preview: {preview}")
                
                # Save DOM to file for inspection
                filename = f"dom_sample_{i}.html"
                filepath = Path(__file__).parent / filename
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(dom_html)
                print(f"   💾 DOM saved to: {filename}")
                
            except Exception as e:
                print(f"   ❌ Error with {url}: {str(e)}")
            
            # Wait between tests
            if i < len(test_urls):
                print("   ⏳ Waiting 2 seconds...")
                await asyncio.sleep(2)
        
        print("\n🎯 Testing DOM with session context manager...")
        
        # Test using session context manager
        async with controller.new_session() as session:
            await session.navigate_to("https://httpbin.org/json")
            
            # Get DOM through controller (should work even with active session)
            dom_html = await controller.get_dom()
            print(f"   📊 Session DOM size: {len(dom_html):,} characters")
            
            # Also test getting page info
            page_info = await session.get_page_info()
            print(f"   📄 Page title: {page_info.title}")
            print(f"   🔗 Page URL: {page_info.url}")
        
        print("\n✅ All DOM tests completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        raise
    
    finally:
        # Clean up
        await controller.close()
        print("🧹 Browser closed and cleanup completed")


async def test_dom_analysis_simulation():
    """Simulate how DOM would be used with an analyzer component."""
    
    print("\n🔬 Simulating DOM Analysis Component Integration...")
    
    config = BrowserConfig(
        browser_type=BrowserType.CHROME,
        headless=True,  # Run headless for this test
        window_size=(1200, 800)
    )
    
    controller = BrowserController(config=config)
    
    try:
        await controller.launch()
        
        # Navigate to a page with structured content
        await controller.navigate_to("https://httpbin.org/html")
        
        # Get DOM for analysis
        dom_html = await controller.get_dom()
        
        # Simulate DOM analyzer component
        print("   🤖 Simulating DOM Analyzer Component...")
        
        def mock_dom_analyzer(html_content):
            """Mock DOM analyzer that would process the HTML."""
            import re
            
            analysis = {
                "total_size": len(html_content),
                "elements": {
                    "headings": len(re.findall(r'<h[1-6]', html_content, re.IGNORECASE)),
                    "paragraphs": len(re.findall(r'<p>', html_content, re.IGNORECASE)),
                    "links": len(re.findall(r'<a\s+[^>]*href', html_content, re.IGNORECASE)),
                    "images": len(re.findall(r'<img\s+[^>]*src', html_content, re.IGNORECASE)),
                    "forms": len(re.findall(r'<form', html_content, re.IGNORECASE)),
                    "inputs": len(re.findall(r'<input', html_content, re.IGNORECASE))
                },
                "has_javascript": '<script' in html_content.lower(),
                "has_css": '<style' in html_content.lower() or 'stylesheet' in html_content.lower(),
                "doctype": html_content.strip().startswith('<!DOCTYPE') or html_content.strip().startswith('<!doctype')
            }
            
            return analysis
        
        # Analyze the DOM
        analysis_result = mock_dom_analyzer(dom_html)
        
        print("   📊 DOM Analysis Results:")
        print(f"      Total Size: {analysis_result['total_size']:,} characters")
        print(f"      Elements Found:")
        for element_type, count in analysis_result['elements'].items():
            if count > 0:
                print(f"        - {element_type.title()}: {count}")
        
        print(f"      Has JavaScript: {'Yes' if analysis_result['has_javascript'] else 'No'}")
        print(f"      Has CSS: {'Yes' if analysis_result['has_css'] else 'No'}")
        print(f"      Valid HTML5: {'Yes' if analysis_result['doctype'] else 'No'}")
        
        print("   ✅ DOM analysis simulation completed!")
        
    finally:
        await controller.close()


def main():
    """Run the DOM tests."""
    print("🧪 Browser Controller DOM Test Suite")
    print("=" * 50)
    
    # Run async tests
    asyncio.run(test_dom_retrieval())
    
    print("\n" + "=" * 50)
    
    # Run DOM analysis simulation
    asyncio.run(test_dom_analysis_simulation())
    
    print("\n🎉 All tests completed!")


if __name__ == "__main__":
    main()