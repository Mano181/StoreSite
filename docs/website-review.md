# Esan Electric website review

Reviewed 14 Nov 2026. Read-only pass; nothing in the site was changed.

**How this was checked**

- Code: `tools/build_pages.py`, `CSS/style.css`, `js/main.js`, all generated `*.html`, asset folders, git state.
- Browser: the working tree served locally (`python3 -m http.server`) at 1280×800 and 360×740 with a mobile user agent. Every page was loaded; all 155 local asset references were requested and none were broken.
- **There is no live site.** `DOMAIN = ""` in `tools/build_pages.py:12` and the brief's URL was a placeholder. Everything that needs a real host (HTTPS, headers, caching, redirects, Core Web Vitals, Google indexing, Google Business Profile) is marked **Unverified**.
- The brief's context block was left as a template. I assumed: wholesale distributor, Tamil Nadu, B2B-first with some retail, goal = catalogue + enquiry by call/WhatsApp/form, static site. Corrections change some priorities (see Open questions).
- Screenshots were taken with the browser pane in the background, so scroll-reveal timing could not be judged. Layout findings below come from DOM measurements.

---

## 1. Verdict

The site is a well-designed brochure that is **not ready to promote**. The visual identity is distinctive and the mobile basics (sticky Call/WhatsApp bar, 44px targets, 16px inputs) are right. But the things that turn a visitor into an enquiry are unfinished:

- The address is a placeholder ("No. 1, Electrical Market Street, Your City — 600001"), the map is a placeholder box, and there is no GSTIN, About page, shop photo or review anywhere.
- The enquiry form cannot send: the access key is `YOUR_WEB3FORMS_ACCESS_KEY`.
- The stylesheet is linked as `css/style.css` but the folder is `CSS/`. On any Linux host (GitHub Pages, Netlify, most shared hosting) every page loads unstyled.
- There are no product pages. A "product" is a card that opens a brand PDF of up to 54 MB, or does nothing at all.
- The home page pulls about 16 MB of autoplay video.
- Nothing can be indexed properly yet: no domain, canonical, sitemap or robots file.

Biggest strengths: design quality, clean generator-based code, accessibility groundwork. Biggest risks: fake-looking contact details, a dead form, and heavy downloads on mobile data. Roughly two to three focused days of work would make it promotable.

---

## 2. Scorecard

| # | Area | Score | Reason |
|---|------|:-----:|--------|
| 1 | First impression and trust | 2 | Clear on what and for whom in 5 seconds; no real address, GSTIN, proof of dealership, reviews or About. |
| 2 | Information architecture | 3 | Simple and consistent 7-category tree with breadcrumbs; no brand pages, no search, several dead-end cards. |
| 3 | Product pages | 1 | None exist. Cards link to raw PDFs or to nothing; no specs, models, price or CTA. |
| 4 | Conversion | 2 | Sticky Call/WhatsApp is good; the form is dead and category pages have no enquiry CTA in the content. |
| 5 | Visual design | 4 | Distinctive, coherent, not template-like; let down by generic stock photos. |
| 6 | Mobile portrait | 4 | No horizontal overflow at 360px, good targets and drawer; PDFs and video are hostile on mobile data. |
| 7 | SEO | 2 | Good titles and one H1 per page; no domain, canonical, sitemap, og:image, address, or city-level terms. |
| 8 | Performance | 2 | Two 8 MB autoplay videos and unoptimised poster JPEGs on the home page; 3 render-blocking Google font families. |
| 9 | Accessibility | 4 | Skip link, focus styles, labels, reduced-motion all present; a few contrast and motion-control gaps. |
| 10 | Security and privacy | 3 | Static site with little attack surface; no spam protection on the form, test pages and price lists would ship publicly. |
| 11 | Code quality | 3 | Single-source generator is a sound choice; dead code, case mismatch, nothing committed, no dependency list. |
| 12 | Content | 2 | Placeholders, typos, brand misspelling, "five" vs "seven" categories, English only. |
| 13 | Competitive position | 2 | Better looking than local competitors; behind them on proof of authorisation and per-product enquiry. |
| 14 | Business features | 2 | Catalogue PDFs exist; no bulk-quote list, GST details, delivery areas, warranty or returns information. |

