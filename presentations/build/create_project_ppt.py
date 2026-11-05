"""Prepare project slide content and layout for native PowerPoint authoring.

Run validate_and_render.ps1 after this script to create the editable PPTX and PDF.
The original reference is read-only.
"""
from pathlib import Path
from xml.etree import ElementTree as ET
from copy import deepcopy
import json
import posixpath
import zipfile

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'presentations'
REFERENCE = Path(r'C:\Users\Admin\Downloads\CRM (1).pptx')
DEST = OUT / 'Online_Shopping_Playwright_Project.pptx'
NS = {
    'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
    'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
}
for prefix, uri in NS.items():
    ET.register_namespace(prefix, uri)
REL = 'http://schemas.openxmlformats.org/package/2006/relationships'
CT = 'http://schemas.openxmlformats.org/package/2006/content-types'
EMU = 914400
NAVY, BLUE, ORANGE = '28344B', 'C7D3E6', 'FF9800'
INK, MUTED, LIGHT, WHITE = '27354A', '59687C', 'F1F5FA', 'FFFFFF'
TEAL = '25756C'


def el(tag, attrs=None, parent=None, text=None):
    prefix, name = tag.split(':')
    result = ET.Element(f'{{{NS[prefix]}}}{name}', {str(k): str(v) for k, v in (attrs or {}).items()})
    if text is not None:
        result.text = text
    if parent is not None:
        parent.append(result)
    return result


def xml(root):
    if root.tag.startswith('{'+REL+'}'):
        ET.register_namespace('', REL)
    elif root.tag.startswith('{'+CT+'}'):
        ET.register_namespace('', CT)
    return ET.tostring(root, encoding='utf-8', xml_declaration=True)


def remove_transitions(root):
    # The reference includes MC choices whose Requires attribute names a prefix.
    # ElementTree renames namespaces without rewriting those string attributes.
    # This deck uses static layouts, so discard transition-only compatibility XML.
    for parent in root.iter():
        for child in list(parent):
            if child.tag.split('}')[-1] in ('AlternateContent', 'transition'):
                parent.remove(child)


def rels(items):
    r = ET.Element(f'{{{REL}}}Relationships')
    for rid, kind, target in items:
        ET.SubElement(r, f'{{{REL}}}Relationship', Id=rid, Type=f'{NS["r"]}/{kind}', Target=target)
    return xml(r)


def tree(parent):
    st = el('p:spTree', parent=parent)
    nv = el('p:nvGrpSpPr', parent=st)
    el('p:cNvPr', {'id': 1, 'name': 'Group'}, nv)
    el('p:cNvGrpSpPr', parent=nv)
    el('p:nvPr', parent=nv)
    gp = el('p:grpSpPr', parent=st)
    x = el('a:xfrm', parent=gp)
    for name, attrs in [('off', {'x': 0, 'y': 0}), ('ext', {'cx': 0, 'cy': 0}),
                        ('chOff', {'x': 0, 'y': 0}), ('chExt', {'cx': 0, 'cy': 0})]:
        el('a:' + name, attrs, x)
    return st


def solid(parent, color):
    fill = el('a:solidFill', parent=parent)
    el('a:srgbClr', {'val': color}, fill)


