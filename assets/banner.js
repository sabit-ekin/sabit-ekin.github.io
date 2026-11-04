// Page banner: a faint animated line drawing behind the title and intro of each section page, about that page:
//   research     side by side: beams from a cell tower and a Wi-Fi access point, a QAM constellation, a neural network
//   publications pages being typeset: two columns and a figure fill in; a finished page gets a gold star
//   leadership   trees grow up from the bottom edge and blossom in gold
//   team         a mesh network grows outward from the mentor's node; gold packets hop along the links
//   teaching     an open book, its pages turning; a wave, a neuron, a chat bubble and an antenna rise from it
//   outreach     the light-wave kit: a phone plays music into an LED, the light carries it to a solar cell and a speaker
// The canvas is decorative (aria-hidden): a strip in the band color across the top of <main>, down to just
// below the intro, with a thin line at its edge. The title, intro and buttons stay clear (see mask()). Colors come from the page's tokens, so it follows light/dark mode. It pauses off screen and in hidden
// tabs, and shows one still frame under prefers-reduced-motion.
(function () {
function start() {
  var motif = (location.pathname.split('/').pop() || '').replace(/\.html$/, '');
  var main = document.getElementById('main'), h1 = main && main.querySelector('h1');
  if (!h1 || !DRAW[motif]) return;
  var wrap = main.querySelector('.wrap');
  var cv = document.createElement('canvas');
  cv.setAttribute('aria-hidden', 'true');
  cv.className = 'pagebanner';
  cv.style.cssText = 'position:absolute;left:0;top:0;width:100%;pointer-events:none;z-index:0';
  main.style.position = 'relative';
  if (wrap) { wrap.style.position = 'relative'; wrap.style.zIndex = '1'; }
  main.insertBefore(cv, main.firstChild);
  var ctx = cv.getContext('2d'), mk = document.createElement('canvas');   // mk: the text mask, see mask()
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)');
  var W = 0, H = 0, dpr = 1, scene = null, C = {}, visible = true, raf = 0, t0 = performance.now();

  function colors() {
    var s = getComputedStyle(document.documentElement);
    function v(n, d) { return (s.getPropertyValue(n) || '').trim() || d; }
    C = { line: v('--line', '#e6e1db'), maroon: v('--maroon', '#500000'), muted: v('--muted', '#625a53'),
          bg: v('--bg', '#fbfaf8'), band: v('--band', '#f3eee7'), gold: v('--sky-gold', '#ecc062') };
    var m = C.bg.match(/^#(..)(..)(..)$/);   // on a light page the sky gold is too pale: use a deeper gold
    if (m && parseInt(m[1], 16) + parseInt(m[2], 16) + parseInt(m[3], 16) > 384) C.gold = '#b98318';
  }
  function size() {
    // the strip ends below the intro: the page's .intro block (publications), else the lede after the title
    var intro = h1.parentElement.matches('.intro') ? h1.parentElement
      : h1.nextElementSibling && h1.nextElementSibling.matches('.lede') ? h1.nextElementSibling : h1;
    var top = main.getBoundingClientRect().top;
    var h = Math.round(intro.getBoundingClientRect().bottom - top + (intro === h1.parentElement ? 30 : 40));
    var w = main.clientWidth;
    dpr = Math.min(window.devicePixelRatio || 1, 2);
    var rg = document.createRange(); rg.selectNodeContents(h1);
    var hr = rg.getBoundingClientRect(), mb = main.getBoundingClientRect();
    var tx = { h1: { left: hr.left - mb.left, right: hr.right - mb.left, top: hr.top - mb.top, bottom: hr.bottom - mb.top } };
    tx.intro = { left: tx.h1.left, right: tx.h1.right, top: tx.h1.top, bottom: tx.h1.bottom };
    textEls().forEach(function (el) {   // the whole intro block: title, intro lines, buttons
      rg.selectNodeContents(el);
      [].forEach.call(rg.getClientRects(), function (r) {
        if (!r.width) return;
        tx.intro.left = Math.min(tx.intro.left, r.left - mb.left); tx.intro.right = Math.max(tx.intro.right, r.right - mb.left);
        tx.intro.bottom = Math.max(tx.intro.bottom, r.bottom - mb.top);
      });
    });
    var moved = !TEXT || Math.abs(tx.h1.left - TEXT.h1.left) + Math.abs(tx.h1.right - TEXT.h1.right) + Math.abs(tx.intro.right - TEXT.intro.right) > 4;
    if (w !== W || h !== H || moved) {   // lay the drawing out again when the banner or the title changes
      W = w; H = h; TEXT = BOX = tx;
      cv.width = mk.width = W * dpr; cv.height = mk.height = H * dpr; cv.style.height = H + 'px';
      scene = DRAW[motif].init(W, H, rng(7));
    }
    mask();
    frame();
  }
  // Keep the text readable: a soft patch of the band color over every line of the title and intro (and the
  // buttons), drawn on top of the drawing, so it only shows in the open space around the text.
  function textEls() {   // the title and the intro under it (on publications.html, the whole .intro block)
    return h1.parentElement.matches('.intro') ? [].slice.call(h1.parentElement.children)
      : [h1].concat(h1.nextElementSibling && h1.nextElementSibling.matches('.lede') ? [h1.nextElementSibling] : []);
  }
  function mask() {
    var box = main.getBoundingClientRect(), rects = [], range = document.createRange();
    textEls().forEach(function (el) {
      if (el.matches('.links')) [].forEach.call(el.children, function (a) { rects.push(a.getBoundingClientRect()); });
      else { range.selectNodeContents(el); [].push.apply(rects, range.getClientRects()); }
    });
    var m = mk.getContext('2d'), pad = 10, far = 10000;
    m.setTransform(1, 0, 0, 1, 0, 0); m.clearRect(0, 0, mk.width, mk.height);
    m.setTransform(dpr, 0, 0, dpr, 0, 0);
    m.fillStyle = '#000'; m.shadowColor = C.band; m.shadowBlur = 16 * dpr; m.shadowOffsetX = far * dpr;
    for (var pass = 0; pass < 2; pass++)   // only the shadow lands on the canvas: a patch with soft edges
      rects.forEach(function (r) {
        if (r.width && r.height)
          m.fillRect(r.left - box.left - pad - far, r.top - box.top - pad, r.width + 2 * pad, r.height + 2 * pad);
      });
  }
  function frame() {
    if (!W || !H) return;   // not laid out yet (e.g. a hidden tab)
    var t = reduce.matches ? 6 : (performance.now() - t0) / 1000;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.fillStyle = C.band; ctx.fillRect(0, 0, W, H);   // the strip has its own tint, with a sharp edge
    DRAW[motif].draw(ctx, scene, t, W, H, C);
    ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.globalAlpha = 1; ctx.drawImage(mk, 0, 0);
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.fillStyle = C.line; ctx.fillRect(0, H - 1, W, 1);
  }
  function loop() { raf = 0; frame(); schedule(); }
  function schedule() { if (!raf && visible && !document.hidden && !reduce.matches) raf = requestAnimationFrame(loop); }

  colors();
  size();
  new MutationObserver(function () { colors(); mask(); frame(); }).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
  var dark = window.matchMedia('(prefers-color-scheme: dark)');
  (dark.addEventListener ? dark.addEventListener('change', function () { colors(); mask(); frame(); }) : null);
  window.addEventListener('resize', size);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(size);
  // the text can reflow after load (web fonts): measure again whenever the title or intro changes size
  if (document.fonts && document.fonts.addEventListener) document.fonts.addEventListener('loadingdone', size);
  if ('ResizeObserver' in window) {
    var ro = new ResizeObserver(function () { size(); });
    [].forEach.call(h1.parentElement.children, function (el) { ro.observe(el); });
  }
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (e) { visible = e[0].isIntersecting; schedule(); }).observe(cv);
  }
  document.addEventListener('visibilitychange', schedule);
  reduce.addEventListener && reduce.addEventListener('change', function () { frame(); schedule(); });
  schedule();
}

