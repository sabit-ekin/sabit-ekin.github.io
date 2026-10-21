import sys, os, math
out = sys.argv[1]
W, H = 400, 300
CSS = """
.ink{stroke:#2e2925;fill:none;stroke-width:2.4;stroke-linecap:round;stroke-linejoin:round}
.ink1{stroke:#2e2925;fill:none;stroke-width:1.4;stroke-linecap:round;stroke-linejoin:round}
.inkf{fill:#2e2925}.mute{stroke:#c4b8ac;fill:none;stroke-width:1.4;stroke-linecap:round}
.mutef{fill:#d9cec3}.soft{fill:#ebe1d6}.paper{fill:#fffdfb}.acc{stroke:#7a1414;fill:none;stroke-width:2.4;stroke-linecap:round;stroke-linejoin:round}
.accf{fill:#7a1414}.acc2f{fill:#a63c3c}.gold{stroke:#d39a2c;fill:none;stroke-width:2.4;stroke-linecap:round;stroke-linejoin:round}.goldf{fill:#d39a2c}
.teal{stroke:#2f6f86;fill:none;stroke-width:2.4;stroke-linecap:round;stroke-linejoin:round}.tealf{fill:#2f6f86}.tealsoft{fill:#d3e4ea}
.sagef{fill:#a9bf98}.sagesoft{fill:#e2ead8}.sage{stroke:#6f8a5e;fill:none;stroke-width:1.6;stroke-linecap:round}
.dash{stroke-dasharray:6 6}.dots{stroke-dasharray:1 6}
.lbl{font:700 10.5px Inter,system-ui,sans-serif;fill:#5a514a;letter-spacing:.06em}
.chip{fill:#fffdfb;stroke:#d9cec3;stroke-width:1}
.s-bg1{stop-color:#fbf7f2}.s-bg2{stop-color:#eee4d9}.s-gold{stop-color:#d39a2c}.s-acc{stop-color:#7a1414}.s-acc2{stop-color:#b04848}
.s-teal{stop-color:#2f6f86}.s-teal2{stop-color:#8fc2d3}.s-moon1{stop-color:#f4efe9}.s-moon2{stop-color:#bdb2a7}
.s-sky1{stop-color:#e7eff1}.s-sky2{stop-color:#f8f2ea}.s-sage1{stop-color:#c4d4b4}.s-sage2{stop-color:#93ab80}
.s-soil1{stop-color:#c9ae92}.s-soil2{stop-color:#a88a6c}.s-metal1{stop-color:#8f2626}.s-metal2{stop-color:#5c0c0c}
.s-wall1{stop-color:#f7f1ea}.s-wall2{stop-color:#ebe0d4}
@media (prefers-color-scheme:dark){
.ink,.ink1{stroke:#ece5de}.inkf{fill:#ece5de}.mute{stroke:#5d544c}.mutef{fill:#4a413a}.soft{fill:#342c27}.paper{fill:#2f2723}
.acc{stroke:#e99a9a}.accf{fill:#e08b8b}.acc2f{fill:#b86464}.gold{stroke:#ecc062}.goldf{fill:#ecc062}.teal{stroke:#86c6da}.tealf{fill:#86c6da}.tealsoft{fill:#1f3b45}
.sagef{fill:#4f6a46}.sagesoft{fill:#27331f}.sage{stroke:#86a476}.lbl{fill:#b3a99f}.chip{fill:#2f2723;stroke:#4a413a}
.s-bg1{stop-color:#2a231f}.s-bg2{stop-color:#1c1714}.s-gold{stop-color:#ecc062}.s-acc{stop-color:#e08b8b}.s-acc2{stop-color:#c46e6e}
.s-teal{stop-color:#3d8aa3}.s-teal2{stop-color:#1f4654}.s-moon1{stop-color:#6b625a}.s-moon2{stop-color:#3b342f}
.s-sky1{stop-color:#1d2a30}.s-sky2{stop-color:#2a231f}.s-sage1{stop-color:#3e5537}.s-sage2{stop-color:#2b3c26}
.s-soil1{stop-color:#5a4838}.s-soil2{stop-color:#3f3226}.s-metal1{stop-color:#d27b7b}.s-metal2{stop-color:#9e4a4a}
.s-wall1{stop-color:#2f2723}.s-wall2{stop-color:#241e1a}}
"""
DEFS = """
<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop class="s-bg1" offset="0"/><stop class="s-bg2" offset="1"/></linearGradient>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop class="s-sky1" offset="0"/><stop class="s-sky2" offset="1"/></linearGradient>
<linearGradient id="wall" x1="0" y1="0" x2="0" y2="1"><stop class="s-wall1" offset="0"/><stop class="s-wall2" offset="1"/></linearGradient>
<linearGradient id="metal" x1="0" y1="0" x2="0" y2="1"><stop class="s-metal1" offset="0"/><stop class="s-metal2" offset="1"/></linearGradient>
<linearGradient id="sage" x1="0" y1="0" x2="0" y2="1"><stop class="s-sage1" offset="0"/><stop class="s-sage2" offset="1"/></linearGradient>
<linearGradient id="soil" x1="0" y1="0" x2="0" y2="1"><stop class="s-soil1" offset="0"/><stop class="s-soil2" offset="1"/></linearGradient>
<linearGradient id="beamG" x1="0" y1="0" x2="1" y2="0"><stop class="s-gold" offset="0" stop-opacity=".55"/><stop class="s-gold" offset="1" stop-opacity=".05"/></linearGradient>
<linearGradient id="beamGv" x1="0" y1="0" x2="0" y2="1"><stop class="s-gold" offset="0" stop-opacity=".5"/><stop class="s-gold" offset="1" stop-opacity=".04"/></linearGradient>
<linearGradient id="beamA" x1="0" y1="0" x2="1" y2="0"><stop class="s-acc2" offset="0" stop-opacity=".75"/><stop class="s-acc2" offset="1" stop-opacity=".18"/></linearGradient>
<linearGradient id="beamT" x1="0" y1="0" x2="1" y2="0"><stop class="s-teal" offset="0" stop-opacity=".45"/><stop class="s-teal" offset="1" stop-opacity=".06"/></linearGradient>
<radialGradient id="earth" cx=".35" cy=".3" r=".8"><stop class="s-teal2" offset="0"/><stop class="s-teal" offset="1"/></radialGradient>
<radialGradient id="moon" cx=".35" cy=".3" r=".8"><stop class="s-moon1" offset="0"/><stop class="s-moon2" offset="1"/></radialGradient>
<radialGradient id="glowG"><stop class="s-gold" offset="0" stop-opacity=".55"/><stop class="s-gold" offset="1" stop-opacity="0"/></radialGradient>
<radialGradient id="glowA"><stop class="s-acc2" offset="0" stop-opacity=".35"/><stop class="s-acc2" offset="1" stop-opacity="0"/></radialGradient>
<radialGradient id="glowT"><stop class="s-teal" offset="0" stop-opacity=".28"/><stop class="s-teal" offset="1" stop-opacity="0"/></radialGradient>
<filter id="sh" x="-20%" y="-20%" width="140%" height="160%"><feDropShadow dx="0" dy="2.5" stdDeviation="2.5" flood-color="#000" flood-opacity=".18"/></filter>
<pattern id="dotgrid" width="16" height="16" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r=".9" class="mutef"/></pattern>
"""
def svg(name, title, body, bg='url(#bg)'):
    # figures with a 3D render in tools/renders/ are built by render_figures.py instead
    if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'renders', name + '.webp')):
        return
    s = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t"><title id="t">{title}</title>'
         f'<style>{CSS}</style><defs>{DEFS}</defs><rect width="{W}" height="{H}" fill="{bg}"/>{body}</svg>')
    open(os.path.join(out, name + '.svg'), 'w').write(s)

def chip(x, y, text, anchor='start'):
    w = 7.2 * len(text) + 16
    x0 = x if anchor == 'start' else (x - w if anchor == 'end' else x - w/2)
    return (f'<g filter="url(#sh)"><rect class="chip" x="{x0:.1f}" y="{y-10}" width="{w:.1f}" height="20" rx="10"/></g>'
            f'<text class="lbl" x="{x0+w/2:.1f}" y="{y+3.6}" text-anchor="middle">{text}</text>')

def rings(x, y, n, r0, dr, a0, a1, cls='gold', fade=True):
    o = ''
    for i in range(n):
        r = r0 + i*dr
        p0 = (x + r*math.cos(math.radians(a0)), y + r*math.sin(math.radians(a0)))
        p1 = (x + r*math.cos(math.radians(a1)), y + r*math.sin(math.radians(a1)))
        op = 1 - i/(n+0.5) if fade else 1
        o += f'<path class="{cls}" opacity="{op:.2f}" d="M{p0[0]:.1f} {p0[1]:.1f} A{r} {r} 0 0 1 {p1[0]:.1f} {p1[1]:.1f}"/>'
    return o

def taper(x0, y0, x1, y1, w0, w1, fill):
    dx, dy = x1-x0, y1-y0; L = math.hypot(dx, dy); nx, ny = -dy/L, dx/L
    pts = [(x0+nx*w0/2, y0+ny*w0/2), (x1+nx*w1/2, y1+ny*w1/2), (x1-nx*w1/2, y1-ny*w1/2), (x0-nx*w0/2, y0-ny*w0/2)]
    return '<polygon fill="%s" points="%s"/>' % (fill, ' '.join(f'{a:.1f},{b:.1f}' for a, b in pts))

def ticks(x0, y0, x1, y1, n, size, cls='acc', op=.8):
    dx, dy = x1-x0, y1-y0; L = math.hypot(dx, dy); nx, ny = -dy/L, dx/L; o = ''
    for i in range(1, n+1):
        t = i/(n+1); cx, cy = x0+dx*t, y0+dy*t; s = size*(0.6+0.6*t)
        o += f'<path class="{cls}" stroke-width="1.6" opacity="{op}" d="M{cx-nx*s:.1f} {cy-ny*s:.1f} Q{cx+dx/L*3:.1f} {cy+dy/L*3:.1f} {cx+nx*s:.1f} {cy+ny*s:.1f}"/>'
    return o

