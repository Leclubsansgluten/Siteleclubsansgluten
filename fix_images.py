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
 
# Régénérer les index de toutes les catégories
print('\nRégénération des index...')
LABELS = {'recettes':'Recettes','sante':'Santé','farines':'Farines','guides':'Conseils'}
EMOJIS = {'recettes':'🍞','sante':'🌿','farines':'⚖️','guides':'📖'}
DESCS  = {
    'recettes': 'Recettes sans gluten testées et approuvées par notre communauté de 100 000 membres.',
    'sante':    'Symptômes, diagnostics, conseils santé pour vivre mieux sans gluten. Articles vérifiés.',
    'farines':  "Comparatifs complets des farines sans gluten. Guides d'utilisation pratiques.",
    'guides':   'Guides pratiques pour bien vivre sans gluten : débuter, voyager, cuisiner avec un petit budget.'
}
 
for cat in ['recettes', 'sante', 'farines', 'guides']:
    if not os.path.exists(cat):
        continue
    label = LABELS[cat]
    emoji = EMOJIS[cat]
    desc  = DESCS[cat]
 
    files_with_date = [(os.path.getmtime(os.path.join(cat,f)), f)
                       for f in os.listdir(cat)
                       if f.endswith('.html') and f != 'index.html']
    files_with_date.sort(reverse=True)
    files = [f for _, f in files_with_date]
 
    cards = ''
    for f in files[:60]:
        fhtml = open(os.path.join(cat, f)).read()
        tm = re.search(r'<title>(.*?) — Le Club', fhtml)
        ft = tm.group(1) if tm else f.replace('-',' ').replace('.html','').capitalize()
        im = re.search(r'<img class="article-hero"[^>]+src="([^"]+)"', fhtml)
        if not im:
            im = re.search(r'"image":"([^"]+)"', fhtml)
        fimg = im.group(1) if im else ''
        cards += f'<a href="/{cat}/{f}" class="card"><div class="card-img-wrap"><img class="card-img" src="{fimg}" alt="{ft}" loading="lazy"/></div><div class="card-body"><div class="card-cat">{emoji} {label}</div><div class="card-title">{ft}</div></div></a>\n'
 
    # Lire l'index existant et remplacer juste la grille d'articles
    idx_path = os.path.join(cat, 'index.html')
    if os.path.exists(idx_path):
        idx_html = open(idx_path).read()
        idx_html = re.sub(
            r'<div class="articles-grid">.*?</div>\s*</div>\s*<script>',
            f'<div class="articles-grid">{cards}</div>\n</div>\n<script>',
            idx_html, flags=re.DOTALL, count=1
        )
        # Mettre à jour le compte d'articles
        idx_html = re.sub(r'\d+ articles', f'{len(files)} articles', idx_html, count=1)
        open(idx_path, 'w').write(idx_html)
        print(f'✅ Index {cat} régénéré — {len(files)} articles')
 
