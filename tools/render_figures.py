"""Project figures from Higgsfield 3D renders, with the label pills of project_figures.py.

Each figure is a 400x300 SVG that embeds a WebP render (tools/renders/<name>.webp) and draws
labels on top, so the page still loads assets/projects/<name>.svg through <img>.
Usage: python3 tools/render_figures.py assets/projects [name ...]
"""
import sys, os, base64

out = sys.argv[1]
only = set(sys.argv[2:])
here = os.path.dirname(os.path.abspath(__file__))
W, H = 400, 300
CSS = """
.lbl{font:700 10.5px Inter,system-ui,sans-serif;fill:#5a514a;letter-spacing:.06em}
.chip{fill:#fffdfb;stroke:#d9cec3;stroke-width:1}
@media (prefers-color-scheme:dark){.lbl{fill:#b3a99f}.chip{fill:#2f2723;stroke:#4a413a}.pic{filter:brightness(.82) saturate(.9)}}
"""
DEFS = ('<filter id="sh" x="-20%" y="-20%" width="140%" height="160%">'
        '<feDropShadow dx="0" dy="2.5" stdDeviation="2.5" flood-color="#000" flood-opacity=".18"/></filter>')


def chip(x, y, text, anchor='start'):
    w = 7.2 * len(text.replace('&amp;', '&')) + 16
    x0 = x if anchor == 'start' else (x - w if anchor == 'end' else x - w/2)
    return (f'<g filter="url(#sh)"><rect class="chip" x="{x0:.1f}" y="{y-10}" width="{w:.1f}" height="20" rx="10"/></g>'
            f'<text class="lbl" x="{x0+w/2:.1f}" y="{y+3.6}" text-anchor="middle">{text}</text>')


def figure(name, title, chips):
    if only and name not in only:
        return
    data = base64.b64encode(open(os.path.join(here, 'renders', name + '.webp'), 'rb').read()).decode()
    body = ''.join(chip(*c) for c in chips)
    s = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t"><title id="t">{title}</title>'
         f'<style>{CSS}</style><defs>{DEFS}</defs>'
         f'<image class="pic" width="{W}" height="{H}" preserveAspectRatio="xMidYMid slice" href="data:image/webp;base64,{data}"/>'
         f'{body}</svg>')
    open(os.path.join(out, name + '.svg'), 'w').write(s)


figure('formula3', 'FORMULA3: an AI controller predicts blockage and reconfigures a transmissive smart surface on a window and a metallic reflector array indoors so that an upper mid-band (FR3) link from an outdoor base station reaches a user while another person walks through the room',
       [(16, 30, '7–24 GHz FR3'), (188, 104, 'TRANSMISSIVE RIS', 'middle'),
        (386, 62, 'REFLECTOR ARRAY', 'end'), (16, 286, 'PREDICT &amp; ADAPT')])

figure('lunarcom', 'Hybrid lunar communication: a ground station on Earth reaches a lunar gateway and a rover on the Moon through both a wide radio link and a narrow optical laser link',
       [(190, 30, 'LUNAR GATEWAY', 'middle'), (150, 112, 'RF', 'middle'), (262, 214, 'OPTICAL', 'middle'),
        (60, 286, 'EARTH', 'middle'), (366, 182, 'MOON', 'middle')])

figure('prime-spectrum', 'Spectrum reallocation: line-of-sight satellite links move from congested sub-10 GHz spectrum to Ku and Ka bands, with AI rain-fade prediction, freeing the lower bands for mobile and broadband coverage in cities',
       [(16, 282, 'SUB-10 GHz FOR MOBILE'), (386, 282, 'Ku / Ka EARTH STATION', 'end'), (280, 30, 'RAIN-FADE AWARE AI', 'middle')])

figure('commawarenet', 'Hybrid terahertz and visible-light network in a smart room: a ceiling luminaire lights a desk user while its terahertz beam is redirected by a smart surface to a second user',
       [(16, 140, 'VISIBLE LIGHT'), (290, 30, 'THz BEAM', 'middle'), (386, 250, 'SMART SURFACE', 'end')])

figure('substation', 'Gunshot detection for energy substation protection: acoustic sensors on a pole detect a gunshot near a fenced substation and alert grid operators',
       [(45, 150, 'GUNSHOT', 'middle'), (200, 284, 'SUBSTATION PROTECTION', 'middle'), (16, 30, 'ACOUSTIC + AI DETECTION')])

figure('offshore', 'Offshore lifting safety: on an offshore platform, a millimeter-wave radar inspects the crane wire and hook, a small robot inspects the structure, and a digital twin predicts problems',
       [(16, 236, 'mmWave RADAR NDT'), (300, 250, 'INSPECTION ROBOT', 'middle'), (386, 282, 'DIGITAL TWIN', 'end')])

