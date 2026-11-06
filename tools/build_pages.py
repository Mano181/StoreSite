import json, html, pathlib, re

"""Regenerates the site's HTML pages (and sitemap/robots/llms.txt once DOMAIN is set).

Run: python tools/build_pages.py
Shared chrome (navbar, footer, icon sprite) lives here, so edit it here and re-run
instead of editing every page. css/ and js/ are NOT generated.
"""
OUT = pathlib.Path(__file__).resolve().parent.parent
# Set to the real site URL (no trailing slash), e.g. "https://www.example.com", once hosting is chosen.
# While empty, canonical/og:url, absolute URLs in structured data, sitemap.xml, robots.txt and llms.txt are omitted.
DOMAIN = ""
PHONE_TEL = "+917200523519"
PHONE_DISP = "+91 72005 23519"
EMAIL = "info@esanelectric.com"
WA = "https://wa.me/917200523519"
NAME = "Esan Electric Company"
# Brand name -> (logo file or None, wordmark colour). With no logo file the name is shown as a coloured wordmark;
# drop the real logo into images/brands/ and set the path to use it.
BRAND_STYLE = {
    "Crompton": (None, "#1f4fa0"), "RR Kabel": (None, "#e30613"), "Legrand": ("images/brands/legrand.svg", None),
    "Anchor": (None, "#d71920"), "Finolex": (None, "#1c3f94"), "CG": (None, "#0b5cab"), "Orient": (None, "#0057a8"),
}
# Brands in the home page's scrolling strip (names supplied by the owner).
BRANDS = ["Crompton", "RR Kabel", "Legrand", "Anchor", "Finolex"]


def brand_mark(name):
    logo, color = BRAND_STYLE[name]
    if logo:
        return f'<img src="{logo}" alt="{html.escape(name)}" loading="lazy">'
    return f'<span style="color:{color}">{html.escape(name)}</span>'


# ── SVG icon sprite (stroke icons, 24x24) ──
SYMBOLS = {
    "bolt": '<path d="M13 2 3 14h9l-1 8 10-12h-9z"/>',
    "phone": '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/>',
    "mail": '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 6L2 7"/>',
    "pin": '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    "fan": '<circle cx="12" cy="12" r="1.8"/><path d="M12 10.2C11 6 11 3 13.5 3c2 0 2.5 2 1.5 4-.7 1.4-1.8 2.4-3 3.2z"/><path transform="rotate(120 12 12)" d="M12 10.2C11 6 11 3 13.5 3c2 0 2.5 2 1.5 4-.7 1.4-1.8 2.4-3 3.2z"/><path transform="rotate(240 12 12)" d="M12 10.2C11 6 11 3 13.5 3c2 0 2.5 2 1.5 4-.7 1.4-1.8 2.4-3 3.2z"/>',
    "plug": '<path d="M12 22v-5"/><path d="M9 8V2"/><path d="M15 8V2"/><path d="M18 8v5a4 4 0 0 1-4 4h-4a4 4 0 0 1-4-4V8Z"/>',
    "switch": '<rect x="6" y="2" width="12" height="20" rx="2"/><rect x="10" y="6" width="4" height="6" rx="1"/><path d="M9 17h6"/>',
    "bulb": '<path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.7 1.3 1.5 1.5 2.5"/><path d="M9 18h6"/><path d="M10 22h4"/>',
    "truck": '<path d="M14 18V6a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2v11a1 1 0 0 0 1 1h2"/><path d="M15 18H9"/><path d="M19 18h2a1 1 0 0 0 1-1v-3.65a1 1 0 0 0-.22-.624l-3.48-4.35A1 1 0 0 0 17.52 8H14"/><circle cx="17" cy="18" r="2"/><circle cx="7" cy="18" r="2"/>',
    "tag": '<path d="M12.586 2.586A2 2 0 0 0 11.172 2H4a2 2 0 0 0-2 2v7.172a2 2 0 0 0 .586 1.414l8.704 8.704a2.426 2.426 0 0 0 3.42 0l6.58-6.58a2.426 2.426 0 0 0 0-3.42z"/><circle cx="7.5" cy="7.5" r=".5"/>',
    "chat": '<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "heater": '<rect x="6" y="2" width="12" height="20" rx="5"/><path d="M12 8c-1.6 2-2.5 3-2.5 4.4a2.5 2.5 0 0 0 5 0C14.5 11 13.6 10 12 8z"/>',
    "home": '<path d="M3 10.5 12 3l9 7.5"/><path d="M5 9v11a1 1 0 0 0 1 1h4v-6h4v6h4a1 1 0 0 0 1-1V9"/>',
}
SPRITE = '<svg width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">' + "".join(
    f'<symbol id="i-{k}" viewBox="0 0 24 24">{v}</symbol>' for k, v in SYMBOLS.items()) + "</svg>"


