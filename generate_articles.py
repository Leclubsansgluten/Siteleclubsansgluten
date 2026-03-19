#!/usr/bin/env python3
import os, re, json, subprocess, urllib.request
from datetime import datetime

API_KEY      = os.environ.get('ANTHROPIC_API_KEY', '')
PEXELS_KEY   = os.environ.get('PEXELS_API_KEY', '')
TODAY_ISO = datetime.now().strftime('%Y-%m-%d')
MONTHS    = ['janvier','février','mars','avril','mai','juin','juillet','août',
             'septembre','octobre','novembre','décembre']
d         = datetime.now()
DATE_FR   = f"{d.day} {MONTHS[d.month-1]} {d.year}"

LABELS = {'recettes':'Recettes','sante':'Santé','farines':'Farines','guides':'Conseils'}
EMOJIS = {'recettes':'🍞','sante':'🌿','farines':'⚖️','guides':'📖'}
DESCS  = {
    'recettes': 'Recettes sans gluten testées et approuvées par notre communauté de 100 000 membres.',
    'sante':    'Symptômes, diagnostics, conseils santé pour vivre mieux sans gluten. Articles vérifiés.',
    'farines':  "Comparatifs complets des farines sans gluten. Guides d'utilisation pratiques.",
    'guides':   'Guides pratiques pour bien vivre sans gluten : débuter, voyager, cuisiner avec un petit budget.'
}
# Images de fallback si Pexels échoue
IMAGES_FALLBACK = {
    'recettes': 'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=1200&q=80',
    'sante':    'https://images.unsplash.com/photo-1540420773420-3366772f4999?w=1200&q=80',
    'farines':  'https://images.unsplash.com/photo-1612200606649-1e95b16fcf2c?w=1200&q=80',
    'guides':   'https://images.unsplash.com/photo-1499636136210-6f4ee915583e?w=1200&q=80',
}

def get_pexels_image(titre, cat):
    """Cherche une photo Pexels en lien avec le titre de l'article."""
    import urllib.request, urllib.parse, json as json2
    try:
        # Nettoyer le titre pour la recherche
        query = titre.replace(':', '').replace('—', '').strip()
        # Limiter à 5 mots pour une meilleure pertinence
        query = ' '.join(query.split()[:5])
        url = f'https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=1&orientation=landscape'
        req = urllib.request.Request(url, headers={'Authorization': PEXELS_KEY})
        data = json2.loads(urllib.request.urlopen(req, timeout=10).read())
        if data.get('photos'):
            img_url = data['photos'][0]['src']['large2x']
            print(f'  📸 Pexels: {img_url[:60]}...')
            return img_url
    except Exception as e:
        print(f'  ⚠️ Pexels échoué: {e}')
    return IMAGES_FALLBACK.get(cat, IMAGES_FALLBACK['recettes'])

def total_articles():
    count = 0
    for root, dirs, files in os.walk('.'):
        for f in files:
            if f.endswith('.html') and f not in ['index.html','template.html',
               'a-propos.html','glossaire.html','calculateur.html',
               'mentions-legales.html','cgv.html']:
                count += 1
    return count

def extract(tag, text):
    m = re.search(r'\['+tag+r'\](.*?)\[/'+tag+r'\]', text, re.DOTALL)
    return m.group(1).strip() if m else ''

def call_api(prompt):
    payload = json.dumps({
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 8000,
        "messages": [{"role": "user", "content": prompt}]
    })
    result = subprocess.run(
        ['curl','-s','https://api.anthropic.com/v1/messages',
         '-H', f'x-api-key: {API_KEY}',
         '-H', 'anthropic-version: 2023-06-01',
         '-H', 'content-type: application/json',
         '-d', payload],
        capture_output=True, text=True, timeout=120
    )
    data = json.loads(result.stdout)
    return data['content'][0]['text']