class Slide:
    def __init__(self, title, section, notes, layout=2):
        self.number = len(SLIDES) + 1
        self.title, self.section, self.notes, self.layout = title, section, notes, layout
        self.root = el('p:sld')
        self.st = tree(el('p:cSld', parent=self.root))
        el('a:masterClrMapping', parent=el('p:clrMapOvr', parent=self.root))
        self.id = 1
        self.shapes = []
        self.images = []
        SLIDES.append(self)
        if layout == 2:
            # Keep all chrome local to the slide. The reference's nested layout
            # transforms display incorrectly in some presentation viewers.
            self.shape(0, 0, 13.333333, .80, NAVY)
            self.shape(0, .80, 13.333333, .08, BLUE)
            self.shape(.55, .80, .82, .08, ORANGE)
            self.text(title, .55, .13, 9.25, .54, size=27, color=WHITE, bold=True, valign='ctr')
            self.text('PLAYWRIGHT PROJECT', 10.23, .28, 2.55, .22, size=10.5, color=WHITE, bold=True, align='r')
            self.text(section.upper(), .55, 1.02, 11.9, .26, size=11, color=MUTED, bold=True)
            self.text('ONLINE SHOPPING  |  PLAYWRIGHT PROJECT', .55, 7.08, 8.3, .22, size=9, color=MUTED)
        else:
            self.shape(0, 0, 13.333333, 7.5, BLUE)
            if layout == 1:
                self.shape(0, 1.60, 13.333333, 4.25, NAVY)
                self.shape(0, 6.26, 13.333333, .12, ORANGE)
            else:
                self.shape(0, 4.40, 13.333333, 2.50, NAVY)
                self.shape(0, 6.90, 13.333333, .10, ORANGE)
        self.shape(11.95, 7.0, 1.383333, .50, ORANGE)
        self.text(f'{self.number:02}', 12.35, 7.10, .64, .27, size=14, color=WHITE, bold=True, align='ctr')

    def shape(self, x, y, w, h, fill=None, stroke=None, geom='rect', name='Shape'):
        self.id += 1
        sp = el('p:sp', parent=self.st)
        nv = el('p:nvSpPr', parent=sp)
        el('p:cNvPr', {'id': self.id, 'name': f'{name} {self.id}'}, nv)
        el('p:cNvSpPr', {'txBox': 1}, nv)
        el('p:nvPr', parent=nv)
        pr = el('p:spPr', parent=sp)
        xf = el('a:xfrm', parent=pr)
        el('a:off', {'x': round(x*EMU), 'y': round(y*EMU)}, xf)
        el('a:ext', {'cx': round(w*EMU), 'cy': round(h*EMU)}, xf)
        el('a:avLst', parent=el('a:prstGeom', {'prst': geom}, pr))
        solid(pr, fill) if fill else el('a:noFill', parent=pr)
        ln = el('a:ln', {'w': 9525}, pr)
        solid(ln, stroke) if stroke else el('a:noFill', parent=ln)
        self.shapes.append({'id': self.id, 'x': x, 'y': y, 'w': w, 'h': h, 'text': '',
                            'fill': fill, 'stroke': stroke, 'geom': geom})
        return sp

    def text(self, text, x, y, w, h, size=20, color=INK, bold=False, fill=None,
             align='l', valign='t', margin=0, font='Arial', stroke=None):
        sp = self.shape(x, y, w, h, fill, stroke, name='Text')
        tx = el('p:txBody', parent=sp)
        bp = el('a:bodyPr', {'wrap': 'square', 'lIns': round(margin*EMU),
            'rIns': round(margin*EMU), 'tIns': round(margin*EMU),
            'bIns': round(margin*EMU), 'anchor': valign}, tx)
        el('a:noAutofit', parent=bp)
        el('a:lstStyle', parent=tx)
        for line in text.split('\n'):
            p = el('a:p', parent=tx)
            pp = el('a:pPr', {'algn': align, 'marL': 0, 'indent': 0}, p)
            el('a:spcPct', {'val': 112000}, el('a:lnSpc', parent=pp))
            el('a:buNone', parent=pp)
            r = el('a:r', parent=p)
            rp = el('a:rPr', {'lang': 'en-US', 'sz': round(size*100), 'b': int(bold)}, r)
            solid(rp, color)
            el('a:latin', {'typeface': font}, rp)
            el('a:t', parent=r, text=line)
            el('a:endParaRPr', {'lang': 'en-US', 'sz': round(size*100)}, p)
        self.shapes[-1].update(text=text, size=size, font=font, color=color, bold=bold,
                               align=align, valign=valign, margin=margin)
        return sp

    def card(self, title, body, x, y, w, h, accent=ORANGE, size=18):
        self.shape(x, y, w, h, LIGHT)
        self.shape(x, y, .055, h, accent)
        self.text(title, x+.22, y+.18, w-.44, .46, size=21, bold=True)
        self.text(body, x+.22, y+.84, w-.44, h-.98, size=size, color=MUTED)

    def label(self, text, x, y, w, h=.62, fill=NAVY, color=WHITE, size=18):
        self.text(text, x, y, w, h, size=size, color=color, bold=True,
                  fill=fill, align='ctr', valign='ctr', margin=.06)

    def arrow(self, x, y, w=.30, h=.20, down=False):
        self.shape(x, y, w, h, ORANGE, geom='downArrow' if down else 'rightArrow')

    def bullets(self, items, x, y, w, size=20, gap=.83):
        for i, text in enumerate(items):
            self.shape(x, y+i*gap+.11, .09, .09, ORANGE)
            self.text(text, x+.25, y+i*gap, w-.25, gap-.12, size=size)

    def strip(self, text, y=6.20, color=NAVY):
        self.text(text, .55, y, 12.17, .50, size=16, color=color, fill=LIGHT, valign='ctr', margin=.12)

    def picture(self, x, y, w, h, filename, crop_bottom=0):
        self.id += 1
        pic = el('p:pic', parent=self.st)
        nv = el('p:nvPicPr', parent=pic)
        el('p:cNvPr', {'id': self.id, 'name': 'Existing order tracking screenshot',
                       'descr': 'Existing project screenshot showing an order awaiting processing.'}, nv)
        el('a:picLocks', {'noChangeAspect': 1}, el('p:cNvPicPr', parent=nv))
        el('p:nvPr', parent=nv)
        bf = el('p:blipFill', parent=pic)
        rid = f'rIdImage{len(self.images)+1}'
        el('a:blip', {f'{{{NS["r"]}}}embed': rid}, bf)
        if crop_bottom:
            el('a:srcRect', {'b': crop_bottom}, bf)
        el('a:fillRect', parent=el('a:stretch', parent=bf))
        sp = el('p:spPr', parent=pic)
        xf = el('a:xfrm', parent=sp)
        el('a:off', {'x': round(x*EMU), 'y': round(y*EMU)}, xf)
        el('a:ext', {'cx': round(w*EMU), 'cy': round(h*EMU)}, xf)
        el('a:avLst', parent=el('a:prstGeom', {'prst': 'rect'}, sp))
        self.images.append((rid, filename))
        self.shapes.append({'id': self.id, 'kind': 'picture', 'filename': filename,
                            'x': x, 'y': y, 'w': w, 'h': h, 'text': '', 'crop_bottom': crop_bottom})


SLIDES = []

s = Slide('Online Shopping Automation', 'Project presentation',
    'This presentation describes the current local project, playwrightProject1. It follows the 21-slide structure and native geometric layouts of the supplied CRM reference. No application brand or client identity is established by the code, so the title uses Online Shopping. The deck documents implemented coverage; it does not claim that the full suite passed. Sources: package.json, playwright.config.js, tests/, POM/.', 1)
s.text('PLAYWRIGHT PROJECT', .62, .35, 7.0, .44, size=19, bold=True)
s.text('ONLINE SHOPPING\nAUTOMATION', .72, 2.08, 10.7, 1.70, size=45, color=WHITE, bold=True)
s.text('JavaScript  |  Page Object Model  |  UI Testing', .75, 4.60, 9.1, .45, size=22, color=ORANGE)
s.text('Customer workflows, framework design and execution', .68, 6.64, 11.5, .35, size=17)

s = Slide('Project Information', 'Overview',
    'The application under test is an online shopping website. The repository contains 11 spec files with one business test each, 24 files under POM, and one authentication setup test. Four product categories are used by the purchase workflow: Books, Fashion, Furniture and Electronics. The configured execution projects use Chromium. Client name and deployment ownership are not provided. Sources: package.json; tests/*.spec.js; POM/; playwright.config.js.')