def pic(src, alt, sizes="100vw", cls="", eager=False, w=None, h=None):
    """<picture> with WebP at 640w and full width (made next to the original on first build; needs Pillow), JPEG/PNG fallback."""
    try:
        from PIL import Image
    except ImportError:
        return f'<img src="{src}" alt="{alt}" loading="lazy"/>'
    f = OUT / src
    base = f.with_suffix("")
    im = Image.open(f)
    iw, ih = im.size
    small = base.parent / (base.name + "-640.webp")
    full = base.parent / (base.name + ".webp")
    for dest, width in ((small, 640), (full, iw)):
        if not dest.exists():
            r = im.convert("RGB") if im.mode not in ("RGB", "RGBA") else im
            if width < iw:
                r = r.resize((width, round(ih * width / iw)), Image.LANCZOS)
            r.save(dest, "WEBP", quality=80, method=6)
    stem = src.rsplit(".", 1)[0]
    c = f' class="{cls}"' if cls else ""
    load = 'fetchpriority="high"' if eager else 'loading="lazy"'
    sw = min(640, iw)
    return (f'<picture><source type="image/webp" srcset="{stem}-640.webp {sw}w, {stem}.webp {iw}w" sizes="{sizes}">'
            f'<img src="{src}" alt="{alt}" width="{w or iw}" height="{h or ih}" {load} decoding="async"{c}></picture>')


def ic(name):
    return f'<svg class="ic" aria-hidden="true"><use href="#i-{name}"/></svg>'


def head(title, desc, path, jsonld=None, noindex=False):
    ld = ""
    for block in (jsonld or []):
        ld += f'\n  <script type="application/ld+json">\n{json.dumps(block, indent=2, ensure_ascii=False)}\n  </script>'
    robots = '\n  <meta name="robots" content="noindex"/>' if noindex else ""
    canon = "" if noindex or not DOMAIN else f'\n  <link rel="canonical" href="{DOMAIN}/{path}"/>'
    og_url = f'\n  <meta property="og:url" content="{DOMAIN}/{path}"/>' if DOMAIN else ""
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(desc)}"/>{robots}{canon}
  <meta name="theme-color" content="#f5f2ec"/>
  <meta property="og:type" content="website"/>
  <meta property="og:site_name" content="{NAME}"/>
  <meta property="og:title" content="{html.escape(title)}"/>
  <meta property="og:description" content="{html.escape(desc)}"/>
{og_url}
  <link rel="icon" href="favicon.svg" type="image/svg+xml"/>
  <link rel="preconnect" href="https://fonts.googleapis.com"/>
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500..800&family=Manrope:wght@400;600;700&display=swap"/>
  <link rel="stylesheet" href="css/style.css"/>{ld}
</head>
<body>
{SPRITE}
<a href="#main" class="skip-link">Skip to content</a>
'''


DROP_DESC = {"fans": "Ceiling, exhaust, table &amp; pedestal", "wires": "Copper house wire by the roll",
             "lighting": "Bulbs, tubes, downlights &amp; battens", "switchgear": "MCBs, RCCBs &amp; distribution boards",
             "heaters": "Storage and instant water heaters"}


def nav(active):
    drop_items = "\n".join(
        f'          <li><a href="{c["file"]}"><strong>{c["label"].replace("&", "&amp;")}</strong><span>{DROP_DESC[k]}</span></a></li>'
        for k, c in CATS.items())
    def a(href, label, key):
        cls = ' class="active" aria-current="page"' if key == active else ""
        return f'      <li><a href="{href}"{cls}>{label}</a></li>'
    return f'''
<nav class="navbar" aria-label="Main">
  <div class="nav-inner">
    <a href="index.html" class="nav-logo" aria-label="Esan Electric home">
      <span class="nl-board"><span class="nl-in"><b>Esan Electric</b><i>Wholesale</i></span></span>
    </a>
    <ul class="nav-links" id="site-menu">
{a("index.html", "Home", "home")}
      <li class="has-drop">
        <a href="products.html"{' class="active" aria-current="page"' if active == "products" else ""}>Products</a>
        <ul class="drop">
{drop_items}
        </ul>
      </li>
{a("wholesale.html", "Our Process", "wholesale")}
{a("contact.html", "Contact", "contact")}
      <li class="drawer-actions"><a href="tel:{PHONE_TEL}" class="da-call">{ic("phone")} Call</a><a href="{WA}" target="_blank" rel="noopener" class="da-wa">{ic("chat")} WhatsApp</a></li>
    </ul>
    <div class="nav-actions">
      <a href="tel:{PHONE_TEL}" class="nav-phone">{ic("phone")} {PHONE_DISP}</a>
      <a href="contact.html" class="btn-teal">Get in Touch</a>
    </div>
    <button class="hamburger" aria-label="Menu" aria-expanded="false" aria-controls="site-menu"><span></span><span></span><span></span></button>
  </div>
</nav>
'''


FOOTER = f'''
<footer class="footer dark">
  <div class="footer-grid">
    <div class="footer-brand">
      <div class="wordmark"><div class="bolt">{ic("bolt")}</div>Esan Electric Company</div>
      <p>Wholesale fans, wires &amp; cables, lighting, MCB switchgear and water heaters for retail shops, dealers, contractors and builders across Tamil Nadu.</p>
      <a href="tel:{PHONE_TEL}" class="footer-phone">{PHONE_DISP}</a>
    </div>
    <div>
      <h4>Quick Links</h4>
      <ul class="footer-links">
        <li><a href="index.html">Home</a></li>
        <li><a href="products.html">Products</a></li>
        <li><a href="fans.html">Fans</a></li>
        <li><a href="wires.html">Wires &amp; Cables</a></li>
        <li><a href="lighting.html">Lighting</a></li>
        <li><a href="switchgear.html">MCB &amp; Switchgear</a></li>
        <li><a href="heaters.html">Water Heaters</a></li>
        <li><a href="wholesale.html">Our Process</a></li>
        <li><a href="contact.html">Contact Us</a></li>
      </ul>
    </div>
    <div>
      <h4>Contact</h4>
      <ul class="footer-contact">
        <li><a href="mailto:{EMAIL}">{ic("mail")} {EMAIL}</a></li>
        <li><a href="contact.html">{ic("pin")} Tamil Nadu</a></li>
      </ul>
    </div>
  </div>
  <div class="footer-bottom">
    <p>© Esan Electric Company. All rights reserved.</p>
    <p>Wholesale supply across Tamil Nadu</p>
  </div>
