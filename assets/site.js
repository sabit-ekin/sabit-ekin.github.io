// Shared scripts for the home page and the section pages; each part does nothing on pages without its elements.

// Top bar: menu button on narrow screens; the link of the current page is marked, and on the home page the
// Contact link takes over from Home once its section is in view (or the page is scrolled to the bottom).
(function () {
  var h = document.querySelector('header.nav'), b = h && h.querySelector('.menu-btn');
  if (!b) return;
  function set(open) { h.classList.toggle('open', open); b.setAttribute('aria-expanded', open); b.textContent = open ? 'Close' : 'Menu'; }
  b.addEventListener('click', function () { set(!h.classList.contains('open')); });
  h.querySelectorAll('#nav-list a').forEach(function (a) { a.addEventListener('click', function () { set(false); }); });
  document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && h.classList.contains('open')) { set(false); b.focus(); } });
  function name(path) { return (path.split('/').pop() || 'index.html').replace(/\.html$/, ''); }
  var page = name(location.pathname), links = Array.prototype.slice.call(h.querySelectorAll('#nav-list a'));
  links.forEach(function (a) {
    var href = a.getAttribute('href');
    if (href.indexOf('#') < 0 && name(href) === page) { a.classList.add('active'); a.setAttribute('aria-current', 'page'); }
  });
  var here = h.querySelector('#nav-list a.active');
  var spied = links.filter(function (a) { return a.getAttribute('href').charAt(0) === '#'; }), cur = null, queued = false;
  if (!spied.length) return;
  var secs = spied.map(function (a) { return document.getElementById(a.getAttribute('href').slice(1)); });
  function spy() {
    queued = false;
    var line = h.offsetHeight + 24, on = -1;
    secs.forEach(function (sec, i) { if (sec && sec.getBoundingClientRect().top <= line) on = i; });
    if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 2) on = secs.length - 1;
    var a = on < 0 ? null : spied[on];
    if (a === cur) return;
    if (cur) { cur.classList.remove('active'); cur.removeAttribute('aria-current'); }
    if (a) { a.classList.add('active'); a.setAttribute('aria-current', 'location'); }
    if (here) here.classList.toggle('active', !a);   // Home is marked except while Contact is
    cur = a;
  }
  function queue() { if (!queued) { queued = true; requestAnimationFrame(spy); } }
  window.addEventListener('scroll', queue, { passive: true });
  window.addEventListener('resize', queue);
  spy();
})();

