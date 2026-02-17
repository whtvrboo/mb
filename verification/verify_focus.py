from playwright.sync_api import sync_playwright

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()
    try:
        page.goto("http://localhost:3000/verify-focus")

        # Wait for the page to load
        page.wait_for_selector('h1:text("Focus Verification")')

        # Press Tab to reach the checkbox
        found_checkbox = False
        for i in range(10):
            page.keyboard.press("Tab")
            page.wait_for_timeout(200)

            # Check active element
            is_checkbox = page.evaluate("""
                () => {
                    const active = document.activeElement;
                    return active && active.type === 'checkbox';
                }
            """)

            if is_checkbox:
                found_checkbox = True
                break

        if found_checkbox:
            print("Checkbox focused!")
            page.screenshot(path="verification/checkbox_focus.png")
        else:
            print("Checkbox NOT focused!")
            # Take a debug screenshot
            page.screenshot(path="verification/debug_fail.png")

        # Now press Tab to go to Radio
        # Depending on tab order, radio might be next.
        # But wait, radio buttons in a group are treated as a single tab stop?
        # Let's see.

        found_radio = False
        for i in range(5):
             page.keyboard.press("Tab")
             page.wait_for_timeout(200)

             is_radio = page.evaluate("""
                () => {
                    const active = document.activeElement;
                    return active && active.type === 'radio';
                }
            """)

             if is_radio:
                 found_radio = True
                 break

        if found_radio:
            print("Radio focused!")
            page.screenshot(path="verification/radio_focus.png")
        else:
            print("Radio NOT focused!")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        browser.close()

with sync_playwright() as playwright:
    run(playwright)
