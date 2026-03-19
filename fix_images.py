#!/usr/bin/env python3
"""
Corrige toutes les images cassées ou en doublon via l'API Pexels.
Lance une fois manuellement depuis GitHub Actions.
"""
import os, re, json, urllib.request, urllib.parse

PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')
DEFAULT_PATTERN = r'https://images\.unsplash\.com/photo-1509440159596-0249088772ff[^"\']*'

FALLBACK = {
    'recettes': 'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=1200&q=80',
    'sante':    'https://images.unsplash.com/photo-1540420773420-3366772f4999?w=1200&q=80',
    'farines':  'https://images.unsplash.com/photo-1612200606649-1e95b16fcf2c?w=1200&q=80',
    'guides':   'https://images.unsplash.com/photo-1499636136210-6f4ee915583e?w=1200&q=80',
}

def get_pexels_image(titre, cat):
    try:
        query = ' '.join(titre.replace(':', '').replace('—', '').split()[:5])
        url = f'https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=1&orientation=landscape'
        req = urllib.request.Request(url, headers={'Authorization': PEXELS_KEY})
        data = json.loads(urllib.request.urlopen(req, timeout=10).read())
        if data.get('photos'):
            return data['photos'][0]['src']['large2x']
    except Exception as e:
        print(f'  ⚠️ Pexels: {e}')
    return FALLBACK.get(cat, FALLBACK['recettes'])

count = 0
for cat in ['recettes', 'sante', 'farines', 'guides']:
    if not os.path.exists(cat):
        continue
    for f in sorted(os.listdir(cat)):
        if not f.endswith('.html') or f == 'index.html':
            continue
        path = f'{cat}/{f}'
        html = open(path).read()
        if not re.search(DEFAULT_PATTERN, html):
            continue
        # Extraire le titre
        tm = re.search(r'<title>(.*?) — Le Club', html)
        titre = tm.group(1) if tm else f.replace('-', ' ').replace('.html', '')
        # Chercher une image Pexels
        new_img = get_pexels_image(titre, cat)
        # Remplacer toutes les occurrences
        html = re.sub(DEFAULT_PATTERN, new_img, html)
        html = re.sub(r'(<meta property="og:image" content=")[^"]+(")', rf'\g<1>{new_img}\g<2>', html)
        html = re.sub(r'("image":")[^"]+(")', rf'\g<1>{new_img}\g<2>', html)
        open(path, 'w').write(html)
        count += 1
        print(f'✅ {cat}/{f.replace(".html","")} → {new_img[:60]}...')

print(f'\n✅ {count} articles corrigés')