def build_index(cat):
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
        fimg = re.sub(r'w=\d+', 'w=600', im.group(1)) if im else IMAGES[3]
        cards += f'<a href="/{cat}/{f}" class="card"><div class="card-img-wrap"><img class="card-img" src="{fimg}" alt="{ft}" loading="lazy"/></div><div class="card-body"><div class="card-cat">{emoji} {label}</div><div class="card-title">{ft}</div></div></a>\n'

    subcats = ''
    if cat == 'recettes':
        subcats = '''<div class="subcats">
<button class="subcat active" onclick="filterCat('toutes',this)">🍽️ Toutes</button>
<button class="subcat" onclick="filterCat('pain',this)">🍞 Pain</button>
<button class="subcat" onclick="filterCat('gateaux',this)">🎂 Gâteaux</button>
<button class="subcat" onclick="filterCat('crepes',this)">🥞 Crêpes</button>
<button class="subcat" onclick="filterCat('plats',this)">🍽️ Plats</button>
<button class="subcat" onclick="filterCat('soupes',this)">🍲 Soupes</button>
</div>
<script>
var currentCat="toutes";
function filterCat(c,b){currentCat=c;document.querySelectorAll(".subcat").forEach(function(x){x.classList.remove("active")});b.classList.add("active");document.getElementById("catSearch").value="";applyFilters();}
function detectCat(c){var cat=c.getAttribute("data-cat");if(cat)return cat;var href=c.getAttribute("href")||"";var slug=href.split("/").pop().replace(".html","").toLowerCase();var title=(c.querySelector(".card-title")||{}).textContent||"";var text=slug+" "+title.toLowerCase();if(/pain|baguette|mie|brioche|chataigne/.test(text))return"pain";if(/crepe|galette|pancake|sarrasin/.test(text))return"crepes";if(/gateau|cake|brownie|cookie|muffin|tarte|citron|tatin|dessert/.test(text))return"gateaux";if(/soupe|veloute|minestrone|bouillon/.test(text))return"soupes";if(/lasagne|quiche|pizza|plat|gratin/.test(text))return"plats";return"toutes";}
function applyFilters(){var q=document.getElementById("catSearch").value.toLowerCase();document.querySelectorAll(".card").forEach(function(c){var t=c.querySelector(".card-title");var cc=detectCat(c);c.style.display=((currentCat==="toutes"||cc===currentCat)&&(!q||(t&&t.textContent.toLowerCase().indexOf(q)>-1)))?"":"none";});}
</script>'''

    bc = f'{{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{{"@type":"ListItem","position":1,"name":"Accueil","item":"https://leclubsansgluten.com/"}},{{"@type":"ListItem","position":2,"name":"{label}","item":"https://leclubsansgluten.com/{cat}/"}}]}}'

    idx = f"""<!DOCTYPE html>
<html lang="fr"><head>
<meta charset="UTF-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>{emoji} {label} sans gluten — Articles et guides — Le Club Sans Gluten</title>
<meta name="description" content="{desc}"/>
<link rel="canonical" href="https://leclubsansgluten.com/{cat}/"/>
<meta property="og:title" content="{label} sans gluten — Le Club Sans Gluten"/>
<meta property="og:description" content="{desc}"/>
<meta property="og:type" content="website"/>
<meta name="twitter:card" content="summary_large_image"/>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Lora:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet"/>
<link rel="stylesheet" href="/assets/style.css"/>
<script type="application/ld+json">{bc}</script>
</head><body>
<div class="top-bar">📚 <a href="https://www.whynottraining.fr/ed790464" target="_blank">La Bible des Farines Sans Gluten</a> → <a href="https://www.whynottraining.fr/ed790464" target="_blank">Je le veux</a></div>
<header class="site-header"><a href="/" class="logo-wrap"><div class="logo">Le Club<em> Sans Gluten</em></div><span class="logo-sub">Le site info sans gluten N°1</span></a><div class="header-search-wrap"><input type="text" class="header-search" placeholder="🔍 Rechercher..." id="headerSearch" autocomplete="off"/><div class="search-results" id="searchResults"></div></div></header>
<nav class="site-nav"><div class="site-nav-inner"><a href="/recettes/">🍞 Recettes</a><a href="/sante/">🌿 Santé</a><a href="/farines/">⚖️ Farines</a><a href="/guides/">📖 Conseils</a></div></nav>
<div class="breadcrumb"><a href="/">Accueil</a><span>›</span><span>{emoji} {label}</span></div>
<div class="home-wrap">
  <div class="section-head" style="margin-top:1.5rem"><h1 class="section-title">{emoji} {label}</h1><span style="font-size:.78rem;color:var(--gray)">{len(files)} articles</span></div>
  {subcats}
  <div class="cat-search-bar"><input type="text" class="cat-search-input" placeholder="🔍 Rechercher dans {label}..." id="catSearch" autocomplete="off"/></div>
  <div class="articles-grid">{cards}</div>
</div>
<script>document.getElementById("catSearch").addEventListener("input",function(){{var q=this.value.toLowerCase();if(typeof applyFilters!=="undefined"){{applyFilters();return;}}document.querySelectorAll(".card").forEach(function(c){{var t=c.querySelector(".card-title");if(t)c.style.display=t.textContent.toLowerCase().indexOf(q)>-1?"":"none";}});}});</script>
<footer class="site-footer"><div class="footer-inner">
  <div class="footer-logo">Le Club <span>Sans Gluten</span></div>
  <div class="footer-links">
    <a href="https://www.whynottraining.fr/08c32d2c-1fbf916c-b0fd38be-d95c800f-ee160319-0993e605" target="_blank">🎁 Guide gratuit</a>
    <a href="https://www.whynottraining.fr/ed790464" target="_blank">📚 La Bible des Farines</a>
    <a href="/a-propos.html">À propos</a>
    <a href="/glossaire.html">Glossaire</a>
  </div>
  <div class="footer-links" style="margin-top:.5rem;font-size:.8rem">
    <a href="/mentions-legales.html">Mentions légales</a>
    <a href="/cgv.html">CGV</a>
  </div>
  <p class="footer-legal">© 2026 Le Club Sans Gluten · Tous droits réservés</p>
</div></footer>
</body></html>"""

    open(f'{cat}/index.html', 'w').write(idx)
    print(f'  ✅ Index {cat} — {len(files)} articles')

