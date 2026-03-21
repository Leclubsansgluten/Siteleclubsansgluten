#!/usr/bin/env python3
"""
Corrige toutes les images de tous les articles via Pexels + Unsplash.
Claude API choisit le meilleur mot-cle de recherche en anglais pour chaque article.
"""
import os, re, json, urllib.request, urllib.parse, subprocess

PEXELS_KEY   = os.environ.get('PEXELS_API_KEY', '')
UNSPLASH_KEY = os.environ.get('UNSPLASH_API_KEY', '')
ANTHROPIC_KEY = os.environ.get('ANTHROPIC_API_KEY', '')

_counter = 0

FALLBACK_POOL = [
    'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=1200&q=80',
    'https://images.unsplash.com/photo-1540420773420-3366772f4999?w=1200&q=80',
    'https://images.unsplash.com/photo-1612200606649-1e95b16fcf2c?w=1200&q=80',
    'https://images.unsplash.com/photo-1547592180-85f173990554?w=1200&q=80',
    'https://images.unsplash.com/photo-1519676867240-f03562e64548?w=1200&q=80',
    'https://images.unsplash.com/photo-1606313564200-e75d5e30476c?w=1200&q=80',
    'https://images.unsplash.com/photo-1568571780765-9276ac8b75a2?w=1200&q=80',
    'https://images.unsplash.com/photo-1574894709920-11b28e7367e3?w=1200&q=80',
    'https://images.unsplash.com/photo-1513104890138-7c749659a591?w=1200&q=80',
    'https://images.unsplash.com/photo-1499636136210-6f4ee915583e?w=1200&q=80',
]

def get_keyword(titre):
    """Demande a Claude le meilleur mot-cle de recherche en anglais."""
    try:
        payload = json.dumps({
            "model": "claude-haiku-4-5-20251001",
            "max_tokens": 20,
            "messages": [{
                "role": "user",
                "content": f"Give me 2-3 English keywords for a food/health photo search for this French article title: '{titre}'. Reply ONLY with the keywords, nothing else. Example: 'chocolate cake' or 'gluten free bread' or 'woman fatigue'"
            }]
        })
        result = subprocess.run(
            ['curl', '-s', 'https://api.anthropic.com/v1/messages',
             '-H', f'x-api-key: {ANTHROPIC_KEY}',
             '-H', 'anthropic-version: 2023-06-01',
             '-H', 'content-type: application/json',
             '-d', payload],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(result.stdout)
        keyword = data['content'][0]['text'].strip().strip('"').strip("'")
        return keyword
    except Exception as e:
        return ''

def search_image(keyword):
    """Cherche une image sur Pexels puis Unsplash."""
    global _counter
    _counter += 1

    # Pexels
    if PEXELS_KEY:
        try:
            page = (_counter % 5) + 1
            url = f'https://api.pexels.com/v1/search?query={urllib.parse.quote(keyword)}&per_page=5&page={page}&orientation=landscape'
            req = urllib.request.Request(url, headers={
                'Authorization': PEXELS_KEY,
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            })
            data = json.loads(urllib.request.urlopen(req, timeout=15).read())
            if data.get('photos'):
                idx = (_counter - 1) % len(data['photos'])
                return data['photos'][idx]['src']['large2x'], 'Pexels'
        except Exception as e:
            pass

    # Unsplash
    if UNSPLASH_KEY:
        try:
            page = (_counter % 10) + 1
            url = f'https://api.unsplash.com/search/photos?query={urllib.parse.quote(keyword)}&per_page=10&page={page}&orientation=landscape'
            req = urllib.request.Request(url, headers={
                'Authorization': f'Client-ID {UNSPLASH_KEY}',
                'Accept-Version': 'v1',
            })
            data = json.loads(urllib.request.urlopen(req, timeout=15).read())
            if data.get('results'):
                idx = (_counter - 1) % len(data['results'])
                return data['results'][idx]['urls']['regular'], 'Unsplash'
        except Exception as e:
            pass

    # Fallback pool
    img = FALLBACK_POOL[(_counter - 1) % len(FALLBACK_POOL)]
    return img, 'Pool'

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

        # Obtenir le mot-clé via Claude
        keyword = get_keyword(titre)
        if not keyword:
            keyword = ' '.join(titre.split()[:3])

        # Chercher l'image
        new_img, source = search_image(keyword)

        # Remplacer l'image
        html = re.sub(r'(<img class="article-hero"[^>]+src=")[^"]+(")', rf'\g<1>{new_img}\g<2>', html)
        html = re.sub(r'(<meta property="og:image" content=")[^"]+(")', rf'\g<1>{new_img}\g<2>', html)
        html = re.sub(r'("image":")[^"]+(")', rf'\g<1>{new_img}\g<2>', html)

        open(path, 'w').write(html)
        count += 1
        print(f'✅ [{source}] {cat}/{f[:40]} — "{keyword}"')

print(f'\n✅ {count} articles mis à jour')