</footer>

<div class="floating-btns">
  <a href="tel:{PHONE_TEL}" class="float-btn ph" data-tip="Call Us" aria-label="Call us">{ic("phone")}</a>
  <a href="{WA}" target="_blank" rel="noopener" class="float-btn wa" data-tip="WhatsApp" aria-label="WhatsApp">{ic("chat")}</a>
</div>
<div class="mobile-bar">
  <a href="tel:{PHONE_TEL}" class="mb-call">{ic("phone")} Call</a>
  <a href="{WA}" target="_blank" rel="noopener" class="mb-wa">{ic("chat")} WhatsApp</a>
</div>

<script src="js/main.js"></script>
</body>
</html>
'''


def page_hero(eyebrow, h1, p, crumb=""):
    top = crumb or f'<div class="section-eyebrow">{eyebrow}</div>'
    return f'''
<main id="main">
<section class="page-hero">
  <div class="container">
  {top}
  <h1>{h1}</h1>
  <p>{p}</p>
  </div>
</section>
'''


# ── Business schema ──
ORG = {
    "@context": "https://schema.org",
    "@type": "WholesaleStore",
    "name": NAME,
    "description": "Wholesale supplier of fans, wires & cables, lighting, MCB switchgear and water heaters for retail shops, dealers, contractors and builders in Tamil Nadu.",
    "telephone": PHONE_TEL,
    "email": EMAIL,
    "areaServed": {"@type": "AdministrativeArea", "name": "Tamil Nadu, India"},
    # Add streetAddress / addressLocality / postalCode here once the real address is known.
    "address": {"@type": "PostalAddress", "addressRegion": "Tamil Nadu", "addressCountry": "IN"},
    "openingHours": "Mo-Sa 09:00-19:00",
    "makesOffer": [{"@type": "Offer", "itemOffered": {"@type": "Product", "name": n}}
                   for n in ("Ceiling fans, exhaust fans, table and pedestal fans",
                             "Electrical wires and cables", "LED lighting", "MCB and switchgear", "Water heaters")],
}

# ── Products: each category lists `types` x `brands`; a card is made for every pair. Groups feed the filter tabs. ──
CATS = {
    "fans": {
        "file": "fans.html", "label": "Fans", "icon": "fan", "img": "images/stock/fans.jpg",
        "blurb": "Ceiling, BLDC, exhaust, table &amp; pedestal fans",
        "title": "Wholesale Fans in Tamil Nadu — Ceiling, BLDC, Exhaust, Table | Esan Electric",
        "desc": "Wholesale ceiling fans, BLDC fans, exhaust fans, table and pedestal fans for retail shops, dealers and contractors across Tamil Nadu. Bulk rates on request.",
        "h1": "Wholesale Fans",
        "lead": "Ceiling, BLDC, exhaust, table and pedestal fans for shops, dealers and project buyers across Tamil Nadu.",
        # (tab group, card label, image). One card per brand is made for each type; brands are owner-confirmed only for fans.
        "types": [("Ceiling Fans", "Ceiling Fan", "images/Products/ceiling-fans/standard-fan.png"),
                  ("Exhaust Fans", "Exhaust Fan", "images/stock/exhaust-fan.jpg"),
                  ("Table &amp; Pedestal", "Table &amp; Pedestal Fan", "images/stock/table-pedestal-fan.jpg")],
        "brands": ["Crompton", "CG", "Anchor", "Orient"],
    },
    "wires": {
        "file": "wires.html", "label": "Wires & Cables", "icon": "plug", "img": "images/stock/wires.jpg",
        "blurb": "Copper house wire and cables by the roll",
        "title": "Bulk Electrical Wires & Cables Supplier in Tamil Nadu | Esan Electric",
        "desc": "Bulk copper house wires and electrical cables for retail shops, electricians, contractors and builders across Tamil Nadu. Per-roll and bulk rates on request.",
        "h1": "Wires &amp; Cables",
        "lead": "Copper house wire and cables supplied by the roll for shops, electricians, contractors and builders across Tamil Nadu.",
        "types": [("House Wire", "House Wire", "images/stock/wires.jpg")],
        "brands": ["RR Kabel", "Anchor"],
    },
    "lighting": {
        "file": "lighting.html", "label": "Lighting", "icon": "bulb", "img": "images/stock/lighting.jpg",
        "blurb": "Bulbs, tubes, downlights &amp; battens",
        "title": "Wholesale LED Lights, Bulbs & Tubes in Tamil Nadu | Esan Electric",
        "desc": "Wholesale LED bulbs, tube lights, downlights and battens for retail shops, dealers and contractors across Tamil Nadu. Bulk rates on request.",
        "h1": "Wholesale LED Lighting",
        "lead": "LED bulbs, tubes, downlights and battens for dealers, contractors and builders across Tamil Nadu.",
        "types": [("Bulbs &amp; Tubes", "LED Bulbs &amp; Tubes", "images/stock/led-bulb.jpg"),
                  ("Downlights &amp; Battens", "Downlights &amp; Battens", "images/stock/lighting.jpg")],
        "brands": ["Crompton", "Anchor"],
    },
    "switchgear": {
        "file": "switchgear.html", "label": "MCB & Switchgear", "icon": "switch", "img": "images/stock/switchgear.jpg",
        "blurb": "MCBs, RCCBs, isolators &amp; distribution boards",
        "title": "Wholesale MCB & Switchgear in Tamil Nadu — MCB, RCCB, Distribution Boards | Esan Electric",
        "desc": "Wholesale MCBs, MCCBs, RCCBs, isolators and distribution boards for retail shops, electricians, contractors and builders across Tamil Nadu. Bulk rates on request.",
        "h1": "MCB &amp; Switchgear",
        "lead": "Circuit breakers, earth-leakage protection, isolators and distribution boards for shops, electricians, contractors and builders across Tamil Nadu.",
        "types": [("Breakers", "MCB &amp; Breakers", "images/stock/switchgear.jpg"),
                  ("Switches &amp; Boards", "Switches &amp; Distribution Boards", "images/stock/distribution-board.jpg")],
        "brands": ["Legrand", "Anchor"],
    },
    # Provisional: the owner supplies water heaters but has not yet sent brands, types or photos.
    "heaters": {
        "file": "heaters.html", "label": "Water Heaters", "icon": "heater", "img": None,
        "blurb": "Water heaters for homes, shops &amp; projects",
        "title": "Wholesale Water Heaters in Tamil Nadu | Esan Electric",
        "desc": "Wholesale water heaters for retail shops, dealers, electricians, contractors and builders across Tamil Nadu. Bulk rates on request.",
        "h1": "Water Heaters",
        "lead": "Water heaters for shops, dealers, electricians, contractors and builders across Tamil Nadu.",
        "types": [("Water Heaters", "Water Heater", None)],
        "brands": [],
    },
}


def brand_cards(cat):
    """(group, label, brand, image) for every type x brand of a category."""
    c = CATS[cat]
    return [(g, label, br, img) for g, label, img in c["types"] for br in c["brands"]]


def product_card(cat, group, label, brand, img):
    title = f"{label} - {brand}"
    attr = html.escape(html.unescape(title), quote=True)
    thumb = (pic(img, attr, "(max-width:560px) 100vw, (max-width:1024px) 50vw, 400px", "fit" if img.startswith("images/Products/") else "") if img else ic(CATS[cat]["icon"]))
    # A brand catalogue PDF dropped into pdfs/<slug>.pdf turns the card into a download link on the next build.
    slug = re.sub(r"[^a-z0-9]+", "-", html.unescape(title).lower()).strip("-")
    pdf = f"pdfs/{slug}.pdf"
    link = (f' href="{pdf}" target="_blank" rel="noopener"') if (OUT / pdf).exists() else ""
    tag = "a" if link else "article"
    hint = '<span class="p-pdf">Download PDF →</span>' if link else ""
    return f'''      <{tag} class="product-card reveal" data-group="{group}"{link}>
        <div class="p-thumb">{thumb}</div>
        <div class="p-body"><span class="p-type">{label}</span><h3 class="p-brandname" aria-label="{attr}">{brand_mark(brand)}</h3>{hint}</div>
      </{tag}>