---

## 3. Findings

Severity: Critical = blocks launch or loses most enquiries. Effort: S under 2 hours, M half a day to a day, L more than a day.

| Area | Issue | Severity | Evidence | Recommended fix | Effort |
|------|-------|----------|----------|-----------------|:------:|
| 11 Code | Stylesheet path case mismatch. Works on macOS, 404s on Linux hosts, so the whole site renders unstyled. | Critical | `build_pages.py:134` emits `css/style.css`; `git ls-files` shows `CSS/style.css`. | Rename the folder to `css/` with `git mv` (two-step rename on macOS). | S |
| 1 Trust | Placeholder address shown to visitors. | Critical | `build_pages.py:766`, rendered on `contact.html`. | Put in the real address; add it to `ORG` (`:259`) and the footer (`:210`, currently just "Tamil Nadu"). | S |
| 4 Conversion | Enquiry form cannot send. JS falls back to a WhatsApp link, so the form silently becomes a second WhatsApp button. | Critical | `build_pages.py:798` `YOUR_WEB3FORMS_ACCESS_KEY`; `main.js:154-157`. | Create the Web3Forms key, set it, send one real test enquiry and confirm it arrives. | S |
| 11 Code | Almost nothing is committed. `images/`, `fonts/`, `pdfs/`, `videos/`, two category pages and `favicon.svg` are untracked; the last commit is 6 Nov. A deploy from git would ship a broken site, and a disk failure loses the work. | Critical | `git status`: 13 modified, 11 untracked paths. | Add `.gitignore` (`.DS_Store`, `.venv/`, `Catalog:List Pdfs/`, `videos/ai-input/`), then commit. Decide PDF hosting first (next row). | S |
| 8 Performance | 1.0 GB of PDFs. `pdfs/` is 727 MB with 50 files, only 21 linked; the same file is stored under several names (the 53.9 MB Crompton catalogue four times). Too large for GitHub Pages (1 GB site limit) and painful in git. | High | `du -sh pdfs`; `ls -laS pdfs`; link audit of `*.html`. | Delete unlinked duplicates, compress the rest (most catalogues will drop to 3–8 MB at 150 dpi), and keep only one copy per catalogue. | M |
| 3 Product | Product cards open raw PDFs in a new tab with no size warning: 54 MB (Crompton fans), 45 MB (Kavaski Kosmo), 32 MB (Norwood), 23 MB (Anchor fans). On 4G that is minutes and real data cost; many will abandon. | High | `fans.html`, `switches.html`, `wires.html` card `href`s; file sizes on disk. | Compress, show "PDF · 6 MB" on the card, and add a "Get rates for this" WhatsApp link beside it. | M |
| 3 Product | Dead-end cards. 12 of 33 cards are not links and offer no action: all of Lighting (6), Water Heaters (3), Industrial Spare (1), and 2 on Wires. | High | Count of `<article class="product-card">` per page; `build_pages.py:424-425`. | Make every card do something: with no PDF, link to WhatsApp or `contact.html` with the product name prefilled. | S |
| 4 Conversion | Category pages have zero contact links inside the page content. The only route to enquire is the nav or the sticky bar, and neither carries the product context. | High | DOM audit: `main a[href^=contact], [href^=tel], [href^=wa.me]` = 0 on all 7 category pages. | Add one CTA block to `category_page()` ("Send us your list for {category}") linking to WhatsApp with the category prefilled. One edit covers 7 pages. | S |
| 8 Performance | Home page loads autoplay video with `preload="auto"`: `fans.mp4` 8.3 MB and `lighting.mp4` 8.2 MB. One measured load transferred 9.8 MB with only one video fetched. | High | `build_pages.py:504`; browser resource timing on `index.html`. | Re-encode to 720p, no audio, about 600–900 KB each; `preload="none"` and start on intersection (the observer already exists in `main.js:184-214`). | M |
| 1 Trust | No GSTIN, no About page, no year established, no owner name, no shop or godown photo, no reviews. B2B buyers in India check GSTIN before a first order. | High | Not present in any page or in `ORG`. | Add a short "About / Company details" block to the contact page and footer: GSTIN, established year, address, real photos. | M |
| 1 Trust | "Dealer & stockist of" strip shows five brand logos with no proof. The local competitor shows authorised-distributor certificates. | High | `build_pages.py:546`; compare kotharicabletronics.com/certifications. | If authorised, show the certificates or say "Authorised dealer" per brand. If not, change wording to "Brands we stock". | S |
| 7 SEO | No domain set, so no canonical, og:url, sitemap, robots or BreadcrumbList is generated. | High | `build_pages.py:12`, `:115-116`, `:446`, `:881`. | Choose the domain (email already uses esanelectric.com) and set `DOMAIN`. | S |
| 7 SEO | Sitemap and llms.txt page lists are hard-coded and omit `industrial-spare.html` and `switches.html`. | Medium | `build_pages.py:879`. | Build the list from `CATS` so new categories are included automatically. | S |
| 7 SEO | No city or locality anywhere. "Tamil Nadu" is too broad to rank for "electrical wholesale in {city}"; LocalBusiness schema has region only. | High | `ORG` at `build_pages.py:250-264`; titles in `CATS`. | Add full address, `geo`, and city name in home title, H1 area, footer and schema. Create and match a Google Business Profile (Unverified whether one exists). | S |
| 12 Content | Category count contradicts itself: products page says "Seven categories"; FAQ, meta descriptions, footer blurb, `ORG.makesOffer` and llms.txt list five. Switches and Industrial Spare are missing from all descriptive copy. | Medium | `build_pages.py:188`, `:254`, `:522`, `:693`, `:519`. | Derive the list in copy from `CATS` labels, or update the five strings. | S |
| 12 Content | Spelling and casing errors in product names: "Rotarty" (Rotary), "Almanord" (the brand is Almonard), "Mcb, Rccb… Rcbo", "Mccb", "Bldc", "Ac box", "DB's". The typo is also baked into a PDF filename because slugs come from labels. | Medium | `build_pages.py:280-282`, `:343-347`; `pdfs/phase-selector-rotarty-db-legrand.pdf`. | Fix labels (MCB, RCCB, RCBO, MCCB, BLDC, AC box, DBs) and rename the two PDFs to match. | S |
| 12 Content | Heater cards read "Venus - Venus", "V-Guard - V-Guard", "Crompton - Crompton". | Medium | `build_pages.py:360-362` with title format at `:417`; seen on `heaters.html`. | Use a real type label, e.g. "Storage & instant water heaters". | S |
| 2 IA | Lighting page shows six cards from two stock photos (3 types × 2 brands), none linked. It reads as filler. | Medium | `build_pages.py:327-332`; `lighting.html`. | Show three real range cards with catalogues, or one honest "ask for our lighting list" block until content exists. | S |
| 5 Design | Stock imagery undermines the wholesale claim: hero is a domestic kitchen; Water Heaters shows a washbasin; Industrial Spare shows a messy panel; the same photo is used for "Distribution Box & MCB" and "Electricians", and another for "Retail shops" and distribution boards. | Medium | `images/stock/`: `switchgear.jpg` = `sector-electrician.jpg` (176,079 bytes), `sector-shop.jpg` = `distribution-board.jpg` (116,402 bytes). | Replace the hero and category photos with real photos of the shop, stock shelves and delivery. Phone photos are fine. | M |
| 5 Design | On home "Featured products", five of seven cards have no video, so a grey icon sits on top of the poster photo. | Medium | `build_pages.py:501-506`; `main.js:186-190` removes the placeholder only when a `<source>` exists; visible at 360px. | Emit the `<video>` and placeholder only when the mp4 exists; otherwise emit the `pic()` image. | S |
| 8 Performance | Video posters use the original JPEGs, not the WebP variants: `wires.jpg` 419 KB, `industrial-spare.jpg` 542 KB, loaded eagerly. | Medium | `build_pages.py:498-499`; resource timing. | Point `poster` at the existing `-640.webp` files. | S |
| 8 Performance | Three Google Fonts families load render-blocking from a third party, while self-hosted copies of two of them sit unused in `fonts/`. | Medium | `build_pages.py:131-133`; `fonts/fonts.css`. | Use the local files, preload the display font, and drop JetBrains Mono or self-host it too. Also removes a third-party request (privacy). | S |
| 8 Performance | Core Web Vitals not measured. | Unverified | No live URL. | After deploy, run PageSpeed Insights (mobile) on `/`, `/fans.html`, `/contact.html`. | S |
| 4 Conversion | On mobile the form starts about 1,270 px down the contact page, below four info cards and the map placeholder. | Medium | `scrollY` 1273 at `.form-card` on 360×740. | At ≤768px put the form first (CSS `order`), details after. | S |
| 4 Conversion | Hero has one button, "Browse Products". The primary action for a wholesale site (get rates) is not in the hero. | Medium | `build_pages.py:602-605`. | Add "Get rates on WhatsApp" as the second hero button. | S |
| 4 Conversion | Phone field accepts any text; buyer-type options exclude electricians and homeowners although the home page targets both. `?category=` prefill has no matching field. | Low | `build_pages.py:807`, `:813-818`; `main.js:216-224`. | Add `inputmode="tel"` and a 10-digit `pattern`; add the two options; drop or implement `category`. | S |
| 4 Conversion | "We reply within an hour" is promised in six places. If it is not met, it damages trust more than no promise. | Medium | `build_pages.py:576`, `:586`, `:670`, `:691`, `:752`, `:836`. | Keep only if staffed for it; otherwise "same working day". | S |
| 10 Security | No spam protection on the form. Web3Forms keys are public by design, so bots will find it. | Medium | `build_pages.py:797-832`: no honeypot or captcha. | Add Web3Forms' hidden `botcheck` checkbox; enable hCaptcha in their dashboard if spam appears. | S |
| 10 Security | Dealer price lists (Finolex, RR Kabel, Orbit, Norwood, Anchor) would be published openly. Manufacturers often restrict list-price circulation, and competitors can read them. | Medium | `pdfs/*pricelist*.pdf`; `wires.html` links. | Owner decision. Safer: catalogues public, price lists sent on request via WhatsApp. | S |
| 10 Security | `videotest.html`, `videotest2.html`, `.DS_Store`, `videos/fans_original.mp4`, `videos/ai-input/` would deploy with the site. | Low | Repo root and `videos/`. | Delete the test pages; ignore the rest. | S |
| 10 Security | HTTPS, HSTS, security headers, caching headers. | Unverified | No host yet. | After deploy, check securityheaders.com and confirm HTTP→HTTPS and www/non-www redirects. | S |
| 11 Code | Dead code: `wholesale_page()` and `FAQ` are never called (the page was deleted), `"catalogs"` and `"video"` keys in `CATS` are never read, `.pdf-link`/`.rack`/`.brands-soon` CSS is orphaned. The FAQ schema went with the page. | Medium | `build_pages.py:681-744`, `:286`, `:270`; `main.js:99`; `style.css:180,335,591`. | Either restore the FAQ on the contact page (useful for SEO and buyers) or delete it; remove the unused keys. | S |
| 11 Code | Stray `</ol>` in the hero markup. | Low | `build_pages.py:606`. | Delete the line. | S |
| 11 Code | Build has hidden side effects and an undeclared dependency: `pic()` writes WebP files during the build and, without Pillow, silently emits different markup with no width/height. No `requirements.txt`; script has no `main` guard and no checks. | Medium | `build_pages.py:80-103`. | Add `requirements.txt` (Pillow); fail loudly if Pillow is missing; add a tiny post-build check that every `href`/`src` exists. | S |
| 11 Code | PDF links depend on an implicit filename convention (slug of label + brand). Renaming a label silently unlinks the card. | Medium | `build_pages.py:421-425`. | Put the PDF path in the `types` tuple explicitly; the unused `catalogs` lists show this was the intent. | S |
| 11 Code | Project `CLAUDE.md` is out of date (says 9 pages including wholesale; says do not hand-edit HTML while `404.html` is called static but is generated). | Low | `CLAUDE.md` vs `build_pages.py:866-870`. | Update after cleanup. | S |
| 9 A11y | Copper `#b8733a` on the page background is 3.39:1, below 4.5:1 for small text (category index numbers, "why" numbers). Other pairs pass: muted 6.12, accent 5.35, white on accent 5.98. | Low | `style.css:188`, `:241`; computed ratios. | Darken copper for text use (about `#8f5626`) or keep copper for decoration only. | S |
| 9 A11y | Autoplay looping videos and the brand marquee have no pause control (WCAG 2.2.2). Reduced-motion is respected, which helps but does not satisfy it. | Low | `build_pages.py:504`; `style.css:622-628`. | Pause the marquee on hover/focus; stop videos after one loop or add a pause button. | S |
| 9 A11y | Mobile drawer does not trap focus; page behind remains tabbable. Escape and `aria-expanded` are handled correctly. | Low | `main.js:18-30`. | Set `inert` on `main` and footer while open. | S |
| 9 A11y | Seven category images on `products.html` and `404.html` have empty alt inside links. The heading gives the link a name, so this is acceptable; noted only for completeness. | Low | `build_pages.py:480`. | No change needed. | – |
| 7 SEO | No `og:image`; WhatsApp link previews (the main sharing channel here) will show no picture. | Medium | `head()` at `build_pages.py:110-139`. | Add one 1200×630 image and the tag. | S |
| 7 SEO | Category pages have a title, H1, one sentence and cards. No text about ranges, sizes or brands, so nothing to rank on. `ItemList` of `Product` without offers gives no rich result. | Medium | `category_page()`; page sizes 10–17 KB of mostly chrome. | Add 80–150 words per category (ranges, sizes, brands, who buys) from a new `CATS` field. | M |
| 7 SEO | Fans title is 76 characters and the home description 203; both will truncate. | Low | Page audit. | Trim to about 60 and 155. | S |
| 2 IA | No brand view. A buyer who wants "everything Legrand" must open three category pages. No search (acceptable at 33 cards). | Low | Nav and `CATS`. | Later: a brands page generated from `BRAND_STYLE` × `CATS`. | M |
| 12 Content | English only. Many electricians and shop owners in Tamil Nadu are more comfortable in Tamil. | Medium | `<html lang="en">`, all copy. | Start with a Tamil line in the hero and a Tamil WhatsApp greeting; full translation later. | M |
| 12 Content | Legal: brand logos and manufacturer catalogues are redistributed. Logos were "sourced from official sites / Wikipedia". | Medium | `build_pages.py:21`; `images/brands/`. | Confirm dealer agreements allow logo and catalogue use; otherwise use wordmarks and link to manufacturer sites. | S |