s.text('Customer journeys from sign-in to order tracking', .55, 1.55, 11.9, .64, size=29, bold=True)
for x, number, caption in [(.55, '11', 'Business scenarios'), (4.68, '24', 'Page object files'), (8.81, '4', 'Product categories')]:
    s.text(number, x, 2.51, 3.90, .87, size=49, bold=True, color=NAVY, align='ctr')
    s.text(caption, x, 3.47, 3.90, .35, size=18, align='ctr', color=MUTED)
s.card('Application scope', 'Products, cart, wishlist, checkout, reviews,\naccount details and order tracking.', .55, 4.34, 7.0, 1.70)
s.card('Current browser', 'Chromium / Desktop Chrome', 7.82, 4.34, 4.89, 1.70, accent=TEAL)
s.strip('One additional setup test creates reusable authentication state.')

s = Slide('Project Business Need', 'Purpose',
    'These are intended benefits of automation, not measured savings. The project uses assertions for customer-visible behavior, persistence and cart calculations. POM classes centralize page details and reusable operations. HTML reports and traces support investigation. Sources: tests/support/cartVerification.js; tests/*.spec.js; playwright.config.js.')
s.card('Protect shopping journeys', 'Check that key customer tasks continue to work\nafter application changes.', .55, 1.58, 5.96, 2.02)
s.card('Reduce repeated manual work', 'Repeat stable regression scenarios with\nconsistent steps and expected results.', 6.75, 1.58, 5.96, 2.02)
s.card('Verify saved state and totals', 'Check cart arithmetic, saved details, wishlist\npersistence and session behavior.', .55, 3.90, 5.96, 2.02, accent=TEAL)
s.card('Make failures explainable', 'Use named tests, HTML results and available\nscreenshots or traces as evidence.', 6.75, 3.90, 5.96, 2.02, accent=TEAL)

s = Slide('Application Modules', 'Business architecture',
    'This is a map of UI areas exercised by the automation, not a claim about the application server architecture. Discovery covers search and four categories. The customer can save products, purchase, review products and maintain account details. Sources: POM/ and tests/.')
s.label('ONLINE SHOPPING APPLICATION', 3.36, 1.59, 6.62, .72, size=23)
for x in [2.45, 6.51, 10.59]:
    s.arrow(x, 2.56, .25, .42, down=True)
s.card('Discover products', 'Search\nBooks and Fashion\nFurniture and Electronics', .55, 3.18, 3.89, 2.51, size=19)
s.card('Shop and purchase', 'Cart and Wishlist\nCheckout and Pending Payments\nOrder Tracking', 4.67, 3.18, 3.89, 2.51, size=18)
s.card('Manage the account', 'Login and Logout\nProfile, Billing and Password\nProduct Reviews', 8.79, 3.18, 3.92, 2.51, size=18)
s.strip('The test suite connects these modules through customer-facing workflows.')

s = Slide('Framework Architecture', 'Automation design',
    'Local CLI commands or CI invoke Playwright Test using playwright.config.js. Specs express scenarios and assertions; page objects provide locators and operations. JSON inputs and fixtures supply data and starting state. Reports and configured artifacts are produced during execution. POM is used with varying depth: some classes are locator holders, others include methods. Sources: playwright.config.js; tests/support/; POM/; testData/testData.json; Jenkinsfile.')
for i, label in enumerate(['Local command\n/ CI', 'Playwright\nconfiguration', 'Test\nspecifications', 'Page Object\nModel', 'Application\nUI']):
    x = .55 + 2.49*i
    s.label(label, x, 1.70, 2.20, 1.02, size=19)
    if i < 4:
        s.arrow(x+2.25, 2.12, .19)
s.card('Inputs and setup', 'JSON test data\nUnique shopper fixture\nSaved authentication state', .55, 3.25, 5.96, 2.05, size=19)
s.card('Responsibilities', 'Specs describe scenarios and assertions.\nPage objects expose locators and actions.\nChecks validate the observed UI behavior.', 6.75, 3.25, 5.96, 2.05, accent=TEAL, size=19)
s.label('Assertions  →  Test results  →  HTML report + configured artifacts', .55, 5.62, 12.16, .74, size=22)

s = Slide('Technology & Structure', 'Framework organization',
    'This is a JavaScript framework. package.json is CommonJS while specs and POM files use import/export syntax handled by Playwright. package.json has no npm scripts. There are 24 page-object files, 11 spec files and a support directory. Manual_Test_Scripts.xlsx is present, but no manual-to-automated mapping is asserted here. Sources: package.json; project file tree; playwright.config.js.')
s.text('Technology stack', .55, 1.58, 5.8, .43, size=25, bold=True)
s.bullets(['JavaScript and Node.js', 'Playwright Test and Chromium', 'Page Object Model and JSON data', 'Jenkins and GitHub Actions', 'HTML reports, screenshots and traces'], .55, 2.27, 5.55, size=21, gap=.74)
s.text('Project organization', 6.60, 1.58, 6.0, .43, size=25, bold=True)
s.text('tests/                  Scenarios + support\nPOM/                    Page objects\ntestData/               Reusable inputs\nplaywright.config.js    Execution setup\nJenkinsfile             CI pipeline\nscreenshots/            Tracking evidence', 6.60, 2.26, 6.10, 3.61, size=16, font='Consolas', fill=LIGHT, margin=.20)
s.strip('Supporting material: Manual_Test_Scripts.xlsx and the framework presentation guide.')

s = Slide('Login & Logout', 'Module 01  /  Account session',
    'TC-010 uses the shopping fixture to register and sign in a unique shopper. It verifies the welcome message and profile email, signs out, checks that the login link is visible and the logout link is absent, then opens and reloads my-account.php and verifies an empty profile email. This is a UI-level session check. Sources: tests/loginLogout.spec.js; POM/loginLogout.page.js; tests/support/shopping.fixture.js.')
s.text('Validate account identity and signed-out behavior', .55, 1.58, 12, .52, size=27, bold=True)
for x, label in [(.55, 'Register + sign in'), (4.72, 'Verify account'), (8.89, 'Sign out + revisit')]:
    s.label(label, x, 2.54, 3.82, .76, size=21)