'''


def category_page(key):
    c = CATS[key]
    label = c["h1"].replace("&amp;", "&")
    products = []
    for i, (_g, label, br, img) in enumerate(brand_cards(key)):
        prod = {"@type": "Product", "name": html.unescape(f"{label} - {br}"), "category": c["label"]}
        if img and DOMAIN:
            prod["image"] = f"{DOMAIN}/{img}"
        products.append({"@type": "ListItem", "position": i + 1, "item": prod})
    ld = [
        {"@context": "https://schema.org", "@type": "ItemList", "name": label, "itemListElement": products},
    ]
    if DOMAIN:
        ld.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{DOMAIN}/"},
            {"@type": "ListItem", "position": 2, "name": "Products", "item": f"{DOMAIN}/products.html"},
            {"@type": "ListItem", "position": 3, "name": c["label"], "item": f"{DOMAIN}/{c['file']}"}]})
    s = head(c["title"], c["desc"], c["file"], ld) + nav("products")
    crumb = f'<nav class="breadcrumb" aria-label="Breadcrumb"><a href="index.html">Home</a> <span>/</span> <a href="products.html">Products</a> <span>/</span> {c["label"].replace("&", "&amp;")}</nav>'
    s += page_hero("Product Category", c["h1"], c["lead"], crumb)
    groups = list(dict.fromkeys(t[0] for t in c["types"]))
    tabs = ""
    if len(groups) > 1:
        tabs = '    <div class="filter-tabs" role="group" aria-label="Filter products">\n      <button type="button" class="filter-tab active" data-filter="all">All</button>\n' + "".join(
            f'      <button type="button" class="filter-tab" data-filter="{g}">{g}</button>\n' for g in groups) + '    </div>\n'
    s += f'''
