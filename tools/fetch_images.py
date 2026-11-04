"""Velocity USA 공식 사이트(velocityusa.com, Shopify)에서 이미지를 받아 images/ 에 저장합니다.

GitHub Actions(.github/workflows/fetch-images.yml)에서 실행됩니다. 로컬에서도 실행할 수 있습니다:
  python3 tools/fetch_images.py

- 제품 이미지: /products.json 에서 제목이 맞는 제품을 찾아 images/<모델>/01.jpg ... 로 저장
- 브랜드 이미지: 메인, About 페이지의 큰 이미지를 images/brand/, images/hero/ 로 저장
- og.jpg: 메인 페이지의 og:image
이미 있는 파일은 건너뜁니다. 교체하려면 파일을 지우고 다시 실행하세요.
받은 원본 주소는 images/_sources.txt 에 기록됩니다.
"""
import json, re, sys, time, pathlib, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
IMG = ROOT / 'images'
BASE = 'https://velocityusa.com'
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36'

# 폴더: (제품 제목 정규식, 받을 장 수). 제목이 맞는 제품 중 이미지가 가장 많은 것부터 채웁니다.
MODELS = {
    'deepv':       (r'^deep v\b(?!.*(wheel|atb))', 4),
    'chukker':     (r'^chukker\b(?!.*wheel)', 3),
    'quill':       (r'^quill\b(?!.*wheel)', 3),
    'aileron':     (r'^aileron\b(?!.*wheel)', 3),
    'cliffhanger': (r'^cliffhanger\b(?!.*wheel)', 3),
    'atlas':       (r'^atlas\b(?!.*wheel)', 3),
    'bluntss':     (r'^blunt ss\b(?!.*wheel)', 3),
    'blunt35':     (r'^blunt 35\b(?!.*wheel)', 3),
    'dually':      (r'^dually\b(?!.*wheel)', 3),
}
PAGES = ['/', '/pages/about', '/pages/the-wheel-department', '/collections/wheels']

log = []

def get(url, accept='*/*'):
    req = urllib.request.Request(url, headers={'User-Agent': UA, 'Accept': accept, 'Referer': BASE + '/'})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()

def sized(src, w=1600):
    src = 'https:' + src if src.startswith('//') else src
    src = re.sub(r'([?&])width=\d+&?', r'\1', src).rstrip('?&')
    return src + ('&' if '?' in src else '?') + f'width={w}'

def save(src, dest, w=1600):
    dest = IMG / dest
    if dest.exists() and dest.stat().st_size > 0:
        print('skip ', dest.relative_to(ROOT)); return True
    dest.parent.mkdir(parents=True, exist_ok=True)
    url = sized(src, w)
    for i in range(3):
        try:
            data = get(url, 'image/jpeg,image/png;q=0.9,image/webp;q=0.8,*/*;q=0.5')
            dest.write_bytes(data)
            log.append(f'{dest.relative_to(ROOT)}\t{url}')
            print('ok   ', dest.relative_to(ROOT), len(data), 'bytes'); return True
        except Exception as e:
            err = e; time.sleep(2 * (i + 1))
    print('FAIL ', url, err); return False

def products():
    out, page = [], 1
    while True:
        data = json.loads(get(f'{BASE}/products.json?limit=250&page={page}', 'application/json'))
        items = data.get('products', [])
        out += items
        if len(items) < 250: return out
        page += 1

def fetch_products():
    items = products()
    print(len(items), 'products')
    fails = 0
    for folder, (pat, n) in MODELS.items():
        rx = re.compile(pat, re.I)
        hits = sorted([p for p in items if rx.search(p['title'].strip())], key=lambda p: -len(p.get('images', [])))
        srcs, seen = [], set()
        for p in hits:
            for im in p.get('images', []):
                key = im['src'].split('?')[0].rsplit('/', 1)[-1]
                if key not in seen:
                    seen.add(key); srcs.append(im['src'])
        print(f'{folder}: {len(hits)} products ({", ".join(p["title"] for p in hits[:3])}) {len(srcs)} images')
        if not srcs:
            print('FAIL  no product matched', pat); fails += 1; continue
        for i in range(n):
            # 이미지가 모자라면 앞의 것을 반복해 빈 칸을 남기지 않습니다.
            fails += not save(srcs[i % len(srcs)], f'{folder}/{i + 1:02d}.jpg')
    return fails

def page_images():
    srcs, seen, og = [], set(), None
    for path in PAGES:
        try:
            html = get(BASE + path, 'text/html').decode('utf-8', 'replace')
        except Exception as e:
            print('skip page', path, e); continue
        if og is None:
            m = re.search(r'<meta[^>]+property="og:image"[^>]+content="([^"]+)"', html)
            og = m and m.group(1)
        for m in re.finditer(r'(?:https?:)?//[\w.-]+/(?:cdn/shop|s/files)/[^"\'\s)]+?\.(?:jpe?g|png|webp)(?:\?[^"\'\s)]*)?', html, re.I):
            src = m.group(0).replace('&amp;', '&')
            name = src.split('?')[0].rsplit('/', 1)[-1].lower()
            if re.search(r'logo|icon|favicon|badge|payment|flag|svg', name):
                continue
            key = re.sub(r'_\d+x\d*|_(small|medium|large|grande)', '', name)
            if key not in seen:
                seen.add(key); srcs.append(src)
    return og, srcs

def fetch_brand():
    og, srcs = page_images()
    print(len(srcs), 'page images')
    fails = 0
    if og:
        fails += not save(og, 'og.jpg', 2400)
    if not srcs:
        print('FAIL  no page images'); return fails + 1
    for i in range(4):
        fails += not save(srcs[i % len(srcs)], f'hero/{i + 1:02d}.jpg', 2400)
    rest = srcs[4:] or srcs
    for i in range(9):
        fails += not save(rest[i % len(rest)], f'brand/{i + 1:02d}.jpg', 2400 if i == 0 else 1600)
    return fails

if __name__ == '__main__':
    fails = fetch_products() + fetch_brand()
    if log:
        with open(IMG / '_sources.txt', 'a') as f:
            f.write('\n'.join(log) + '\n')
    print('fails:', fails)
    sys.exit(1 if fails else 0)
