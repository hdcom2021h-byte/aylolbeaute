from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from datetime import date, timedelta
import json, re, functools
import html5lib, tinycss2
from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parents[2]
summary = {'html': [], 'css': [], 'javascript': [], 'viewports': [], 'issues': []}

def assert_path(value, relative_to=root):
    assert not re.match(r'^[A-Za-z]:|^file:|^\\', value), value
    if not value or value.startswith('#') or urlsplit(value).scheme: return
    path = relative_to / unquote(urlsplit(value).path)
    assert path.is_file(), str(path)
    # Linux hosting is case-sensitive, unlike the local Windows filesystem.
    current = root
    for part in path.relative_to(root).parts:
        assert part in [entry.name for entry in current.iterdir()], str(path)
        current = current / part

class Markup(HTMLParser):
    def __init__(self): super().__init__(); self.ids=[]; self.links=[]
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a: self.ids.append(a['id'])
        for key in ['src', 'href', 'poster']:
            if key in a:
                assert_path(a[key])
                if a[key].startswith('#'): self.links.append(a[key][1:])

markup = Markup()
scripts = []
def css_check(css, label):
    def rules_check(rules):
        for rule in rules:
            assert rule.type != 'error', (label, rule)
            if rule.type == 'qualified-rule' or (rule.type == 'at-rule' and rule.lower_at_keyword == 'font-face'):
                for item in tinycss2.parse_declaration_list(rule.content, skip_comments=True, skip_whitespace=True):
                    assert item.type != 'error', (label, item)
            elif rule.type == 'at-rule' and rule.content is not None:
                rules_check(tinycss2.parse_rule_list(rule.content, skip_comments=True, skip_whitespace=True))
    rules_check(tinycss2.parse_stylesheet(css, skip_comments=True, skip_whitespace=True))
    summary['css'].append(label)

for name in ['index.html', 'headr.html', 'footer.html']:
    text = (root/name).read_text(encoding='utf-8')
    parser = html5lib.HTMLParser()
    (parser.parse if name == 'index.html' else parser.parseFragment)(text)
    assert not parser.errors, (name, parser.errors)
    assert '\ufffd' not in text and not re.search(r'\?{3,}',text)
    markup.feed(text)
    scripts += [(name, s) for s in re.findall(r'<script(?:\s[^>]*)?>([\s\S]*?)</script>',text) if s.strip()]
    for css in re.findall(r'<style[^>]*>([\s\S]*?)</style>',text): css_check(css,name)
    summary['html'].append(name)
assert len(markup.ids) == len(set(markup.ids))
assert all(not link or link in markup.ids for link in markup.links)
for path in (root/'media').rglob('*.css'):
    text = path.read_text(encoding='utf-8'); css_check(text,str(path.relative_to(root)))
    for match in re.findall(r'url\([\'"]?([^\)\'"\s]+)',text): assert_path(match,path.parent)
for path in (root/'media').rglob('*.js'):
    scripts.append((str(path.relative_to(root)),path.read_text(encoding='utf-8')))
    assert not re.search(r'[A-Za-z]:[\\/]|file://',path.read_text(encoding='utf-8')),path
gallery=json.loads((root/'media/gallery/gallery.js').read_text(encoding='utf-8').split(' = ',1)[1].rstrip(';\n'))
for item in gallery: assert_path(item['src'])
summary['gallery_items']=len(gallery)
summary['largest_media_mb']=round(max(p.stat().st_size for p in (root/'media').rglob('*') if p.is_file())/1048576,2)

class Handler(SimpleHTTPRequestHandler):
    def log_message(self,*args): pass
    def copyfile(self,source,outputfile):
        try: super().copyfile(source,outputfile)
        except (ConnectionResetError,BrokenPipeError): pass
    def do_GET(self):
        if self.path.startswith('/preview/'):
            self.path=self.path[len('/preview'):]
        super().do_GET()