def person(x, y, s=1.0, shirt='url(#metal)', pose='stand'):
    # front-facing person, feet at y
    k = s
    o = f'<g filter="url(#sh)">'
    o += f'<path fill="{shirt}" d="M{x-17*k} {y-34*k} q0 -22 17 -24 q17 2 17 24 v10 h-34 z"/>'
    if pose == 'stand':
        o += f'<rect class="inkf" x="{x-12*k}" y="{y-25*k}" width="9*k" height="25" rx="3"/>'.replace('9*k', f'{9*k}').replace('height="25"', f'height="{25*k}"')
        o += f'<rect class="inkf" x="{x+3*k}" y="{y-25*k}" width="{9*k}" height="{25*k}" rx="3"/>'
    o += f'<circle fill="#e7c3a3" cx="{x}" cy="{y-68*k}" r="{11*k}"/>'
    o += f'<path class="inkf" d="M{x-11*k} {y-70*k} q2 -13 11 -12 q10 -1 11 12 q-6 -6 -11 -5 q-6 -1 -11 5 z"/>'
    o += '</g>'
    return o

# ---------- 1. CommAwareNet ----------
b = '<rect x="0" y="0" width="400" height="214" fill="url(#wall)"/>'
b += '<polygon class="soft" points="0,214 400,214 400,300 0,300"/>'
for i in range(0, 420, 40): b += f'<path class="mute" d="M{200+(i-200)*0.55:.0f} 214 L{i} 300"/>'
b += '<path class="mute" d="M0 240 H400 M0 268 H400"/><path class="ink1" d="M0 214 H400"/><rect class="mutef" x="0" y="0" width="400" height="14"/>'
# window
b += '<rect class="paper" x="150" y="48" width="70" height="56" rx="3"/><rect fill="url(#sky)" x="154" y="52" width="62" height="48"/><path class="ink1" d="M150 48 h70 v56 h-70 z M185 48 v56 M150 76 h70"/>'
# luminaire
b += '<rect fill="url(#glowG)" x="20" y="0" width="150" height="70"/>'
b += '<polygon fill="url(#beamGv)" points="70,26 120,26 170,214 20,214"/>'
b += '<g filter="url(#sh)"><rect fill="url(#metal)" x="64" y="14" width="62" height="14" rx="4"/></g>'
for i in range(5): b += f'<circle class="goldf" cx="{72+i*11.5:.1f}" cy="30" r="2.6"/>'
# desk + laptop + person 1
b += '<g filter="url(#sh)"><rect class="paper" x="44" y="186" width="96" height="8" rx="2"/><path class="ink1" d="M52 194 v40 M132 194 v40"/></g>'
b += '<path class="inkf" d="M98 186 l10 -22 h26 l-6 22 z"/><rect class="goldf" x="110" y="168" width="18" height="12" rx="1" opacity=".8"/>'
b += person(76, 236, 0.85)
# RIS panel
b += '<g filter="url(#sh)"><rect class="paper" x="300" y="40" width="80" height="120" rx="6"/></g>'
for r in range(6):
    for c in range(4):
        op = 0.25 + 0.75*((r + c*2) % 5)/4
        b += f'<rect class="accf" opacity="{op:.2f}" x="{306+c*18.5:.1f}" y="{46+r*18.8:.1f}" width="15" height="15.5" rx="2.5"/>'
b += '<rect class="ink1" x="300" y="40" width="80" height="120" rx="6"/>'
# THz beams
b += taper(126, 24, 302, 84, 4, 22, 'url(#beamA)') + ticks(126, 24, 302, 84, 6, 9)
b += taper(302, 112, 236, 186, 18, 6, 'url(#beamA)') + ticks(302, 112, 236, 186, 3, 8)
b += '<circle class="accf" cx="236" cy="186" r="3.5"/>'
b += person(240, 260, 1.0)
b += '<rect class="inkf" x="252" y="190" width="9" height="15" rx="2"/>'
b += chip(20, 64, 'VISIBLE LIGHT') + chip(196, 32, 'THz BEAM') + chip(386, 176, 'SMART SURFACE', 'end')
svg('commawarenet', 'Hybrid terahertz and visible-light network in a smart room: a ceiling luminaire lights a desk user while its terahertz beam is redirected by a smart surface to a second user', b)

# ---------- 2. SpiderNET ----------
b = '<rect width="400" height="300" fill="url(#dotgrid)" opacity=".7"/>'
# city blocks
for (x, y, w, h) in [(14,18,70,46),(100,14,56,40),(238,20,64,40),(318,16,68,52),(16,236,60,48),(96,250,70,36),(250,244,56,42),(322,226,64,58),(16,118,44,64),(346,112,44,70)]:
    b += f'<rect class="soft" x="{x}" y="{y}" width="{w}" height="{h}" rx="4"/>'
b += '<path class="mute" d="M0 92 H400 M0 214 H400 M92 0 V300 M308 0 V300" stroke-width="7" opacity=".45"/>'
nodes = {'c':(200,150),'a':(118,98),'b':(282,96),'d':(120,206),'e':(286,204),'f':(200,62),'g':(200,246),'h':(56,150),'i':(344,150)}
active = {'c','a','e','g','i'}
# web
edges = [('c',k) for k in nodes if k!='c'] + [('a','f'),('f','b'),('b','i'),('i','e'),('e','g'),('g','d'),('d','h'),('h','a')]
for u,v in edges:
    (x0,y0),(x1,y1) = nodes[u],nodes[v]
    on = u in active and v in active
    da = '' if on else 'stroke-dasharray="4 5"'
    b += f'<path class="{"acc" if on else "mute"}" stroke-width="{2 if on else 1.3}" {da} d="M{x0} {y0} L{x1} {y1}"/>'
for k,(x,y) in nodes.items():
    if k in active:
        r = 50 if k=='c' else 38
        b += f'<circle fill="url(#glowA)" cx="{x}" cy="{y}" r="{r}"/>'
users = [(96,82),(134,118),(108,112),(300,214),(272,222),(296,190),(190,262),(214,266),(356,138),(338,168),(182,138),(222,164)]
for (x,y) in users:
    b += f'<g filter="url(#sh)"><rect class="paper" x="{x-4}" y="{y-6}" width="8" height="12" rx="2"/></g><rect class="goldf" x="{x-2.6}" y="{y-4}" width="5.2" height="7" rx="1"/>'
for k,(x,y) in nodes.items():
    on = k in active
    big = 1.3 if k=='c' else 1
    o = f'<g transform="translate({x} {y}) scale({big})"><g filter="url(#sh)">'
    o += f'<path fill="{"url(#metal)" if on else "#cfc4b9"}" d="M-7 12 L0 -12 L7 12 Z"/></g>'
    o += f'<path class="ink1" d="M-4 4 H4 M-5.5 9 H5.5" opacity=".6"/>'
    o += f'<circle class="{"goldf" if on else "mutef"}" cx="0" cy="-13" r="3.2"/>'
    if on: o += rings(0,-13,2,7,5,-150,-30,'gold')
    else: o += '<text class="lbl" x="9" y="-12" style="font-size:9px">z</text>'
    o += '</g>'
    b += o
b += '<g><rect class="chip" x="120" y="274" width="250" height="20" rx="10"/><circle class="accf" cx="136" cy="284" r="4"/><text class="lbl" x="146" y="287.6">ACTIVE</text>'
b += '<circle fill="#cfc4b9" cx="206" cy="284" r="4"/><text class="lbl" x="216" y="287.6">SLEEPING</text><rect class="goldf" x="288" y="279" width="6" height="9" rx="1"/><text class="lbl" x="300" y="287.6">USERS</text></g>'
svg('spidernet', 'Demand-driven elastic network over a city: base stations near users are switched on and linked in a web, while idle ones sleep to save energy', b)

# ---------- 3. LunarCom ----------
b = ''
import random; random.seed(4)
for _ in range(60):
    x, y, r = random.uniform(0,400), random.uniform(0,300), random.choice([.6,.8,1,1.3])
    b += f'<circle class="mutef" cx="{x:.0f}" cy="{y:.0f}" r="{r}"/>'
# Earth
b += '<circle fill="url(#glowT)" cx="92" cy="206" r="104"/>'
b += '<g filter="url(#sh)"><circle fill="url(#earth)" cx="92" cy="206" r="70"/></g>'
b += '<path class="sagef" opacity=".9" d="M52 160 q18 -14 34 -4 q8 10 24 4 q10 8 2 18 q-14 4 -22 16 q-14 6 -26 -6 q-14 -8 -12 -28 z M98 214 q16 -6 28 6 q8 14 -4 30 q-10 10 -20 0 q-6 -16 -4 -36 z M40 226 q10 -4 14 6 q-2 10 -12 8 z"/>'
b += '<path class="paper" opacity=".55" d="M40 186 q26 -8 54 2 M60 248 q30 -10 60 -2" stroke="#fff" stroke-width="3" fill="none"/>'
# ground station dish on Earth limb
b += '<g transform="translate(140 152) rotate(35)"><path class="paper" d="M-12 0 a12 9 0 0 0 24 0 z"/><path class="ink1" d="M-12 0 a12 9 0 0 0 24 0 z M0 4 v10"/><circle class="accf" cx="0" cy="-6" r="2"/></g>'
# Moon
b += '<g filter="url(#sh)"><circle fill="url(#moon)" cx="322" cy="96" r="48"/></g>'
for (x,y,r) in [(304,82,9),(336,112,7),(332,74,5),(312,116,4),(346,90,3.5)]:
    b += f'<circle class="mutef" cx="{x}" cy="{y}" r="{r}"/><path class="ink1" opacity=".25" d="M{x-r} {y} a{r} {r} 0 0 0 {2*r} 0"/>'