s.arrow(4.43, 2.82, .23)
s.arrow(8.60, 2.82, .23)
s.card('Before logout', 'Welcome message matches the shopper.\nAccount email matches the created user.', .55, 3.85, 5.96, 1.94)
s.card('After logout', 'Login link returns; logout link disappears.\nAccount email stays empty after reload.', 6.75, 3.85, 5.96, 1.94, accent=TEAL)
s.strip('Key files: loginLogout.spec.js  •  loginLogout.page.js  •  shopping.fixture.js')

s = Slide('Product Search & Cart', 'Modules 02–03  /  Product discovery and calculations',
    'Product search looks up a TV by the JSON-defined search term and verifies the product heading. Repeated Add to Cart opens a specific product and adds it three times. The test checks one row after each addition, and calls checkCart for quantities one and three. checkCart parses currency and checks row total = quantity * unit price + shipping, and grand total equals row total. The formula reflects this application and the current one-product cart. Sources: tests/searchProduct.spec.js; tests/repeatedAddToCart.spec.js; tests/support/cartVerification.js; POM/searchProduct.page.js.')
s.card('Search the correct product', 'Enter the configured keyword.\nOpen the exact matching product.\nVerify its details heading.', .55, 1.66, 5.96, 2.71, size=20)
s.card('Add the same product repeatedly', 'Add the product three times.\nVerify one row; quantity grows from 1 to 3.\nCheck price, shipping and totals.', 6.75, 1.66, 5.96, 2.71, size=19)
s.text('Row total = quantity × unit price + shipping', .55, 4.87, 12.16, .75, size=27, color=WHITE, bold=True, fill=NAVY, align='ctr', valign='ctr')
s.strip('For the tested single-product cart: grand total must equal the row total.')

s = Slide('Wishlist Persistence', 'Module 04  /  Saved products',
    'TC-006 verifies a product persists in the wishlist after a logout/login cycle using the same generated account. It checks the product heading before saving, then one wishlist row and a visible product link after login. The test does not follow that link to recheck the details heading. The local let wishlist declaration shadows the outer variable, so the afterEach cleanup hook currently returns without cleanup. Sources: tests/wishlistPersistence.spec.js; POM/wishlistPersistence.page.js; tests/support/shopping.fixture.js.')
s.text('A saved product should survive a new login', .55, 1.58, 12.1, .55, size=28, bold=True)
steps = [('Open product', 'Verify the product heading'), ('Save to wishlist', 'Verify one saved row'), ('Logout + login', 'Use the same account'), ('Reopen wishlist', 'Verify the saved product')]
for i, (title, body) in enumerate(steps):
    x = .55 + i*3.10
    s.label(f'{i+1:02}', x, 2.51, .68, .62, fill=ORANGE, color=NAVY, size=21)
    s.text(title, x, 3.42, 2.83, .70, size=22, bold=True)
    s.text(body, x, 4.28, 2.83, .97, size=20, color=MUTED)
    if i < 3:
        s.arrow(x+2.74, 2.74, .25)
s.strip('Persistence check: saved data remains available across the session boundary.')

s = Slide('Wishlist to Cart', 'Module 05  /  Saved-product purchase intent',
    'TC-007 adds a saved wishlist product to the cart. It captures the displayed current price, excluding the old-price span, and compares it with the cart price. checkCart verifies one row, quantity one and totals. Reload must preserve the cart, and its link must open the correct product. Limitation: local let declarations shadow the outer wishlist/cart variables, so the afterEach cleanup hooks currently return without cleanup. The presentation does not claim cleanup succeeds. Sources: tests/wishlistToCart.spec.js; POM/wishlistToCart.page.js; tests/support/cartVerification.js.')
s.label('Save product', .55, 1.66, 3.70, .76, size=22)
s.arrow(4.48, 1.94)
s.label('Read wishlist price', 4.99, 1.66, 3.71, .76, size=22)
s.arrow(8.93, 1.94)
s.label('Add to cart', 9.44, 1.66, 3.27, .76, size=22)
s.card('Price and quantity', 'Cart price equals the saved-product price.\nOne cart row contains one unit.\nRow and grand totals are consistent.', .55, 3.05, 5.96, 2.57, size=20)
s.card('Persistence and identity', 'Reload the page and check the cart again.\nOpen the product using its cart link.\nVerify the expected product heading.', 6.75, 3.05, 5.96, 2.57, accent=TEAL, size=20)
s.strip('Reusable assertion helper: checkCart(cart, 1)')

s = Slide('Product Reviews', 'Module 06  /  Product-specific persistence',
    'TC-008 creates a review summary containing a UUID, selects each configured rating and submits the form. After revisiting the same product URL it checks exactly one review with that summary, the reviewer name and review text. Submission-response checks and review-identifier attachments are commented out. The test suite implements no review-deletion operation, so submitted reviews remain. Sources: tests/productReview.spec.js; POM/productReview.page.js.')
s.card('Create a distinct review', 'Open the intended product.\nSelect the configured ratings.\nEnter a unique summary and review text.', .55, 1.66, 5.96, 2.62, size=20)
s.card('Verify it on the same product', 'Revisit the product and open reviews.\nFind exactly one matching summary.\nCheck reviewer name and review content.', 6.75, 1.66, 5.96, 2.62, accent=TEAL, size=20)
s.label('Unique review identifier', .55, 4.92, 3.70, .78, size=20)
s.arrow(4.48, 5.22)
s.label('Revisit product', 4.99, 4.92, 3.71, .78, size=20)
s.arrow(8.93, 5.22)
s.label('Assert persisted content', 9.44, 4.92, 3.27, .78, size=18)
s.strip('The checks validate saved UI content; submitted reviews currently remain in the application.')

s = Slide('Billing & Profile Updates', 'Modules 07–08  /  Customer details',
    'The billing scenario uses the chromium-authenticated project and checks updated billing values after reload. The profile scenario uses a unique-account fixture and checks name/contact after reload and re-login, then restores the original values. These tests do not imply all application data is cleaned up. Sources: tests/updateBillingAddress.spec.js; tests/updateProfile.spec.js; POM/updateBillling.page.js; POM/updateProfile.page.js; playwright.config.js.')