<section class="products-section">
  <div class="container">
{tabs}'''
    # Godown rack: one labelled shelf per type group
    for i, g in enumerate(groups):
        cards = [b for b in brand_cards(key) if b[0] == g]
        if cards:
            s += f'''    <section class="rack" data-group="{g}" aria-label="{g}">
      <div class="rack-tag">Rack {chr(65 + i)} · {g}</div>
      <div class="products-grid">
''' + "\n".join(product_card(key, *b) for b in cards) + '''      </div>
    </section>
'''
    if not c["brands"]:
        s += f'''    <div class="brands-soon">{ic(c["icon"])}<div><h3>Brands coming soon</h3><p>We supply {c["label"].lower()}. Tell us what you need and we will send a quote.</p><a href="contact.html?category={key}" class="text-link">Request a quote {ic("arrow")}</a></div></div>
'''
    s += '''    <p class="back-link"><a href="products.html">← All categories</a></p>
  </div>
</section>
</main>
'''
    return s + FOOTER


def cat_cards(h="h3"):
    out = ""
    for n, (k, c) in enumerate(CATS.items(), 1):
        out += f'''      <a href="{c["file"]}" class="cat-card reveal-scale">
        <div class="cat-thumb{"" if c["img"] else " cat-icon"}">{pic(c["img"], "", "(max-width:1024px) 100vw, 40vw") if c["img"] else ic(c["icon"])}</div>
        <div class="cat-info">
          <div class="cat-idx">0{n}</div>
          <h3>{c["label"].replace("&", "&amp;")}</h3>
          <p>{c["blurb"]}</p>
        </div>
        <div class="cat-arrow">{ic("arrow")}</div>
      </a>
'''
    return out


def switch_plate():
    out = ""
    for n, (k, c) in enumerate(CATS.items(), 1):
        out += f'''      <a href="{c["file"]}" class="rocker" role="listitem">
        <span class="rk-win" aria-hidden="true">{pic(c["img"], "", "(max-width:560px) 45vw, 18vw") if c["img"] else ic(c["icon"])}</span>
        <span class="rk-led" aria-hidden="true"></span>
        <span class="rk-key" aria-hidden="true">{ic(c["icon"])}</span>
        <span class="rk-label"><small>0{n}</small>{c["label"].replace("&", "&amp;")}</span>
      </a>
'''
    return out


def products_page():
    s = head("Wholesale Fans, Wires & LED Lighting — Product Range | Esan Electric",
             "Browse Esan Electric's wholesale range: fans, wires and cables, LED lighting, MCB switchgear and water heaters for retail shops, dealers and contractors across Tamil Nadu.",
             "products.html") + nav("products")
    s += page_hero("Product Range", "What We Supply",
                   "Five focused categories, supplied wholesale to shops, dealers, contractors and builders across Tamil Nadu.")
    s += f'''
<section class="products-section">
  <div class="container">
    <div class="bento">
{cat_cards()}    </div>
  </div>
</section>
</main>
'''
    return s + FOOTER


def index_page():
    s = head("Esan Electric — Wholesale Fans, Wires & LED Lighting in Tamil Nadu",
             "Esan Electric Company supplies fans, wires & cables, LED lighting, MCB switchgear and water heaters wholesale to retail shops, dealers, contractors and builders across Tamil Nadu. Request our rate sheet.",
             "index.html", [ORG]) + nav("home")
    strip = ""
    if BRANDS:
        def tags(extra=""):
            return "".join(f'<li{extra} style="--sw:{(-3, 2.5, -2, 3.5)[i % 4]}deg">{brand_mark(b)}</li>' for i, b in enumerate(BRANDS))
        marks = tags() + tags(' aria-hidden="true" class="dup"') * 2
        strip = f'''
<section class="brands" aria-label="Brands we stock">
  <div class="container"><span class="brands-label">Dealer &amp; stockist of</span></div>
  <div class="brands-belt"><ul>{marks}</ul></div>
