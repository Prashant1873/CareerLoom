import os
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

SCREENSHOTS_DIR = Path(__file__).resolve().parent.parent / "screenshots"
SCREENSHOTS_DIR.mkdir(parents=True, exist_ok=True)

def take_all_screenshots():
    print("Launching Chromium...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Create high-DPI desktop browser context
        context = browser.new_context(
            viewport={"width": 1440, "height": 900},
            device_scale_factor=2, # High-res retina
            color_scheme="light",
        )
        page = context.new_page()

        print("Navigating to CareerLoom UI...")
        page.goto("http://localhost:5173", wait_until="networkidle")

        # Ensure light mode is strictly set
        page.evaluate("""() => {
            localStorage.setItem('careerloom_theme', 'light');
            document.documentElement.setAttribute('data-theme', 'light');
        }""")
        
        # Click the light mode segment button if available
        try:
            light_btn = page.locator('button.theme-segment-btn:has-text("Light")')
            if light_btn.count() > 0:
                light_btn.first.click()
        except Exception as e:
            print(f"Theme toggle click note: {e}")

        page.wait_for_timeout(1000)

        # Wait for job cards to render
        try:
            page.wait_for_selector(".stream-job-card, .job-card, [data-testid='job-card']", timeout=10000)
        except Exception as e:
            print(f"Job card selector note: {e}")

        page.wait_for_timeout(1500)

        # 1. Main Dashboard Overview in Light Mode
        shot_1 = SCREENSHOTS_DIR / "01_light_mode_dashboard.png"
        page.screenshot(path=str(shot_1))
        print(f"Saved: {shot_1.name}")

        # 2. Job Detail / Inspector Pane
        try:
            cards = page.locator(".stream-job-card, .job-card")
            if cards.count() > 0:
                cards.first.click()
                page.wait_for_timeout(1200)
                shot_2 = SCREENSHOTS_DIR / "02_light_mode_job_detail.png"
                page.screenshot(path=str(shot_2))
                print(f"Saved: {shot_2.name}")
        except Exception as e:
            print(f"Error capturing job detail: {e}")

        # 3. Career Directory Modal
        try:
            dir_btn = page.locator('button:has-text("Directory"), .career-directory-nav-btn, [data-testid="career-directory-btn"]')
            if dir_btn.count() > 0:
                dir_btn.first.click()
                page.wait_for_timeout(1500)
                shot_3 = SCREENSHOTS_DIR / "03_light_mode_career_directory.png"
                page.screenshot(path=str(shot_3))
                print(f"Saved: {shot_3.name}")

                # Close modal with Esc
                page.keyboard.press("Escape")
                page.wait_for_timeout(800)
        except Exception as e:
            print(f"Error capturing directory modal: {e}")

        # 4. Filter by India PM Roles & Metro Tech Hub
        try:
            pm_btn = page.locator('.pm-direct-nav-btn, .pm-pill')
            if pm_btn.count() > 0:
                pm_btn.first.click()
                page.wait_for_timeout(1500)
                shot_4 = SCREENSHOTS_DIR / "04_light_mode_india_leads.png"
                page.screenshot(path=str(shot_4))
                print(f"Saved: {shot_4.name}")
        except Exception as e:
            print(f"Error capturing India view: {e}")

        # 5. Natural Language Omnibox Search
        try:
            search_input = page.locator('.omnibox-input, input[placeholder*="Search"], input[type="text"]')
            if search_input.count() > 0:
                search_input.first.click()
                search_input.first.fill("product entry level")
                page.keyboard.press("Enter")
                page.wait_for_timeout(1500)
                shot_5 = SCREENSHOTS_DIR / "05_light_mode_nlp_search.png"
                page.screenshot(path=str(shot_5))
                print(f"Saved: {shot_5.name}")
        except Exception as e:
            print(f"Error capturing search view: {e}")

        # 6. Referral Pitch Generator Modal & Generated Pitch View
        try:
            ref_btn = page.locator('.stream-referral-btn, .inspector-referral-btn')
            if ref_btn.count() > 0:
                ref_btn.first.click()
                page.wait_for_timeout(1000)
                # Fill form fields
                page.locator('input[placeholder*="Arjun"]').fill('Aarav Patel')
                page.locator('input[placeholder*="example.com"]').fill('aarav@example.com')
                page.locator('input[placeholder*="linkedin"]').fill('https://linkedin.com/in/aarav')
                page.locator('input[placeholder*="drive"]').fill('https://drive.google.com/file/d/sample')
                page.wait_for_timeout(500)
                shot_6 = SCREENSHOTS_DIR / "06_light_mode_referral_modal.png"
                page.screenshot(path=str(shot_6))
                print(f"Saved: {shot_6.name}")

                # Submit to view generated pitch
                submit_btn = page.locator('.lead-submit-btn')
                if submit_btn.count() > 0:
                    submit_btn.first.click()
                    page.wait_for_selector('.pitch-textarea', timeout=8000)
                    page.wait_for_timeout(1000)
                    shot_7 = SCREENSHOTS_DIR / "07_light_mode_referral_pitch.png"
                    page.screenshot(path=str(shot_7))
                    print(f"Saved: {shot_7.name}")

                page.keyboard.press("Escape")
                page.wait_for_timeout(600)
        except Exception as e:
            print(f"Error capturing referral modal: {e}")

        browser.close()
        print("All screenshots successfully captured!")

if __name__ == "__main__":
    take_all_screenshots()
