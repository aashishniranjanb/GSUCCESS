import os
from playwright.sync_api import sync_playwright

os.makedirs('reports/screenshots/syllabus_discovery', exist_ok=True)

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
        
        # 1. Level 1: Subject Discovery View
        page.goto('http://localhost:3000/study', wait_until='domcontentloaded')
        page.wait_for_timeout(1500)
        page.screenshot(path=f'reports/screenshots/syllabus_discovery/{name}_level1_subjects_viewport.png', full_page=False)
        page.screenshot(path=f'reports/screenshots/syllabus_discovery/{name}_level1_subjects_full.png', full_page=True)
        
        # 2. Level 2: Selected Subject Topics View (e.g. Pharmacology)
        page.goto('http://localhost:3000/study?exam_subject=pharmacology', wait_until='domcontentloaded')
        page.wait_for_timeout(1500)
        page.screenshot(path=f'reports/screenshots/syllabus_discovery/{name}_level2_topics_viewport.png', full_page=False)
        page.screenshot(path=f'reports/screenshots/syllabus_discovery/{name}_level2_topics_full.png', full_page=True)
        
        context.close()
    browser.close()
print('All syllabus discovery screenshots captured successfully!')