def build_sitemap():
    freqs = {'recettes':'daily','sante':'weekly','farines':'weekly','guides':'weekly'}
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sm += f'  <url><loc>https://leclubsansgluten.com/</loc><lastmod>{TODAY_ISO}</lastmod><changefreq>daily</changefreq><priority>1.0</priority></url>\n'
    for c in ['recettes','sante','farines','guides']:
        sm += f'  <url><loc>https://leclubsansgluten.com/{c}/</loc><lastmod>{TODAY_ISO}</lastmod><changefreq>{freqs[c]}</changefreq><priority>0.9</priority></url>\n'
        for f in sorted([f for f in os.listdir(c) if f.endswith('.html') and f != 'index.html'], reverse=True):
            sm += f'  <url><loc>https://leclubsansgluten.com/{c}/{f.replace(".html","")}.html</loc><lastmod>{TODAY_ISO}</lastmod><changefreq>{freqs[c]}</changefreq><priority>0.8</priority></url>\n'
    sm += '</urlset>'
    open('sitemap.xml', 'w').write(sm)
    print(f'  ✅ Sitemap — {sm.count("<url>")} URLs')

    # Ping Google
    try:
        urllib.request.urlopen('https://www.google.com/ping?sitemap=https://leclubsansgluten.com/sitemap.xml', timeout=10)
        print('  ✅ Google pingé')
    except Exception as e:
        print(f'  ⚠️ Ping Google: {e}')

def generate_article(cat, index_num):
    label = LABELS[cat]
    emoji = EMOJIS[cat]
    prompt = f"""Tu es un expert SEO et rédacteur spécialisé dans l'alimentation sans gluten pour leclubsansgluten.com.