</section>'''
    shelf = f'''<figure class="hero-photo">
        {pic("images/stock/hero.jpg", "A ceiling fan and brass pendant lamps", "(max-width:1024px) 100vw, 40vw", eager=True)}
      </figure>'''
    # Order dockets: who we supply (owner's three customer types plus homes)
    sectors = "".join(f"""      <article class="docket reveal">
        <div class="docket-head"><span>Docket No. {i + 1:02d}</span><span class="docket-stamp">{lot}</span></div>
        <div class="docket-photo">{pic(f"images/stock/{img}.jpg", "", "(max-width:600px) 100vw, (max-width:1024px) 50vw, 25vw")}</div>
        <h3>{t}</h3>
        <p>{p}</p>
      </article>
""" for i, (img, lot, t, p) in enumerate([
        ("sector-shop", "Shop lots", "Retail shops &amp; dealers", "Restock fast-moving fans, wires and lights at wholesale rates, in lot sizes that suit a shop."),
        ("sector-electrician", "Job lots", "Electricians", "Wire, fans and fittings for the jobs you take on, quoted together in one list."),
        ("sector-site", "Project lots", "Contractors", "Project quantities of wire, fans and lighting, delivered to your site within Tamil Nadu."),
        ("sector-home", "Home sets", "Homes &amp; apartments", "Ceiling fans, house wire and LED lighting for residential projects."),
    ]))
    why = "".join(f"""        <li class="why-item reveal">
          <span class="why-n">0{n}</span>
          <div>
            <h3>{ic(i)} {t}</h3>
            <p>{p}</p>
          </div>
        </li>
""" for n, (i, t, p) in enumerate([
        ("check", "Branded stock", "We resell manufacturers&#39; brands, so you can stock the names your customers ask for."),
        ("tag", "Wholesale rates", "Rates are quoted on request and depend on quantity, with bulk benefits on larger orders."),
        ("clock", "Quotes within an hour", "Send your list and we reply with rates within an hour."),
        ("truck", "Supply across Tamil Nadu", "We supply to shops, sites and godowns within Tamil Nadu."),
        ("phone", "Talk to a person", "Call, WhatsApp or use the form, Mon–Sat, 9 AM–7 PM."),
    ], 1))
    steps = "".join(f"""        <li class="reveal">
          <span class="step-num">0{n}</span>
          <h3>{t}</h3>
          <p>{p}</p>
        </li>
""" for n, t, p in [
        (1, "Build your list", "Tell us what you need and how much, using the enquiry form, a call or WhatsApp."),
        (2, "Get wholesale rates", "We reply within an hour with rates and any bulk benefits."),
        (3, "Receive in Tamil Nadu", "Confirm the order and we arrange supply to your shop or site."),
    ])
    uline = (
        '<svg class="uline" viewBox="0 0 300 24" preserveAspectRatio="none" aria-hidden="true">'
        '<path class="sw" d="M3 20C70 12 170 8 297 9C190 13 80 21 3 20Z"/>'
        '<circle class="spark" r="3.2" cx="0" cy="0"/>'
        '<g class="flick"><path d="M298 9l5-4M298 9l6 1M298 9l4 5"/></g></svg>')
    s += f"""
<main id="main">
<section class="hero">
  <div class="hero-grid">
    <div class="hero-content">
      <div class="hero-tag">Wholesale supply &middot; Tamil Nadu</div>
      <h1>Quality Electricals at the <span class="hl">Right Price.{uline}</span></h1>
      <p class="hero-sub">Stock your shop or supply your next project. Esan Electric supplies fans, wires &amp; cables, LED lighting, MCB switchgear and water heaters to retail shops, dealers, contractors and builders across Tamil Nadu.</p>
      <div class="hero-btns">
        <a href="products.html" class="btn-hero-primary">Browse Products {ic("arrow")}</a>
        <span class="open-chip" id="openChip"><span class="dot"></span><span class="oc-text">Mon–Sat, 9 AM–7 PM</span></span>
      </div>
      </ol>
    </div>
    <div class="hero-media">
      {shelf}
    </div>
  </div>
</section>

<section class="categories">
  <div class="container">
    <div class="section-head split">
      <div>
        <span class="docket-eyebrow">Featured products</span>
        <h2 class="wipe">What we supply.</h2>
        <p>Crafting Spaces, Powering Progress</p>
      </div>
      <a href="products.html" class="text-link">View all products {ic("arrow")}</a>
    </div>
    <div class="plate" role="list">
{switch_plate()}    </div>
  </div>
</section>
{strip}
<section class="sectors">
  <div class="container">
    <div class="section-head center">
      <h2 class="wipe">Solutions for Every Electrical Need</h2>
      <p>Whatever your order size, we have a route for you.</p>
    </div>
    <div class="dockets">
{sectors}    </div>
    <div class="route-pick reveal">
      <a href="contact.html?type=retail" class="route"><span class="route-q">Run a shop?</span><span class="route-a">Request dealer rates {ic("arrow")}</span></a>
      <a href="contact.html?type=contractor" class="route route-hot"><span class="route-q">On a project?</span><span class="route-a">Request a project quote {ic("arrow")}</span></a>
    </div>
  </div>
</section>

<section class="why dark">
  <div class="container why-wrap">
    <div class="why-head">
      <h2 class="wipe">Why shops and contractors buy from Esan Electric.</h2>
      <figure class="why-photo">{pic("images/stock/sector-builder.jpg", "Builders reviewing plans on site", "(max-width:1024px) 100vw, 40vw")}</figure>
    </div>
    <ol class="why-list">
{why}    </ol>
  </div>
</section>

<section class="process">
  <div class="container">
    <div class="process-head">
      <h2 class="wipe">Our simple ordering process</h2>
      <p>From your list to your shop or site in three steps.</p>
    </div>
    <ol class="wire-steps">
{steps}    </ol>
  </div>
</section>

<section class="cta-band dark">
  <div class="container cta-inner reveal">
    <div class="cta-text">
      <h2>Request your wholesale quote today.</h2>
      <p>Tell us what you need and the quantity. We reply with rates within an hour.</p>
      <a href="{WA}" target="_blank" rel="noopener" class="cta-wa">{ic("chat")} Or message us on WhatsApp</a>
    </div>
    <a href="contact.html" class="cta-circle">Get in Touch {ic("arrow")}</a>
  </div>
</section>
</main>
"""
    return s + FOOTER


FAQ = [
    ("Do you supply electrical wires in bulk?",
     "Yes. We supply copper house wire and cables by the roll and in bulk quantities for shops, electricians, contractors and builders in Tamil Nadu. Send us the gauge and quantity for a quote."),
    ("Can a retail shop buy fans and lights wholesale from you?",
     "Yes. Retail shops and dealers can buy ceiling fans, exhaust fans, table fans, pedestal fans and LED lighting at wholesale rates. Request our rate sheet for current dealer rates."),
    ("What is the minimum order quantity?",
     "Minimum order quantities depend on the product. Ask us for the minimum order for the specific model or gauge you need."),
    ("Do you deliver across Tamil Nadu?",
     "Yes. We supply to shops, sites and godowns within Tamil Nadu. Tell us your town or city when you enquire."),
    ("Do you list prices on the website?",
     "No. Rates change with quantity and market conditions, so we quote on request. Fill the enquiry form, call or message us on WhatsApp and we respond within an hour."),
    ("Which products do you sell?",
     "We sell five categories: fans (ceiling, BLDC, exhaust, table and pedestal), wires and cables, LED lighting (bulbs, tubes, downlights and battens), MCB and switchgear (MCBs, MCCBs, RCCBs, isolators and distribution boards), and water heaters."),
]


def wholesale_page():
    ld = [{"@context": "https://schema.org", "@type": "FAQPage",
           "mainEntity": [{"@type": "Question", "name": q,
                           "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}]
    s = head("Our Process: Wholesale Supply for Shops, Dealers & Contractors in Tamil Nadu | Esan Electric",
             "How to buy fans, wires, LED lighting, MCB switchgear and water heaters wholesale from Esan Electric: who we supply, minimum orders, how to get rates, and delivery within Tamil Nadu.",
             "wholesale.html", ld) + nav("wholesale")
    s += page_hero("How we work", "Our Simple Process",
                   "We tailor our approach to your needs, whether you&#39;re an individual homeowner, a large-scale contractor or a shop owner.")
    work = "".join(f'''        <li class="reveal">
          <span class="step-num">0{n}</span>
          <div>
            <h3>{t}</h3>
            <p>{d}</p>
          </div>
        </li>
