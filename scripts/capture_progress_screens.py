import asyncio
import os
from playwright.async_api import async_playwright

VIEWPORTS = [
    {"name": "mobile_393", "width": 393, "height": 852},
    {"name": "mobile_360", "width": 360, "height": 800},
    {"name": "tablet_768", "width": 768, "height": 1024},
    {"name": "desktop_1366", "width": 1366, "height": 900},
]

OUTPUT_DIR = "reports/screenshots/progress"

TABS = [
    {"tab": "overview", "label": "Overview"},
    {"tab": "syllabus", "label": "Syllabus"},
    {"tab": "activity", "label": "Activity"},
    {"tab": "performance", "label": "Mastery"},
    {"tab": "achievements", "label": "Rewards"},
]

async def capture_progress_experience():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        # 1. Capture 5 screens on Primary Target Viewport: 393x852
        ctx_393 = await browser.new_context(
            viewport={"width": 393, "height": 852},
            device_scale_factor=2,
        )
        page_393 = await ctx_393.new_page()

        for tab_info in TABS:
            url = f"http://localhost:3000/progress?tab={tab_info['tab']}" if tab_info["tab"] != "overview" else "http://localhost:3000/progress"
            await page_393.goto(url, wait_until="networkidle")
            await page_393.wait_for_timeout(1000)
            await page_393.screenshot(
                path=f"{OUTPUT_DIR}/393x852_screen_{tab_info['tab']}.png",
                full_page=False,
            )
            print(f"Captured 393x852_screen_{tab_info['tab']}.png")

        await ctx_393.close()

        # 2. Capture other viewports on default Overview screen
        for vp in VIEWPORTS:
            if vp["name"] == "mobile_393":
                continue

            ctx = await browser.new_context(
                viewport={"width": vp["width"], "height": vp["height"]},
                device_scale_factor=2,
            )
            p_vp = await ctx.new_page()
            await p_vp.goto("http://localhost:3000/progress", wait_until="networkidle")
            await p_vp.wait_for_timeout(1000)
            await p_vp.screenshot(
                path=f"{OUTPUT_DIR}/{vp['name']}_overview.png",
                full_page=False,
            )
            print(f"Captured {vp['name']}_overview.png")
            await ctx.close()

        await browser.close()

if __name__ == "__main__":
    asyncio.run(capture_progress_experience())
