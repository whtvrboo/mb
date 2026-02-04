from playwright.sync_api import sync_playwright, expect
import re

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            print("Navigating to verify-modal on port 3001...")
            page.goto("http://localhost:3001/verify-modal")

            # Modal should be open by default now
            print("Waiting for modal...")
            modal = page.locator('div[role="dialog"]')
            expect(modal).to_be_visible()

            # Verify ARIA attributes
            print("Verifying ARIA attributes...")
            expect(modal).to_have_attribute("aria-modal", "true")
            expect(modal).to_have_attribute("aria-labelledby", re.compile(r"v-0-\d+"))

            # Verify Close button
            close_btn = modal.get_by_role("button", name="Close modal")
            expect(close_btn).to_be_visible()

            # Screenshot
            print("Taking screenshot...")
            page.screenshot(path="verification/modal_accessibility.png")
            print("Success!")

        except Exception as e:
            print(f"Error: {e}")
            try:
                page.screenshot(path="verification/error.png")
            except:
                pass
            raise e
        finally:
            browser.close()

if __name__ == "__main__":
    run()