s.card('Billing address', 'Update the configured address fields.\nSave and reload the account page.\nCompare persisted field values.\n\nStarting state: saved authentication.', .55, 1.66, 5.96, 3.86, size=20)
s.card('Profile details', 'Update the shopper name and contact.\nCheck after reload and re-login.\nRestore the original name and contact.\n\nStarting state: unique shopper fixture.', 6.75, 1.66, 5.96, 3.86, accent=TEAL, size=20)
s.strip('The key assertion is persistence after a refresh or a new login session.')

s = Slide('Password Change Validation', 'Module 09  /  Negative account scenario',
    'This is an incorrect-current-password rejection scenario, not successful password-change coverage. The test signs in with the configured existing account, submits an invalid current password with a proposed new password, checks the configured error dialog, logs out and verifies that login with the original password still works. Sources: tests/changePassword.spec.js; POM/changePassword.page.js; testData/testData.json.')
s.text('Reject an incorrect current password', .55, 1.58, 12.1, .56, size=29, bold=True)
s.bullets(['Open the change-password form for the signed-in shopper.', 'Enter an incorrect current password and a proposed new password.', 'Verify the expected rejection message.', 'Sign in again using the original password.'], .55, 2.48, 11.9, size=23, gap=.87)
s.strip('Expected behavior: the invalid request leaves the existing password usable.')

s = Slide('Checkout & Pending Payments', 'Module 10  /  Incomplete checkout',
    'The paymentPending scenario reuses shared saved authentication. It adds a book, proceeds to checkout without submitting payment, and opens the pending-payments view. The assertion checks the expected URL and a matching product heading. It can match an older entry and does not uniquely correlate the newly created order. Sources: tests/paymentPending.spec.js; POM/myAccount.page.js; playwright.config.js.')
s.label('Add a product', .55, 1.71, 3.70, .76, size=22)
s.arrow(4.48, 2.00)
s.label('Reach checkout', 4.99, 1.71, 3.71, .76, size=22)
s.arrow(8.93, 2.00)
s.label('Leave payment pending', 9.44, 1.71, 3.27, .76, size=19)
s.card('Business check', 'A shopper can find an unpaid product\nin the pending-payments view.', .55, 3.16, 5.96, 2.11, size=22)
s.card('Implemented assertion', 'The pending-payments page contains\nthe expected product name.', 6.75, 3.16, 5.96, 2.11, accent=TEAL, size=22)
s.strip('Next improvement: correlate the assertion to the exact order created by this test.')

s = Slide('Purchase & Order Tracking', 'Module 11  /  End-to-end journey',
    'The purchase test creates a unique account, signs in, adds one product from each of Books, Fashion, Furniture and Electronics, sets billing and shipping fields, reapplies billing as a workaround documented in the source, and submits the internet-banking option. It asserts the configured tracking-link count, captures each popup and logs out. It does not verify external payment settlement or assert each order status. The image is an existing repository artifact, screenshots/track-order-1.png; it shows Order Not Process Yet and is not evidence of a new run. Sources: tests/purchaseAndTrackOrder.spec.js; POM/trackproduct.page.js; screenshots/track-order-1.png.')
s.bullets(['Register and sign in with a new account.', 'Add products from all four categories.', 'Set billing and shipping, then check out.', 'Submit the internet-banking option.', 'Verify links and capture each popup.'], .55, 1.66, 6.00, size=21, gap=.79)
s.text('Existing project evidence', 7.01, 1.66, 5.38, .44, size=23, bold=True)
s.shape(6.95, 2.36, 5.76, 2.54, LIGHT)
s.picture(7.12, 2.58, 5.40, 1.35, 'track-order-1.png', crop_bottom=75000)
s.text('Tracking popup from screenshots/\nStatus shown: order not yet processed', 7.17, 4.17, 5.14, .58, size=15, color=MUTED)
s.strip('Coverage: UI checkout and tracking availability; payment settlement is not asserted.')

s = Slide('Functional Dependencies', 'Authentication and test setup',
    'Six specs import shopping.fixture: repeatedAddToCart, wishlistPersistence, wishlistToCart, productReview, updateProfile and loginLogout. Two specs use saved authentication: paymentPending and updateBillingAddress. Three remaining specs arrange their own starting state: searchProduct, purchaseAndTrackOrder and changePassword. The shared-state project depends on setup and a saved session file. The fixture performs session teardown but does not delete generated accounts. Sources: tests imports; tests/support/shopping.fixture.js; tests/auth.setup.js; playwright.config.js.')
s.card('Unique shopper fixture', 'Fresh shopper per test.\nSix scenarios use the fixture.\nSession teardown follows.', .55, 1.66, 3.89, 2.91, size=18)
s.card('Shared authentication', 'Setup saves the login state.\nTwo specs reuse the session.\nSetup runs before both specs.', 4.67, 1.66, 3.89, 2.91, accent=TEAL, size=18)
s.card('Scenario-specific setup', 'Three other scenarios arrange\ntheir own starting state.\nJSON supplies reusable input values.', 8.79, 1.66, 3.92, 2.91, size=18)
s.label('setup', .55, 5.17, 2.35, .65)
s.arrow(3.11, 5.40)
s.label('Saved browser state', 3.64, 5.17, 4.20, .65)
s.arrow(8.05, 5.40)
s.label('chromium-authenticated', 8.58, 5.17, 4.13, .65, size=17)
s.strip('Execution uses one worker to reduce conflicts with shared account data.')

s = Slide('Business Workflows', 'From user action to assertion',
    'This slide provides two concise demonstration paths directly connected to source scenarios. The wishlist-to-cart path should show persistence, item identity and the reusable cart assertion helper. The login/logout path should show the identity check followed by signed-out assertions. These are implemented test expectations, not fresh execution results. Sources: tests/wishlistToCart.spec.js; tests/loginLogout.spec.js; tests/support/cartVerification.js.')