**Root causes** (one fix solves many rows):

1. **Owner information was never filled in.** Address, GSTIN, map, form key, domain, authorisation status. This single gap accounts for most Critical and High items in trust, conversion and SEO.
2. **"Product" means "PDF".** Dead-end cards, huge downloads, no CTA, thin category pages and weak structured data all follow from having no product-level content or action.
3. **Copy is typed in several places instead of derived from `CATS`.** This causes the five/seven mismatch, the incomplete sitemap list and the stale FAQ.
4. **Media was added without a size budget.** Videos, posters and PDFs.

---

## 4. Top 10 fixes, ranked by business impact per effort

- [ ] 1. Replace the placeholder address; add GSTIN, map embed and full address to contact page, footer and `ORG` schema.
- [ ] 2. Set the Web3Forms key, add the `botcheck` honeypot, and send a real test enquiry.
- [ ] 3. Rename `CSS/` to `css/`, add `.gitignore`, commit everything that the site needs.
- [ ] 4. Add an enquiry CTA to every category page and make every card actionable (WhatsApp with product name prefilled).
- [ ] 5. Fix home page weight: compress the two videos, `preload="none"`, WebP posters, no placeholder icon over photos.
- [ ] 6. Compress and de-duplicate PDFs; show file size on cards; decide whether price lists are public.
- [ ] 7. Choose the domain, set `DOMAIN`, generate the page list from `CATS`, add `og:image`.
- [ ] 8. Fix content errors: Almonard, Rotary, MCB/RCCB/MCCB/BLDC casing, "Venus - Venus", five vs seven categories.
- [ ] 9. Prove the brand claims: certificates or "Brands we stock"; add established year and real photos.
- [ ] 10. Create or claim the Google Business Profile and make name, address and phone identical to the site.

