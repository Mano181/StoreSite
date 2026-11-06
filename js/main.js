// Signal JS is active so CSS can enable scroll-reveal hiding (else content always shows)
document.documentElement.classList.add('js');

const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
const finePointer = matchMedia('(hover: hover) and (pointer: fine)').matches;

// ── Navbar: surface once scrolled, hide on scroll down, show on scroll up ──
const navbar = document.querySelector('.navbar');
let lastY = window.scrollY;
window.addEventListener('scroll', () => {
  const y = window.scrollY;
  navbar?.classList.toggle('scrolled', y > 40);
  const locked = document.body.classList.contains('nav-open') || navbar?.contains(document.activeElement);
  navbar?.classList.toggle('hide', y > lastY && y > 200 && !locked);
  lastY = y;
}, { passive: true });

// ── Mobile drawer ──
const hamburger = document.querySelector('.hamburger');
const navLinks = document.querySelector('.nav-links');
function setDrawer(open) {
  navLinks?.classList.toggle('open', open);
  document.body.classList.toggle('nav-open', open);
  hamburger?.setAttribute('aria-expanded', String(open));
}
hamburger?.addEventListener('click', () => setDrawer(hamburger.getAttribute('aria-expanded') !== 'true'));
navLinks?.querySelectorAll('a').forEach(a => a.addEventListener('click', () => setDrawer(false)));
document.addEventListener('keydown', e => {
  if (e.key === 'Escape' && hamburger?.getAttribute('aria-expanded') === 'true') { setDrawer(false); hamburger.focus(); }
});

// ── Active nav link ──
const page = window.location.pathname.split('/').pop() || 'index.html';
document.querySelectorAll('.nav-links a, .footer-links a').forEach(a => {
  if (a.getAttribute('href') === page) a.classList.add('active');
});

// ── Scroll reveal (stagger within each parent group) ──
const revealEls = document.querySelectorAll('.reveal, .reveal-left, .reveal-scale, .wipe, .wire-steps');
if ('IntersectionObserver' in window) {
  const observer = new IntersectionObserver(entries => {
    entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('visible'); observer.unobserve(e.target); } });
  }, { threshold: 0.12 });
  const seen = new Map();
  revealEls.forEach(el => {
    const n = seen.get(el.parentElement) || 0;
    seen.set(el.parentElement, n + 1);
    el.style.setProperty('--rd', `${Math.min(n, 5) * 70}ms`);
    observer.observe(el);
  });
} else {
  revealEls.forEach(el => el.classList.add('visible'));
}

// ── Open-now chip (Mon–Sat 9:00–19:00 IST, the hours stated on the site) ──
const chip = document.getElementById('openChip');
if (chip) {
  const ist = new Date(new Date().toLocaleString('en-US', { timeZone: 'Asia/Kolkata' }));
  const open = ist.getDay() !== 0 && ist.getHours() >= 9 && ist.getHours() < 19;
  chip.classList.toggle('is-open', open);
  chip.querySelector('.oc-text').textContent = open ? 'Open now · Call or WhatsApp' : 'Closed · We reply from 9 AM';
}

// ── Magnetic CTA circle ──
const cta = document.querySelector('.cta-circle');
if (cta && finePointer && !reduceMotion) {
  cta.addEventListener('pointermove', e => {
    const r = cta.getBoundingClientRect();
    const dx = (e.clientX - r.left - r.width / 2) / (r.width / 2);
    const dy = (e.clientY - r.top - r.height / 2) / (r.height / 2);
    cta.style.setProperty('--mx', `${dx * 6}px`);
    cta.style.setProperty('--my', `${dy * 6}px`);
  });
  cta.addEventListener('pointerleave', () => { cta.style.setProperty('--mx', '0px'); cta.style.setProperty('--my', '0px'); });
}

// ── Category filter tabs ──
document.querySelectorAll('.filter-tab').forEach(tab => tab.addEventListener('click', () => {
  document.querySelectorAll('.filter-tab').forEach(t => t.classList.toggle('active', t === tab));
  document.querySelectorAll('.product-card, .rack').forEach(c => c.classList.toggle('hidden', tab.dataset.filter !== 'all' && c.dataset.group !== tab.dataset.filter));
}));

