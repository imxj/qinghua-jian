"""Build a self-contained Pages artifact using only the Python standard library."""
import json
import shutil
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit, parse_qs

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / '_site'
subprocess.run([sys.executable, str(ROOT / 'tools/build_reading.py')], cwd=ROOT, check=True)
if SITE.exists():
    shutil.rmtree(SITE)
SITE.mkdir()
for name in ['index.html', 'reading.html', 'gallery.html', 'annotations.json', 'image-index.json']:
    shutil.copy2(ROOT / name, SITE / name)
if (ROOT / 'favicon.svg').exists():
    shutil.copy2(ROOT / 'favicon.svg', SITE / 'favicon.svg')
shutil.copytree(ROOT / 'photos', SITE / 'photos')
(SITE / 'sources').mkdir()
shutil.copy2(ROOT / 'sources/qinghua-exhibition-2016-public.pdf', SITE / 'sources/qinghua-exhibition-2016-public.pdf')
(SITE / '.nojekyll').write_text('')

data = json.loads((SITE / 'annotations.json').read_text())
slip_keys = {row['key'] for row in data['slips']}
image_ids = {row['id'] for row in data['images']}
catalog = json.loads((SITE / 'image-index.json').read_text())
assert {r['id'] for r in catalog['original_images']} <= image_ids
assert len(slip_keys) == len(data['slips'])
for row in data['images']:
    assert set(row['slip_keys']) <= slip_keys, row['id']
    assert (SITE / row['local_path']).is_file(), row['local_path']
    assert row['observation'] and row['status'], row['id']

class Links(HTMLParser):
    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key not in ('href', 'src') or not value:
                continue
            parts = urlsplit(value)
            if parts.scheme or parts.netloc or not parts.path:
                continue
            assert not parts.path.startswith('/'), ('root-relative URL', value)
            target = SITE / unquote(parts.path)
            if target.is_dir():
                target = target / 'index.html'
            assert target.is_file(), ('missing local asset', value)
            if parts.path == 'reading.html' and parts.fragment:
                params = parse_qs(parts.fragment)
                for key in params.get('slip', []):
                    assert key in slip_keys, ('unknown slip link', key)
                for key in params.get('image', []):
                    assert key in image_ids, ('unknown image link', key)

for page in SITE.glob('*.html'):
    Links().feed(page.read_text())
for path in list(SITE.glob('*.html')) + list(SITE.glob('*.json')):
    text = path.read_text()
    assert '/Users/' not in text and 'file://' not in text, ('local machine reference', path.name)
print(json.dumps({'site': str(SITE.relative_to(ROOT)), **data['stats']}, ensure_ascii=False, indent=2))