''' for n, t, d in [
        (1, "Requirement &amp; Sampling", "We analyze your project needs. For architects and interiors, we provide product samples to ensure the perfect match."),
        (2, "Quote &amp; Approval", "We provide detailed, competitive quotes, including for bulk orders."),
        (3, "Delivery &amp; Support", "Once confirmed, we ensure swift dispatch from our ready stock, coordinating logistics to meet your site timeline."),
    ])
    s += f'''
<section class="process">
  <div class="container">
    <div class="process-grid">
      <div class="process-img reveal-left">{pic("images/stock/process.jpg", "Boxed stock stacked in a warehouse", "(max-width:1024px) 100vw, 50vw")}</div>
      <ol class="process-steps">
{work}      </ol>
    </div>
  </div>
</section>

<section class="products-section">
  <div class="container narrow">
'''
    s += '''
    <h2>Frequently asked questions</h2>
    <div class="faq">
'''
    for q, a in FAQ:
        s += f'      <details><summary>{html.escape(q)}</summary><p>{html.escape(a)}</p></details>\n'
    s += '''    </div>
    <p style="margin-top:32px;"><a href="contact.html" class="btn-teal">Get Our Rate Sheet</a></p>
  </div>
</section>
</main>
'''
    return s + FOOTER


def contact_page():
    s = head("Contact Esan Electric — Request Wholesale Rates in Tamil Nadu",
             "Send a wholesale enquiry to Esan Electric for fans, wires, LED lighting, MCB switchgear and water heaters, or call and WhatsApp us. We reply within an hour.",
             "contact.html") + nav("contact")
    s += page_hero("Contact Us", "Get in Touch",
                   "Tell us what you need and how much. <strong class=\"reply\">We reply within an hour.</strong>")
    s += f'''
