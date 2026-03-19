#!/usr/bin/env python3
"""
Script de correction des images — à exécuter une seule fois.
Corrige tous les articles qui ont encore l'image par défaut (pain).
"""
import os, re

# Image par défaut à remplacer (l'ancienne photo de pain)
DEFAULT_IMGS = [
    'photo-1509440159596-0249088772ff',
]

# Images variées selon les mots-clés du slug
def get_image(slug, cat):
    slug_lower = slug.lower()
    # Recettes
    if any(w in slug_lower for w in ['gateau','anniversaire','cake','fondant']):
        return 'https://images.unsplash.com/photo-1558636508-e0969431e67f?w=1200&q=80'
    if any(w in slug_lower for w in ['dessert','brownie','cookie','muffin']):
        return 'https://images.unsplash.com/photo-1587241321921-91a834d6d191?w=1200&q=80'
    if any(w in slug_lower for w in ['crepe','pancake','galette']):
        return 'https://images.unsplash.com/photo-1519676867240-f03562e64548?w=1200&q=80'
    if any(w in slug_lower for w in ['baguette','pain-de-mie','pain-maison']):
        return 'https://images.unsplash.com/photo-1549931319-a545dcf3bc7f?w=1200&q=80'
    if any(w in slug_lower for w in ['pain','boulangerie','brioche','chataigne']):
        return 'https://images.unsplash.com/photo-1509440159596-0249088772ff?w=1200&q=80'
    if any(w in slug_lower for w in ['pizza','lasagne','quiche','plat']):
        return 'https://images.unsplash.com/photo-1574894709920-11b28e7367e3?w=1200&q=80'
    if any(w in slug_lower for w in ['soupe','veloute','minestrone']):
        return 'https://images.unsplash.com/photo-1547592166-23ac45744acd?w=1200&q=80'
    if any(w in slug_lower for w in ['petit-dejeuner','breakfast','gouter','biscuit']):
        return 'https://images.unsplash.com/photo-1533089860892-a7c6f0a88666?w=1200&q=80'
    # Santé
    if any(w in slug_lower for w in ['grossesse','bebe','enfant']):
        return 'https://images.unsplash.com/photo-1544126592-807ade215a0b?w=1200&q=80'
    if any(w in slug_lower for w in ['sport','fitness','musculation']):
        return 'https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=1200&q=80'
    if any(w in slug_lower for w in ['peau','acne','eczema']):
        return 'https://images.unsplash.com/photo-1512290923902-8a9f81dc236c?w=1200&q=80'
    if any(w in slug_lower for w in ['fatigue','energie','hormone']):
        return 'https://images.unsplash.com/photo-1540420773420-3366772f4999?w=1200&q=80'
    if any(w in slug_lower for w in ['mental','depression','anxiete','cerveau']):
        return 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=1200&q=80'
    if any(w in slug_lower for w in ['poids','minceur','regime']):
        return 'https://images.unsplash.com/photo-1490645935967-10de6ba17061?w=1200&q=80'
    # Farines
    if any(w in slug_lower for w in ['farine','mix','psyllium','feculent']):
        return 'https://images.unsplash.com/photo-1612200606649-1e95b16fcf2c?w=1200&q=80'
    # Guides
    if any(w in slug_lower for w in ['restaurant','paris','voyage']):
        return 'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=1200&q=80'
    if any(w in slug_lower for w in ['budget','course','liste']):
        return 'https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=1200&q=80'
    if any(w in slug_lower for w in ['noel','fete','anniversaire']):
        return 'https://images.unsplash.com/photo-1482575832494-771f74bf6857?w=1200&q=80'
    if any(w in slug_lower for w in ['ecole','enfant','enfants']):
        return 'https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=1200&q=80'
    # Par défaut selon catégorie
    defaults = {
        'recettes': 'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=1200&q=80',
        'sante':    'https://images.unsplash.com/photo-1540420773420-3366772f4999?w=1200&q=80',
        'farines':  'https://images.unsplash.com/photo-1585478259715-4c6d5047b7c1?w=1200&q=80',
        'guides':   'https://images.unsplash.com/photo-1499636136210-6f4ee915583e?w=1200&q=80',
    }
    return defaults.get(cat, 'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=1200&q=80')

count = 0
for cat in ['recettes', 'sante', 'farines', 'guides']:
    for f in os.listdir(cat):
        if not f.endswith('.html') or f == 'index.html':
            continue
        path = f'{cat}/{f}'
        html = open(path).read()
        
        # Vérifier si l'article a l'image par défaut
        has_default = any(d in html for d in DEFAULT_IMGS)
        if not has_default:
            continue
            
        slug = f.replace('.html', '')
        new_img = get_image(slug, cat)
        
        # Remplacer toutes les occurrences de l'image par défaut
        for d in DEFAULT_IMGS:
            html = re.sub(
                r'https://images\.unsplash\.com/' + d + r'[^"\']*',
                new_img,
                html
            )
        
        # Mettre à jour og:image
        html = re.sub(
            r'(<meta property="og:image" content=")[^"]+(")',
            rf'\g<1>{new_img}\g<2>',
            html
        )
        # Mettre à jour schema image
        html = re.sub(
            r'("image":")[^"]+(")',
            rf'\g<1>{new_img}\g<2>',
            html
        )
        
        open(path, 'w').write(html)
        count += 1
        print(f'✅ {cat}/{slug} → {new_img[-50:]}')

print(f'\n✅ {count} articles corrigés')

# Mettre à jour les index après correction
import subprocess
subprocess.run(['python3', '-c', '''
import os, re
cats_config = {
    "recettes": ("Recettes", "🍞", "Recettes sans gluten testées et approuvées."),
    "sante": ("Santé", "🌿", "Conseils santé pour vivre mieux sans gluten."),
    "farines": ("Farines", "⚖️", "Comparatifs des farines sans gluten."),
    "guides": ("Conseils", "📖", "Guides pratiques sans gluten."),
}
for cat, (label, emoji, desc) in cats_config.items():
    files_with_date = [(os.path.getmtime(os.path.join(cat,f)), f) for f in os.listdir(cat) if f.endswith(".html") and f != "index.html"]
    files_with_date.sort(reverse=True)
    files = [f for _, f in files_with_date]
    cards = ""
    for f in files[:60]:
        fhtml = open(os.path.join(cat,f)).read()
        tm = re.search(r"<title>(.*?) — Le Club", fhtml)
        title = tm.group(1) if tm else f.replace("-"," ").replace(".html","").capitalize()
        im = re.search(r"<img class=\\"article-hero\\"[^>]+src=\\"([^\\"]+)\\"", fhtml)
        if not im: im = re.search(r"\\"image\\":\\"([^\\"]+)\\"", fhtml)
        img = re.sub(r"w=\\d+", "w=600", im.group(1)) if im else ""
        cards += f\'<a href="/{cat}/{f}" class="card"><div class="card-img-wrap"><img class="card-img" src="{img}" alt="{title}" loading="lazy"/></div><div class="card-body"><div class="card-cat">{emoji} {label}</div><div class="card-title">{title}</div></div></a>\\n\'
    print(f"Index {cat}: {len(files)} articles")
'''], check=False)
print('✅ Script terminé — les index seront mis à jour au prochain run du workflow')