s.text('Workflow A  /  Saved product to purchase intent', .55, 1.62, 12.0, .48, size=25, bold=True)
for i, item in enumerate(['Product details', 'Wishlist', 'Cart', 'Reload + verify']):
    x = .55+i*3.10
    s.label(item, x, 2.40, 2.86, .72, size=19)
    if i < 3:
        s.arrow(x+2.89, 2.67, .18)
s.text('Assertions: product identity • price equality • quantity • totals • persisted cart', .55, 3.40, 12.1, .62, size=20, color=MUTED)
s.text('Workflow B  /  Authenticated user to signed-out state', .55, 4.32, 12.0, .48, size=25, bold=True)
for i, item in enumerate(['Login', 'Check account', 'Logout', 'Revisit account']):
    x = .55+i*3.10
    s.label(item, x, 5.08, 2.86, .72, fill=BLUE, color=NAVY, size=19)
    if i < 3:
        s.arrow(x+2.89, 5.35, .18)
s.strip('Assertions: welcome and email match → login link returns → account email stays empty.')

s = Slide('Execution & Reporting', 'Running and investigating tests',
    'BASE_URL must be present in .env or the process environment and must use HTTP or HTTPS. The three active projects are setup, chromium-authenticated and chromium. workers is one. Retries are two when CI is truthy and zero locally. The global reporter is HTML and trace is on-first-retry. Six fixture specs override diagnostics to screenshot only-on-failure and trace retain-on-failure. No fresh suite run was performed for preparing this deck. An existing .last-run.json reports failed, but it is insufficient to compute a complete suite pass rate. Sources: playwright.config.js; tests/*.spec.js; test-results/.last-run.json.')
s.text('PowerShell commands', .55, 1.65, 6.08, .42, size=25, bold=True)
s.text('npx playwright test\n\nnpx playwright test `\n  --project=chromium-authenticated\n\nnpx playwright show-report', .55, 2.40, 6.19, 3.10, size=18, font='Consolas', fill=LIGHT, margin=.20)
s.text('Execution settings', 7.10, 1.65, 5.61, .42, size=25, bold=True)
s.bullets(['Chromium; one worker', 'Two retries when CI is enabled', 'HTML results for each test run', 'Failure artifacts where configured'], 7.10, 2.40, 5.61, size=21, gap=.78)
s.strip('Prerequisite: configure BASE_URL. Coverage shown here is based on source, not a new test run.')

s = Slide('CI & Delivery Workflow', 'Continuous integration',
    'Jenkinsfile uses agent any but runs bat commands, so it requires a Windows-capable agent. BASE_URL is injected through the Project_BaseURL credential. The pipeline installs dependencies and browsers, runs tests, and publishes the HTML report when present. It does not explicitly set CI. GitHub Actions runs on Ubuntu for pushes/pull requests to main/master, uses npm ci and uploads the report with 30-day retention. It currently does not inject the required BASE_URL. The files establish intended CI behavior, not a successful run. Sources: Jenkinsfile; .github/workflows/playwright.yml; playwright.config.js.')
s.card('Jenkins', 'Windows commands (bat)\nBASE_URL from a Jenkins credential\nInstall dependencies and browsers\nRun tests and publish the HTML report', .55, 1.66, 5.96, 3.28, size=20)
s.card('GitHub Actions', 'Push / pull request to main or master\nUbuntu runner with Node.js\nInstall, run tests and upload the report\nReport artifact retention: 30 days', 6.75, 1.66, 5.96, 3.28, accent=TEAL, size=20)
s.label('Install dependencies', .55, 5.36, 3.70, .65, size=20)
s.arrow(4.48, 5.60)
s.label('Run Playwright tests', 4.99, 5.36, 3.71, .65, size=20)
s.arrow(8.93, 5.60)
s.label('Publish report', 9.44, 5.36, 3.27, .65, size=20)
s.strip('Configuration gap: supply BASE_URL in GitHub Actions before running the workflow.', y=6.33)

s = Slide('Coverage & Next Improvements', 'Implemented scope and development priorities',
    'Coverage totals are based on 11 business tests in 11 spec files. Shopping and discovery: search, repeated cart, wishlist persistence, wishlist to cart, product reviews (5). Account management: login/logout, profile update, incorrect-password rejection, billing update (4). Checkout and orders: purchase/tracking and pending payments (2). The sample reference had an effort table, but this repository provides no approved estimates, so the deck uses verified inventory and future priorities. Improvement priorities include fixing shadowed cleanup references in wishlistToCart and wishlistPersistence, stronger exact-order assertions, account/review cleanup, environment configuration and enabling additional browsers. No pass rate or time saving is claimed.')
s.text('Implemented scenarios', .55, 1.58, 5.88, .45, size=25, bold=True)
rows = [('Shopping and discovery', '5'), ('Account management', '4'), ('Checkout and orders', '2'), ('Total business scenarios', '11')]
for i, (name, count) in enumerate(rows):
    y = 2.35+i*.72
    fill = NAVY if i == 3 else LIGHT
    color = WHITE if i == 3 else INK
    s.text(name, .55, y, 4.91, .65, size=19, color=color, fill=fill, margin=.14, valign='ctr', bold=i==3)
    s.text(count, 5.47, y, .90, .65, size=23, color=color, fill=fill, align='ctr', valign='ctr', bold=True)
s.text('Next improvements', 6.93, 1.58, 5.78, .45, size=25, bold=True)
s.bullets(['Repair both wishlist cleanup hooks.', 'Verify exact orders and stronger checkout outcomes.', 'Complete account / review data cleanup.', 'Configure CI inputs and expand browser coverage.'], 6.93, 2.35, 5.78, size=20, gap=.87)
s.strip('The framework provides reusable workflow coverage and a clear path to stronger evidence.')

