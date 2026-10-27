// Theme picker: Light, Dark, or System (the default). The choice is kept in localStorage and applied as
// data-theme on <html> (an inline script in <head> applies it before the page paints). Pages with
// <picture><source media="(prefers-color-scheme: dark)"> logos get the matching logo; SVG figures shown as
// <img> follow the page's color-scheme.
(function () {
  var root = document.documentElement, KEY = 'theme';
  var box = document.querySelector('.theme'); if (!box) return;
  var btn = box.querySelector('.theme-btn'), menu = box.querySelector('.theme-menu');
  var items = Array.prototype.slice.call(menu.querySelectorAll('[data-set]'));
  // logo <source>s: re-queried on each apply, since this script runs before the footer is parsed
  function sources() {
    return Array.prototype.slice.call(document.querySelectorAll('source[media*="prefers-color-scheme"], source[data-media]'));
  }

  function get() { try { var t = localStorage.getItem(KEY); return t === 'light' || t === 'dark' ? t : 'system'; } catch (e) { return 'system'; } }
  function apply(t) {
    if (t === 'system') delete root.dataset.theme; else root.dataset.theme = t;
    sources().forEach(function (s) {
      if (!s.dataset.media) s.dataset.media = s.media;
      s.media = t === 'dark' ? 'all' : t === 'light' ? 'not all' : s.dataset.media;
    });
    items.forEach(function (it) { it.setAttribute('aria-checked', it.dataset.set === t); });
    btn.dataset.current = t;
    btn.setAttribute('aria-label', 'Color theme: ' + t + ' (change)');
  }
  function save(t) { try { if (t === 'system') localStorage.removeItem(KEY); else localStorage.setItem(KEY, t); } catch (e) {} }
  function open(yes, focusItem) {
    menu.hidden = !yes; btn.setAttribute('aria-expanded', yes);
    if (yes && focusItem) (menu.querySelector('[aria-checked="true"]') || items[0]).focus();
  }

  btn.addEventListener('click', function () { open(menu.hidden, true); });
  items.forEach(function (it, i) {
    it.addEventListener('click', function () { save(it.dataset.set); apply(it.dataset.set); open(false); btn.focus(); });
    it.addEventListener('keydown', function (e) {
      var k = e.key, n = items.length;
      if (k === 'ArrowDown' || k === 'ArrowUp') { e.preventDefault(); items[(i + (k === 'ArrowDown' ? 1 : n - 1)) % n].focus(); }
      else if (k === 'Home' || k === 'End') { e.preventDefault(); items[k === 'Home' ? 0 : n - 1].focus(); }
      else if (k === 'Tab') open(false);
    });
  });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && !menu.hidden) { open(false); btn.focus(); } });
  document.addEventListener('click', function (e) { if (!menu.hidden && !box.contains(e.target)) open(false); });
  // another tab changed the theme
  window.addEventListener('storage', function (e) { if (e.key === KEY) apply(get()); });
  apply(get());
  document.addEventListener('DOMContentLoaded', function () { apply(get()); });
})();
