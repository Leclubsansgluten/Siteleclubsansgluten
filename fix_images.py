#!/usr/bin/env python3
"""
Remplace TOUTES les images de TOUS les articles via Pexels.
"""
import os, re, json, urllib.request, urllib.parse
 
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')
 
FALLBACK = {
    'recettes': 'https://images.pexels.com/photos/1640777/pexels-photo-1640777.jpeg?w=1200',
    'sante':    'https://images.pexels.com/photos/1640777/pexels-photo-1640777.jpeg?w=1200',
    'farines':  'https://images.pexels.com/photos/1640777/pexels-photo-1640777.jpeg?w=1200',
    'guides':   'https://images.pexels.com/photos/1640777/pexels-photo-1640777.jpeg?w=1200',
}
 
def get_pexels_image(titre, cat):
    try:
        query = ' '.join(titre.replace(':', '').replace('—', '').split()[:5])
        url = f'https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=1&orientation=landscape'
        req = urllib.request.Request(url, headers={
            'Authorization': PEXELS_KEY,
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json',
        })
        data = json.loads(urllib.request.urlopen(req, timeout=15).read())
        if data.get('photos'):
            return data['photos'][0]['src']['large2x']
    except Exception as e:
        print(f'  Pexels erreur: {e}')
    return FALLBACK.get(cat)
 
count = 0
for cat in ['recettes', 'sante', 'farines', 'guides']:
    if not os.path.exists(cat):
        continue
    for f in sorted(os.listdir(cat)):
        if not f.endswith('.html') or f == 'index.html':
            continue
        path = f'{cat}/{f}'
        html = open(path).read()
        
        # Extraire le titre
        tm = re.search(r'<title>(.*?) — Le Club', html)
        titre = tm.group(1) if tm else f.replace('-', ' ').replace('.html', '')
        
        # Chercher image Pexels
        new_img = get_pexels_image(titre, cat)
        
        # Remplacer l'image hero
        html = re.sub(
            r'(<img class="article-hero"[^>]+src=")[^"]+(")',
            rf'\g<1>{new_img}\g<2>',
            html
        )
        # Remplacer og:image
        html = re.sub(
            r'(<meta property="og:image" content=")[^"]+(")',
            rf'\g<1>{new_img}\g<2>',
            html
        )
        # Remplacer dans schema
        html = re.sub(
            r'("image":")[^"]+(")',
            rf'\g<1>{new_img}\g<2>',
            html
        )
        
        open(path, 'w').write(html)
        count += 1
        print(f'✅ {cat}/{f.replace(".html","")} → {new_img[:60]}...')
 
print(f'\n✅ {count} articles mis à jour avec images Pexels')
 