// ── Contact form (Web3Forms; set the access key in contact.html) ──
const WA_NUMBER = '917200523519';
const form = document.getElementById('inquiryForm');
const statusEl = document.getElementById('formStatus');
const successEl = document.getElementById('formSuccess');

function waLink(data) {
  const lines = ['Hi Esan Electric, I would like wholesale rates.',
    data.get('message') && `Requirement: ${data.get('message')}`,
    data.get('city') && `Town/City: ${data.get('city')}`,
    data.get('name') && `Name: ${data.get('name')}`].filter(Boolean);
  return `https://wa.me/${WA_NUMBER}?text=${encodeURIComponent(lines.join('\n'))}`;
}

// Inline validation: show a message only after the user leaves a field
const MESSAGES = { name: 'Please enter your name.', phone: 'Please enter a phone number we can call.', message: 'Tell us which products and how many.' };
function checkField(el) {
  el.parentElement.querySelector('.field-error')?.remove();
  el.removeAttribute('aria-invalid');
  if (el.checkValidity()) return;
  const msg = Object.assign(document.createElement('span'), { className: 'field-error', textContent: MESSAGES[el.name] || 'This field needs attention.', id: `${el.id}-err` });
  el.parentElement.appendChild(msg);
  el.setAttribute('aria-invalid', 'true');
  el.setAttribute('aria-describedby', msg.id);
}
form?.querySelectorAll('[required]').forEach(el => {
  el.addEventListener('blur', () => checkField(el));
  el.addEventListener('input', () => { if (el.hasAttribute('aria-invalid')) checkField(el); });
});

form?.addEventListener('submit', async e => {
  e.preventDefault();
  const required = [...form.querySelectorAll('[required]')];
  required.forEach(checkField);
  const bad = required.find(el => !el.checkValidity());
  if (bad) { bad.focus(); return; }
  const data = new FormData(form);
  const btn = form.querySelector('.btn-submit');
  const label = btn.querySelector('.bt');
  btn.disabled = true;
  btn.setAttribute('aria-busy', 'true');
  label.textContent = 'Sending…';
  try {
    const res = await fetch(form.action, { method: 'POST', body: data, headers: { Accept: 'application/json' } });
    if (!res.ok || !(await res.json()).success) throw new Error('send failed');
    document.getElementById('waFollow').href = waLink(data);
    form.reset();
    form.hidden = true;
    form.parentElement.querySelectorAll(':scope > h3, :scope > p').forEach(n => n.hidden = true);
    successEl.hidden = false;
    successEl.querySelector('h3').focus?.();
    showToast('Enquiry sent. We\'ll reach out shortly.');
  } catch {
    showToast('Could not send. Please use WhatsApp or call us.');
    statusEl.innerHTML = `<a href="${waLink(data)}" target="_blank" rel="noopener">Send this enquiry on WhatsApp →</a>`;
  }
  btn.disabled = false;
  btn.removeAttribute('aria-busy');
  label.textContent = 'Send Enquiry';
});

document.getElementById('formAgain')?.addEventListener('click', () => {
  successEl.hidden = true;
  form.hidden = false;
  form.parentElement.querySelectorAll(':scope > h3, :scope > p').forEach(n => n.hidden = false);
  statusEl.textContent = '';
});

function showToast(msg) {
  let t = document.getElementById('toast');
  if (!t) {
    t = Object.assign(document.createElement('div'), { id: 'toast', className: 'toast' });
    t.setAttribute('role', 'status');
    document.body.appendChild(t);
  }
  t.innerHTML = '<svg class="ic" aria-hidden="true"><use href="#i-check"/></svg><span></span>';
  t.lastChild.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 3500);
}

// ── Switch plate: flip the rocker, then follow the link ──
document.querySelectorAll('.rocker').forEach(r => r.addEventListener('click', e => {
  if (reduceMotion || e.metaKey || e.ctrlKey || e.shiftKey || e.button) return;
  e.preventDefault();
  r.classList.add('flip');
  setTimeout(() => { window.location.href = r.href; }, 220);
}));

// ── Prefill contact form from ?category= and ?type= ──
if (form) {
  const params = new URLSearchParams(window.location.search);
  ['category', 'type'].forEach(k => {
    const v = params.get(k);
    const field = form.querySelector(`[name="${k === 'type' ? 'buyer_type' : k}"]`);
    if (v && field) field.value = v;
  });
}
