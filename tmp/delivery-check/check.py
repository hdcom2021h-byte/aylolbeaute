from playwright.sync_api import sync_playwright
from datetime import date, timedelta

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe', headless=True)
    page = browser.new_page(viewport={'width': 1440, 'height': 900}, reduced_motion='reduce')
    errors, bad = [], []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.on('response', lambda r: bad.append((r.status, r.url)) if r.status >= 400 else None)
    page.goto('http://127.0.0.1:8000/index.html')
    page.locator('#aylolHeader').wait_for()
    page.evaluate('document.fonts.ready')
    for w, h in [(1440, 900), (820, 1180), (390, 844)]:
        page.set_viewport_size({'width': w, 'height': h})
        for target in ['services', 'reservations', 'prices', 'gallery', 'offers', 'contact', 'booking', 'home']:
            if w <= 1080:
                page.locator('#aylolMenuBtn').click()
                page.locator('.aylol-mobile-links a[href="#' + target + '"]').click()
            else:
                page.locator('.aylol-nav a[href="#' + target + '"]').click()
            page.wait_for_timeout(120)
            g = page.evaluate('''id=>{const s=document.getElementById(id),c=s.querySelector(':scope > .container')||s;
                return {top:c.getBoundingClientRect().top,header:document.getElementById('aylolHeader').getBoundingClientRect().bottom,
                overflow:document.documentElement.scrollWidth>innerWidth}}''', target)
            assert not g['overflow'], (w, target, g)
            if target != 'home': assert g['top'] >= g['header'] - 2, (w, target, g)
        print('PASS navigation', w, h, flush=True)
        page.screenshot(path=f'tmp/delivery-check/home-{w}.png')
    page.set_viewport_size({'width': 1440, 'height': 900})
    summary = page.locator('.price-card summary').first
    summary.click()
    assert page.locator('.price-card').first.evaluate('(e)=>e.open')
    summary.click()
    assert not page.locator('.price-card').first.evaluate('(e)=>e.open')
    page.locator('#priceSearch').fill('150')
    assert page.locator('.price-card[open]').count() > 0
    page.locator('#priceSearch').fill('')
    page.locator('[data-gallery-filter="nails"]').click()
    assert page.locator('.gallery-item:not(.hidden)').count() == 7
    page.locator('.gallery-item:not(.hidden)').first.click()
    assert 'open' in page.locator('#lightboxModal').get_attribute('class')
    page.keyboard.press('Escape')
    assert 'open' not in page.locator('#lightboxModal').get_attribute('class')
    page.locator('[data-gallery-filter="hair"]').click()
    assert page.locator('.gallery-item:not(.hidden)').count() == 1
    page.locator('.gallery-video-card').click()
    assert page.locator('#galleryVideoDialog').evaluate('(e)=>e.open')
    page.keyboard.press('Escape')
    assert not page.locator('#galleryVideoDialog').evaluate('(e)=>e.open')
    page.locator('[data-gallery-filter="all"]').click()
    page.locator('#nationalOfferDetails').click()
    assert page.locator('#nationalOfferDialog').evaluate('(e)=>e.open')
    page.keyboard.press('Escape')
    assert not page.locator('#nationalOfferDialog').evaluate('(e)=>e.open')
    page.locator('input[name="rating"][value="4"]').check()
    page.locator('#anonymousReviewNote').fill('Review test')
    page.locator('#anonymousReviewForm button[type="submit"]').click()
    assert page.locator('[data-anonymous-review]').count() == 1
    page.locator('#customerName').fill('Test')
    page.locator('#customerPhone').fill('0560000000')
    page.locator('#bookingDate').fill((date.today() + timedelta(days=3)).isoformat())
    page.locator('#bookingTime').fill('10:00')
    page.locator('#bookingService').select_option(index=1)
    page.locator('#bookingForm button[type="submit"]').click()
    assert 'open' in page.locator('#bookingModal').get_attribute('class')
    page.keyboard.press('Escape')
    page.locator('.aylol-nav a[href="#contact"]').click()
    page.wait_for_timeout(150)
    page.screenshot(path='tmp/delivery-check/contact-desktop.png')
    print('PASS prices, dialogs, anonymous rating and booking preview', flush=True)
    print('HTTP_FAILURES', bad, 'JS_ERRORS', errors, flush=True)
    assert not errors and not bad
    browser.close()
