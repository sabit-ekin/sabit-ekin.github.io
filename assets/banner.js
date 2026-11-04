// Page banner: a faint animated line drawing behind the title and intro of each section page, about that page:
//   research     antennas sweep tapered beams with wavefront ticks; targets light up as a beam passes
//   publications a network of papers; citations run along it as dashed paths
//   leadership   trees grow up from the bottom edge and blossom in gold
//   team         mentor hubs with students orbiting them; signals pass between them
//   teaching     signals on graph paper: carrier, message, and the modulated wave
//   outreach     ripples spread from a few sources; houses and schools light up as a ripple reaches them
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
    if (w !== W || h !== H) {
      W = w; H = h;
      cv.width = mk.width = W * dpr; cv.height = mk.height = H * dpr; cv.style.height = H + 'px';
      scene = DRAW[motif].init(W, H, rng(7));
    }
    mask();
    frame();
  }
  // Keep the text readable: a soft patch of the band color over every line of the title and intro (and the
  // buttons), drawn on top of the drawing, so it only shows in the open space around the text.
  function mask() {
    var box = main.getBoundingClientRect(), rects = [], range = document.createRange();
    var els = h1.parentElement.matches('.intro') ? [].slice.call(h1.parentElement.children)
      : [h1].concat(h1.nextElementSibling && h1.nextElementSibling.matches('.lede') ? [h1.nextElementSibling] : []);
    els.forEach(function (el) {
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
function alpha(ctx, a) { ctx.globalAlpha = Math.max(0, Math.min(1, a)); }
function scatter(W, H, step, R) {   // points on a jittered grid that covers the banner
  var pts = [];
  for (var y = step * 0.4; y < H + step * 0.3; y += step * 0.8)
    for (var x = step * 0.3; x < W + step * 0.3; x += step)
      pts.push({ x: x + (R() - 0.5) * step * 0.8, y: y + (R() - 0.5) * step * 0.6, p: R() * 6.28 });
  return pts;
}
function neighbours(pts, k) {   // edges to each point's k nearest points (no duplicates)
  var edges = [], seen = {};
  pts.forEach(function (a, i) {
    pts.map(function (b, j) { return { j: j, d: (a.x - b.x) * (a.x - b.x) + (a.y - b.y) * (a.y - b.y) }; })
      .sort(function (p, q) { return p.d - q.d; }).slice(1, k + 1)
      .forEach(function (n) {
        var key = Math.min(i, n.j) + '-' + Math.max(i, n.j);
        if (!seen[key]) { seen[key] = 1; edges.push([i, n.j]); }
      });
  });
  return edges;
}
function drift(p, t, amp) { return { x: p.x + Math.sin(t * 0.25 + p.p) * amp, y: p.y + Math.cos(t * 0.21 + p.p * 1.3) * amp }; }
function star(ctx, x, y, r) {   // four-point sparkle
  ctx.beginPath();
  ctx.moveTo(x, y - r); ctx.quadraticCurveTo(x, y, x + r, y); ctx.quadraticCurveTo(x, y, x, y + r);
  ctx.quadraticCurveTo(x, y, x - r, y); ctx.quadraticCurveTo(x, y, x, y - r); ctx.fill();
}

// ---- the drawings --------------------------------------------------------------------------------------------
var DRAW = {
  // Antennas sweep tapered beams; ticks travel out along each beam; targets light up when a beam passes over them.
  research: {
    init: function (W, H, R) {
      var ants = [], n = Math.max(2, Math.round(W / 420));
      for (var i = 0; i < n; i++) ants.push({ x: (i + 0.5 + (R() - 0.5) * 0.4) * W / n, y: H * (0.78 + R() * 0.15),
        base: -Math.PI / 2 + (R() - 0.5) * 0.6, sweep: 0.5 + R() * 0.35, speed: 0.18 + R() * 0.12, p: R() * 6.28 });
      var dots = [];
      for (var j = 0; j < W / 26; j++) dots.push({ x: R() * W, y: R() * H * 0.85, lit: 0 });
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
        // antenna: mast and dish
        alpha(ctx, 0.55); ctx.strokeStyle = C.muted; ctx.lineWidth = 1.5;
        ctx.beginPath(); ctx.moveTo(a.x, a.y); ctx.lineTo(a.x, a.y + 26); ctx.moveTo(a.x - 8, a.y + 26); ctx.lineTo(a.x + 8, a.y + 26); ctx.stroke();
        ctx.fillStyle = C.maroon; alpha(ctx, 0.6); ctx.beginPath(); ctx.arc(a.x, a.y, 3.2, 0, 6.28); ctx.fill();
      });
      s.dots.forEach(function (d) {
        d.lit = Math.max(0, d.lit - 0.012);
        alpha(ctx, 0.35 + d.lit * 0.5); ctx.fillStyle = d.lit > 0.05 ? C.maroon : C.muted;
        ctx.beginPath(); ctx.arc(d.x, d.y, 1.6 + d.lit * 2, 0, 6.28); ctx.fill();
      });
      alpha(ctx, 1);
    }
  },

  // Papers (small pages) linked to their neighbours; a citation runs along a few links as a dashed path.
  publications: {
    init: function (W, H, R) {
      var pts = scatter(W, H, 120, R);
      return { pts: pts, edges: neighbours(pts, 3), adj: null, paths: [], next: 0, R: R };
    },
    draw: function (ctx, s, t, W, H, C) {
      var P = s.pts.map(function (p) { return drift(p, t, 5); });
      if (!s.adj) { s.adj = s.pts.map(function () { return []; }); s.edges.forEach(function (e) { s.adj[e[0]].push(e[1]); s.adj[e[1]].push(e[0]); }); }
      ctx.strokeStyle = C.line; ctx.lineWidth = 1; alpha(ctx, 1);
      ctx.beginPath();
      s.edges.forEach(function (e) { ctx.moveTo(P[e[0]].x, P[e[0]].y); ctx.lineTo(P[e[1]].x, P[e[1]].y); });
      ctx.stroke();
      // a new citation path every ~1.6 s
      if (t > s.next) {
        var i = Math.floor(s.R() * P.length), path = [i];
        for (var k = 0; k < 4; k++) { var nb = s.adj[path[path.length - 1]].filter(function (j) { return path.indexOf(j) < 0; }); if (!nb.length) break; path.push(nb[Math.floor(s.R() * nb.length)]); }
        s.paths.push({ path: path, t0: t }); s.next = t + 1.6;
        s.paths = s.paths.filter(function (p) { return t - p.t0 < 7; });
      }
      var lit = {};
      s.paths.forEach(function (p) {
        var age = t - p.t0, prog = Math.min(age / 0.7, p.path.length - 1), fade = age > 4.5 ? 1 - (age - 4.5) / 2.5 : 1;
        ctx.setLineDash([5, 5]); ctx.strokeStyle = C.maroon; ctx.lineWidth = 1.3; alpha(ctx, 0.5 * fade);
        ctx.beginPath(); ctx.moveTo(P[p.path[0]].x, P[p.path[0]].y);
        for (var k = 1; k <= Math.ceil(prog); k++) {
          var a = P[p.path[k - 1]], b = P[p.path[k]], f = Math.min(1, prog - (k - 1));
          ctx.lineTo(a.x + (b.x - a.x) * f, a.y + (b.y - a.y) * f);
          if (f >= 1) lit[p.path[k]] = Math.max(lit[p.path[k]] || 0, fade);
        }
        ctx.stroke(); ctx.setLineDash([]);
        lit[p.path[0]] = Math.max(lit[p.path[0]] || 0, fade);
      });
      P.forEach(function (p, i) {   // each paper: a small page with two text lines
        var l = lit[i] || 0, w = 9, h = 12;
        alpha(ctx, 1); ctx.fillStyle = C.bg; ctx.strokeStyle = l ? C.maroon : C.line; ctx.lineWidth = 1.1;
        ctx.beginPath(); ctx.rect(p.x - w / 2, p.y - h / 2, w, h); ctx.fill(); alpha(ctx, l ? 0.35 + 0.5 * l : 1); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(p.x - 2.5, p.y - 2); ctx.lineTo(p.x + 2.5, p.y - 2); ctx.moveTo(p.x - 2.5, p.y + 1.5); ctx.lineTo(p.x + 1.5, p.y + 1.5); ctx.stroke();
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

  // Mentor hubs with students orbiting them; links to each hub, dashed links between hubs, pulses along them.
  team: {
    init: function (W, H, R) {
      var hubs = [], n = Math.max(3, Math.round(W / 260));
      for (var i = 0; i < n; i++) {
        var h = { x: (i + 0.5) * W / n + (R() - 0.5) * 60, y: H * (0.25 + R() * 0.5), sats: [] };
        var m = 3 + Math.floor(R() * 4);
        for (var j = 0; j < m; j++) h.sats.push({ r: 34 + R() * 46, a: R() * 6.28, w: (R() < 0.5 ? -1 : 1) * (0.05 + R() * 0.08), s: 2.4 + R() * 1.4 });
        hubs.push(h);
      }
      return { hubs: hubs };
    },
    draw: function (ctx, s, t, W, H, C) {
      var hubs = s.hubs;
      ctx.lineWidth = 1;
      // hub to hub
      ctx.strokeStyle = C.maroon; ctx.setLineDash([5, 6]); alpha(ctx, 0.28);
      ctx.beginPath();
      for (var i = 1; i < hubs.length; i++) { ctx.moveTo(hubs[i - 1].x, hubs[i - 1].y); ctx.lineTo(hubs[i].x, hubs[i].y); }
      ctx.stroke(); ctx.setLineDash([]);
      for (i = 1; i < hubs.length; i++) {   // a signal travelling between hubs
        var f = ((t * 0.18 + i * 0.37) % 1), a = hubs[i - 1], b = hubs[i];
        alpha(ctx, 0.55 * Math.sin(f * Math.PI)); ctx.fillStyle = C.maroon;
        ctx.beginPath(); ctx.arc(a.x + (b.x - a.x) * f, a.y + (b.y - a.y) * f, 2.6, 0, 6.28); ctx.fill();
      }
      hubs.forEach(function (h, hi) {
        // orbits
        ctx.strokeStyle = C.line; alpha(ctx, 1);
        h.sats.forEach(function (st) { ctx.beginPath(); ctx.arc(h.x, h.y, st.r, 0, 6.28); ctx.stroke(); });
        h.sats.forEach(function (st, si) {
          var ang = st.a + t * st.w, x = h.x + Math.cos(ang) * st.r, y = h.y + Math.sin(ang) * st.r;
          ctx.strokeStyle = C.line; alpha(ctx, 1); ctx.beginPath(); ctx.moveTo(h.x, h.y); ctx.lineTo(x, y); ctx.stroke();
          var pulse = (t * 0.5 + si * 0.23 + hi * 0.31) % 1;   // a pulse from the hub to each student
          alpha(ctx, 0.5 * (1 - pulse)); ctx.fillStyle = C.maroon;
          ctx.beginPath(); ctx.arc(h.x + (x - h.x) * pulse, h.y + (y - h.y) * pulse, 1.8, 0, 6.28); ctx.fill();
          alpha(ctx, 1); ctx.fillStyle = C.bg; ctx.strokeStyle = C.muted; alpha(ctx, 0.6);
          ctx.beginPath(); ctx.arc(x, y, st.s, 0, 6.28); ctx.fill(); ctx.stroke();
        });
        // hub with wireless arcs
        alpha(ctx, 0.55); ctx.fillStyle = C.maroon; ctx.beginPath(); ctx.arc(h.x, h.y, 5, 0, 6.28); ctx.fill();
        ctx.strokeStyle = C.maroon; ctx.lineWidth = 1.3;
        for (var k = 0; k < 2; k++) {
          var r = 10 + ((t * 12 + k * 9) % 18);
          alpha(ctx, 0.45 * (1 - (r - 10) / 18));
          ctx.beginPath(); ctx.arc(h.x, h.y, r, -Math.PI * 0.8, -Math.PI * 0.2); ctx.stroke();
        }
        ctx.lineWidth = 1;
      });
      alpha(ctx, 1);
    }
  },

  // Graph paper with three signals scrolling across: a carrier, a message, and the modulated (AM) wave.
  teaching: {
    init: function () { return {}; },
    draw: function (ctx, s, t, W, H, C) {
      ctx.lineWidth = 1; ctx.strokeStyle = C.line; alpha(ctx, 0.7);
      ctx.beginPath();
      for (var x = 0; x < W; x += 24) { ctx.moveTo(x + 0.5, 0); ctx.lineTo(x + 0.5, H); }
      for (var y = 0; y < H; y += 24) { ctx.moveTo(0, y + 0.5); ctx.lineTo(W, y + 0.5); }
      ctx.stroke();
      alpha(ctx, 1); ctx.beginPath();
      for (x = 0; x < W; x += 120) { ctx.moveTo(x + 0.5, 0); ctx.lineTo(x + 0.5, H); }
      ctx.stroke();
      var mid = H * 0.55, amp = Math.min(H * 0.22, 60);
      function wave(fn, color, a, width, dash) {
        ctx.strokeStyle = color; alpha(ctx, a); ctx.lineWidth = width; ctx.setLineDash(dash || []);
        ctx.beginPath();
        for (var x = 0; x <= W; x += 2) { var y = mid - fn(x) * amp; x ? ctx.lineTo(x, y) : ctx.moveTo(x, y); }
        ctx.stroke(); ctx.setLineDash([]);
      }
      var m = function (x) { return 0.55 * Math.sin(x / 140 - t * 0.9); };
      wave(function (x) { return 1 + m(x); }, C.maroon, 0.28, 1.2, [6, 6]);                 // envelope (message)
      wave(function (x) { return -(1 + m(x)); }, C.maroon, 0.28, 1.2, [6, 6]);
      wave(function (x) { return (1 + m(x)) * Math.sin(x / 9 - t * 4); }, C.maroon, 0.24, 1.3);  // AM wave
      wave(function (x) { return 0.35 * Math.sin(x / 55 - t * 1.6) - 1.55; }, C.muted, 0.35, 1.1); // a lower, slower tone
      alpha(ctx, 1);
    }
  },

  // Ripples spread from a few sources; houses and schools light up when a ripple reaches them.
  outreach: {
    init: function (W, H, R) {
      var src = [], n = Math.max(2, Math.round(W / 500));
      for (var i = 0; i < n; i++) src.push({ x: (i + 0.5) * W / n + (R() - 0.5) * 120, y: H * (0.3 + R() * 0.4), p: R() * 4 });
      var homes = [];
      for (i = 0; i < W * H / 9000; i++) homes.push({ x: R() * W, y: R() * H, school: R() < 0.2, lit: 0 });
      return { src: src, homes: homes, last: 0 };
    },
    draw: function (ctx, s, t, W, H, C) {
      var period = 4, maxR = Math.max(W / s.src.length, H) * 0.9, dt = Math.min(0.1, Math.max(0, t - s.last)); s.last = t;
      ctx.strokeStyle = C.maroon; ctx.lineWidth = 1.3;
      s.src.forEach(function (sc) {
        for (var k = 0; k < 3; k++) {
          var r = (((t + sc.p) / period + k / 3) % 1) * maxR;
          alpha(ctx, 0.38 * (1 - r / maxR)); ctx.beginPath(); ctx.arc(sc.x, sc.y, r, 0, 6.28); ctx.stroke();
          s.homes.forEach(function (h) { if (Math.abs(Math.hypot(h.x - sc.x, h.y - sc.y) - r) < 3) h.lit = 1; });
        }
        alpha(ctx, 0.6); ctx.fillStyle = C.maroon; ctx.beginPath(); ctx.arc(sc.x, sc.y, 4, 0, 6.28); ctx.fill();
      });
      s.homes.forEach(function (h) {
        h.lit = Math.max(0, h.lit - dt * 0.6);
        var w = h.school ? 14 : 9, hh = h.school ? 9 : 7;
        ctx.lineWidth = 1.1; ctx.strokeStyle = h.lit > 0.05 ? C.maroon : C.muted; alpha(ctx, 0.35 + 0.5 * h.lit);
        ctx.fillStyle = C.gold;
        ctx.beginPath();
        ctx.moveTo(h.x - w / 2, h.y); ctx.lineTo(h.x - w / 2, h.y - hh); ctx.lineTo(h.x, h.y - hh - 6); ctx.lineTo(h.x + w / 2, h.y - hh); ctx.lineTo(h.x + w / 2, h.y); ctx.closePath();
        if (h.lit > 0.05) { alpha(ctx, 0.55 * h.lit); ctx.fill(); alpha(ctx, 0.35 + 0.5 * h.lit); }
        ctx.stroke();
        if (h.school) { ctx.beginPath(); ctx.moveTo(h.x, h.y - hh - 6); ctx.lineTo(h.x, h.y - hh - 12); ctx.lineTo(h.x + 4, h.y - hh - 10); ctx.lineTo(h.x, h.y - hh - 9); ctx.stroke(); }
      });
      alpha(ctx, 1);
    }
  }
};

start();
})();