// ---- helpers -------------------------------------------------------------------------------------------------
function rng(seed) {   // small seeded random, so a layout is the same on every visit
  return function () {
    seed |= 0; seed = seed + 0x6D2B79F5 | 0;
    var t = Math.imul(seed ^ seed >>> 15, 1 | seed);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  };
}
function clear(hex) {   // the same color, fully transparent
  var m = /^#?(..)(..)(..)$/.exec(hex.trim());
  return m ? 'rgba(' + parseInt(m[1], 16) + ',' + parseInt(m[2], 16) + ',' + parseInt(m[3], 16) + ',0)' : 'rgba(0,0,0,0)';
}
var TEXT = null, BOX = null;   // where the title sits (main's coordinates; BOX: the drawing's own), see size()
var FADE = 1;   // extra opacity for every drawing step, used to cross-fade between the research drawings
function alpha(ctx, a) { ctx.globalAlpha = Math.max(0, Math.min(1, a)) * FADE; }
function star(ctx, x, y, r) {   // four-point sparkle
  ctx.beginPath();
  ctx.moveTo(x, y - r); ctx.quadraticCurveTo(x, y, x + r, y); ctx.quadraticCurveTo(x, y, x, y + r);
  ctx.quadraticCurveTo(x, y, x - r, y); ctx.quadraticCurveTo(x, y, x, y - r); ctx.fill();
}

// A drawing that takes turns between other drawings: each plays for P seconds, then cross-fades (X s) into the
// next. Each part gets its own scene, and u, the time since it came in (negative while it is fading in).
function cycle(parts, under) {
  var P = 9, X = 1.4;
  return {
    init: function (W, H, R) { return parts.map(function (p) { return DRAW[p].init(W, H, R); }); },
    draw: function (ctx, s, t, W, H, C) {
      if (under) under(ctx, t, W, H, C);
      var n = parts.length, k = Math.floor(t / P) % n, u = t % P, f = u > P - X ? (u - (P - X)) / X : 0;
      FADE = 1 - f; DRAW[parts[k]].draw(ctx, s[k], t, W, H, C, u);
      if (f) { var j = (k + 1) % n; FADE = f; DRAW[parts[j]].draw(ctx, s[j], t, W, H, C, u - P); }
      FADE = 1; ctx.globalAlpha = 1;
    }
  };
}
// A drawing made of other drawings side by side, one per column, with soft edges where neighbours meet. Each
// part is drawn on its own canvas as if it were the whole banner. Below MIN px wide the parts take turns (cycle).
// under (optional) draws a shared background first.
function split(parts, under) {
  var MIN = 900, EDGE = 40, P = 9, turns = cycle(parts, under);
  return {
    init: function (W, H, R) {
      if (W < MIN) return { turns: turns.init(W, H, R) };
      var n = parts.length;
      return { cols: parts.map(function (p, i) {
        var x = Math.round(i * W / n), w = Math.round((i + 1) * W / n) - x;
        BOX = TEXT && { h1: { left: TEXT.h1.left - x, right: TEXT.h1.right - x, top: TEXT.h1.top, bottom: TEXT.h1.bottom } };
        var col = { p: p, x: x, w: w, c: document.createElement('canvas'), s: DRAW[p].init(w, H, R) };
        BOX = TEXT;
        return col;
      }) };
    },
    draw: function (ctx, s, t, W, H, C) {
      if (s.turns) return turns.draw(ctx, s.turns, t, W, H, C);
      if (under) under(ctx, t, W, H, C);
      var k = ctx.getTransform().a, last = s.cols.length - 1, u = t % P;
      s.cols.forEach(function (col, i) {
        var c = col.c, g = c.getContext('2d');
        if (c.width !== col.w * k || c.height !== H * k) { c.width = col.w * k; c.height = H * k; }
        g.setTransform(1, 0, 0, 1, 0, 0); g.globalAlpha = 1; g.clearRect(0, 0, c.width, c.height);
        g.setTransform(k, 0, 0, k, 0, 0);
        // a part that plays out over time (loop: true) restarts every P seconds, fading out and back in
        FADE = DRAW[col.p].loop ? Math.max(0, Math.min(1, u / 0.4, (P - u) / 0.7)) : 1;
        DRAW[col.p].draw(g, col.s, t, col.w, H, C, u);
        FADE = 1;
        g.globalAlpha = 1; g.globalCompositeOperation = 'destination-in';   // fade the edges shared with a neighbour
        var gr = g.createLinearGradient(0, 0, col.w, 0), e = EDGE / col.w;
        gr.addColorStop(0, i ? 'rgba(0,0,0,0)' : '#000'); gr.addColorStop(e, '#000');
        gr.addColorStop(1 - e, '#000'); gr.addColorStop(1, i < last ? 'rgba(0,0,0,0)' : '#000');
        g.fillStyle = gr; g.fillRect(0, 0, col.w, H); g.globalCompositeOperation = 'source-over';
        ctx.globalAlpha = 1; ctx.drawImage(c, col.x, 0, col.w, H);
      });
    }
  };
}

