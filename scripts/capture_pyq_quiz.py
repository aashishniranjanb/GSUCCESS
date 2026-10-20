import asyncio
import os
from playwright.async_api import async_playwright

VIEWPORTS = [
    {"name": "mobile_393", "width": 393, "height": 852},
    {"name": "mobile_360", "width": 360, "height": 800},
    {"name": "tablet_768", "width": 768, "height": 1024},
    {"name": "desktop_1366", "width": 1366, "height": 900},
]

OUTPUT_DIR = "reports/screenshots/pyq_quiz"

async def capture_pyq_quiz():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        for vp in VIEWPORTS:
            context = await browser.new_context(
                viewport={"width": vp["width"], "height": vp["height"]},
                device_scale_factor=2,
            )
            page = await context.new_page()

            # 1. Load PYQ Quiz page
            await page.goto("http://localhost:3000/pyqs", wait_until="domcontentloaded")
            await page.wait_for_selector("button:has-text('Filters')", timeout=10000)
            await page.wait_for_selector("fieldset button", timeout=15000)
            await page.wait_for_timeout(600)

            # Unanswered state
            await page.screenshot(
                path=f"{OUTPUT_DIR}/{vp['name']}_unanswered.png",
                full_page=False,
            )
            print(f"Captured {vp['name']}_unanswered.png")

            # For mobile_393: Capture Filter Dialog, Correct Answer, and Incorrect Answer
            if vp["name"] == "mobile_393":
                # Open Filters
                filter_btn = page.locator("button", has_text="Filters")
                if await filter_btn.count() > 0:
                    await filter_btn.first.click()
                    await page.wait_for_timeout(600)
                    await page.screenshot(
                        path=f"{OUTPUT_DIR}/393x852_filters_open.png",
                        full_page=False,
                    )
                    print("Captured 393x852_filters_open.png")
                    # Close filter dialog
                    close_btn = page.locator("button[aria-label='Close filters']")
                    if await close_btn.count() > 0:
                        await close_btn.click()
                        await page.wait_for_timeout(400)

                # Click Option A (Option 0 is active metabolite acyclovir triphosphate which is correct for Q1)
                opt_a = page.locator("fieldset button").first
                if await opt_a.count() > 0:
                    await opt_a.click()
                    await page.wait_for_timeout(1000)
                    await page.screenshot(
                        path=f"{OUTPUT_DIR}/393x852_correct.png",
                        full_page=False,
                    )
                    print("Captured 393x852_correct.png")

                # Advance to next question to test incorrect answer
                next_btn = page.locator("button", has_text="Next Question")
                if await next_btn.count() > 0:
                    await next_btn.click()
                    await page.wait_for_timeout(1200)

                    # Click wrong option (Option D - 4th button)
                    opt_wrong = page.locator("fieldset button").nth(3)
                    if await opt_wrong.count() > 0:
                        await opt_wrong.click()
                        await page.wait_for_timeout(1000)
                        await page.screenshot(
                            path=f"{OUTPUT_DIR}/393x852_incorrect.png",
                            full_page=False,
                        )
                        print("Captured 393x852_incorrect.png")

            await context.close()

        await browser.close()

if __name__ == "__main__":
    asyncio.run(capture_pyq_quiz())