# rover
b += '<g transform="translate(300 146)"><rect fill="url(#metal)" x="-10" y="-8" width="20" height="8" rx="2"/><circle class="inkf" cx="-7" cy="1" r="3"/><circle class="inkf" cx="7" cy="1" r="3"/><path class="ink1" d="M4 -8 v-7 h6"/></g>'
# Gateway
gx, gy = 236, 58
b += f'<g transform="translate({gx} {gy}) rotate(-12)" filter="url(#sh)">'
b += '<rect fill="url(#metal)" x="-12" y="-9" width="24" height="18" rx="3"/>'
for side in (-1,1):
    for j in range(3):
        b += f'<rect class="tealf" x="{(16 if side>0 else -40)+j*8.5}" y="-8" width="7.5" height="16" rx="1"/>'
    b += f'<path class="ink1" d="M{12*side} 0 H{16*side}"/>'
b += '<path class="ink1" d="M0 -9 v-6"/><circle class="goldf" cx="0" cy="-16" r="2.4"/></g>'
# links
b += taper(142, 150, 230, 74, 14, 30, 'url(#beamT)')
b += '<path class="teal dash" stroke-width="1.8" d="M142 150 L228 76"/>'
b += f'<path class="gold" stroke-width="4" opacity=".25" d="M146 146 L{gx-6} {gy+8}"/><path class="gold" stroke-width="1.8" d="M146 146 L{gx-6} {gy+8}"/>'
b += f'<path class="gold" stroke-width="4" opacity=".25" d="M{gx+12} {gy+10} L300 138"/><path class="gold" stroke-width="1.8" d="M{gx+12} {gy+10} L300 138"/>'
b += chip(200, 122, 'OPTICAL') + chip(150, 104, 'RF', 'middle') + chip(236, 22, 'LUNAR GATEWAY', 'middle') + chip(92, 288, 'EARTH', 'middle') + chip(322, 168, 'MOON', 'middle')
svg('lunarcom', 'Hybrid lunar communication: a ground station on Earth reaches a lunar gateway and a rover on the Moon through both a wide radio link and a narrow optical laser link', b)

# ---------- 4. Light-wave sensing ----------
b = '<rect x="0" y="0" width="400" height="226" fill="url(#wall)"/><polygon class="soft" points="0,226 400,226 400,300 0,300"/><path class="ink1" d="M0 226 H400"/>'
# lamp
b += '<path class="ink1" d="M98 0 V22"/><g filter="url(#sh)"><path fill="url(#metal)" d="M74 22 H122 L114 40 H82 Z"/></g><circle fill="url(#glowG)" cx="98" cy="44" r="40"/>'
b += '<polygon fill="url(#beamG)" points="86,40 112,40 286,96 268,176"/>'
# person seated, side profile facing left
px = 300
b += '<g filter="url(#sh)">'
b += f'<path class="mutef" d="M{px-6} 176 h56 v10 h-56 z M{px+44} 120 h8 v66 h-8 z M{px} 186 v40 M{px+46} 186 v40"/>'
b += f'<path class="ink1" d="M{px} 186 v40 M{px+46} 186 v40"/>'
b += f'<path fill="url(#metal)" d="M{px-14} 172 q-6 -40 6 -64 q10 -14 26 -10 q14 6 14 30 v44 z"/>'
b += f'<path class="inkf" d="M{px-14} 172 h40 v12 h-62 q-8 0 -8 8 v34 h-10 v-40 q0 -14 14 -14 z"/>'
b += f'<circle fill="#e7c3a3" cx="{px+4}" cy="82" r="15"/><path class="inkf" d="M{px-6} 74 q4 -14 18 -10 q8 4 6 18 q-6 -10 -14 -8 z"/>'
b += '</g>'
# chest motion arrows
b += f'<path class="acc" stroke-width="1.8" d="M{px-30} 128 h-12 M{px-36} 122 l-6 6 l6 6"/><path class="acc" stroke-width="1.8" d="M{px-30} 142 h-12 M{px-36} 136 l-6 6 l6 6" opacity=".5"/>'
# reflected rays to detector
b += taper(272, 136, 132, 178, 22, 6, 'url(#beamG)')
b += '<path class="gold dash" stroke-width="1.6" d="M272 128 L134 174 M272 146 L134 182"/>'
# detector + laptop on table
b += '<g filter="url(#sh)"><rect class="paper" x="24" y="196" width="150" height="8" rx="2"/></g><path class="ink1" d="M34 204 v22 M164 204 v22"/>'
b += '<g filter="url(#sh)"><rect fill="url(#metal)" x="118" y="170" width="26" height="26" rx="4"/></g><circle class="paper" cx="131" cy="183" r="6"/><circle class="goldf" cx="131" cy="183" r="3"/>'
b += '<path class="ink1" d="M118 190 q-14 8 -30 4"/>'
b += '<g filter="url(#sh)"><path class="inkf" d="M36 196 l6 -40 h52 l-4 40 z"/></g><rect class="paper" x="44" y="160" width="44" height="30" rx="2"/>'
b += '<path class="acc" stroke-width="1.4" d="M47 172 q5 -8 10 0 t10 0 t10 0 t10 0"/><path class="gold" stroke-width="1.4" d="M47 184 h6 l2 -6 l3 10 l2 -4 h8 l2 -6 l3 10 l2 -4 h8"/>'
# inset panel
b += '<g filter="url(#sh)"><rect class="paper" x="204" y="238" width="182" height="52" rx="10"/></g>'
b += '<path class="acc" stroke-width="1.8" d="M214 256 q11 -12 22 0 t22 0 t22 0 t22 0 t22 0 t22 0 t22 0"/>'
b += '<path class="gold" stroke-width="1.8" d="M214 278 h14 l3 -9 l4 15 l3 -6 h16 l3 -9 l4 15 l3 -6 h16 l3 -9 l4 15 l3 -6 h16 l3 -9 l4 15 l3 -6 h16"/>'
b += chip(16, 250, 'BREATHING') + chip(16, 278, 'HEARTBEAT')
b += '<circle class="accf" cx="122" cy="250" r="4"/><circle class="goldf" cx="122" cy="278" r="4"/>'
b += chip(132, 62, 'LED LIGHTING') + chip(150, 214, 'REFLECTED LIGHT')
svg('lightwave-sensing', 'Non-contact light-wave sensing: a ceiling lamp lights a seated person, a photodetector on the desk captures light reflected from the chest, and the signal reveals breathing and heartbeat', b)

# ---------- 5. ViLDAR ----------
b = '<rect width="400" height="150" fill="url(#sky)"/>'
b += '<path class="sagef" d="M0 150 q60 -26 120 -10 q60 -24 140 -4 q70 -22 140 0 V170 H0 Z" opacity=".8"/>'
b += '<polygon class="soft" points="0,150 400,150 400,300 0,300"/>'
b += '<polygon class="mutef" points="176,150 224,150 400,300 0,300" opacity=".9"/>'
for i in range(5):
    y0 = 156 + i*i*6.5; y1 = y0 + 4 + i*3
    w0 = 1 + (y0-150)/150*5; w1 = 1 + (y1-150)/150*5
    b += f'<polygon class="paper" points="{200-w0/2:.1f},{y0:.1f} {200+w0/2:.1f},{y0:.1f} {200+w1/2:.1f},{y1:.1f} {200-w1/2:.1f},{y1:.1f}"/>'
# car front view (center-left lane)
cx, cy = 150, 236
b += f'<ellipse class="mutef" cx="{cx}" cy="{cy+28}" rx="62" ry="7" opacity=".7"/>'
b += f'<g filter="url(#sh)"><path fill="url(#metal)" d="M{cx-58} {cy+20} v-26 q0 -10 10 -14 l16 -26 q4 -6 12 -6 h40 q8 0 12 6 l16 26 q10 4 10 14 v26 z"/></g>'
b += f'<path class="paper" opacity=".85" d="M{cx-34} {cy-22} l12 -20 q2 -4 7 -4 h30 q5 0 7 4 l12 20 z"/>'
b += f'<rect class="inkf" x="{cx-22}" y="{cy+2}" width="44" height="10" rx="2" opacity=".75"/>'
b += f'<rect class="inkf" x="{cx-54}" y="{cy+18}" width="16" height="14" rx="3"/><rect class="inkf" x="{cx+38}" y="{cy+18}" width="16" height="14" rx="3"/>'
for sx in (-1, 1):
    b += f'<circle fill="url(#glowG)" cx="{cx+sx*42}" cy="{cy-2}" r="26"/><ellipse class="goldf" cx="{cx+sx*42}" cy="{cy-2}" rx="9" ry="6"/><ellipse class="paper" cx="{cx+sx*42}" cy="{cy-2}" rx="4" ry="2.5"/>'
# light to pole
b += '<polygon fill="url(#beamG)" points="194,232 330,104 352,136"/>'
b += '<path class="gold dash" stroke-width="1.5" d="M192 234 L338 116"/>'
# pole + detector
b += '<g filter="url(#sh)"><rect class="inkf" x="344" y="96" width="6" height="190" rx="2"/><rect fill="url(#metal)" x="326" y="104" width="22" height="32" rx="4"/></g><circle class="paper" cx="337" cy="120" r="6"/><circle class="goldf" cx="337" cy="120" r="3"/>'
# motion lines
# inset plot: received power vs time
b += '<g filter="url(#sh)"><rect class="paper" x="16" y="44" width="168" height="96" rx="10"/></g>'
b += '<path class="ink1" d="M30 124 H172 M30 124 V58"/>'
b += '<path class="gold" stroke-width="2.2" d="M34 120 C72 118 100 106 122 84 C136 70 146 62 160 58"/>'
for (x,y) in [(62,117),(92,110),(118,89),(142,66)]: b += f'<circle class="accf" cx="{x}" cy="{y}" r="2.6"/>'
b += '<text class="lbl" x="36" y="68" style="font-size:9px">POWER</text><text class="lbl" x="172" y="136" style="font-size:9px" text-anchor="end">TIME</text>'
b += chip(300, 82, 'PHOTODETECTOR', 'middle') + chip(20, 26, 'SPEED FROM HEADLIGHTS')
svg('vildar', 'Visible-light detection and ranging: an approaching car’s headlights reach a roadside photodetector, and the rising received power over time gives the car’s speed', b)