s = Slide('Thank You', 'Questions',
    'Close by emphasizing the separation of tests, page objects, fixtures and JSON data. The repository covers eleven business scenarios with checks for calculations, persistence and session behavior. Suggested discussion topics are the POM design, authentication trade-offs, CI configuration and stronger future assertions. Sources for slide facts are included throughout the speaker notes.', 3)
s.text('PLAYWRIGHT PROJECT', .62, .35, 7.0, .44, size=19, bold=True)
s.text('THANK YOU', .72, 2.08, 10.1, 1.0, size=49, bold=True, color=NAVY)
s.text('Questions & Discussion', .75, 3.25, 10.5, .52, size=27, color=MUTED)
s.text('11 scenarios. Reusable page objects.\nCustomer-focused assertions.', .72, 4.76, 7.24, 1.20, size=28, color=WHITE, bold=True)


def notes_xml(slide):
    root = el('p:notes')
    st = tree(el('p:cSld', parent=root))
    sp = el('p:sp', parent=st)
    nv = el('p:nvSpPr', parent=sp)
    el('p:cNvPr', {'id': 2, 'name': 'Speaker notes'}, nv)
    el('p:cNvSpPr', parent=nv)
    el('p:ph', {'type': 'body', 'idx': 1}, el('p:nvPr', parent=nv))
    el('p:spPr', parent=sp)
    tx = el('p:txBody', parent=sp)
    el('a:bodyPr', parent=tx)
    el('a:lstStyle', parent=tx)
    for line in [slide.title, '', slide.notes]:
        p = el('a:p', parent=tx)
        r = el('a:r', parent=p)
        el('a:rPr', {'lang': 'en-US', 'sz': 1200}, r)
        el('a:t', parent=r, text=line)
    el('a:masterClrMapping', parent=el('p:clrMapOvr', parent=root))
    return xml(root)