---

## 5. Quick wins (under a day in total)

- `git mv` the CSS folder; delete `videotest*.html`; add `.gitignore`.
- Remove the stray `</ol>` (`build_pages.py:606`).
- Fill address, GSTIN, map, Web3Forms key, `DOMAIN`.
- Add `botcheck` field, `inputmode="tel"` and `pattern` on the phone input, two extra buyer types.
- Add the second hero button (WhatsApp).
- Add the CTA block in `category_page()`.
- Fix the label typos and heater labels; rename the two affected PDFs.
- Point video `poster` at `-640.webp`; set `preload="none"`.
- Switch to the self-hosted fonts already in `fonts/`.
- Build the sitemap page list from `CATS`.
- Reorder the contact page on mobile so the form comes first.
- Darken copper where it is used for text.

---

## 6. Larger improvements, in small shippable steps

**A. Trust (do first)**
1. Company details block: address, GSTIN, hours, established year.
2. Real photos: shopfront, stock, delivery vehicle. Replace hero, then category covers.
3. Authorisation: certificates or reworded strip.
4. Link to Google reviews once the profile has some.

**B. From PDF cards to an enquiry flow**
1. Explicit `pdf` field per card; file size on the card; compressed files.
2. Each card gets two actions: "View catalogue" and "Get rates" (WhatsApp prefilled with brand and range).
3. Add 80–150 words and a short spec list (sizes, ratings, pack sizes) per category in `CATS`.
4. Only if enquiries justify it: a simple "quote list" (add items, send the list to WhatsApp). No cart or login needed at this scale.

