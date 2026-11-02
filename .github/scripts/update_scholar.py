"""Update the citation count and h-index on index.html from the Google Scholar profile.

Run weekly on Sabit's Mac by tools/scholar_weekly.sh (launchd), or by hand: python3 .github/scripts/update_scholar.py
Writes nothing if Scholar cannot be read or the numbers look wrong (exits 1).
"""
import datetime, re, sys, urllib.request

PROFILE = 'https://scholar.google.com/citations?user=cgJM6k0AAAAJ&hl=en'
PAGE = 'index.html'
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36'

def fetch():
    req = urllib.request.Request(PROFILE, headers={'User-Agent': UA, 'Accept-Language': 'en-US,en;q=0.9'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode('utf-8', 'replace')

def main():
    try:
        html = fetch()
    except Exception as e:
        sys.exit(f'Could not reach Google Scholar: {e}')
    # profile table: citations (all, since), h-index (all, since), i10-index (all, since)
    nums = [int(n) for n in re.findall(r'class="gsc_rsb_std">(\d+)<', html)]
    if len(nums) < 4:
        sys.exit('Google Scholar did not return the profile table (likely blocked); nothing changed.')
    cites, h = nums[0], nums[2]

    page = open(PAGE, encoding='utf-8').read()
    # the card also names the source and month: <small><a href="…">Google Scholar</a>, November&nbsp;2026</small>
    stat = re.search(r'<div class="stat"><b>([\d,]+)\+</b><span>citations · h-index (\d+)</span>'
                     r'<small>(<a href="[^"]+">Google Scholar</a>), [A-Z][a-z]+&nbsp;\d{4}</small></div>', page)
    if not stat:
        sys.exit('Citation stat not found in index.html; nothing changed.')
    old_cites = int(stat.group(1).replace(',', ''))
    if cites < old_cites * 0.9 or h < 1:
        sys.exit(f'Numbers look wrong (Scholar {cites}, page {old_cites}+); nothing changed.')

    shown = f'{cites // 10 * 10:,}'          # rounded down to the nearest 10, shown with "+"
    month = datetime.date.today().strftime('%B %Y')
    new = page.replace(stat.group(0), f'<div class="stat"><b>{shown}+</b><span>citations · h-index {h}</span>'
                                      f'<small>{stat.group(3)}, {month.replace(" ", "&nbsp;")}</small></div>')
    if new == page:
        print(f'No change ({shown}+ citations, h-index {h}).')
        return
    new = re.sub(r'Last updated [A-Z][a-z]+ \d{4}', f'Last updated {month}', new)
    open(PAGE, 'w', encoding='utf-8').write(new)
    print(f'Updated: {shown}+ citations, h-index {h} (Scholar: {cites}).')

if __name__ == '__main__':
    main()