// Career path: reveal the steps as they scroll into view, staggered within each batch (a row on wide screens)
(function () {
  var steps = document.querySelectorAll('.path li');
  if (!steps.length || !('IntersectionObserver' in window)) return;
  var io = new IntersectionObserver(function (es) {
    var n = 0;
    es.forEach(function (e) {
      if (!e.isIntersecting) return;
      e.target.style.setProperty('--d', (n++ * .32) + 's');
      e.target.classList.add('in');
      io.unobserve(e.target);
    });
  }, { threshold: .5 });
  steps.forEach(function (li) { io.observe(li); });
})();
// By the numbers: each figure counts up from zero as it scrolls into view. The page source keeps the final
// values (build_cv.py and update_scholar.py edit them there); screen readers read them from a hidden copy.
(function () {
  if (!('IntersectionObserver' in window) || matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  var counters = [];
  document.querySelectorAll('.stat b').forEach(function (b) {
    var text = b.textContent, m = /^(\D*)([\d,]+(?:\.\d+)?)(\D*)$/.exec(text);
    if (!m) return;  // not a single number (the award's year range)
    var dec = (m[2].split('.')[1] || '').length, to = parseFloat(m[2].replace(/,/g, '')),
        fmt = { minimumFractionDigits: dec, maximumFractionDigits: dec, useGrouping: m[2].indexOf(',') >= 0 },
        sr = document.createElement('span'), shown = document.createElement('span');
    sr.className = 'sr-only'; sr.textContent = text;
    shown.setAttribute('aria-hidden', 'true');
    b.textContent = ''; b.append(sr, shown);
    b.parentNode.dataset.count = counters.length;
    counters.push(function (f) { shown.textContent = f < 1 ? m[1] + (to * f).toLocaleString('en-US', fmt) + m[3] : text; });
    counters[counters.length - 1](0);
  });
  function run(set, delay) {
    var t0 = performance.now() + delay;
    requestAnimationFrame(function step(now) {
      var t = Math.min(Math.max((now - t0) / 1200, 0), 1);
      set(1 - Math.pow(1 - t, 3));  // ease out: fast at first, settling on the value
      if (t < 1) requestAnimationFrame(step);
    });
  }
  var io = new IntersectionObserver(function (es) {
    var n = 0;
    es.forEach(function (e) {
      if (!e.isIntersecting) return;
      io.unobserve(e.target);
      run(counters[e.target.dataset.count], n++ * 80);
    });
  }, { threshold: .5 });
  document.querySelectorAll('.stat[data-count]').forEach(function (s) { io.observe(s); });
  window.addEventListener('beforeprint', function () { io.disconnect(); counters.forEach(function (set) { set(1); }); });
})();

// Research banner: AI at the center of a small universe. The research areas orbit as planets (depth-sorted,
// lit by the core) and send data packets inward; one area at a time is featured, or the one under the pointer.
(function () {
  var fig = document.getElementById('sky'); if (!fig) return;
  var cv = fig.querySelector('canvas'), ctx = cv.getContext('2d'), still = matchMedia('(prefers-reduced-motion: reduce)');
  var AREAS = [
    { name: 'Communications', sub: 'RF · mmWave · THz · optical', c: 'comms', f: .42, w: .32, a0: 0 },
    { name: 'Sensing', sub: 'vital signs · gestures · radar', c: 'sense', f: .6, w: .22, a0: 2.1 },
    { name: 'Internet of Things', sub: 'livestock · soil · LoRa', c: 'iot', f: .78, w: .16, a0: 4.0 },
    { name: 'Space links', sub: 'satellites · lunar RF/optical', c: 'moon', f: .96, w: .11, a0: 5.4 }
  ];
  var S = {}, W, H, small, stars = [], disk = [], pk = [], waves = [], sph = [], edges = [], flash = 0, feat = 0, featT = 0, tiltS = .5, phiS = 0, ptr = null, t = 0, last = 0, run = false, raf = 0;

  function rgb(c) { var s = document.createElement('span'); s.style.color = c; document.body.appendChild(s); var v = getComputedStyle(s).color.match(/[\d.]+/g); s.remove(); return v.slice(0, 3).map(Number); }
  function colors() { var cs = getComputedStyle(document.documentElement); ['bg', 'gold', 'text', 'muted', 'comms', 'sense', 'iot', 'moon'].forEach(function (n) { S[n] = rgb(cs.getPropertyValue('--sky-' + n).trim()); }); }
  function sc(n, a) { var c = S[n]; return 'rgba(' + c[0] + ',' + c[1] + ',' + c[2] + ',' + (a == null ? 1 : a) + ')'; }
  function font(w, px) { return w + ' ' + px + 'px Inter, system-ui, sans-serif'; }
  function dust(r) { return { a: Math.random() * 6.283, r: .16 + .5 * r, c: ['comms', 'sense', 'iot', 'moon', 'gold'][Math.random() * 5 | 0] }; }

  function layout() {
    var r = cv.getBoundingClientRect(), dpr = Math.min(devicePixelRatio || 1, 2);
    W = r.width; H = r.height; small = W < 560; cv.width = Math.round(W * dpr); cv.height = Math.round(H * dpr); ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    stars = []; for (var i = 0; i < 220; i++) stars.push({ x: Math.random(), y: Math.random(), z: Math.random(), tw: Math.random() * 6 });
    disk = []; for (i = 0; i < 300; i++) disk.push(dust(Math.random()));
  }
  // points on a sphere for the AI core, joined to their near neighbours
  (function () { var n = 46; for (var i = 0; i < n; i++) { var y = 1 - 2 * (i + .5) / n, r = Math.sqrt(1 - y * y), th = i * 2.39996; sph.push([Math.cos(th) * r, y, Math.sin(th) * r]); }
    for (i = 0; i < n; i++) for (var j = i + 1; j < n; j++) { var dx = sph[i][0] - sph[j][0], dy = sph[i][1] - sph[j][1], dz = sph[i][2] - sph[j][2]; if (dx * dx + dy * dy + dz * dz < .3) edges.push([i, j]); } })();

  function spark(x, y, R, rot) { var k = R * .14; ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.beginPath(); ctx.moveTo(0, -R); ctx.bezierCurveTo(k, -k, k, -k, R, 0); ctx.bezierCurveTo(k, k, k, k, 0, R); ctx.bezierCurveTo(-k, k, -k, k, -R, 0); ctx.bezierCurveTo(-k, -k, -k, -k, 0, -R); ctx.fill(); ctx.restore(); }
  function halo(x, y, r, c, a) { var g = ctx.createRadialGradient(x, y, r * .9, x, y, r * 1.6); g.addColorStop(0, sc(c, a)); g.addColorStop(1, sc(c, 0)); ctx.fillStyle = g; ctx.beginPath(); ctx.arc(x, y, r * 1.6, 0, 6.283); ctx.fill(); }
  function pill(text, x, y, px, color, w) { ctx.font = font(w || 600, px); var tw = ctx.measureText(text).width, h = px + 9, x0 = x - tw / 2 - 8; ctx.fillStyle = sc('bg', .7); ctx.beginPath(); ctx.roundRect(x0, y - h / 2, tw + 16, h, h / 2); ctx.fill(); ctx.fillStyle = color; ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; ctx.fillText(text, x0 + 8, y + .5); }
  function tag(i, x, y, on) {
    var px = small ? 9 : 11; ctx.font = font(600, px); var tw = ctx.measureText(AREAS[i].name).width, h = px + 10, w = tw + 26, x0 = x - w / 2;
    ctx.fillStyle = sc('bg', .72); ctx.beginPath(); ctx.roundRect(x0, y - h / 2, w, h, h / 2); ctx.fill(); if (on) { ctx.strokeStyle = sc('gold', .7); ctx.lineWidth = 1; ctx.stroke(); }
    ctx.fillStyle = sc(AREAS[i].c === 'moon' ? 'muted' : AREAS[i].c); ctx.beginPath(); ctx.arc(x0 + 10, y, 3.2, 0, 6.283); ctx.fill();
    ctx.fillStyle = on ? sc('gold') : sc('text', .8); ctx.textAlign = 'left'; ctx.textBaseline = 'middle'; ctx.fillText(AREAS[i].name, x0 + 18, y + .5);
    if (on && !small) pill(AREAS[i].sub, x, y + h / 2 + 11, 10, sc('text', .72), 500);
  }
  function ball(i, x, y, r, lx, ly, dim) {   // shaded planet, lit from the core, with its area symbol
    var base = S[AREAS[i].c], lite = 'rgb(' + base.map(function (v) { return Math.round(v + (255 - v) * .45); }).join(',') + ')', g = ctx.createRadialGradient(x - r * .4, y - r * .45, r * .1, x, y, r);
    g.addColorStop(0, lite); g.addColorStop(1, 'rgb(' + base.join(',') + ')'); ctx.globalAlpha = dim; ctx.fillStyle = g; ctx.beginPath(); ctx.arc(x, y, r, 0, 6.283); ctx.fill();
    var ang = Math.atan2(ly - y, lx - x); ctx.fillStyle = 'rgba(0,0,0,.28)'; ctx.beginPath(); ctx.arc(x, y, r, ang + Math.PI / 2, ang + Math.PI * 1.5); ctx.ellipse(x, y, r * .45, r, ang, Math.PI * 1.5, Math.PI / 2, true); ctx.fill();
    ctx.strokeStyle = sc('text', .9); ctx.fillStyle = sc('text', .9); ctx.lineWidth = Math.max(1.2, r * .1); ctx.lineCap = 'round'; ctx.lineJoin = 'round'; var u = r * .5;
    if (i === 0) { [.45, .8].forEach(function (k) { ctx.beginPath(); ctx.arc(x - u * .6, y + u * .6, u * 1.6 * k, -1.35, -.2); ctx.stroke(); }); ctx.beginPath(); ctx.arc(x - u * .6, y + u * .6, r * .1, 0, 6.283); ctx.fill(); }
    if (i === 1) { ctx.beginPath(); ctx.moveTo(x - u * 1.3, y); ctx.lineTo(x - u * .5, y); ctx.lineTo(x - u * .2, y - u * .9); ctx.lineTo(x + u * .25, y + u * .8); ctx.lineTo(x + u * .55, y); ctx.lineTo(x + u * 1.3, y); ctx.stroke(); }
    if (i === 2) { var nn = [[-.8, .5], [.8, .5], [0, -.8]]; ctx.beginPath(); nn.forEach(function (a, k) { var b = nn[(k + 1) % 3]; ctx.moveTo(x + a[0] * u, y + a[1] * u); ctx.lineTo(x + b[0] * u, y + b[1] * u); }); ctx.stroke(); nn.forEach(function (a) { ctx.beginPath(); ctx.arc(x + a[0] * u, y + a[1] * u, r * .14, 0, 6.283); ctx.fill(); }); }
    if (i === 3) { ctx.fillStyle = 'rgba(0,0,0,.18)'; [[-.35, -.3, .28], [.4, .2, .2], [-.1, .5, .14]].forEach(function (c) { ctx.beginPath(); ctx.arc(x + c[0] * r, y + c[1] * r, c[2] * r, 0, 6.283); ctx.fill(); }); }
    ctx.globalAlpha = 1;
  }
  function sat(x, y, s, a) { ctx.fillStyle = sc('gold', a); ctx.fillRect(x - 11 * s, y - 2 * s, 8 * s, 4 * s); ctx.fillRect(x + 3 * s, y - 2 * s, 8 * s, 4 * s); ctx.fillStyle = sc('text', a); ctx.fillRect(x - 3 * s, y - 3 * s, 6 * s, 6 * s); }

  function frame(now) {
    var dt = Math.min(.05, (now - (last || now)) / 1000); last = now; t += dt; draw(dt);
    if (run) raf = requestAnimationFrame(frame);
  }
  function draw(dt) {
    var cx = W / 2, cy = H / 2 + 4, px = ptr ? ptr.x / W - .5 : 0, py = ptr ? ptr.y / H - .5 : 0;
    var RX = Math.min(W / 2 - (small ? 26 : 60), H * 1.3), base = Math.min(.8, Math.max(.36, H * .4 / RX)), e = Math.min(1, dt * 3);
    tiltS += (base + py * .2 - tiltS) * e; phiS += (px * .5 - phiS) * e;
    var tilt = tiltS, R0 = Math.min(H * .12, 48);
    // night sky
    ctx.fillStyle = sc('bg'); ctx.fillRect(0, 0, W, H);
    [[.25, .35, 'comms'], [.75, .62, 'sense'], [.5, .5, 'gold']].forEach(function (nb) { var g = ctx.createRadialGradient(W * nb[0], H * nb[1], 0, W * nb[0], H * nb[1], H * .9); g.addColorStop(0, sc(nb[2], .15)); g.addColorStop(1, sc(nb[2], 0)); ctx.fillStyle = g; ctx.fillRect(0, 0, W, H); });
    stars.forEach(function (s) { var x = (s.x * W - px * 30 * s.z + W) % W, y = (s.y * H - py * 20 * s.z + H) % H, k = s.z > .8 ? 1.8 : 1.1; ctx.fillStyle = sc('text', .25 + .6 * s.z * (.6 + .4 * Math.sin(t * 2 + s.tw))); ctx.fillRect(x, y, k, k); });
    // planets
    var pl = AREAS.map(function (p, i) { var a = p.a0 + t * p.w + phiS, rx = RX * p.f, ry = rx * tilt, z = Math.sin(a), k = .8 + .35 * (z + 1) / 2; return { i: i, a: a, x: cx + Math.cos(a) * rx, y: cy + Math.sin(a) * ry, z: z, rx: rx, ry: ry, k: k, r: (small ? 13 : 21) * k }; });
    var hov = -1; if (ptr) pl.forEach(function (q) { if (Math.hypot(ptr.x - q.x, ptr.y - q.y) < q.r + 10) hov = q.i; });
    featT += dt; if (hov >= 0) { feat = hov; featT = 0; } else if (featT > 3.4) { featT = 0; feat = (feat + 1) % 4; }
    // orbits and comet trails
    pl.forEach(function (q) {
      ctx.strokeStyle = sc(q.i === feat ? 'gold' : 'text', q.i === feat ? .32 : .1); ctx.lineWidth = 1; ctx.beginPath(); ctx.ellipse(cx, cy, q.rx, q.ry, 0, 0, 6.283); ctx.stroke();
      for (var s = 0; s < 22; s++) { var a0 = q.a - (s + 1) * .045, a1 = q.a - s * .045, f = 1 - s / 22; ctx.strokeStyle = sc(AREAS[q.i].c === 'moon' ? 'muted' : AREAS[q.i].c, .55 * f * q.k); ctx.lineWidth = 3 * f * q.k + .5; ctx.beginPath(); ctx.moveTo(cx + Math.cos(a0) * q.rx, cy + Math.sin(a0) * q.ry); ctx.lineTo(cx + Math.cos(a1) * q.rx, cy + Math.sin(a1) * q.ry); ctx.stroke(); }
    });
    // dust disk spiralling into the core
    disk.forEach(function (p) { p.a += dt * (.5 / p.r); p.r -= dt * .02; if (p.r < .14) { var n = dust(1); p.a = n.a; p.r = n.r; p.c = n.c; } });
    function drawDust(front) { disk.forEach(function (p) { if ((Math.sin(p.a) >= 0) !== front) return; var rx = RX * .42 * p.r * 1.6; ctx.fillStyle = sc(p.c, .25 + .5 * (1 - p.r)); ctx.fillRect(cx + Math.cos(p.a) * rx - .8, cy + Math.sin(p.a) * rx * tilt - .8, 1.6, 1.6); }); }
    // data packets with comet tails
    if (dt && Math.random() < dt * 3) pk.push({ i: Math.random() < .5 ? feat : Math.random() * 4 | 0, s: 0, bend: (Math.random() - .5) * .8 });
    function at(p, s) { var q = pl[p.i], mx = (q.x + cx) / 2 - (q.y - cy) * p.bend, my = (q.y + cy) / 2 + (q.x - cx) * p.bend * tilt; return { x: (1 - s) * (1 - s) * q.x + 2 * (1 - s) * s * mx + s * s * cx, y: (1 - s) * (1 - s) * q.y + 2 * (1 - s) * s * my + s * s * cy }; }
    function drawPk(front) { pk.forEach(function (p) { if ((pl[p.i].z * (1 - p.s) >= 0) !== front) return; var c = AREAS[p.i].c === 'moon' ? 'gold' : AREAS[p.i].c;
      for (var k = 7; k >= 0; k--) { var q = at(p, Math.max(0, p.s - k * .025)); ctx.fillStyle = sc(k ? 'gold' : c, k ? .5 * (1 - k / 8) : 1); ctx.beginPath(); ctx.arc(q.x, q.y, k ? 2.2 * (1 - k / 9) : 2.6, 0, 6.283); ctx.fill(); } }); }
    pk = pk.filter(function (p) { p.s += dt / 1.6; if (p.s >= 1) { flash = Math.min(1, flash + .5); if (Math.random() < .3) waves.push(0); return false; } return true; });
    function planet(q) {
      var on = q.i === feat, r = q.r * (on ? 1.12 : 1), dim = .55 + .45 * (q.z + 1) / 2, c = AREAS[q.i].c, k;
      if (on) halo(q.x, q.y, r * 1.5, 'gold', .3);
      halo(q.x, q.y, r, c === 'moon' ? 'text' : c, .35 * dim);
      var rr = r * 1.9; if (q.i === 3) { ctx.strokeStyle = sc('muted', .75 * dim); ctx.lineWidth = Math.max(1.5, r * .16); ctx.beginPath(); ctx.ellipse(q.x, q.y, rr, rr * .32, -.35, Math.PI, 2 * Math.PI); ctx.stroke(); }
      ball(q.i, q.x, q.y, r, cx, cy, dim);
      if (q.i === 3) { ctx.strokeStyle = sc('muted', .85 * dim); ctx.beginPath(); ctx.ellipse(q.x, q.y, rr, rr * .32, -.35, 0, Math.PI); ctx.stroke(); }
      if (q.i === 0) { var ma = t * 2, mx = q.x + Math.cos(ma) * r * 1.9, my = q.y + Math.sin(ma) * r * .8; sat(mx, my, .55 * q.k, dim); for (k = 0; k < 4; k++) { var uu = (t * 1.5 + k / 4) % 1; ctx.fillStyle = sc('gold', dim); ctx.beginPath(); ctx.arc(q.x + (mx - q.x) * uu, q.y + (my - q.y) * uu, 1.2, 0, 6.283); ctx.fill(); } }
      if (q.i === 1) { var hb = (t * 1.2) % 1; ctx.strokeStyle = sc('sense', (1 - hb) * .8 * dim); ctx.lineWidth = 1.5; ctx.beginPath(); ctx.arc(q.x, q.y, r + 3 + hb * 14, 0, 6.283); ctx.stroke(); }
      if (q.i === 2) { for (k = 0; k < 3; k++) { var a2 = t * 1.6 + k * 2.094; ctx.fillStyle = sc('gold', dim); ctx.beginPath(); ctx.arc(q.x + Math.cos(a2) * r * 1.6, q.y + Math.sin(a2) * r * .6, 1.8, 0, 6.283); ctx.fill(); } }
      q.rr = r;
    }
    pl.filter(function (q) { return q.z < 0; }).forEach(planet); drawPk(false); drawDust(false);
    // the AI core: light rays, glow, and a rotating neural sphere
    flash = Math.max(0, flash - dt * 1.5);
    for (var i = 0; i < 14; i++) { var a = i / 14 * 6.283 + t * .08, L = R0 * (1.9 + .5 * Math.sin(t * 1.3 + i * 2.1)) * (1 + .3 * flash), g = ctx.createLinearGradient(cx, cy, cx + Math.cos(a) * L, cy + Math.sin(a) * L);
      g.addColorStop(0, sc('gold', .32)); g.addColorStop(1, sc('gold', 0)); ctx.strokeStyle = g; ctx.lineWidth = 2.2 - (i % 2); ctx.beginPath(); ctx.moveTo(cx + Math.cos(a) * R0 * .7, cy + Math.sin(a) * R0 * .7); ctx.lineTo(cx + Math.cos(a) * L, cy + Math.sin(a) * L); ctx.stroke(); }
    waves = waves.filter(function (w) { return w < 1; }).map(function (w) { w += dt * .45; var rw = R0 + w * RX * .9; ctx.strokeStyle = sc('gold', .45 * (1 - w)); ctx.lineWidth = 1.5; ctx.beginPath(); ctx.ellipse(cx, cy, rw, rw * tilt, 0, 0, 6.283); ctx.stroke(); return w; });
    var gl = ctx.createRadialGradient(cx, cy, 0, cx, cy, R0 * 3.2); gl.addColorStop(0, sc('gold', .55 + .25 * flash)); gl.addColorStop(.35, sc('gold', .18)); gl.addColorStop(1, sc('gold', 0)); ctx.fillStyle = gl; ctx.beginPath(); ctx.arc(cx, cy, R0 * 3.2, 0, 6.283); ctx.fill();
    var ry = t * .45, rx = .35, pr = sph.map(function (p) { var x = p[0] * Math.cos(ry) + p[2] * Math.sin(ry), z = -p[0] * Math.sin(ry) + p[2] * Math.cos(ry), y = p[1] * Math.cos(rx) - z * Math.sin(rx); z = p[1] * Math.sin(rx) + z * Math.cos(rx); return { x: cx + x * R0, y: cy + y * R0, z: z }; });
    ctx.lineWidth = 1; edges.forEach(function (e) { var p = pr[e[0]], q = pr[e[1]]; ctx.strokeStyle = sc('gold', .12 + .35 * ((p.z + q.z) / 2 + 1) / 2 + .2 * flash); ctx.beginPath(); ctx.moveTo(p.x, p.y); ctx.lineTo(q.x, q.y); ctx.stroke(); });
    pr.forEach(function (p, i) { var lit = Math.sin(t * 3 + i * 1.7) > .85; ctx.fillStyle = lit ? sc('text', .95) : sc('gold', .35 + .6 * (p.z + 1) / 2); ctx.beginPath(); ctx.arc(p.x, p.y, (lit ? 2.2 : 1.1) + .9 * (p.z + 1) / 2, 0, 6.283); ctx.fill(); });
    ctx.fillStyle = sc('gold'); spark(cx, cy, 6 + 3 * flash, t * .6);
    var fq = pl[feat]; ctx.strokeStyle = sc('gold', .35); ctx.lineWidth = 1; ctx.setLineDash([2, 4]); ctx.beginPath(); ctx.moveTo(cx, cy); ctx.lineTo(fq.x, fq.y); ctx.stroke(); ctx.setLineDash([]);
    drawDust(true); drawPk(true); pl.filter(function (q) { return q.z >= 0; }).forEach(planet);
    pl.forEach(function (q) { tag(q.i, q.x, Math.min(H - 12, q.y + q.rr + (q.i === 3 ? 16 : 14)), q.i === feat); });
    pill('AI', cx, cy + R0 + 16, small ? 11 : 13, sc('gold'));
  }

  function pos(e) { var r = cv.getBoundingClientRect(); return { x: e.clientX - r.left, y: e.clientY - r.top }; }
  cv.addEventListener('pointermove', function (e) { if (e.pointerType === 'mouse') ptr = pos(e); });
  cv.addEventListener('pointerdown', function (e) { ptr = pos(e); if (!run) draw(0); });
  cv.addEventListener('pointerleave', function (e) { if (e.pointerType === 'mouse') ptr = null; });
  function start() { if (run || still.matches) return; run = true; last = 0; raf = requestAnimationFrame(frame); }
  function stop() { run = false; cancelAnimationFrame(raf); }
  colors(); layout(); t = 2; for (var k = 0; k < 40; k++) draw(.05);   // settle into a finished first frame
  new IntersectionObserver(function (es) { es[0].isIntersecting ? start() : stop(); }).observe(cv);
  document.addEventListener('visibilitychange', function () { document.hidden ? stop() : start(); });
  var rz; addEventListener('resize', function () { clearTimeout(rz); rz = setTimeout(function () { layout(); if (!run) draw(0); }, 150); });
  still.addEventListener('change', function () { still.matches ? stop() : start(); });
})();