**C. Local SEO**
1. Domain, canonical, sitemap, robots live; submit to Search Console.
2. Google Business Profile with matching details.
3. City name in titles, H1 support text and schema (`address`, `geo`).
4. Restore the FAQ (with `FAQPage` schema) on the contact page.
5. Later: a brands page and a "delivery areas" section naming the districts served.

**D. Performance**
1. Video and poster fixes (quick wins above).
2. PDF compression pipeline: one documented command, run before commit.
3. Measure with PageSpeed Insights on a mid-range Android profile and fix what it reports, rather than guessing.

**E. Maintainability**
1. `requirements.txt`; fail the build if Pillow is missing.
2. Post-build link check (every local `href`, `src`, `srcset`, `poster` exists, case-sensitive). This would have caught the CSS path.
3. Remove dead code and unused CSS; update `CLAUDE.md`.

**F. Language**
1. Tamil line in hero and Tamil WhatsApp prefill.
2. Tamil versions of the home and contact pages if enquiries show demand.

---

## 7. Already good; do not change

- **The generator approach.** One Python file for nav, footer, icons and catalogue data is right for a site this size. Do not move to a framework or CMS.
- **Visual identity.** Docket/stamp/cable motifs, the type pairing and the cream-red-copper palette are distinctive and consistent across pages.
- **Mobile action bar.** Fixed Call/WhatsApp bar, 52 px high, with matching body padding so it never covers content.
- **Mobile basics.** No horizontal overflow at 360 px; hamburger and filter tabs are 44 px; inputs are 16 px so iOS does not zoom; the drawer lists all categories plus Call/WhatsApp.
- **Form behaviour.** Validation on blur, clear messages, `aria-invalid`, focus moves to the first bad field, WhatsApp fallback on failure, "Continue on WhatsApp" after success.
- **Accessibility groundwork.** Skip link, `:focus-visible` styles, labelled fields, `aria-current`, Escape closes the drawer, `prefers-reduced-motion` honoured in CSS and JS, content visible without JS.
- **Images.** `<picture>` with WebP, `srcset`/`sizes`, width and height set (no layout shift), lazy loading, `fetchpriority` on the hero.
- **Open/closed chip** using IST. Useful and honest.
- **Titles and H1s.** One H1 per page, unique descriptive titles with "wholesale" and the region.
- **No third-party scripts, trackers or cookies.** Keep it that way; if analytics is wanted, pick a cookieless one.
- **Honest "rates on request" positioning**, explained in the copy.

