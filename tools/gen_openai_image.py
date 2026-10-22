"""Generate a project figure with the OpenAI image API, using an existing render as the style reference.

The API key is read from the OPENAI_API_KEY environment variable, or from ~/.config/openai/key
(one line, chmod 600). It is never printed or written anywhere else.

Usage:
  python3 tools/gen_openai_image.py --list-models
  python3 tools/gen_openai_image.py --name v2x --ref tools/renders/formula3.webp \
      --prompt-file tools/image_prompts/v2x.txt [--model gpt-image-1] [--n 2]
Output: tools/scenes/out/openai-<name>-<i>.png (git-ignored); then convert with cwebp to tools/renders/.
"""
import argparse, base64, os, sys
from pathlib import Path

from openai import OpenAI


def api_key():
    k = os.environ.get('OPENAI_API_KEY', '').strip()
    f = Path.home() / '.config' / 'openai' / 'key'
    if not k and f.exists():
        k = f.read_text().strip()
    if not k:
        sys.exit('No API key: set OPENAI_API_KEY or create ~/.config/openai/key (chmod 600).')
    return k


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--list-models', action='store_true')
    ap.add_argument('--name')
    ap.add_argument('--ref', action='append', default=[])
    ap.add_argument('--prompt-file')
    ap.add_argument('--model', default='gpt-image-1')
    ap.add_argument('--size', default='1536x1024')
    ap.add_argument('--quality', default='high')
    ap.add_argument('--n', type=int, default=1)
    a = ap.parse_args()
    client = OpenAI(api_key=api_key())
    if a.list_models:
        ids = sorted(m.id for m in client.models.list() if 'image' in m.id or 'dall' in m.id)
        print('\n'.join(ids) or '(no image models visible to this key)')
        return
    prompt = Path(a.prompt_file).read_text().strip()
    out = Path(__file__).resolve().parent / 'scenes' / 'out'
    out.mkdir(parents=True, exist_ok=True)
    refs = [open(r, 'rb') for r in a.ref]
    try:
        if refs:
            r = client.images.edit(model=a.model, image=refs, prompt=prompt, size=a.size, quality=a.quality, n=a.n)
        else:
            r = client.images.generate(model=a.model, prompt=prompt, size=a.size, quality=a.quality, n=a.n)
    finally:
        for f in refs:
            f.close()
    for i, d in enumerate(r.data, 1):
        p = out / f'openai-{a.name}-{i}.png'
        p.write_bytes(base64.b64decode(d.b64_json))
        print('saved', p)


if __name__ == '__main__':
    main()
