#!/usr/bin/env python3
"""
Test Playwright browser functionality
"""

import asyncio
from playwright.async_api import async_playwright

async def test_browser():
    """Test if Playwright browser works correctly"""
    print("🧪 Testing Playwright Browser")
    print("=" * 60)
    
    try:
        print("\n1. Starting Playwright...")
        playwright = await async_playwright().start()
        print("   ✅ Playwright started")
        
        print("\n2. Launching Chromium browser...")
        browser = await playwright.chromium.launch(
            headless=False,  # Show the browser
            slow_mo=500      # Slow down for visibility
        )
        print("   ✅ Browser launched")
        
        print("\n3. Creating new page...")
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        page = await context.new_page()
        print("   ✅ Page created")
        
        print("\n4. Navigating to test site...")
        await page.goto('https://example.com')
        print("   ✅ Navigation successful")
        
        print("\n5. Taking screenshot...")
        await page.screenshot(path='test_screenshot.png')
        print("   ✅ Screenshot saved as test_screenshot.png")
        
        print("\n6. Waiting 3 seconds...")
        await page.wait_for_timeout(3000)
        
        print("\n7. Closing browser...")
        await browser.close()
        await playwright.stop()
        print("   ✅ Browser closed cleanly")
        
        print("\n" + "=" * 60)
        print("✅ All tests passed! Playwright is working correctly.")
        print("\nYou can now run the main agent:")
        print("   python3 aiviizn_real_agent.py")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Install Playwright browser:")
        print("      python3 -m playwright install chromium")
        print("   2. If on macOS, you may need to allow app in Security settings")
        print("   3. Try with headless mode:")
        print("      Change headless=False to headless=True")
        return False

def main():
    """Run the test"""
    success = asyncio.run(test_browser())
    if not success:
        print("\n⚠️ Please fix the issues above before running the agent")
        exit(1)

if __name__ == "__main__":
    main()