# ---------- 6. mmWave & THz channels ----------
b = '<rect width="400" height="300" fill="url(#sky)"/>'
b += '<rect class="sagef" x="0" y="246" width="400" height="54" opacity=".75"/><path class="sage" d="M0 246 H400"/>'
# building
b += '<g filter="url(#sh)"><rect class="paper" x="330" y="96" width="58" height="150" rx="3"/></g>'
for r in range(6):
    for c in range(3): b += f'<rect class="tealsoft" x="{338+c*17}" y="{106+r*22}" width="11" height="14" rx="1"/>'
b += '<rect class="ink1" x="330" y="96" width="58" height="150" rx="3"/>'
# cloud + rain
b += '<g filter="url(#sh)"><path class="paper" d="M34 92 a22 22 0 0 1 34 -20 a30 30 0 0 1 56 4 a20 20 0 0 1 6 40 H48 a18 18 0 0 1 -14 -24 z"/></g>'
b += '<path class="ink1" d="M34 92 a22 22 0 0 1 34 -20 a30 30 0 0 1 56 4 a20 20 0 0 1 6 40 H48 a18 18 0 0 1 -14 -24 z"/>'
for i in range(14):
    x = 46 + (i*13) % 84 + (i//7)*6; y = 128 + (i*29) % 70
    b += f'<path class="teal" stroke-width="1.6" d="M{x} {y} l-3 9"/>'
# drone
dx, dy = 196, 56
b += f'<g transform="translate({dx} {dy})" filter="url(#sh)">'
b += '<path class="ink" d="M-14 -2 L-40 -10 M14 -2 L40 -10"/>'
for sx in (-40, 40):
    b += f'<ellipse class="mutef" cx="{sx}" cy="-14" rx="18" ry="3"/><path class="ink1" d="M{sx} -10 v-4"/>'
b += '<rect fill="url(#metal)" x="-18" y="-10" width="36" height="18" rx="7"/><path class="ink1" d="M-8 8 l-4 8 M8 8 l4 8"/>'
b += '<rect class="goldf" x="-6" y="8" width="12" height="6" rx="2"/></g>'
# main beam (attenuated passing rain edge) to ground array
b += taper(dx, dy+16, 262, 238, 6, 30, 'url(#beamA)')
b += ticks(dx, dy+16, 262, 236, 6, 10)
# multipath via building
b += '<path class="gold dash" stroke-width="1.8" d="M204 72 L330 150 L276 236"/>'
b += '<path class="gold dash" stroke-width="1.4" opacity=".6" d="M190 74 L150 246 L252 240"/>'
# ground station with phased array
b += '<g filter="url(#sh)"><rect class="inkf" x="258" y="236" width="8" height="16"/><g transform="translate(262 232) rotate(-28)"><rect fill="url(#metal)" x="-20" y="-6" width="40" height="10" rx="2"/>'
for j in range(5): b += f'<rect class="goldf" x="{-17+j*7.6}" y="-4" width="5" height="6" rx="1"/>'
b += '</g></g>'
b += chip(214, 172, 'mmWave / THz', 'end') + chip(330, 82, 'REFLECTION', 'middle') + chip(20, 220, 'RAIN FADE') + chip(110, 274, 'MULTIPATH')
svg('mmwave-thz', 'Millimeter-wave and terahertz channels: a drone sends a narrow beam to a ground phased array while rain attenuates the link and a building and the ground create reflected multipath', b)

# ---------- 7. Rural IoT ----------
b = '<rect width="400" height="300" fill="url(#sky)"/>'
b += '<circle fill="url(#glowG)" cx="60" cy="50" r="40"/><circle class="goldf" cx="60" cy="50" r="13" opacity=".85"/>'
b += '<path fill="url(#sage)" d="M0 150 q80 -40 170 -10 q90 -50 230 -14 V230 H0 Z" opacity=".75"/>'
b += '<path fill="url(#sage)" d="M0 190 q120 -30 220 -6 q100 -18 180 0 V236 H0 Z"/>'
b += '<rect fill="url(#soil)" x="0" y="232" width="400" height="68"/><path class="ink1" d="M0 232 H400"/>'
for x in range(8, 400, 22): b += f'<path class="sage" d="M{x} 232 q3 -9 6 0 M{x+8} 232 q2 -6 4 0"/>'
# barn
b += '<g filter="url(#sh)"><path fill="url(#metal)" d="M214 186 V150 l26 -20 l26 20 v36 z"/></g><path class="paper" d="M232 186 v-20 h16 v20 z" opacity=".9"/><path class="ink1" d="M232 166 l16 20 M248 166 l-16 20"/>'
# cows
def cow(x, y, s=1):
    o = f'<g transform="translate({x} {y}) scale({s})" filter="url(#sh)">'
    o += '<path class="paper" d="M0 0 h46 q10 0 10 10 v14 q0 4 -4 4 h-52 q-4 0 -4 -4 v-14 q0 -10 4 -10 z"/>'
    o += '<path class="inkf" d="M10 4 q8 -4 12 4 q-2 8 -12 6 z M34 12 q6 -2 8 4 q-4 6 -10 2 z"/>'
    o += '<path class="ink1" d="M2 28 v12 M12 28 v12 M40 28 v12 M50 28 v12"/>'
    o += '<path class="paper" d="M54 2 l12 -6 h8 q4 0 4 4 v10 q0 4 -4 4 h-12 z"/><path class="ink1" d="M54 2 l12 -6 h8 q4 0 4 4 v10 q0 4 -4 4 h-12 z"/>'
    o += '<path class="ink1" d="M0 0 h46 q10 0 10 10 v14 q0 4 -4 4 h-52 q-4 0 -4 -4 v-14 q0 -10 4 -10 z M-4 6 q-8 6 -6 18"/>'
    o += '<rect class="goldf" x="58" y="10" width="7" height="8" rx="2"/></g>'
    return o
b += cow(40, 182) + cow(122, 196, .85)
b += rings(102, 196, 3, 8, 7, -60, 30, 'gold') + rings(178, 208, 2, 7, 7, -60, 30, 'gold')
# tower on hill
tx = 334
b += '<g filter="url(#sh)">'
b += f'<path class="ink" d="M{tx-16} 214 L{tx} 64 L{tx+16} 214"/>'
for y in range(84, 214, 26):
    w = (y-64)/150*16
    b += f'<path class="ink1" d="M{tx-w} {y} H{tx+w} M{tx-w} {y} L{tx+w+4} {y+26} M{tx+w} {y} L{tx-w-4} {y+26}"/>'
b += f'<rect fill="url(#metal)" x="{tx-6}" y="54" width="12" height="16" rx="2"/></g>'
b += rings(tx, 62, 4, 14, 12, 150, 210, 'acc')
# links to tower
b += f'<path class="gold dots" stroke-width="2.2" d="M106 186 Q220 90 {tx-8} 70"/><path class="gold dots" stroke-width="2.2" d="M182 198 Q250 120 {tx-8} 74"/>'
# underground sensor + roots
b += '<path class="ink1" opacity=".5" d="M150 232 q-4 14 -14 22 M150 232 q2 16 10 26 M152 232 v20"/>'
b += '<g filter="url(#sh)"><rect fill="url(#metal)" x="196" y="252" width="30" height="20" rx="4"/></g><rect class="goldf" x="202" y="258" width="18" height="4" rx="1"/>'
b += rings(211, 252, 3, 8, 8, -150, -30, 'gold')
b += f'<path class="teal dots" stroke-width="2.2" d="M214 232 Q270 140 {tx-8} 78"/>'
b += chip(386, 32, 'LoRa GATEWAY', 'end') + chip(20, 290, 'UNDERGROUND SOIL SENSOR') + chip(20, 160, 'TAGGED CATTLE')
svg('rural-iot', 'Rural Internet of Things: tagged cattle and an underground soil sensor on a farm send data over long-range LoRa radio to a gateway tower on the hill', b)

# ---------- 8. mmWave radar blood pressure ----------
b = '<rect x="0" y="0" width="400" height="214" fill="url(#wall)"/><polygon class="soft" points="0,214 400,214 400,300 0,300"/><path class="ink1" d="M0 214 H400"/>'
# table
b += '<g filter="url(#sh)"><rect class="paper" x="30" y="166" width="230" height="10" rx="2"/></g><path class="ink1" d="M44 176 v38 M246 176 v38"/>'
# radar board
b += '<g filter="url(#sh)"><rect fill="url(#metal)" x="52" y="112" width="52" height="54" rx="5"/></g>'
for r in range(3):
    for c in range(3): b += f'<rect class="goldf" x="{59+c*15}" y="{119+r*15}" width="9" height="9" rx="1.5"/>'
b += '<path class="ink1" d="M60 166 v-4 M96 166 v-4"/>'
# person seated right, facing left, arm on table
px = 300
b += '<g filter="url(#sh)">'
b += f'<path class="mutef" d="M{px+30} 108 h8 v78 h-8 z M{px-14} 176 h52 v10 h-52 z"/>'
b += f'<path fill="url(#metal)" d="M{px-18} 172 q-4 -42 8 -66 q10 -12 24 -8 q14 6 14 30 v44 z"/>'
b += f'<path class="inkf" d="M{px-18} 172 h44 v12 h-60 q-8 0 -8 8 v28 h-10 v-34 q0 -14 14 -14 z"/>'
b += f'<path fill="url(#metal)" d="M{px-12} 124 q-20 20 -60 36 l4 8 q40 -10 64 -30 z"/>'
b += f'<ellipse fill="#e7c3a3" cx="{px-70}" cy="163" rx="9" ry="5"/>'
b += f'<rect fill="#e7c3a3" x="{px-4}" y="88" width="10" height="14"/><circle fill="#e7c3a3" cx="{px+1}" cy="74" r="15"/><path class="inkf" d="M{px-9} 66 q4 -14 18 -10 q8 4 6 18 q-6 -10 -14 -8 z"/>'
b += '</g>'
# beams to wrist and neck
b += taper(104, 132, 226, 162, 8, 18, 'url(#beamA)') + ticks(104, 132, 226, 162, 4, 8)
b += taper(104, 124, 292, 94, 8, 18, 'url(#beamA)') + ticks(104, 124, 292, 94, 5, 8)
b += '<circle fill="url(#glowA)" cx="230" cy="163" r="16"/><circle fill="url(#glowA)" cx="296" cy="94" r="16"/>'
# inset: chirp + BP waveform
b += '<g filter="url(#sh)"><rect class="paper" x="22" y="226" width="356" height="64" rx="10"/></g>'
b += '<path class="gold" stroke-width="1.8" d="M38 276 L68 242 V276 L98 242 V276 L128 242 V276"/>'
b += '<text class="lbl" x="38" y="288" style="font-size:9px">FMCW CHIRPS</text>'
b += '<path class="ink1" d="M150 236 V280" opacity=".4"/>'
b += '<path class="acc" stroke-width="2.2" d="M166 272 C176 272 178 240 190 242 C200 244 198 260 208 258 C216 256 218 272 228 272 C238 272 240 240 252 242 C262 244 260 260 270 258 C278 256 280 272 290 272 C300 272 302 240 314 242 C324 244 322 260 332 258 C340 256 342 272 352 272 H362"/>'
b += '<text class="lbl" x="166" y="288" style="font-size:9px">ARTERIAL PULSE</text>'
b += chip(78, 92, 'mmWave RADAR', 'middle') + chip(200, 196, 'WRIST', 'middle') + chip(250, 40, 'NECK', 'middle')
svg('radar-bp', 'Non-invasive blood-pressure sensing: a millimeter-wave radar on a desk steers beams to a seated person’s wrist and neck at the same time and recovers the arterial pulse waveform', b)
print('ok')

# ---------- 9. FORMULA3 ----------
b = '<rect width="400" height="300" fill="url(#sky)"/>'
b += '<rect class="sagef" x="0" y="250" width="400" height="50" opacity=".7"/><path class="sage" d="M0 250 H400"/>'
# base station
b += '<g filter="url(#sh)"><path class="ink" d="M44 250 L56 120 L68 250 M47 214 H65 M50 180 H62 M52 150 H60"/><rect fill="url(#metal)" x="46" y="104" width="20" height="26" rx="3"/></g>'
for j in range(3): b += f'<rect class="goldf" x="50" y="{109+j*7}" width="12" height="4" rx="1"/>'
# building with room cutaway
b += '<g filter="url(#sh)"><rect class="paper" x="170" y="60" width="216" height="190" rx="4"/></g>'
b += '<rect fill="url(#wall)" x="182" y="92" width="192" height="146"/><path class="ink1" d="M170 60 h216 v190 h-216 z M182 92 h192 v146 h-192 z"/>'
b += '<path class="mute" d="M182 214 H374"/>'
# window with transmissive RIS on facade
b += '<rect class="tealsoft" x="170" y="118" width="12" height="70"/>'
for r in range(7): b += f'<rect class="accf" opacity="{0.35+0.6*((r*3)%5)/4:.2f}" x="171" y="{120+r*9.6:.1f}" width="10" height="7.5" rx="1.5"/>'
# MRA on back wall (metallic strips)
for k in range(6): b += f'<rect class="mutef" x="{336+k*5}" y="104" width="3.4" height="60" rx="1"/>'
b += '<rect class="ink1" x="332" y="100" width="34" height="68" rx="3"/>'
# beams
b += taper(66, 116, 172, 150, 6, 24, 'url(#beamA)') + ticks(66, 116, 172, 150, 4, 9)
b += taper(182, 154, 334, 132, 18, 10, 'url(#beamA)') + ticks(182, 154, 334, 132, 4, 8)
b += taper(334, 142, 262, 200, 10, 6, 'url(#beamA)')
# people: user + walker (blocker)
b += person(258, 238, .82) + '<rect class="inkf" x="266" y="196" width="7" height="12" rx="1.5"/>'
b += person(224, 238, .82, shirt='#9a8f86')
b += '<path class="acc" stroke-width="1.8" d="M206 232 h-14 M198 226 l-6 6 l6 6" opacity=".7"/>'
# AI controller chip
b += '<g filter="url(#sh)"><rect class="paper" x="88" y="34" width="62" height="36" rx="8"/></g>'
b += '<rect fill="url(#metal)" x="104" y="42" width="20" height="20" rx="3"/><path class="ink1" d="M100 46 h4 M100 52 h4 M100 58 h4 M124 46 h4 M124 52 h4 M124 58 h4"/>'
b += '<text class="lbl" x="134" y="56" style="font-size:10px">AI</text>'
b += '<path class="gold dots" stroke-width="2" d="M118 70 Q120 100 60 104 M150 54 Q180 70 176 118 M150 48 Q300 30 348 98"/>'
b += chip(16, 86, '7–24 GHz FR3') + chip(176, 274, 'TRANSMISSIVE RIS', 'middle') + chip(386, 186, 'REFLECTOR ARRAY', 'end') + chip(386, 40, 'PREDICT &amp; ADAPT', 'end')
svg('formula3', 'FORMULA3: an AI controller predicts blockage and reconfigures a transmissive smart surface on a window and a metallic reflector array indoors so that an upper mid-band (FR3) link from an outdoor base station reaches a user while another person walks through the room', b)

# ---------- Outreach: DIY light-wave kit ----------
b = '<rect x="0" y="0" width="400" height="200" fill="url(#wall)"/><polygon class="soft" points="0,200 400,200 400,300 0,300"/><path class="ink1" d="M0 200 H400"/>'
b += '<g filter="url(#sh)"><rect class="paper" x="20" y="186" width="360" height="12" rx="3"/></g>'
# phone
b += '<g filter="url(#sh)"><rect class="inkf" x="36" y="128" width="34" height="58" rx="6"/></g><rect class="paper" x="40" y="134" width="26" height="44" rx="2"/>'
b += '<path class="accf" d="M48 162 v-14 l10 -3 v14"/><circle class="accf" cx="46" cy="162" r="3"/><circle class="accf" cx="56" cy="159" r="3"/>'
b += '<path class="ink1" d="M70 176 q20 8 32 -2"/>'
# transmitter board with LED
b += '<g filter="url(#sh)"><rect fill="url(#metal)" x="100" y="150" width="54" height="36" rx="5"/></g>'
b += '<rect class="goldf" x="108" y="158" width="10" height="8" rx="1"/><rect class="paper" x="124" y="160" width="20" height="4" rx="1" opacity=".7"/>'
b += '<circle fill="url(#glowG)" cx="160" cy="160" r="36"/><path class="paper" d="M154 152 h10 a5 5 0 0 1 0 16 h-10 z"/><circle class="goldf" cx="164" cy="160" r="5"/>'
b += '<polygon fill="url(#beamG)" points="168,154 270,136 270,184 168,166"/>'
for k in range(4): b += f'<path class="gold" stroke-width="1.6" opacity="{.9-k*.18:.2f}" d="M{186+k*20} {152-k*2} v{16+k*4}"/>'
# receiver: solar cell + speaker
b += '<g filter="url(#sh)"><rect class="tealf" x="270" y="132" width="34" height="54" rx="3"/></g>'
for r in range(4): b += f'<path class="paper" stroke="currentColor" d="M272 {140+r*12} H302" stroke-width=".8" opacity=".5"/>'
b += '<path class="ink1" d="M304 176 q12 6 22 0"/>'
b += '<g filter="url(#sh)"><rect class="inkf" x="326" y="140" width="38" height="46" rx="6"/></g><circle class="mutef" cx="345" cy="165" r="12"/><circle class="inkf" cx="345" cy="165" r="5"/>'
b += rings(364, 160, 3, 10, 9, -50, 50, 'acc')
b += chip(53, 112, 'MUSIC', 'middle') + chip(130, 216, 'LED TRANSMITTER', 'middle') + chip(218, 112, 'DATA ON LIGHT', 'middle') + chip(310, 216, 'SOLAR RECEIVER', 'middle')
b += '<text class="lbl" x="200" y="270" text-anchor="middle" style="font-size:12px">200+ KITS · K-12 TO UNDERGRADUATE</text>'
svg('outreach-diy', 'DIY light-wave communication kit: a phone plays music into an LED transmitter, the music travels as flickering light to a solar-cell receiver, and a speaker plays it back', b)

# ---------- Outreach: PETE-Kits rural ----------
b = '<rect width="400" height="300" fill="url(#sky)"/>'
b += '<path fill="url(#sage)" d="M0 170 q100 -40 200 -10 q110 -36 200 0 V300 H0 Z"/>'
for x in range(0, 400, 26): b += f'<path class="sage" opacity=".5" d="M{x} 300 Q{x+60} 220 {200+(x-200)*0.3:.0f} 180"/>'
# schoolhouse
b += '<g filter="url(#sh)"><path class="paper" d="M150 236 V176 l50 -34 l50 34 v60 z"/></g><path class="ink1" d="M150 236 V176 l50 -34 l50 34 v60 z"/>'
b += '<path fill="url(#metal)" d="M140 180 l60 -44 l60 44 l-8 4 l-52 -38 l-52 38 z"/><rect fill="url(#metal)" x="192" y="116" width="16" height="22" rx="2"/><circle class="goldf" cx="200" cy="126" r="4"/>'
b += '<rect class="accf" x="190" y="204" width="20" height="32" rx="2"/><rect class="tealsoft" x="162" y="190" width="18" height="16" rx="1"/><rect class="tealsoft" x="220" y="190" width="18" height="16" rx="1"/>'
# silo + barn
b += '<g filter="url(#sh)"><rect class="mutef" x="318" y="140" width="26" height="80" rx="3"/><path class="mutef" d="M318 142 a13 12 0 0 1 26 0"/><path fill="url(#metal)" d="M290 222 v-36 l22 -14 l22 14 v36 z" transform="translate(-30 0)"/></g>'
# kit box with sensors
b += '<g filter="url(#sh)"><rect class="paper" x="40" y="214" width="78" height="46" rx="6"/></g>'
b += '<rect class="tealf" x="48" y="222" width="26" height="18" rx="2"/><rect class="accf" x="80" y="222" width="12" height="12" rx="2"/><rect class="goldf" x="96" y="222" width="14" height="8" rx="2"/><path class="ink1" d="M52 248 h56"/>'
b += rings(108, 214, 3, 10, 9, -140, -40, 'gold')
b += '<path class="gold dots" stroke-width="2" d="M112 200 Q150 150 192 120"/>'
b += chip(78, 280, 'TECH EXPERIENCE KIT', 'middle') + chip(200, 98, 'RURAL K-12 SCHOOLS', 'middle') + chip(386, 262, 'RURAL ENTREPRENEURSHIP', 'end')
svg('outreach-pete', 'PETE-Kits rural outreach: a connected technology kit with sensors and a tablet links to a rural schoolhouse next to farmland, bringing hands-on technology to K-12 students', b)

# ---------- Outreach: student research ----------
b = '<rect x="0" y="0" width="400" height="206" fill="url(#wall)"/><polygon class="soft" points="0,206 400,206 400,300 0,300"/><path class="ink1" d="M0 206 H400"/>'
b += '<g filter="url(#sh)"><rect class="paper" x="40" y="176" width="320" height="10" rx="2"/></g><path class="ink1" d="M54 186 v40 M346 186 v40"/>'
# oscilloscope
b += '<g filter="url(#sh)"><rect class="inkf" x="60" y="108" width="96" height="68" rx="6"/></g><rect class="tealsoft" x="68" y="116" width="62" height="44" rx="3"/>'
b += '<path class="teal" stroke-width="1.6" d="M70 140 q6 -16 12 0 t12 0 t12 0 t12 0 t12 0"/><path class="gold" stroke-width="1.4" d="M70 150 h10 v-6 h10 v6 h10 v-6 h10 v6 h10"/>'
for j in range(3): b += f'<circle class="mutef" cx="143" cy="{122+j*14}" r="4"/>'
# SDR board + antenna
b += '<g filter="url(#sh)"><rect fill="url(#metal)" x="176" y="150" width="56" height="26" rx="4"/></g><rect class="goldf" x="184" y="157" width="12" height="10" rx="1"/><rect class="paper" x="202" y="158" width="22" height="4" opacity=".7"/>'
b += '<path class="ink" d="M226 150 v-34"/><circle class="accf" cx="226" cy="114" r="3.5"/>' + rings(226, 114, 3, 9, 8, -150, -30, 'gold')
# laptop
b += '<g filter="url(#sh)"><path class="inkf" d="M250 176 l8 -44 h64 l-6 44 z"/></g><rect class="paper" x="260" y="136" width="56" height="34" rx="2"/>'
b += '<path class="acc" stroke-width="1.4" d="M264 162 l8 -10 l8 6 l8 -14 l8 8 l8 -6 l8 4"/>'
# two students
b += person(130, 256, .9) + person(300, 256, .9, shirt='#2f6f86')
b += chip(108, 90, 'OK-LSAMP', 'middle') + chip(226, 76, 'NSF REU', 'middle') + chip(388, 110, 'UNDERGRAD SCHOLARS', 'end')
svg('outreach-research', 'Student research programs: two undergraduate researchers at a lab bench with an oscilloscope, a software-defined radio with an antenna, and a laptop plotting results', b)

# ---------- Outreach: schools and museums ----------
b = '<rect width="400" height="300" fill="url(#sky)"/><polygon class="soft" points="0,232 400,232 400,300 0,300"/><path class="ink1" d="M0 232 H400"/>'
# museum building
b += '<g filter="url(#sh)"><path class="paper" d="M40 232 V120 H360 V232 Z"/></g><path fill="url(#metal)" d="M30 122 L200 60 L370 122 Z"/><rect class="mutef" x="36" y="120" width="328" height="10"/>'
for x in range(64, 360, 52): b += f'<rect class="soft" x="{x}" y="132" width="16" height="100"/><path class="ink1" d="M{x} 132 v100 M{x+16} 132 v100"/>'
b += '<circle class="goldf" cx="200" cy="100" r="9" opacity=".9"/>'
# light demo in front
b += '<g filter="url(#sh)"><rect class="paper" x="96" y="200" width="208" height="10" rx="2"/></g>'
b += '<g filter="url(#sh)"><rect fill="url(#metal)" x="112" y="178" width="30" height="22" rx="4"/></g><circle class="goldf" cx="146" cy="189" r="5"/>'
b += '<polygon fill="url(#beamG)" points="148,183 252,172 252,206 148,195"/>'
b += '<g filter="url(#sh)"><rect class="tealf" x="252" y="172" width="30" height="28" rx="3"/></g>'
b += rings(282, 186, 3, 8, 8, -50, 50, 'acc')
# small visitors
for (x, s, c) in [(80, .62, 'url(#metal)'), (330, .58, '#2f6f86'), (360, .5, '#d39a2c')]:
    b += person(x, 262, s, shirt=c)
b += chip(200, 30, 'HANDS-ON SCIENCE', 'middle') + chip(20, 284, 'NATIONAL LAB DAY') + chip(386, 284, 'CHILDREN’S MUSEUM', 'end')
svg('outreach-museum', 'Schools and museums: a light-wave communication demo set up in front of a museum building, with young visitors watching a light beam carry a signal to a receiver', b)
print('outreach ok')

# ---------- 10. Prime Spectrum (EAGER) ----------
b = '<rect width="400" height="300" fill="url(#sky)"/>'
b += '<rect class="sagef" x="0" y="258" width="400" height="42" opacity=".7"/><path class="sage" d="M0 258 H400"/>'
# spectrum bar
b += '<g filter="url(#sh)"><rect class="paper" x="16" y="16" width="368" height="64" rx="10"/></g>'
b += '<rect class="tealf" opacity=".85" x="28" y="40" width="150" height="18" rx="4"/><rect class="accf" opacity=".85" x="186" y="40" width="186" height="18" rx="4"/>'
b += '<path class="ink1" d="M182 34 v30" stroke-dasharray="3 3"/>'
b += '<text class="lbl" x="103" y="32" text-anchor="middle">BELOW 10 GHz</text><text class="lbl" x="279" y="32" text-anchor="middle">ABOVE 10 GHz · Ku / Ka</text>'
b += '<text class="lbl" x="103" y="73" text-anchor="middle" style="font-size:8.5px">FREED FOR MOBILE &amp; BROADBAND</text><text class="lbl" x="279" y="73" text-anchor="middle" style="font-size:8.5px">LINE-OF-SIGHT LINKS MOVE UP</text>'
b += '<path class="paper" d="M120 49 h120" stroke="#fff" stroke-width="2.5" fill="none"/><path fill="#fff" d="M240 43 l12 6 l-12 6 z"/>'
# satellite
b += '<g transform="translate(250 104) rotate(10)" filter="url(#sh)"><rect fill="url(#metal)" x="-11" y="-8" width="22" height="16" rx="3"/>'
for side in (-1, 1):
    for j in range(3): b += f'<rect class="tealf" x="{(15 if side>0 else -38)+j*8}" y="-7" width="7" height="14" rx="1"/>'
b += '</g>'
# earth station dish
b += '<g filter="url(#sh)"><path class="paper" d="M300 214 a30 22 -30 0 1 52 -30 z"/></g><path class="ink" d="M300 214 a30 22 -30 0 1 52 -30 z M326 200 l-8 -18 M318 214 l-6 44 M334 210 l8 48"/>'
b += taper(250, 112, 318, 186, 6, 26, 'url(#beamA)') + ticks(250, 112, 318, 186, 4, 9)
# rain cloud over link
b += '<g filter="url(#sh)"><path class="paper" d="M300 128 a14 14 0 0 1 22 -12 a18 18 0 0 1 34 4 a12 12 0 0 1 2 24 h-52 a12 12 0 0 1 -6 -16 z"/></g>'
for i in range(6): b += f'<path class="teal" stroke-width="1.5" d="M{312+i*8} {150+(i%2)*6} l-3 8"/>'
# AI forecast badge
b += '<g filter="url(#sh)"><rect class="paper" x="350" y="160" width="40" height="40" rx="8"/></g><rect fill="url(#metal)" x="360" y="170" width="20" height="20" rx="3"/><text class="lbl" x="370" y="184" text-anchor="middle" style="font-size:8px;fill:#fff">AI</text>'
# city with NLOS coverage
for (x, w, h) in [(24,26,70),(54,22,96),(80,30,60),(114,20,84)]:
    b += f'<g filter="url(#sh)"><rect class="paper" x="{x}" y="{258-h}" width="{w}" height="{h}" rx="2"/></g>'
    for r in range(int(h/18)): b += f'<rect class="tealsoft" x="{x+5}" y="{258-h+8+r*18}" width="{w-10}" height="8" rx="1"/>'
b += '<g filter="url(#sh)"><path class="ink" d="M164 258 L172 150 L180 258 M166 226 H178 M168 194 H176"/><rect fill="url(#metal)" x="164" y="140" width="16" height="16" rx="3"/></g>'
b += '<circle fill="url(#glowT)" cx="172" cy="150" r="80"/>'
b += rings(172, 148, 4, 14, 12, 150, 250, 'teal')
for (x, y) in [(60, 150), (98, 182), (128, 160)]:
    b += f'<g filter="url(#sh)"><rect class="paper" x="{x-4}" y="{y-6}" width="8" height="13" rx="2"/></g><rect class="tealf" x="{x-2.6}" y="{y-4}" width="5.2" height="8" rx="1"/>'
b += chip(16, 282, 'SUB-10 GHz FOR MOBILE') + chip(386, 282, 'Ku / Ka EARTH STATION', 'end')
svg('prime-spectrum', 'Spectrum reallocation: line-of-sight satellite links move from congested sub-10 GHz spectrum to Ku and Ka bands, with AI rain-fade prediction, freeing the lower bands for mobile and broadband coverage in cities', b)
print('spectrum ok')

# ======== additional projects ========
def ground(y=250, cls='sagef'):
    return f'<rect class="{cls}" x="0" y="{y}" width="400" height="{300-y}" opacity=".75"/><path class="sage" d="M0 {y} H400"/>'

# A. Cognitive radio CubeSats
b = ''
random.seed(7)
for _ in range(45):
    b += f'<circle class="mutef" cx="{random.uniform(0,400):.0f}" cy="{random.uniform(0,200):.0f}" r="{random.choice([.6,.9,1.2])}"/>'
b += '<path fill="url(#earth)" d="M-40 300 Q200 170 440 300 Z"/><path class="sagef" opacity=".8" d="M40 300 q40 -46 110 -50 q30 10 20 50 z M250 262 q40 -10 70 6 q4 20 -16 32 h-60 z"/>'
b += '<circle fill="url(#glowT)" cx="200" cy="300" r="160" opacity=".6"/>'
def cubesat(x, y, r=0):
    o = f'<g transform="translate({x} {y}) rotate({r})" filter="url(#sh)"><rect fill="url(#metal)" x="-11" y="-11" width="22" height="22" rx="3"/><path class="paper" d="M-11 -3 H11 M-11 4 H11" stroke="#fff" stroke-width="1" opacity=".5"/>'
    o += '<rect class="tealf" x="-36" y="-6" width="22" height="12" rx="1"/><rect class="tealf" x="14" y="-6" width="22" height="12" rx="1"/><path class="ink1" d="M0 -11 v-8"/><circle class="goldf" cx="0" cy="-20" r="2.4"/></g>'
    return o
b += cubesat(90, 96, -10) + cubesat(214, 64, 6) + cubesat(320, 110, 14)
b += '<path class="gold dash" stroke-width="1.8" d="M104 92 L200 68 M228 70 L306 104"/>'
b += '<path class="acc" stroke-width="2" d="M214 86 L196 230"/><circle class="accf" cx="196" cy="234" r="4"/>'
# spectrum panel
b += '<g filter="url(#sh)"><rect class="paper" x="16" y="150" width="150" height="70" rx="10"/></g>'
hs = [30, 8, 36, 10, 6, 28, 9, 34]
for i, hh in enumerate(hs):
    cls = 'accf' if hh > 20 else 'goldf'
    b += f'<rect class="{cls}" opacity="{.85 if hh>20 else .9}" x="{28+i*16}" y="{206-hh}" width="11" height="{hh}" rx="2"/>'
b += '<path class="ink1" d="M26 207 H156"/><text class="lbl" x="28" y="166" style="font-size:9px">BUSY</text><text class="lbl" x="70" y="166" style="font-size:9px;fill:#b07a10">FREE → USE</text>'
b += chip(200, 24, 'CUBESAT NETWORK', 'middle') + chip(386, 160, 'COGNITIVE RADIO', 'end') + chip(196, 276, 'GROUND STATION', 'middle')
svg('cubesat-cr', 'Cognitive radio for small satellites: three CubeSats share a network and sense the spectrum, using free channels to reach a ground station on Earth', b)

# B. FAA ILS Zone 3 measurements
b = '<rect width="400" height="300" fill="url(#sky)"/>' + ground(190)
b += '<polygon class="mutef" points="150,190 250,190 360,300 40,300"/>'
for i in range(6):
    y0 = 196 + i*i*3.4; y1 = y0 + 3 + i*1.6
    b += f'<rect class="paper" x="{198-0.5-i*0.4:.1f}" y="{y0:.1f}" width="{3+i*0.9:.1f}" height="{y1-y0:.1f}"/>'
b += '<path class="paper" d="M150 190 L40 300 M250 190 L360 300" stroke="#fff" stroke-width="2" fill="none"/>'
# localizer array at far end
b += '<g filter="url(#sh)">'
for i in range(9): b += f'<rect fill="url(#metal)" x="{168+i*7.5}" y="176" width="4" height="14" rx="1"/>'
b += '</g>'
b += '<polygon fill="url(#beamGv)" points="200,180 330,40 70,40" opacity=".7"/>'
b += '<path class="acc dash" stroke-width="2" d="M200 186 L112 60"/>'
# drone with receiver
b += '<g transform="translate(150 96)" filter="url(#sh)"><path class="ink" d="M-12 -2 L-32 -8 M12 -2 L32 -8"/><ellipse class="mutef" cx="-32" cy="-11" rx="14" ry="2.5"/><ellipse class="mutef" cx="32" cy="-11" rx="14" ry="2.5"/><rect fill="url(#metal)" x="-14" y="-8" width="28" height="14" rx="6"/><rect class="goldf" x="-5" y="6" width="10" height="5" rx="1"/></g>'
b += rings(150, 112, 2, 8, 7, 40, 140, 'gold')
# aircraft
b += '<g transform="translate(70 52) rotate(28)" filter="url(#sh)"><path class="paper" d="M-24 0 h48 l6 4 h-60 z"/><path class="paper" d="M-4 2 l-10 14 h6 l12 -14 z M-20 0 l-6 -8 h5 l8 8 z"/><path class="ink1" d="M-24 0 h48 l6 4 h-60 z"/></g>'
b += chip(386, 30, 'ILS LOCALIZER SIGNAL', 'end') + chip(16, 150, 'DRONE-BORNE SDR') + chip(200, 284, 'ZONE 3 MEASUREMENTS', 'middle')
svg('faa-ils', 'FAA instrument landing system measurements: a drone carrying a software-defined radio flies the approach path and measures the localizer signal from the antenna array at the end of the runway', b)

# C. Hybrid VLC/RF V2X
b = '<rect width="400" height="300" fill="url(#sky)"/>' + ground(170)
b += '<rect class="mutef" x="0" y="196" width="400" height="74"/><path class="paper" d="M0 233 H400" stroke="#fff" stroke-width="3" stroke-dasharray="18 14" fill="none"/>'
def car(x, y, flip=False, shade='url(#metal)'):
    s = -1 if flip else 1
    o = f'<g transform="translate({x} {y}) scale({s} 1)" filter="url(#sh)"><path fill="{shade}" d="M-46 10 v-14 q0 -6 6 -8 l14 -14 q4 -4 10 -4 h28 q6 0 10 4 l12 14 q12 2 12 10 v12 z"/>'
    o += '<path class="tealsoft" d="M-24 -10 l10 -12 h22 v12 z M12 -10 v-12 h4 l12 12 z"/><circle class="inkf" cx="-28" cy="12" r="8"/><circle class="inkf" cx="28" cy="12" r="8"/><circle class="mutef" cx="-28" cy="12" r="3"/><circle class="mutef" cx="28" cy="12" r="3"/>'
    o += '<rect class="goldf" x="40" y="-4" width="6" height="6" rx="1"/><rect class="accf" x="-48" y="-4" width="4" height="6" rx="1"/></g>'
    return o
b += car(96, 214) + car(300, 214)
b += '<polygon fill="url(#beamG)" points="142,212 250,198 250,226"/>'
for k in range(4): b += f'<path class="gold" stroke-width="1.6" opacity="{.9-k*.18:.2f}" d="M{164+k*20} {208-k*2} v{10+k*4}"/>'
# roadside unit
b += '<g filter="url(#sh)"><rect class="inkf" x="196" y="96" width="6" height="100" rx="2"/><rect fill="url(#metal)" x="186" y="84" width="26" height="18" rx="3"/></g>'
b += rings(199, 92, 3, 12, 11, 200, 340, 'teal') 
b += '<path class="teal dash" stroke-width="1.6" d="M190 104 Q140 140 110 190 M208 104 Q260 140 290 190"/>'
b += chip(200, 270, 'VISIBLE-LIGHT V2V', 'middle') + chip(200, 40, 'RF (DSRC) BACKUP', 'middle') + chip(16, 150, 'HEADLIGHTS') + chip(386, 150, 'TAILLIGHTS', 'end')
svg('v2x', 'Hybrid visible-light and radio vehicle links: a following car talks to the car ahead through headlight and taillight light, while a roadside unit provides a radio backup link to both', b)

# D. UAV-to-wearables UWB
b = '<rect width="400" height="300" fill="url(#sky)"/>' + ground(246)
b += '<g transform="translate(250 70)" filter="url(#sh)"><path class="ink" d="M-14 -2 L-38 -10 M14 -2 L38 -10"/><ellipse class="mutef" cx="-38" cy="-13" rx="16" ry="3"/><ellipse class="mutef" cx="38" cy="-13" rx="16" ry="3"/><rect fill="url(#metal)" x="-16" y="-9" width="32" height="16" rx="6"/><rect class="goldf" x="-5" y="7" width="10" height="5" rx="1"/></g>'
# UWB pulses along path
import math as _m
x0, y0, x1, y1 = 246, 84, 150, 188
for i in range(5):
    t = (i+1)/6; cx = x0+(x1-x0)*t; cy = y0+(y1-y0)*t
    b += f'<g transform="translate({cx:.1f} {cy:.1f}) rotate(-47)"><path class="acc" stroke-width="2" d="M-12 0 h7 l2 -8 l3 16 l3 -12 l2 4 h7"/></g>'
b += person(140, 246, 1.1)
b += '<rect class="goldf" x="112" y="196" width="10" height="7" rx="2"/><circle fill="url(#glowG)" cx="117" cy="199" r="16"/>'
# runner trail & second wearable person
b += person(330, 246, .8, shirt='#2f6f86') + '<rect class="goldf" x="312" y="208" width="8" height="6" rx="2"/>'
b += '<path class="acc dash" stroke-width="1.6" d="M256 86 L318 206"/>'
b += chip(250, 28, 'UAV', 'middle') + chip(16, 150, 'ULTRA-WIDEBAND PULSES') + chip(140, 284, 'WEARABLE SENSOR', 'middle') + chip(386, 150, 'CHANNEL MEASUREMENTS', 'end')
svg('uav-wearables', 'Drone-to-wearable links: a drone exchanges ultra-wideband pulses with wearable sensors on people below, and the team measures and models these channels', b)

# E. Gunshot detection substation
b = '<rect width="400" height="300" fill="url(#sky)"/>' + ground(232)
# power lines
b += '<path class="ink" d="M40 232 V90 M28 100 H52 M30 116 H50 M360 232 V90 M348 100 H372 M350 116 H370"/><path class="ink1" d="M28 100 Q200 140 348 100 M52 100 Q200 142 372 100"/>'
# transformers
for x in (130, 200):
    b += f'<g filter="url(#sh)"><rect class="mutef" x="{x}" y="176" width="52" height="56" rx="4"/></g>'
    for k in range(4): b += f'<rect class="paper" x="{x+6+k*11}" y="182" width="6" height="40" rx="1" opacity=".7"/>'
    b += f'<path class="ink1" d="M{x+12} 176 v-18 M{x+26} 176 v-24 M{x+40} 176 v-18"/><circle class="accf" cx="{x+26}" cy="150" r="4"/>'
# fence
b += '<path class="mute" d="M100 210 H300 M100 222 H300" stroke-width="1.4"/>'
for x in range(100, 304, 14): b += f'<path class="mute" d="M{x} 204 v28"/>'
# acoustic sensor pole
b += '<g filter="url(#sh)"><rect class="inkf" x="302" y="140" width="5" height="92" rx="2"/><rect fill="url(#metal)" x="292" y="126" width="24" height="18" rx="4"/></g><circle class="goldf" cx="304" cy="135" r="4"/>'
b += rings(304, 135, 3, 12, 10, 120, 240, 'gold')
# sound source
b += '<g opacity=".8">' + rings(70, 176, 3, 8, 9, -60, 60, 'acc') + '</g><circle class="accf" cx="70" cy="176" r="4"/>'
# alert panel
b += '<g filter="url(#sh)"><rect class="paper" x="290" y="30" width="96" height="58" rx="10"/></g><path class="accf" d="M312 74 l12 -24 l12 24 z"/><text class="lbl" x="330" y="69" style="font-size:9px;fill:#fff" text-anchor="middle">!</text><text class="lbl" x="342" y="56" style="font-size:9px">ALERT</text><text class="lbl" x="342" y="70" style="font-size:9px">GRID</text>'
b += chip(70, 150, 'GUNSHOT', 'middle') + chip(200, 284, 'SUBSTATION PROTECTION', 'middle') + chip(16, 40, 'ACOUSTIC + AI DETECTION')
svg('substation', 'Gunshot detection for energy substation protection: acoustic sensors on a pole detect a gunshot near a fenced substation and alert grid operators', b)

# F. Offshore lifting safety
b = '<rect width="400" height="200" fill="url(#sky)"/><rect class="tealsoft" x="0" y="200" width="400" height="100"/>'
for y in (220, 250, 280): b += f'<path class="teal" stroke-width="1.4" opacity=".5" d="M0 {y} q25 -6 50 0 t50 0 t50 0 t50 0 t50 0 t50 0 t50 0 t50 0"/>'
# platform
b += '<g filter="url(#sh)"><rect fill="url(#metal)" x="40" y="150" width="200" height="16" rx="2"/></g><path class="ink" d="M60 166 V290 M220 166 V290 M60 200 L220 260 M220 200 L60 260"/>'
b += '<rect class="paper" x="70" y="118" width="60" height="32" rx="2"/><path class="ink1" d="M70 118 h60 v32 h-60 z"/>'
# crane
b += '<path class="ink" d="M170 150 V70 L330 40 M170 70 L330 40 M178 150 L178 80"/>'
for i in range(5): b += f'<path class="ink1" d="M{186+i*28} {67-i*5.3:.1f} L{200+i*28} {64-i*5.3:.1f}"/>'
b += '<path class="ink1" d="M320 42 V140"/><g filter="url(#sh)"><rect class="goldf" x="304" y="140" width="34" height="26" rx="3"/></g>'
# radar scanning hook/wire
b += '<g filter="url(#sh)"><rect fill="url(#metal)" x="232" y="110" width="22" height="18" rx="3"/></g>'
b += taper(254, 118, 316, 110, 6, 26, 'url(#beamA)') + ticks(254, 118, 316, 110, 3, 8)
# robot crawler on platform
b += '<g filter="url(#sh)"><rect class="tealf" x="146" y="136" width="20" height="12" rx="3"/></g><circle class="inkf" cx="150" cy="149" r="2.5"/><circle class="inkf" cx="162" cy="149" r="2.5"/><path class="ink1" d="M156 136 v-6 h6"/>'
# digital twin inset
b += '<g filter="url(#sh)"><rect class="paper" x="290" y="200" width="96" height="80" rx="10"/></g>'
b += '<path class="acc" stroke-width="1.3" d="M304 266 V232 L366 216 M304 232 L366 216 M362 218 V246"/><rect class="acc" stroke-width="1.3" x="354" y="246" width="16" height="12" rx="2" fill="none"/><text class="lbl" x="338" y="274" text-anchor="middle" style="font-size:9px">DIGITAL TWIN</text>'
b += chip(250, 30, 'mmWave RADAR NDT', 'middle') + chip(16, 106, 'INSPECTION ROBOT')
svg('offshore', 'Offshore lifting safety: on an offshore platform, a millimeter-wave radar inspects the crane wire and hook, a small robot inspects the structure, and a digital twin predicts problems', b)

# G. Rail track transitions with fiber sensors
b = '<rect width="400" height="300" fill="url(#sky)"/>' + ground(200)
# bridge deck left, embankment right
b += '<g filter="url(#sh)"><rect class="mutef" x="0" y="184" width="180" height="16"/><rect class="mutef" x="20" y="200" width="18" height="60"/><rect class="mutef" x="120" y="200" width="18" height="60"/></g>'
b += '<path fill="url(#soil)" d="M180 200 L180 184 H400 V300 H180 Z" opacity=".55"/>'
# rails & ties
for x in range(6, 400, 18): b += f'<rect class="inkf" opacity=".55" x="{x}" y="180" width="8" height="6" rx="1"/>'
b += '<path class="ink" d="M0 178 H400"/><path class="ink1" d="M0 182 H400"/>'
# fiber line with sensing points
b += '<path class="teal" stroke-width="2.2" d="M0 192 H400"/>'
for x in range(40, 400, 50): b += f'<circle class="paper" cx="{x}" cy="192" r="4"/><circle class="teal" stroke-width="1.6" cx="{x}" cy="192" r="4"/>'
b += '<circle fill="url(#glowA)" cx="180" cy="186" r="30"/><path class="acc" stroke-width="2" d="M172 206 l8 -10 l8 10" />'
# train
b += '<g filter="url(#sh)"><path fill="url(#metal)" d="M230 176 V128 q0 -12 12 -12 h120 q16 0 24 14 l12 22 v24 z"/></g>'
for i in range(4): b += f'<rect class="tealsoft" x="{246+i*28}" y="130" width="20" height="16" rx="2"/>'
b += '<rect class="goldf" x="384" y="150" width="8" height="8" rx="2"/>' + ''.join(f'<circle class="inkf" cx="{x}" cy="177" r="6"/><circle class="mutef" cx="{x}" cy="177" r="2"/>' for x in (250, 272, 350, 372))
# monitor panel
b += '<g filter="url(#sh)"><rect class="paper" x="16" y="26" width="150" height="78" rx="10"/></g><path class="ink1" d="M28 92 H154 M28 92 V40"/>'
b += '<path class="teal" stroke-width="1.8" d="M30 80 C60 80 70 78 84 70 C92 50 98 46 104 66 C112 78 130 80 152 80"/><circle class="accf" cx="98" cy="50" r="3"/>'
b += '<text class="lbl" x="34" y="44" style="font-size:9px">STRAIN</text>'
b += chip(386, 40, 'OPTICAL FIBER SENSORS', 'end') + chip(200, 284, 'BRIDGE-TO-EMBANKMENT TRANSITION', 'middle')
svg('rail', 'Intelligent rail track transitions: optical fiber sensors along the rail measure strain where a bridge meets the embankment as a train passes, and a monitor flags the weak spot', b)

# H. NASA 6G platform testbed
b = '<rect x="0" y="0" width="400" height="214" fill="url(#wall)"/><polygon class="soft" points="0,214 400,214 400,300 0,300"/><path class="ink1" d="M0 214 H400"/>'
# rack
b += '<g filter="url(#sh)"><rect class="inkf" x="30" y="60" width="90" height="170" rx="6"/></g>'
for i in range(6):
    b += f'<rect fill="url(#metal)" x="38" y="{70+i*26}" width="74" height="20" rx="3"/><circle class="goldf" cx="{48}" cy="{80+i*26}" r="2.5"/><rect class="paper" x="58" y="{77+i*26}" width="40" height="5" rx="1" opacity=".6"/>'
# antenna array panels
for (x, y) in [(170, 90), (330, 100)]:
    b += f'<g filter="url(#sh)"><rect class="paper" x="{x}" y="{y}" width="50" height="60" rx="5"/></g>'
    for r in range(4):
        for c in range(3): b += f'<rect class="accf" x="{x+7+c*14}" y="{y+7+r*13}" width="9" height="9" rx="1.5"/>'
    b += f'<path class="ink" d="M{x+25} {y+60} V214"/>'
b += taper(220, 120, 330, 128, 10, 22, 'url(#beamA)') + ticks(220, 120, 330, 128, 4, 9)
# sensing target
b += '<g filter="url(#sh)"><circle class="tealf" cx="272" cy="196" r="12"/></g>' + rings(272, 196, 2, 18, 9, -150, -30, 'teal')
b += '<path class="gold dash" stroke-width="1.6" d="M220 136 L264 186 M330 140 L282 186"/>'
# laptop
b += '<g filter="url(#sh)"><path class="inkf" d="M140 250 l6 -30 h48 l-4 30 z"/></g><rect class="paper" x="150" y="224" width="40" height="22" rx="2"/><path class="acc" stroke-width="1.2" d="M153 240 l6 -8 l6 4 l6 -10 l6 6 l8 -4"/>'
b += chip(75, 40, 'SDR RACK', 'middle') + chip(276, 60, '6G COMMUNICATION', 'middle') + chip(386, 262, 'JOINT SENSING', 'end')
svg('testbed-6g', 'Versatile 6G experimental platform: a rack of software-defined radios drives two antenna arrays that communicate with each other and sense a target at the same time, monitored from a laptop', b)
print('extra ok')