def build():
    OUT.mkdir(exist_ok=True)
    parts = {}
    with zipfile.ZipFile(REFERENCE) as reference:
        parts['ppt/theme/theme1.xml'] = reference.read('ppt/theme/theme1.xml')
        master = ET.fromstring(reference.read('ppt/slideMasters/slideMaster1.xml'))
        remove_transitions(master)
        st = master.find('p:cSld/p:spTree', NS)
        for shape in list(st)[2:]:
            st.remove(shape)
        ids = master.find('p:sldLayoutIdLst', NS)
        for item in list(ids)[3:]:
            ids.remove(item)
        parts['ppt/slideMasters/slideMaster1.xml'] = xml(master)
        parts['ppt/slideMasters/_rels/slideMaster1.xml.rels'] = rels(
            [(f'rId{i}', 'slideLayout', f'../slideLayouts/slideLayout{i}.xml') for i in range(1, 4)]
            + [('rIdTheme', 'theme', '../theme/theme1.xml')])
        for i in range(1, 4):
            root = ET.fromstring(reference.read(f'ppt/slideLayouts/slideLayout{i}.xml'))
            remove_transitions(root)
            st = root.find('p:cSld/p:spTree', NS)
            for shape in list(st):
                # Retain native geometric chrome; replace branding, placeholders and old text.
                if shape.tag == f'{{{NS["p"]}}}pic' or shape.find('.//p:ph', NS) is not None or shape.find('.//a:t', NS) is not None:
                    st.remove(shape)
            parts[f'ppt/slideLayouts/slideLayout{i}.xml'] = xml(root)
            parts[f'ppt/slideLayouts/_rels/slideLayout{i}.xml.rels'] = rels([('rId1', 'slideMaster', '../slideMasters/slideMaster1.xml')])
        nm = ET.fromstring(reference.read('ppt/notesMasters/notesMaster1.xml'))
        parts['ppt/notesMasters/notesMaster1.xml'] = xml(nm)
        parts['ppt/notesMasters/_rels/notesMaster1.xml.rels'] = rels([('rId1', 'theme', '../theme/theme1.xml')])

    presentation = el('p:presentation')
    el('p:sldMasterId', {'id': 2147483648, f'{{{NS["r"]}}}id': 'rIdMaster'}, el('p:sldMasterIdLst', parent=presentation))
    el('p:notesMasterId', {f'{{{NS["r"]}}}id': 'rIdNotes'}, el('p:notesMasterIdLst', parent=presentation))
    sl = el('p:sldIdLst', parent=presentation)
    for s in SLIDES:
        el('p:sldId', {'id': 255+s.number, f'{{{NS["r"]}}}id': f'rIdSlide{s.number}'}, sl)
        parts[f'ppt/slides/slide{s.number}.xml'] = xml(s.root)
        sr = [('rIdLayout', 'slideLayout', f'../slideLayouts/slideLayout{s.layout}.xml'),
              ('rIdNotes', 'notesSlide', f'../notesSlides/notesSlide{s.number}.xml')]
        for rid, filename in s.images:
            sr.append((rid, 'image', f'../media/{filename}'))
            parts[f'ppt/media/{filename}'] = (ROOT/'screenshots'/filename).read_bytes()
        parts[f'ppt/slides/_rels/slide{s.number}.xml.rels'] = rels(sr)
        parts[f'ppt/notesSlides/notesSlide{s.number}.xml'] = notes_xml(s)
        parts[f'ppt/notesSlides/_rels/notesSlide{s.number}.xml.rels'] = rels([
            ('rIdMaster', 'notesMaster', '../notesMasters/notesMaster1.xml'),
            ('rIdSlide', 'slide', f'../slides/slide{s.number}.xml')])
    el('p:sldSz', {'cx': 12192000, 'cy': 6858000, 'type': 'screen16x9'}, presentation)
    el('p:notesSz', {'cx': 6858000, 'cy': 9144000}, presentation)
    parts['ppt/presentation.xml'] = xml(presentation)
    parts['ppt/_rels/presentation.xml.rels'] = rels([
        ('rIdMaster', 'slideMaster', 'slideMasters/slideMaster1.xml'),
        ('rIdNotes', 'notesMaster', 'notesMasters/notesMaster1.xml')]
        + [(f'rIdSlide{s.number}', 'slide', f'slides/slide{s.number}.xml') for s in SLIDES])
    parts['_rels/.rels'] = rels([('rId1', 'officeDocument', 'ppt/presentation.xml'),
        ('rId3', 'extended-properties', 'docProps/app.xml')])
    rr = ET.fromstring(parts['_rels/.rels'])
    ET.SubElement(rr, f'{{{REL}}}Relationship', Id='rId2',
        Type='http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties', Target='docProps/core.xml')
    parts['_rels/.rels'] = xml(rr)
    parts['docProps/core.xml'] = b'''<?xml version="1.0" encoding="UTF-8"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><dc:title>Online Shopping Automation Using Playwright</dc:title><dc:subject>Project architecture, modules and implemented test coverage</dc:subject><dc:creator>Project Presentation</dc:creator><dc:description>21-slide project deck adapted from the supplied CRM presentation. Source-grounded coverage and speaker notes.</dc:description><dcterms:created xsi:type="dcterms:W3CDTF">2026-11-05T00:00:00Z</dcterms:created><cp:lastModifiedBy>Project Presentation</cp:lastModifiedBy></cp:coreProperties>'''
    parts['docProps/app.xml'] = f'''<?xml version="1.0" encoding="UTF-8"?><Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"><Application>Microsoft Office PowerPoint</Application><PresentationFormat>On-screen Show (16:9)</PresentationFormat><Slides>{len(SLIDES)}</Slides><Notes>{len(SLIDES)}</Notes></Properties>'''.encode()
    content_types = ET.Element(f'{{{CT}}}Types')
    for extension, kind in [('rels', 'application/vnd.openxmlformats-package.relationships+xml'), ('xml', 'application/xml'), ('png', 'image/png')]:
        ET.SubElement(content_types, f'{{{CT}}}Default', Extension=extension, ContentType=kind)
    for name in parts:
        if not name.endswith('.xml'):
            continue
        if name == 'ppt/presentation.xml':
            kind = 'application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml'
        elif name.startswith('ppt/theme/'):
            kind = 'application/vnd.openxmlformats-officedocument.theme+xml'
        elif name.startswith('ppt/'):
            group = name.split('/')[1]
            kind = 'application/vnd.openxmlformats-officedocument.presentationml.' + {
                'slides': 'slide', 'slideLayouts': 'slideLayout', 'slideMasters': 'slideMaster',
                'notesSlides': 'notesSlide', 'notesMasters': 'notesMaster'}[group] + '+xml'
        elif name.endswith('core.xml'):
            kind = 'application/vnd.openxmlformats-package.core-properties+xml'
        else:
            kind = 'application/vnd.openxmlformats-officedocument.extended-properties+xml'
        ET.SubElement(content_types, f'{{{CT}}}Override', PartName='/'+name, ContentType=kind)
    parts['[Content_Types].xml'] = xml(content_types)
    # Verify every internal relationship resolves before writing the artifact.
    for name, data in parts.items():
        if name.endswith('.xml') or name.endswith('.rels'):
            ET.fromstring(data)
        if not name.endswith('.rels'):
            continue
        base = '' if name == '_rels/.rels' else posixpath.dirname(posixpath.dirname(name))
        for relationship in ET.fromstring(data):
            target = posixpath.normpath(posixpath.join(base, relationship.attrib['Target']))
            assert target in parts, (name, target)
    for s in SLIDES:
        for shape in s.shapes:
            assert shape['x'] >= 0 and shape['y'] >= 0
            assert shape['x']+shape['w'] <= 13.334 and shape['y']+shape['h'] <= 7.5, (s.number, shape)
    # Retain the reference's presentation-level package scaffolding. Office's
    # native package is the authoritative source for master/layout registration.
    with zipfile.ZipFile(REFERENCE) as reference:
        package = {name: reference.read(name) for name in reference.namelist()}
    preserve = {'ppt/presentation.xml', 'ppt/_rels/presentation.xml.rels',
                'ppt/slideMasters/slideMaster1.xml', 'ppt/slideMasters/_rels/slideMaster1.xml.rels',
                '[Content_Types].xml'}
    for name, data in parts.items():
        if name not in preserve:
            package[name] = data
    existing_ct = ET.fromstring(package['[Content_Types].xml'])
    existing_overrides = {item.attrib.get('PartName') for item in existing_ct}
    for item in content_types:
        if item.tag.endswith('Override') and item.attrib['PartName'] not in existing_overrides:
            existing_ct.append(deepcopy(item))
    package['[Content_Types].xml'] = xml(existing_ct)
    with zipfile.ZipFile(DEST, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, data in package.items():
            archive.writestr(name, data)
    manifest = [{'slide': s.number, 'title': s.title, 'notes': s.notes, 'layout': s.layout, 'shapes': s.shapes} for s in SLIDES]
    (OUT/'build'/'slide_manifest.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding='utf-8')
    (OUT/'Online_Shopping_Playwright_Speaker_Notes.md').write_text('\n\n'.join(
        f'## {s.number:02}. {s.title}\n\n{s.notes}' for s in SLIDES), encoding='utf-8')
    print(json.dumps({'file': str(DEST), 'slides': len(SLIDES), 'bytes': DEST.stat().st_size,
                      'native_editable_shapes': sum(len(s.shapes) for s in SLIDES)}))


def write_manifest():
    OUT.mkdir(exist_ok=True)
    manifest = [{'slide': s.number, 'title': s.title, 'notes': s.notes,
                 'layout': s.layout, 'shapes': s.shapes} for s in SLIDES]
    (OUT/'build'/'slide_manifest.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding='utf-8')
    (OUT/'Online_Shopping_Playwright_Speaker_Notes.md').write_text('\n\n'.join(
        f'## {s.number:02}. {s.title}\n\n{s.notes}' for s in SLIDES), encoding='utf-8')
    print(json.dumps({'slides': len(SLIDES), 'manifest': str(OUT/'build'/'slide_manifest.json')}))


if __name__ == '__main__':
    write_manifest()
