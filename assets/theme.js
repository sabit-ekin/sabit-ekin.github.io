// Light/dark switch. The page follows the system until the visitor picks the other mode; picking the mode
// that matches the system goes back to following it. A forced mode is kept in localStorage and applied as
// data-theme on <html> (an inline script in <head> applies it before the page paints); the switch's look
// comes from CSS, so it is right before this script runs. Pages with
// <picture><source media="(prefers-color-scheme: dark)"> logos get the matching logo; SVG figures shown as
// <img> follow the page's color-scheme.
(function () {
  var root = document.documentElement, KEY = 'theme';
  var btn = document.querySelector('.theme-toggle'); if (!btn) return;
  var mq = window.matchMedia ? matchMedia('(prefers-color-scheme: dark)') : null;
  function sys() { return mq && mq.matches ? 'dark' : 'light'; }
  function read() { try { var t = localStorage.getItem(KEY); return t === 'light' || t === 'dark' ? t : null; } catch (e) { return null; } }
  var forced = read();  // kept in memory too, for browsers that block storage
  // logo <source>s: re-queried on each apply, since this script runs before the footer is parsed
  function sources() {
    return Array.prototype.slice.call(document.querySelectorAll('source[media*="prefers-color-scheme"], source[data-media]'));
  }

  function apply() {
    var t = forced || sys(), next = t === 'dark' ? 'light' : 'dark';
    if (forced) root.dataset.theme = forced; else delete root.dataset.theme;
    sources().forEach(function (s) {
      if (!s.dataset.media) s.dataset.media = s.media;
      s.media = forced === 'dark' ? 'all' : forced === 'light' ? 'not all' : s.dataset.media;
    });
    btn.setAttribute('aria-checked', t === 'dark');
    btn.title = 'Switch to ' + next + ' mode' + (next === sys() ? ' (system)' : '');
  }

  btn.addEventListener('click', function () {
    var next = (forced || sys()) === 'dark' ? 'light' : 'dark';
    forced = next === sys() ? null : next;
    try { if (forced) localStorage.setItem(KEY, forced); else localStorage.removeItem(KEY); } catch (e) {}
    apply();
  });
  if (mq) { if (mq.addEventListener) mq.addEventListener('change', apply); else if (mq.addListener) mq.addListener(apply); }
  // another tab changed the theme
  window.addEventListener('storage', function (e) { if (e.key === KEY) { forced = read(); apply(); } });
  apply();
  document.addEventListener('DOMContentLoaded', apply);
})();