---

## 8. Competitive comparison

Evidence is limited: two sites browsed directly, the rest from search listings only.

| Competitor | What they do better | Worth copying |
|------------|--------------------|---------------|
| Kothari Cabletronics, Chennai (kotharicabletronics.com, browsed) | "Serving India since 1995" in the hero; a certificates page with authorised-distributor certificates for Finolex, Polycab, Orbit and others; a "Request Quote" button on every product; "Industries we serve"; compliance and test-certificate statements. | Certificates page, per-item quote button, year established. |
| Seth Electricals, Chennai (IndiaMART profile, browsed) | Founding year (1973), named owners, team description, product counts, testimonials tab, GST and trust badges supplied by the marketplace. | Named people and history; consider an IndiaMART listing as an extra lead source that links back to the site. |
| Vashi Integrated Solutions (search listing only; **Unverified**) | Listed prices inclusive of GST, national presence, many brands. | Not a realistic model at this scale; note only that buyers increasingly expect GST-clear pricing. |
| Moglix / Industrybuying (search listing only; **Unverified**) | Full e-commerce, GST invoicing, search and filters by spec. | Do not copy. Compete on speed of reply, local delivery and relationship. |
| Bharat Traders, Chennai (Google Sites page; content did not load, **Unverified**) | – | – |