// ---- the drawings --------------------------------------------------------------------------------------------
var DRAW = {
  // Research shows three drawings side by side, blending into each other: beams from a cell tower and a Wi-Fi
  // access point, a QAM constellation, and a neural network. On narrow screens they take turns instead.
  research: split(['beams', 'qam', 'neural']),

  // Antennas sweep tapered beams; ticks travel out along each beam; targets light up when a beam passes over them.
  beams: {
    init: function (W, H, R) {
      var ants = [], n = Math.max(2, Math.round(W / 420));
      // alternately a cell tower standing at the bottom and a Wi-Fi access point hanging from the top (beaming down)
      for (var i = 0; i < n; i++) {
        var wifi = i % 2 === 1;   // the tower first: on the left it stands clear of the title
        ants.push({ kind: wifi ? 'wifi' : 'tower', x: (i + 0.5 + (R() - 0.5) * 0.4) * W / n, y: wifi ? 30 + R() * H * 0.08 : H - 50,
          base: (wifi ? 1 : -1) * Math.PI / 2 + (R() - 0.5) * 0.6, sweep: 0.5 + R() * 0.35, speed: 0.18 + R() * 0.12, p: R() * 6.28 });
      }
      if (BOX) {   // keep the beams clear of the title: both left of it on wide margins, else the access point after it
        var L = BOX.h1.left, Rt = BOX.h1.right, wide = L > 260;
        ants.forEach(function (a) {
          a.x = a.kind === 'wifi' ? (wide ? L - 70 : Math.min(W - 50, Rt + 70)) : (wide ? L * 0.35 : Math.max(30, Math.min(L - 40, W * 0.15)));
        });
      }
      var dots = [];
      for (var j = 0; j < W / 26; j++) dots.push({ x: R() * W, y: H * (0.15 + R() * 0.85), lit: 0 });
      return { ants: ants, dots: dots };
    },
    draw: function (ctx, s, t, W, H, C) {
      ctx.lineCap = 'round';
      s.ants.forEach(function (a) {
        var ang = a.base + Math.sin(t * a.speed + a.p) * a.sweep, len = H * 1.1, wid = 0.13;
        // beam wedge
        var g = ctx.createLinearGradient(a.x, a.y, a.x + Math.cos(ang) * len, a.y + Math.sin(ang) * len);
        g.addColorStop(0, C.maroon); g.addColorStop(1, clear(C.maroon));   // fade to clear maroon, not clear black
        alpha(ctx, 0.2); ctx.fillStyle = g;
        ctx.beginPath(); ctx.moveTo(a.x, a.y);
        ctx.lineTo(a.x + Math.cos(ang - wid) * len, a.y + Math.sin(ang - wid) * len);
        ctx.lineTo(a.x + Math.cos(ang + wid) * len, a.y + Math.sin(ang + wid) * len);
        ctx.closePath(); ctx.fill();
        // wavefront ticks moving out
        ctx.strokeStyle = C.maroon; ctx.lineWidth = 1.4;
        for (var k = 0; k < 6; k++) {
          var r = ((t * 46 + k * len / 6) % len);
          alpha(ctx, 0.45 * (1 - r / len));
          ctx.beginPath(); ctx.arc(a.x, a.y, r, ang - wid * 0.8, ang + wid * 0.8); ctx.stroke();
        }
        // which targets are inside the beam
        s.dots.forEach(function (d) {
          var da = Math.atan2(d.y - a.y, d.x - a.x) - ang;
          da = Math.atan2(Math.sin(da), Math.cos(da));
          if (Math.abs(da) < wid) d.lit = 1;
        });
        DRAW.beams[a.kind](ctx, a, t, H, C);
      });
      s.dots.forEach(function (d) {
        d.lit = Math.max(0, d.lit - 0.012);
        alpha(ctx, 0.35 + d.lit * 0.5); ctx.fillStyle = d.lit > 0.05 ? C.maroon : C.muted;
        ctx.beginPath(); ctx.arc(d.x, d.y, 1.6 + d.lit * 2, 0, 6.28); ctx.fill();
      });
      alpha(ctx, 1);
    },
    // a ceiling-mounted Wi-Fi access point: a rod from the top edge, a rounded box, two antennas, a status light
    wifi: function (ctx, a, t, H, C) {
      ctx.lineWidth = 1.6; ctx.strokeStyle = C.maroon; alpha(ctx, 0.75);
      ctx.beginPath(); ctx.moveTo(a.x, 0); ctx.lineTo(a.x, a.y - 14);
      ctx.moveTo(a.x - 14, a.y - 2); ctx.lineTo(a.x - 21, a.y + 14); ctx.moveTo(a.x + 14, a.y - 2); ctx.lineTo(a.x + 21, a.y + 14);
      ctx.stroke();
      ctx.beginPath();
      if (ctx.roundRect) ctx.roundRect(a.x - 21, a.y - 14, 42, 13, 4); else ctx.rect(a.x - 21, a.y - 14, 42, 13);
      alpha(ctx, 1); ctx.fillStyle = C.band; ctx.fill(); alpha(ctx, 0.8); ctx.stroke();
      ctx.lineWidth = 1.4;   // a Wi-Fi sign under the box, curving downward, its arcs lighting up in turn
      for (var k = 0; k < 3; k++) {
        alpha(ctx, 0.3 + 0.6 * Math.max(0, Math.sin(t * 3 - k * 0.9)));
        ctx.beginPath(); ctx.arc(a.x, a.y - 4, 7 + k * 4.5, Math.PI * 0.3, Math.PI * 0.7); ctx.stroke();
      }
      alpha(ctx, 0.5 + 0.5 * Math.abs(Math.sin(t * 2.2))); ctx.fillStyle = C.gold;
      ctx.beginPath(); ctx.arc(a.x + 14, a.y - 7.5, 2, 0, 6.29); ctx.fill();
    },
    // a lattice cell tower standing on the bottom edge, with three panel antennas at the top
    tower: function (ctx, a, t, H, C) {
      var top = a.y, bot = H - 1, hw = 11;
      ctx.lineWidth = 1.3; ctx.strokeStyle = C.muted; alpha(ctx, 0.6);
      ctx.beginPath(); ctx.moveTo(a.x - hw, bot); ctx.lineTo(a.x - 2.5, top + 6); ctx.moveTo(a.x + hw, bot); ctx.lineTo(a.x + 2.5, top + 6);
      for (var k = 0, n = 4; k < n; k++) {   // cross bracing
        var y1 = bot - (bot - top - 6) * k / n, y2 = bot - (bot - top - 6) * (k + 1) / n;
        var w1 = hw - (hw - 2.5) * k / n, w2 = hw - (hw - 2.5) * (k + 1) / n;
        ctx.moveTo(a.x - w1, y1); ctx.lineTo(a.x + w2, y2); ctx.moveTo(a.x + w1, y1); ctx.lineTo(a.x - w2, y2);
      }
      ctx.moveTo(a.x, top + 6); ctx.lineTo(a.x, top - 4);
      ctx.stroke();
      alpha(ctx, 0.65); ctx.fillStyle = C.maroon;   // panel antennas
      ctx.fillRect(a.x - 9, top - 2, 3, 10); ctx.fillRect(a.x - 1.5, top - 6, 3, 10); ctx.fillRect(a.x + 6, top - 2, 3, 10);
      alpha(ctx, 0.5 + 0.5 * Math.abs(Math.sin(t * 1.7))); ctx.fillStyle = C.gold;
      ctx.beginPath(); ctx.arc(a.x, top - 8, 1.8, 0, 6.29); ctx.fill();
    }
  },

  // Pages being typeset: two columns of lines and a figure fill in; a finished page gets a gold star.
  publications: {
    init: function (W, H, R) {
      var pages = [], n = Math.max(4, Math.round(W / 190)), ph = Math.min(H * 0.62, 120), pw = ph * 0.77;
      for (var i = 0; i < n; i++)
        pages.push({ x: (i + 0.5) * W / n - pw / 2 + (R() - 0.5) * 40, y: (H - ph) * (0.2 + 0.6 * R()), w: pw, h: ph, rot: (R() - 0.5) * 0.12,
          d: R() * 4, fig: R() < 0.5 ? 0 : 1 });
      return { pages: pages };
    },
    draw: function (ctx, s, t, W, H, C) {
      var L = 12, u = t % L;
      s.pages.forEach(function (p) {
        var g = Math.max(0, u - p.d), out = u > 11 ? 12 - u : 1;
        ctx.save(); ctx.translate(p.x + p.w / 2, p.y + p.h / 2); ctx.rotate(p.rot); ctx.translate(-p.w / 2, -p.h / 2);
        alpha(ctx, 0.9); ctx.fillStyle = C.bg; ctx.fillRect(0, 0, p.w, p.h);
        alpha(ctx, 0.6); ctx.strokeStyle = C.line; ctx.lineWidth = 1; ctx.strokeRect(0.5, 0.5, p.w - 1, p.h - 1);
        var m = p.w * 0.09, cw = (p.w - 3 * m) / 2, lines = Math.floor((p.h - 22 - m) / 5.5), done = g * 9;
        alpha(ctx, 0.6 * out); ctx.fillStyle = C.maroon;
        if (done > 0) ctx.fillRect(m + p.w * 0.1, m, (p.w - 2 * m - p.w * 0.2) * Math.min(1, done / 3), 3.5);   // title
        for (var c = 0; c < 2; c++) for (var l = 0; l < lines; l++) {
          var idx = 3 + c * lines + l, f = Math.max(0, Math.min(1, done - idx)); if (!f) continue;
          var ly = m + 14 + l * 5.5, lx = m + c * (cw + m);
          var isFig = (c === p.fig) && l >= 2 && l < 8;
          if (isFig) {
            if (l === 2) { alpha(ctx, 0.5 * out); ctx.strokeStyle = C.muted; ctx.strokeRect(lx, ly, cw, 30);
              alpha(ctx, 0.7 * out * f); ctx.strokeStyle = C.gold; ctx.beginPath();
              for (var v = 0; v <= cw - 4; v += 2) { var yy = ly + 24 - (v / (cw - 4)) * 16 - Math.sin(v / 3) * 2; v ? ctx.lineTo(lx + 2 + v, yy) : ctx.moveTo(lx + 2 + v, yy); }
              ctx.stroke(); }
            continue;
          }
          alpha(ctx, 0.35 * out); ctx.fillStyle = C.muted; ctx.fillRect(lx, ly, cw * (l % 5 === 4 ? 0.6 : 1) * f, 2);
        }
        if (done > 3 + 2 * lines) { alpha(ctx, 0.9 * out * Math.min(1, (done - 3 - 2 * lines) / 4)); ctx.fillStyle = C.gold; star(ctx, p.w - 6, 6, 8); }
        ctx.restore();
      });
      alpha(ctx, 1);
    }
  },

  // Trees grow up from the bottom edge, branch by branch, and blossom in gold at the tips (building programs).
  leadership: {
    init: function (W, H, R) {
      var trees = [], n = Math.max(2, Math.round(W / 380));
      for (var i = 0; i < n; i++) {
        var br = [], leaves = [];
        (function g(x, y, ang, len, d, t0) {
          var x2 = x + Math.cos(ang) * len, y2 = y + Math.sin(ang) * len, dur = 0.65;
          br.push({ x1: x, y1: y, x2: x2, y2: y2, d: d, t0: t0, dur: dur });
          if (d >= 6 || len < 9) { leaves.push({ x: x2, y: y2, t0: t0 + dur, r: 2.5 + R() * 2.5 }); return; }
          var kids = R() < 0.3 ? 3 : 2;
          for (var k = 0; k < kids; k++)
            g(x2, y2, ang + (k - (kids - 1) / 2) * (0.45 + R() * 0.3) + (R() - 0.5) * 0.2, len * (0.7 + R() * 0.1), d + 1, t0 + dur);
        })((i + 0.5 + (R() - 0.5) * 0.5) * W / n, H, -Math.PI / 2 + (R() - 0.5) * 0.3, H * 0.24, 0, 0);
        trees.push({ br: br, leaves: leaves, o: i * 3.3 });
      }
      return { trees: trees };
    },
    draw: function (ctx, s, t, W, H, C) {
      var P = 14;
      ctx.lineCap = 'round';
      s.trees.forEach(function (tr) {
        var g = ((t - tr.o) % P + P) % P, fade = g > 11 ? 1 - (g - 11) / 3 : 1;
        ctx.strokeStyle = C.maroon;
        tr.br.forEach(function (b) {
          var f = Math.max(0, Math.min(1, (g - b.t0) / b.dur));
          if (!f) return;
          alpha(ctx, 0.34 * fade); ctx.lineWidth = Math.max(0.7, 3.2 - b.d * 0.45);
          ctx.beginPath(); ctx.moveTo(b.x1, b.y1); ctx.lineTo(b.x1 + (b.x2 - b.x1) * f, b.y1 + (b.y2 - b.y1) * f); ctx.stroke();
        });
        ctx.fillStyle = C.gold;
        tr.leaves.forEach(function (l) {
          var f = Math.max(0, Math.min(1, (g - l.t0) / 0.6));
          if (!f) return;
          alpha(ctx, 0.8 * fade); star(ctx, l.x, l.y, l.r * (0.4 + 0.6 * f) * (0.85 + 0.15 * Math.sin(t * 2 + l.x)));
        });
      });
      alpha(ctx, 1);
    }
  },

  // A mesh network grows: devices join one by one, outward from the mentor's (gold), each linking to its two
  // nearest neighbours; gold packets hop along the links. Nodes keep clear of the title and intro.
  team: {
    init: function (W, H, R) {
      var n = Math.max(12, Math.min(40, Math.round(W * H / 8000))), pts = [], tries = 0;
      var bx = BOX && BOX.intro;
      while (pts.length < n && tries++ < 2000) {
        var x = 16 + R() * (W - 32), y = 14 + R() * (H - 28);
        if (bx && x > bx.left - 16 && x < bx.right + 16 && y > bx.top - 12 && y < bx.bottom + 12) continue;
        if (pts.some(function (p) { return Math.hypot(p.x - x, p.y - y) < 34; })) continue;
        pts.push({ x: x, y: y });
      }
      var m = pts.reduce(function (a, p) { return p.x > a.x ? p : a; }, pts[0]);   // the mentor: the right-most node
      pts.sort(function (a, b) { return Math.hypot(a.x - m.x, a.y - m.y) - Math.hypot(b.x - m.x, b.y - m.y); });
      var links = [];
      pts.forEach(function (p, i) {
        pts.slice(0, i).map(function (q, j) { return { j: j, d: Math.hypot(q.x - p.x, q.y - p.y) }; })
          .sort(function (a, b) { return a.d - b.d; }).slice(0, 2)
          .forEach(function (e) { links.push({ a: e.j, b: i, p: R() * 3 }); });
      });
      return { pts: pts, links: links };
    },
    draw: function (ctx, s, t, W, H, C) {
      var step = 0.32, L = s.pts.length * step + 7, u = t % L, out = u > L - 1 ? L - u : 1;
      ctx.lineWidth = 1.2;
      s.links.forEach(function (l) {
        var A = s.pts[l.a], B = s.pts[l.b], f = Math.max(0, Math.min(1, (u - l.b * step) / 0.4));
        if (!f) return;
        alpha(ctx, 0.32 * out); ctx.strokeStyle = C.maroon;
        ctx.beginPath(); ctx.moveTo(A.x, A.y); ctx.lineTo(A.x + (B.x - A.x) * f, A.y + (B.y - A.y) * f); ctx.stroke();
        if (f < 1) return;
        var ph = (t * 0.7 + l.p) % 2.2;   // a packet now and then, either way along the link
        if (ph < 1) {
          var q = l.p > 1.5 ? 1 - ph : ph;
          alpha(ctx, 0.85 * out); ctx.fillStyle = C.gold; ctx.beginPath(); ctx.arc(A.x + (B.x - A.x) * q, A.y + (B.y - A.y) * q, 2.2, 0, 6.29); ctx.fill();
        }
      });
      s.pts.forEach(function (p, i) {
        var a = u - i * step; if (a < 0) return;
        var g = Math.min(1, a / 0.3) * out, r = i ? 4.5 : 6.5;
        alpha(ctx, g); ctx.fillStyle = C.band; ctx.beginPath(); ctx.arc(p.x, p.y, r, 0, 6.29); ctx.fill();
        alpha(ctx, (i ? 0.55 : 0.8) * g); ctx.strokeStyle = i ? C.maroon : C.gold; ctx.lineWidth = 1.4; ctx.stroke();
        ctx.beginPath(); ctx.moveTo(p.x, p.y - r); ctx.lineTo(p.x, p.y - r - 5); ctx.stroke();   // a little antenna
        if (!i) { ctx.fillStyle = C.gold; ctx.beginPath(); ctx.arc(p.x, p.y, 2.5, 0, 6.29); ctx.fill(); }
        if (a < 1) { alpha(ctx, 0.6 * (1 - a)); ctx.strokeStyle = C.gold; ctx.lineWidth = 1; ctx.beginPath(); ctx.arc(p.x, p.y, r + a * 14, 0, 6.29); ctx.stroke(); }
      });
      alpha(ctx, 1);
    }
  },

  // An open book beside the intro, its pages turning; small symbols of what is taught rise from it:
  // a wave, a neuron, a chat bubble, an antenna.
  teaching: {
    init: function (W, H, R) {
      var left = BOX ? BOX.intro.right + 40 : W * 0.6, room = W - 20 - left;
      if (room < 160) {   // no room beside the intro (phones): a smaller book above the title, on the right
        var sw = 60, top = BOX ? BOX.h1.top : H * 0.4;
        return { cx: W - sw - 18, by: Math.max(sw * 0.36 + 6, top - 14 - sw * 0.36 * 0.7), bw: sw };
      }
      var bw = Math.min(150, Math.max(80, room * 0.36));
      return { cx: left + room / 2, by: H - bw * 0.36 * 0.7 - 30, bw: bw };   // the book's lower edge sits 30 px above the strip's bottom
    },
    draw: function (ctx, s, t, W, H, C) {
      var cx = s.cx, by = s.by, bw = s.bw, bh = bw * 0.36;
      ctx.lineJoin = 'round'; ctx.lineWidth = 1.4;
      [-1, 1].forEach(function (sd) {   // the two halves of the open book
        alpha(ctx, 0.9); ctx.fillStyle = C.bg; ctx.strokeStyle = C.maroon;
        ctx.beginPath(); ctx.moveTo(cx, by); ctx.quadraticCurveTo(cx + sd * bw * 0.5, by - bh * 0.6, cx + sd * bw, by - bh * 0.25);
        ctx.lineTo(cx + sd * bw, by + bh * 0.55); ctx.quadraticCurveTo(cx + sd * bw * 0.5, by + bh * 0.2, cx, by + bh * 0.7); ctx.closePath(); ctx.fill();
        alpha(ctx, 0.6); ctx.stroke();
        for (var l = 0; l < 4; l++) { alpha(ctx, 0.3); ctx.strokeStyle = C.muted; ctx.beginPath();
          var yy = by - bh * 0.15 + l * bh * 0.17; ctx.moveTo(cx + sd * 6, yy + 2); ctx.quadraticCurveTo(cx + sd * bw * 0.5, yy - bh * 0.3, cx + sd * (bw - 6), yy - bh * 0.05); ctx.stroke(); }
        ctx.strokeStyle = C.maroon;
      });
      var ph = (t * 0.5) % 1, ang = ph * Math.PI;   // a page turning
      alpha(ctx, 0.75); ctx.fillStyle = C.bg; ctx.beginPath(); ctx.moveTo(cx, by);
      var px = cx + Math.cos(ang) * bw, py = by - bh * 0.25 - Math.sin(ang) * bh * 1.4;
      ctx.quadraticCurveTo((cx + px) / 2, Math.min(by, py) - bh * 0.4, px, py); ctx.lineTo(px, py + bh * 0.8); ctx.quadraticCurveTo((cx + px) / 2, by + bh * 0.3, cx, by + bh * 0.7); ctx.closePath(); ctx.fill();
      alpha(ctx, 0.5); ctx.stroke();
      for (var k = Math.floor((t - 4) / 0.9); k <= Math.floor(t / 0.9); k++) {   // rising symbols
        if (k < 0) continue;
        var age = t - k * 0.9, R = rng(k * 11 + 1), kind = k % 4, sx = cx + (R() - 0.5) * bw * 1.8 + Math.sin(age * 1.5 + k) * 10, sy = by - bh - age * (H / 5), z = bw / 70;
        if (age < 0 || age > 4 || sy < 6) continue;
        var a = Math.min(1, age * 2) * (1 - age / 4);
        alpha(ctx, 0.85 * a); ctx.strokeStyle = kind % 2 ? C.gold : C.maroon; ctx.fillStyle = ctx.strokeStyle; ctx.lineWidth = 1.5 / z; ctx.save(); ctx.translate(sx, sy); ctx.scale(z, z); sx = sy = 0; ctx.beginPath();   // symbols grow with the book
        if (kind === 0) { for (var v = -9; v <= 9; v++) { var wy = sy - Math.sin(v / 9 * Math.PI * 2) * 4; v > -9 ? ctx.lineTo(sx + v, wy) : ctx.moveTo(sx + v, wy); } ctx.stroke(); }
        else if (kind === 1) { ctx.arc(sx, sy, 4, 0, 6.29); ctx.fill(); [[-9, -6], [-9, 6], [9, 0]].forEach(function (d) { ctx.beginPath(); ctx.moveTo(sx, sy); ctx.lineTo(sx + d[0], sy + d[1]); ctx.stroke(); }); }
        else if (kind === 2) { if (ctx.roundRect) ctx.roundRect(sx - 9, sy - 6, 18, 11, 4); else ctx.rect(sx - 9, sy - 6, 18, 11); ctx.moveTo(sx - 3, sy + 5); ctx.lineTo(sx - 6, sy + 9); ctx.lineTo(sx + 1, sy + 5); ctx.stroke(); }
        else { ctx.moveTo(sx, sy + 8); ctx.lineTo(sx, sy - 4); ctx.stroke(); [5, 9].forEach(function (r) { ctx.beginPath(); ctx.arc(sx, sy - 4, r, -Math.PI * 0.8, -Math.PI * 0.2); ctx.stroke(); }); }
        ctx.restore();
      }
      alpha(ctx, 1);
    }
  },

  // The light-wave kit from the outreach program: a phone plays music into an LED, the music crosses as flickering light to a
  // solar cell, and a speaker plays it back, with notes floating up.
  outreach: {
    init: function (W, H, R) {
      var left = BOX ? BOX.intro.right + 30 : W * 0.55, room = W - 16 - left, z;
      if (room >= 240) { z = Math.min(1.35, room / 380, (H - 30) / 110); return { z: z, x: left + (room - 380 * z) / 2, y: H / 2 - 55 * z }; }
      z = Math.min(0.5, (W - 32) / 380);   // phones: small, in the bottom-right corner
      return { z: z, x: W - 380 * z - 14, y: H - 100 * z - 6 };
    },
    draw: function (ctx, s, t, W, H, C) {
      ctx.save(); ctx.translate(s.x, s.y); ctx.scale(s.z, s.z);
      ctx.lineWidth = 1.6; ctx.lineJoin = 'round'; ctx.lineCap = 'round';
      function rr(x, y, w, h, r) { ctx.beginPath(); ctx.moveTo(x + r, y); ctx.arcTo(x + w, y, x + w, y + h, r); ctx.arcTo(x + w, y + h, x, y + h, r); ctx.arcTo(x, y + h, x, y, r); ctx.arcTo(x, y, x + w, y, r); ctx.closePath(); }
      function note(x, y, sz) { ctx.beginPath(); ctx.ellipse(x, y, sz * 0.55, sz * 0.4, -0.4, 0, 6.29); ctx.fill(); ctx.fillRect(x + sz * 0.42, y - sz * 1.6, sz * 0.16, sz * 1.6); ctx.fillRect(x + sz * 0.42, y - sz * 1.6, sz * 0.6, sz * 0.18); }
      var on = rng(Math.floor(t * 14))() > 0.35;
      // phone
      alpha(ctx, 0.55); ctx.strokeStyle = C.maroon; rr(0, 24, 34, 62, 6); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(13, 30); ctx.lineTo(21, 30); ctx.stroke();
      alpha(ctx, 0.8); ctx.fillStyle = C.gold; note(14, 60 + Math.sin(t * 4) * 2, 7);
      // wires
      alpha(ctx, 0.4); ctx.strokeStyle = C.muted; ctx.lineWidth = 1.3;
      ctx.beginPath(); ctx.moveTo(34, 72); ctx.bezierCurveTo(52, 92, 66, 92, 80, 76); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(302, 76); ctx.bezierCurveTo(314, 92, 326, 92, 334, 72); ctx.stroke();
      // LED on a little board
      ctx.lineWidth = 1.6; alpha(ctx, 0.55); ctx.strokeStyle = C.maroon; rr(72, 66, 26, 12, 3); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(78, 66); ctx.lineTo(78, 58); ctx.moveTo(92, 66); ctx.lineTo(92, 58); ctx.stroke();
      ctx.beginPath(); ctx.arc(85, 50, 8, Math.PI, 0); ctx.lineTo(93, 58); ctx.lineTo(77, 58); ctx.closePath();
      alpha(ctx, on ? 0.85 : 0.3); ctx.fillStyle = C.gold; ctx.fill(); alpha(ctx, 0.6); ctx.stroke();
      // the light beam, with pulses travelling along it
      var x0 = 96, x1 = 266;
      ctx.beginPath(); ctx.moveTo(x0, 46); ctx.lineTo(x1, 34); ctx.lineTo(x1, 66); ctx.lineTo(x0, 54); ctx.closePath();
      alpha(ctx, 0.12); ctx.fillStyle = C.gold; ctx.fill();
      for (var k = Math.floor(t * 14) - 20; k <= Math.floor(t * 14); k++) {
        var px = x0 + (t - k / 14) * 150; if (px > x1 || px < x0) continue;
        if (rng(k)() <= 0.35) continue;   // the same on/off pattern the LED blinked
        var hw = 4 + (px - x0) / (x1 - x0) * 12;
        alpha(ctx, 0.75); ctx.fillRect(px, 50 - hw, 4, hw * 2);
      }
      // solar cell
      var hit = rng(Math.floor((t - (x1 - x0) / 150) * 14))() > 0.35;
      alpha(ctx, hit ? 0.35 : 0.1); ctx.fillStyle = C.gold; ctx.fillRect(270, 26, 32, 50);
      alpha(ctx, 0.55); ctx.strokeStyle = C.maroon; ctx.strokeRect(270, 26, 32, 50);
      ctx.lineWidth = 1; ctx.beginPath();
      for (var i = 1; i < 4; i++) { ctx.moveTo(270, 26 + i * 12.5); ctx.lineTo(302, 26 + i * 12.5); }
      ctx.moveTo(286, 26); ctx.lineTo(286, 76); ctx.stroke();
      // speaker, with sound arcs and notes floating up
      ctx.lineWidth = 1.6; alpha(ctx, 0.6); ctx.fillStyle = C.maroon;
      ctx.beginPath(); ctx.moveTo(332, 42); ctx.lineTo(340, 42); ctx.lineTo(352, 30); ctx.lineTo(352, 70); ctx.lineTo(340, 58); ctx.lineTo(332, 58); ctx.closePath(); ctx.fill();
      ctx.strokeStyle = C.maroon;
      for (var j = 0; j < 3; j++) {
        var f = ((t * 0.9 + j / 3) % 1);
        alpha(ctx, 0.5 * (1 - f)); ctx.beginPath(); ctx.arc(352, 50, 8 + f * 26, -0.7, 0.7); ctx.stroke();
      }
      for (var n = Math.floor(t / 0.7) - 5; n <= Math.floor(t / 0.7); n++) {
        var a = t - n * 0.7, Rn = rng(n * 13 + 1); if (a < 0 || a > 3) continue;
        alpha(ctx, 0.8 * Math.min(1, a * 3) * (1 - a / 3)); ctx.fillStyle = Rn() < 0.5 ? C.gold : C.maroon;
        note(360 + a * 8 + Math.sin(a * 3 + n) * 5, 34 - a * 22, 5 + Rn() * 2);
      }
      ctx.restore(); alpha(ctx, 1);
    }
  }
  ,
  // A neural network; signals travel forward through the layers, and nodes glow gold as one passes.
  neural: {
    init: function (W, H, R) {
      var L = Math.max(5, Math.round(W / 150)), layers = [];
      for (var i = 0; i < L; i++) {
        var n = 3 + Math.floor(R() * 4), col = [];
        for (var j = 0; j < n; j++) col.push({ x: (i + 0.5) * W / L, y: H * (0.14 + 0.72 * (j + 0.5) / n) });   // layers in straight columns
        layers.push(col);
      }
      return { layers: layers };
    },
    draw: function (ctx, s, t, W, H, C) {
      var Ls = s.layers, L = Ls.length, hop = 0.32, gap = 0.28, dur = (L - 1) * hop;
      ctx.lineWidth = 1; ctx.strokeStyle = C.muted; alpha(ctx, 0.1);
      for (var i = 0; i < L - 1; i++) Ls[i].forEach(function (a) { Ls[i + 1].forEach(function (b) {
        ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(b.x, b.y); ctx.stroke(); }); });
      var glow = Ls.map(function (c) { return c.map(function () { return 0; }); });
      for (var k = Math.floor((t - dur - 1) / gap); k <= Math.floor(t / gap); k++) {
        if (k < 0) continue;
        var age = t - k * gap; if (age < 0 || age > dur + 1) continue;
        var R = rng(k * 7919 + 3), path = Ls.map(function (c) { return Math.floor(R() * c.length); });
        var pos = Math.min(age / hop, L - 1), fade = age > dur ? 1 - (age - dur) : 1;
        ctx.strokeStyle = C.maroon; ctx.lineWidth = 1.3;
        for (var q = 0; q < Math.ceil(pos); q++) {
          var a = Ls[q][path[q]], b = Ls[q + 1][path[q + 1]], f = Math.min(1, pos - q);
          alpha(ctx, 0.32 * fade); ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(a.x + (b.x - a.x) * f, a.y + (b.y - a.y) * f); ctx.stroke();
          if (f < 1) { alpha(ctx, 0.9 * fade); ctx.fillStyle = C.gold; ctx.beginPath(); ctx.arc(a.x + (b.x - a.x) * f, a.y + (b.y - a.y) * f, 2.6, 0, 6.29); ctx.fill(); }
        }
        for (var q2 = 0; q2 <= Math.floor(pos); q2++) {
          var since = age - q2 * hop;
          glow[q2][path[q2]] = Math.max(glow[q2][path[q2]], Math.max(0, 1 - since / 0.8) * fade);
        }
      }
      Ls.forEach(function (c, i) { c.forEach(function (n, j) {
        alpha(ctx, 1); ctx.fillStyle = C.band; ctx.beginPath(); ctx.arc(n.x, n.y, 4.5, 0, 6.29); ctx.fill();
        alpha(ctx, 0.45); ctx.strokeStyle = C.maroon; ctx.lineWidth = 1.2; ctx.stroke();
        if (glow[i][j] > 0) { alpha(ctx, 0.85 * glow[i][j]); ctx.fillStyle = C.gold; ctx.beginPath(); ctx.arc(n.x, n.y, 4.5, 0, 6.29); ctx.fill(); }
      }); });
      alpha(ctx, 1);
    }
  },

  // A QAM constellation; received symbols land around the ideal points, and the noise slowly rises and falls.
  qam: {
    init: function (W, H, R) {
      // one constellation, high in the banner so all 16 points sit above the intro text
      var n = 1, cs = [], sp = Math.min(H * 0.12, 28);
      for (var i = 0; i < n; i++) cs.push({ x: (i + 0.5) * W / n, y: Math.min(H * 0.3, sp * 2.1 + 8), sp: sp, p: R() * 6.28 });
      return { cs: cs };
    },
    draw: function (ctx, s, t, W, H, C) {
      var gap = 0.025, life = 2.4;
      s.cs.forEach(function (c, ci) {
        var sp = c.sp, ext = sp * 2.1, z = sp / 22;
        ctx.strokeStyle = C.muted; ctx.lineWidth = 1; alpha(ctx, 0.28);
        ctx.beginPath(); ctx.moveTo(c.x - ext, c.y); ctx.lineTo(c.x + ext, c.y); ctx.moveTo(c.x, c.y - ext); ctx.lineTo(c.x, c.y + ext); ctx.stroke();
        alpha(ctx, 0.45); ctx.strokeStyle = C.maroon;
        for (var i = 0; i < 4; i++) for (var j = 0; j < 4; j++) {
          var px = c.x + (i - 1.5) * sp, py = c.y + (j - 1.5) * sp;
          ctx.beginPath(); ctx.arc(px, py, 4 * z, 0, 6.29); ctx.stroke();
        }
        for (var k = Math.floor((t - life) / gap); k <= Math.floor(t / gap); k++) {
          if (k < 0) continue;
          var age = t - k * gap; if (age < 0 || age > life) continue;
          var R = rng(k * 131 + ci * 7 + 1), sym = Math.floor(R() * 16), tk = k * gap;
          var noise = sp * (0.1 + 0.22 * (0.5 + 0.5 * Math.sin(tk * 0.35 + c.p)));
          var x = c.x + ((sym & 3) - 1.5) * sp + (R() + R() + R() - 1.5) * noise, y = c.y + ((sym >> 2) - 1.5) * sp + (R() + R() + R() - 1.5) * noise;
          var fresh = age < 0.25;
          alpha(ctx, fresh ? 0.95 : 0.55 * (1 - age / life)); ctx.fillStyle = fresh ? C.gold : C.maroon;
          ctx.beginPath(); ctx.arc(x, y, (fresh ? 2.4 : 1.5) * z, 0, 6.29); ctx.fill();
        }
      });
      alpha(ctx, 1);
    }
  }
  
};

start();
})();