server=ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Handler,directory=str(root)))
Thread(target=server.serve_forever,daemon=True).start()
url=f'http://127.0.0.1:{server.server_port}/preview/'
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe',headless=True)
    context=browser.new_context(viewport={'width':1440,'height':900}, reduced_motion='reduce')
    page=context.new_page(); errors=[]; failed=[]; requests=[]
    page.on('pageerror',lambda e:errors.append(str(e)))
    page.on('response',lambda r:failed.append((r.status,r.url)) if r.status>=400 else None)
    page.on('request',lambda r:requests.append(r.url))
    page.goto(url+'index.html');page.locator('#aylolHeader').wait_for();page.locator('#aylolFooterYear').wait_for();page.evaluate('document.fonts.ready')
    print('PASS static parsing, paths, and subdirectory page load',flush=True)
    for label,script in scripts:
        page.evaluate('(script)=>{new Function(script);}',script)
        summary['javascript'].append(label)
    for width,height in [(320,740),(390,844),(768,1024),(820,1180),(1081,900),(1440,900),(1920,1080)]:
        page.set_viewport_size({'width':width,'height':height})
        for target in ['home','services','reservations','prices','gallery','offers','contact','booking']:
            if width<=1080:
                page.locator('#aylolMenuBtn').click();page.locator(f'.aylol-mobile-links a[href="#{target}"]').click()
            else:page.locator(f'.aylol-nav a[href="#{target}"]').click()
            page.wait_for_timeout(60)
            assert not page.evaluate('document.documentElement.scrollWidth>innerWidth'),(width,target)
            rect=page.evaluate('''id=>{let s=document.getElementById(id),c=s.querySelector(':scope>.container')||s;return {top:c.getBoundingClientRect().top,header:document.getElementById('aylolHeader').getBoundingClientRect().bottom}}''',target)
            if target!='home':assert rect['top']>=rect['header']-2,(width,target,rect)
        summary['viewports'].append([width,height])
        print('PASS viewport',width,flush=True)
    # Every footer anchor remains on this subdirectory and targets an existing element.
    for link in page.locator('#footer-placeholder a[href^="#"]').all():
        link.click();page.wait_for_timeout(50)
        assert page.url.startswith(url)
    # Validate all images, including lazy gallery assets, by visiting their sections.
    for selector in ['#services','#reservations','#gallery','#offers','#home']:
        page.locator(selector).scroll_into_view_if_needed()
    for image in page.locator('img[src]:visible').all():
        image.scroll_into_view_if_needed()
        image.evaluate('(i)=>i.decode()')
    page.locator('#nationalOfferDetails').click()
    page.locator('#nationalOfferDialog img').evaluate('(i)=>i.decode()')
    page.keyboard.press('Escape')
    assert page.locator('.gallery-item').count()==len(gallery)
    page.locator('[data-gallery-filter="hair"]').click();page.locator('.gallery-video-card').click()
    player=page.locator('#galleryVideoDialog video')
    page.wait_for_function("document.querySelector('#galleryVideoDialog video').readyState>=2")
    assert player.evaluate('(v)=>v.error===null')
    page.keyboard.press('Escape');assert player.evaluate('(v)=>v.paused')
    page.locator('[data-gallery-filter="all"]').click()
    # Focus must remain in the booking modal and return on close.
    page.locator('#customerName').fill('Test');page.locator('#customerPhone').fill('0560000000')
    page.locator('#bookingDate').fill((date.today()+timedelta(days=3)).isoformat())
    page.locator('#bookingTime').fill('10:00');page.locator('#bookingService').select_option(index=1)
    page.locator('#bookingForm button[type="submit"]').click()
    assert page.evaluate('document.activeElement.id')=='closeBookingModal'
    page.keyboard.press('Shift+Tab');assert page.evaluate('document.activeElement.id')=='sendWhatsAppBooking'
    page.keyboard.press('Tab');assert page.evaluate('document.activeElement.id')=='closeBookingModal'
    page.keyboard.press('Escape');assert page.locator('#bookingForm button[type="submit"]').evaluate('(e)=>e===document.activeElement')
    page.set_viewport_size({'width':390,'height':844})
    page.locator('#aylolMenuBtn').click();page.locator('#aylolMenuClose').click()
    assert page.evaluate('document.activeElement.id')=='aylolMenuBtn'
    # Direct URL navigation after component loading.
    page.goto(url+'index.html#gallery');page.locator('#aylolHeader').wait_for();page.wait_for_timeout(300)
    assert page.locator('#gallery>.container').evaluate('(e)=>e.getBoundingClientRect().top')>=75
    assert not errors,errors
    assert not failed,failed
    assert all(request.startswith(url) for request in requests),[r for r in requests if not r.startswith(url)]
    summary['javascript_errors']=errors;summary['http_failures']=failed;summary['subdirectory_static_test']='passed'
    browser.close()
server.shutdown()
(root/'tmp/delivery-check/static-audit-results.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps(summary,indent=2,ensure_ascii=True))
