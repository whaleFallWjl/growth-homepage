from html.parser import HTMLParser
from pathlib import Path
import subprocess
import tempfile
import os

class Check(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.anchors = []
        self.assets = []
        self.scripts = []
        self.in_script = False
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a:
            self.ids.append(a['id'])
        if tag == 'a' and a.get('href', '').startswith('#'):
            self.anchors.append(a['href'][1:])
        if 'src' in a or tag == 'link':
            self.assets.append(a)
        if tag == 'script':
            self.in_script = True
    def handle_endtag(self, tag):
        if tag == 'script':
            self.in_script = False
    def handle_data(self, data):
        if self.in_script:
            self.scripts.append(data)

root = Path(__file__).resolve().parent
html = (root / 'index.html').read_text()
c = Check()
c.feed(html)
assert len(c.ids) == len(set(c.ids)), 'duplicate IDs'
assert all(not a or a in c.ids for a in c.anchors), 'broken anchor'
assert not c.assets, 'unexpected asset dependency'
assert '<html lang="zh-CN">' in html
assert 'prefers-reduced-motion' in html
assert html.rstrip().endswith('</body></html>')
with tempfile.TemporaryDirectory(dir=os.environ.get('TMPDIR')) as tmp:
    js = Path(tmp) / 'script.js'
    js.write_text('\n'.join(c.scripts))
    subprocess.run(['node', '--check', str(js)], check=True)
print('PASS: unique IDs, anchors, no asset dependencies, language, reduced motion, complete HTML, JS syntax')