Where Esan Electric already wins: design quality, mobile experience, clarity of who it serves. Where it loses: proof (certificates, history, people, GSTIN) and a per-product way to ask for a price.

---

## 9. Business gaps

| Expected by customers | Status | Suggestion |
|-----------------------|--------|------------|
| GSTIN and invoice details | Missing | Add GSTIN; state "GST invoice with every order". |
| Delivery areas and charges | "Across Tamil Nadu" only | Name districts, typical lead time, own vehicle or transport. |
| Minimum order | FAQ answer existed but the page was removed | Restore FAQ. |
| Payment terms | Missing | One line: advance, UPI, credit for regular dealers. |
| Warranty and returns | Missing | State that manufacturer warranty applies and how claims are handled. |
| Bulk quote | Form and WhatsApp only | Allow attaching or pasting a BOQ; later a quote list. |
| Brand catalogues | Present but heavy | Compress, label sizes. |
| Price lists | Present, public | Decide policy (see Findings). |
| Dealer or contractor login | Missing | Not needed yet. A WhatsApp broadcast list for price updates does the same job. |
| Product comparison, stock status | Missing | Not needed at this stage. |

---

## 10. Open questions

1. What is the real address, city, PIN and GSTIN? Is there a Google Business Profile?
2. Which domain and host will be used? (Email already uses esanelectric.com.)
3. Is the business an **authorised** dealer for Crompton, RR Kabel, Legrand, Anchor and Finolex? Are certificates available to show?
4. May manufacturer price lists and catalogues be published openly under your dealer terms?
5. Who answers enquiries, and is "within an hour" realistic during 9 AM–7 PM?
6. B2B and B2C split: should homeowners be invited (the home page says yes, the form says no)?
7. Is "Kavaski" the correct brand spelling? Does Orient supply house wire to you, as listed on the wires page?
8. Are the five missing category videos coming, or should those cards be static images?
9. Was removing the wholesale/FAQ page intentional?
10. Is Tamil wanted on the site?
11. Year established, and any customer names or reviews that can be quoted?