<section class="contact-section">
  <div class="container">
    <div class="contact-layout">

      <div class="contact-left reveal-left">
        <h2>We're here<br>to help.</h2>
        <p>Reach us by phone, WhatsApp or the enquiry form.</p>

        <div class="info-card">
          <div class="i-icon">{ic("pin")}</div>
          <div>
            <h4>Address</h4>
            <p>No. 1, Electrical Market Street<br>Your City — 600001, Tamil Nadu</p>
          </div>
        </div>
        <div class="info-card">
          <div class="i-icon">{ic("phone")}</div>
          <div>
            <h4>Phone</h4>
            <a href="tel:{PHONE_TEL}">{PHONE_DISP}</a>
          </div>
        </div>
        <div class="info-card">
          <div class="i-icon">{ic("mail")}</div>
          <div>
            <h4>Email</h4>
            <a href="mailto:{EMAIL}">{EMAIL}</a>
          </div>
        </div>
        <div class="info-card">
          <div class="i-icon">{ic("clock")}</div>
          <div>
            <h4>Business Hours</h4>
            <p>Mon – Sat: 9:00 AM – 7:00 PM<br>Sunday: Closed</p>
          </div>
        </div>

        <div class="map-box">{ic("pin")} Add Google Maps embed here</div>
      </div>

      <div class="form-card reveal">
        <h3>Send an Enquiry</h3>
        <p>Fill in your details and we'll get back to you with rates and availability.</p>
        <form id="inquiryForm" action="https://api.web3forms.com/submit" method="POST" novalidate>
          <input type="hidden" name="access_key" value="YOUR_WEB3FORMS_ACCESS_KEY"/>
          <input type="hidden" name="subject" value="New wholesale enquiry — Esan Electric"/>
          <div class="form-row">
            <div class="form-group">
              <label for="f-name">Full name</label>
              <input id="f-name" type="text" name="name" placeholder="Your name" autocomplete="name" required/>
            </div>
            <div class="form-group">
              <label for="f-phone">Phone number</label>
              <input id="f-phone" type="tel" name="phone" placeholder="+91 XXXXX XXXXX" autocomplete="tel" required/>
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label for="f-type">I am a</label>
              <select id="f-type" name="buyer_type">
                <option value="">— Select —</option>
                <option value="retail">Retail shop / dealer</option>
                <option value="contractor">Contractor / builder</option>
                <option value="other">Other</option>
              </select>
            </div>
            <div class="form-group">
              <label for="f-city">Town or city</label>
              <input id="f-city" type="text" name="city" placeholder="Where should we deliver?"/>
            </div>
          </div>
          <div class="form-group">
            <label for="f-message">Products &amp; quantities</label>
            <textarea id="f-message" name="message" placeholder="e.g. 1.5 sq mm wire, 50 rolls; 48&quot; ceiling fans, 100 pcs" required></textarea>
            <span class="hint">Include the size, rating or quantity if you know it.</span>
          </div>
          <button type="submit" class="btn-submit"><span class="spin" aria-hidden="true"></span><span class="bt">Send Enquiry</span></button>
          <p id="formStatus" class="form-status" role="status" aria-live="polite"></p>
        </form>
        <div class="form-success" id="formSuccess" hidden>
          <div class="ok">{ic("check")}</div>
          <h3>Enquiry sent</h3>
          <p>Thanks. We will reply within an hour.</p>
          <a id="waFollow" href="{WA}" target="_blank" rel="noopener" class="btn-submit">{ic("chat")} Continue on WhatsApp</a>
          <button type="button" class="link-btn" id="formAgain">Send another enquiry</button>
        </div>
      </div>

    </div>
  </div>
</section>
</main>
'''
    return s + FOOTER


def not_found_page():
    s = head("Page not found — Esan Electric", "Page not found.", "404.html", noindex=True) + nav("")
    s += page_hero("404", "Page not found", "That page doesn't exist. Try one of these instead.")
    s += f'''
<section class="products-section">
  <div class="container">
    <div class="bento">
{cat_cards()}    </div>
    <p class="back-link"><a href="index.html">← Back to home</a></p>
  </div>
</section>
</main>
'''
    return s + FOOTER


files = {"index.html": index_page(), "products.html": products_page(),
         "wholesale.html": wholesale_page(), "contact.html": contact_page(),
         "404.html": not_found_page()}
for k, c in CATS.items():
    files[c["file"]] = category_page(k)
for name, content in files.items():
    (OUT / name).write_text(content, encoding="utf-8", newline="\n")

(OUT / "favicon.svg").write_text(
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="8" fill="#ca0006"/>'
    '<path d="M18 5 8 18h7l-1 9 10-13h-7z" fill="#ffffff"/></svg>\n', encoding="utf-8", newline="\n")

# ── root files ──
pages = ["index.html", "products.html", "fans.html", "wires.html", "lighting.html", "switchgear.html", "heaters.html", "wholesale.html", "contact.html"]
root_files = {}
if DOMAIN:
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for p in pages:
        loc = f"{DOMAIN}/" if p == "index.html" else f"{DOMAIN}/{p}"
        sm += f"  <url><loc>{loc}</loc></url>\n"
    root_files["sitemap.xml"] = sm + "</urlset>\n"
    root_files["robots.txt"] = f"User-agent: *\nAllow: /\n\nSitemap: {DOMAIN}/sitemap.xml\n"
    root_files["llms.txt"] = (
        f"# {NAME}\n\n"
        "> Wholesale supplier of fans, wires & cables, LED lighting, MCB switchgear and water heaters for retail shops, dealers, contractors and builders "
        "in Tamil Nadu, India. Prices are quoted on request.\n\n"
        "## What we sell\n"
        "- Fans: ceiling (standard, BLDC, designer, high-speed), exhaust, table and pedestal fans\n"
        "- Wires & cables: copper house wire by the roll and in bulk\n"
        "- Lighting: LED bulbs, tube lights, downlights and battens\n"
        "- MCB & switchgear: MCBs, MCCBs, RCCBs, isolators and distribution boards\n"
        "- Water heaters\n\n"
        "## Who we supply\n"
        "- Retail shops and dealers restocking in wholesale lots\n"
        "- Contractors and builders needing project quantities\n"
        "- Service area: Tamil Nadu only\n\n"
        "## How to buy\n"
        f"Request rates via the enquiry form, phone {PHONE_DISP}, WhatsApp {WA}, or email {EMAIL}. "
        "We reply within an hour. Business hours: Mon-Sat 9:00 AM-7:00 PM.\n\n"
        "## Pages\n" + "".join(f"- [{p}]({DOMAIN}/{p})\n" for p in pages))
for name in ("sitemap.xml", "robots.txt", "llms.txt"):
    f = OUT / name
    if name in root_files:
        f.write_text(root_files[name], encoding="utf-8", newline="\n")
    elif f.exists():
        f.unlink()
print("done")
