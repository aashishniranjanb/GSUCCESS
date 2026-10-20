import os
from playwright.sync_api import sync_playwright

os.makedirs('reports/screenshots/four_screen_flow', exist_ok=True)

viewports = [
    ('360x800', 360, 800),
    ('393x852', 393, 852),
    ('768x1024', 768, 1024),
    ('1366x900', 1366, 900)
]

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    for name, w, h in viewports:
        context = browser.new_context(viewport={'width': w, 'height': h})
        page = context.new_page()
        
        # Screen 1: Syllabus Explorer (Home) - Reference A & Reference B Phone 1
        page.goto('http://localhost:3000/study', wait_until='domcontentloaded')
        page.wait_for_timeout(1000)
        page.screenshot(path=f'reports/screenshots/four_screen_flow/{name}_screen1_explorer_viewport.png', full_page=False)
        page.screenshot(path=f'reports/screenshots/four_screen_flow/{name}_screen1_explorer_full.png', full_page=True)
        
        # Screen 2: Subject Overview (Pharmacology) - Reference B Phone 2
        page.goto('http://localhost:3000/study?exam_subject=pharmacology', wait_until='domcontentloaded')
        page.wait_for_timeout(1000)
        page.screenshot(path=f'reports/screenshots/four_screen_flow/{name}_screen2_subject_viewport.png', full_page=False)
        page.screenshot(path=f'reports/screenshots/four_screen_flow/{name}_screen2_subject_full.png', full_page=True)
        
        # Screen 3: Unit View (Topic List) - Reference B Phone 3
        page.goto('http://localhost:3000/study?exam_subject=pharmacology&unit=pharmacology__anatomy_physiology_and_health_education', wait_until='domcontentloaded')
        page.wait_for_timeout(1000)
        page.screenshot(path=f'reports/screenshots/four_screen_flow/{name}_screen3_unit_viewport.png', full_page=False)
        page.screenshot(path=f'reports/screenshots/four_screen_flow/{name}_screen3_unit_full.png', full_page=True)
        
        # Screen 4: Topic Detail - Reference B Phone 4
        page.goto('http://localhost:3000/study?exam_subject=pharmacology&unit=pharmacology__anatomy_physiology_and_health_education&topic=pharmacology__anatomy_physiology_and_health_education__autonomic_nervous_system', wait_until='domcontentloaded')
        page.wait_for_timeout(1000)
        page.screenshot(path=f'reports/screenshots/four_screen_flow/{name}_screen4_topic_viewport.png', full_page=False)
        page.screenshot(path=f'reports/screenshots/four_screen_flow/{name}_screen4_topic_full.png', full_page=True)
        
        context.close()
    browser.close()
print('All 4-screen flow screenshots captured successfully!')