figure('rail', 'Intelligent rail track transitions: optical fiber sensors along the rail measure strain where a bridge meets the embankment as a train passes, and a monitor flags the weak spot',
       [(386, 250, 'OPTICAL FIBER SENSORS', 'end'), (200, 284, 'BRIDGE-TO-EMBANKMENT TRANSITION', 'middle')])

figure('testbed-6g', 'Versatile 6G experimental platform: a rack of software-defined radios drives two antenna arrays that communicate with each other and sense a target at the same time, monitored from a laptop',
       [(60, 230, 'SDR RACK', 'middle'), (180, 30, '6G COMMUNICATION', 'middle'), (330, 280, 'JOINT SENSING', 'middle')])

figure('spidernet', 'Demand-driven elastic network over a city: base stations near users are switched on and linked in a web, while idle ones sleep to save energy',
       [(60, 30, 'SLEEPING', 'middle'), (340, 50, 'ACTIVE', 'middle')])

figure('lightwave-sensing', 'Non-contact light-wave sensing: a ceiling lamp lights a seated person, a photodetector on the desk captures light reflected from the chest, and the signal reveals breathing and heartbeat',
       [(130, 20, 'LED LIGHTING'), (205, 68, 'REFLECTED LIGHT', 'middle'), (386, 250, 'BREATHING', 'end'), (386, 278, 'HEARTBEAT', 'end')])

figure('vildar', 'Visible-light detection and ranging: an approaching car’s headlights reach a roadside photodetector, and the rising received power over time gives the car’s speed',
       [(200, 60, 'PHOTODETECTOR', 'middle'), (16, 30, 'SPEED FROM HEADLIGHTS')])

figure('faa-ils', 'FAA instrument landing system measurements: a drone carrying a software-defined radio flies the approach path and measures the localizer signal from the antenna array at the end of the runway',
       [(200, 90, 'ILS LOCALIZER SIGNAL', 'middle'), (16, 120, 'DRONE-BORNE SDR'), (200, 284, 'ZONE 3 MEASUREMENTS', 'middle')])

figure('cubesat-cr', 'Cognitive radio for small satellites: three CubeSats share a network and sense the spectrum, using free channels to reach a ground station on Earth',
       [(80, 40, 'CUBESAT NETWORK', 'middle'), (386, 100, 'COGNITIVE RADIO', 'end'), (180, 270, 'GROUND STATION', 'middle')])

figure('mmwave-thz', 'Millimeter-wave and terahertz channels: a drone sends a narrow beam to a ground phased array while rain attenuates the link and a building and the ground create reflected multipath',
       [(220, 40, 'mmWave / THz', 'middle'), (330, 40, 'REFLECTION', 'middle'), (16, 130, 'RAIN FADE'), (300, 250, 'MULTIPATH', 'middle')])

figure('rural-iot', 'Rural Internet of Things: tagged cattle and an underground soil sensor on a farm send data over long-range LoRa radio to a gateway tower on the hill',
       [(290, 30, 'LoRa GATEWAY', 'end'), (386, 290, 'UNDERGROUND SOIL SENSOR', 'end'), (16, 120, 'TAGGED CATTLE')])

figure('radar-bp', 'Non-invasive blood-pressure sensing: a millimeter-wave radar on a desk steers beams to a seated person’s wrist and neck at the same time and recovers the arterial pulse waveform',
       [(310, 228, 'mmWave RADAR', 'middle'), (150, 200, 'WRIST', 'middle'), (200, 20, 'NECK', 'middle')])

# Rendered locally with three.js (tools/scenes/), not Higgsfield.
figure('uav-wearables', 'Drone-to-wearable links: a drone exchanges ultra-wideband pulses with wearable sensors on people below, and the team measures and models these channels',
       [(200, 44, 'UAV', 'middle'), (310, 128, 'ULTRA-WIDEBAND PULSES', 'middle'), (16, 128, 'WEARABLE SENSOR'), (392, 236, 'CHANNEL MEASUREMENTS', 'end')])

figure('v2x', 'Hybrid visible-light and radio vehicle links: a following car talks to the car ahead through headlight and taillight light, while a roadside unit provides a radio backup link to both',
       [(240, 30, 'RF (DSRC) BACKUP', 'middle'), (100, 195, 'HEADLIGHTS', 'middle'), (250, 222, 'TAILLIGHTS', 'middle'), (200, 282, 'VISIBLE-LIGHT V2V', 'middle')])
