#!/usr/bin/env python3
import os, re, json, subprocess, urllib.request
from datetime import datetime

API_KEY      = os.environ.get('ANTHROPIC_API_KEY', '')
PEXELS_KEY    = os.environ.get('PEXELS_API_KEY', '')
UNSPLASH_KEY  = os.environ.get('UNSPLASH_API_KEY', '')
TODAY_ISO = datetime.now().strftime('%Y-%m-%d')
MONTHS    = ['janvier','février','mars','avril','mai','juin','juillet','août',
             'septembre','octobre','novembre','décembre']
d         = datetime.now()
DATE_FR   = f"{d.day} {MONTHS[d.month-1]} {d.year}"

LABELS = {'recettes':'Recettes','sante':'Santé','farines':'Farines','guides':'Conseils'}
EMOJIS = {'recettes':'🍞','sante':'🌿','farines':'⚖️','guides':'📖'}

# Auteurs par catégorie
AUTHORS = {
    'recettes': {
        'name': 'Sophie',
        'role': 'Recettes sans gluten',
        'bio': 'Cuisinière passionnée et intolérante au gluten depuis 8 ans, Sophie teste toutes ses recettes chez elle avant de les publier.'
    },
    'farines': {
        'name': 'Claire',
        'role': 'Farines & Pâtisserie',
        'bio': 'Ancienne boulangère reconvertie dans le sans gluten, Claire maîtrise les farines alternatives depuis plus de 10 ans.'
    },
    'sante': {
        'name': 'Marie',
        'role': 'Nutrition & Santé',
        'bio': 'Diplômée en nutrition, Marie accompagne les femmes intolérantes au gluten dans leur transition alimentaire.'
    },
    'guides': {
        'name': 'Max',
        'role': 'Conseils & Lifestyle',
        'bio': 'Blogueur sans gluten depuis 2017, Max a testé tous les restaurants, voyages et astuces du quotidien.'
    },
}

DESCS  = {
    'recettes': 'Recettes sans gluten testées et approuvées par notre communauté de 100 000 membres.',
    'sante':    'Symptômes, diagnostics, conseils santé pour vivre mieux sans gluten. Articles vérifiés.',
    'farines':  "Comparatifs complets des farines sans gluten. Guides d'utilisation pratiques.",
    'guides':   'Guides pratiques pour bien vivre sans gluten : débuter, voyager, cuisiner avec un petit budget.'
}

UNSPLASH_POOL = [
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
    'https://images.unsplash.com/photo-1549931319-a545dcf3bc7f?w=1200&q=80',
    'https://images.unsplash.com/photo-1598373182133-52452f7691ef?w=1200&q=80',
    'https://images.unsplash.com/photo-1476718406336-bb5a9690ee2a?w=1200&q=80',
    'https://images.unsplash.com/photo-1607958996333-41aef7caefaa?w=1200&q=80',
    'https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=1200&q=80',
    'https://images.unsplash.com/photo-1544126592-807ade215a0b?w=1200&q=80',
    'https://images.unsplash.com/photo-1585478259715-4c6d5047b7c1?w=1200&q=80',
    'https://images.unsplash.com/photo-1490645935967-10de6ba17061?w=1200&q=80',
    'https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=1200&q=80',
    'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=1200&q=80',
]

_img_counter = 0

def get_existing_titles():
    """Retourne la liste des titres d articles deja publies pour eviter les doublons."""
    titles = []
    for cat in ['recettes', 'sante', 'farines', 'guides']:
        if not os.path.exists(cat):
            continue
        for f in os.listdir(cat):
            if not f.endswith('.html') or f == 'index.html':
                continue
            try:
                fhtml = open(os.path.join(cat, f)).read()
                tm = re.search(r'<title>(.*?) — Le Club', fhtml)
                if tm:
                    titles.append(tm.group(1))
            except:
                pass
    return titles

def get_keyword(titre):
    try:
        payload = json.dumps({
            "model": "claude-haiku-4-5-20251001",
            "max_tokens": 20,
            "messages": [{
                "role": "user",
                "content": "Give me 2-3 English keywords for a food/health photo search for this French article title: '" + titre + "'. Reply ONLY with the keywords, nothing else. Example: 'chocolate cake' or 'gluten free bread' or 'woman fatigue'"
            }]
        })
        result = subprocess.run(
            ['curl', '-s', 'https://api.anthropic.com/v1/messages',
             '-H', 'x-api-key: ' + API_KEY,
             '-H', 'anthropic-version: 2023-06-01',
             '-H', 'content-type: application/json',
             '-d', payload],
            capture_output=True, text=True, timeout=15
        )
        data = json.loads(result.stdout)
        keyword = data['content'][0]['text'].strip().strip('"').strip("'")
        return keyword
    except Exception as e:
        return ' '.join(titre.split()[:3])

def get_pexels_image(titre, cat):
    global _img_counter
    _img_counter += 1
    import urllib.parse, json as json2

    try:
        keyword = get_keyword(titre)
        query = keyword if keyword else ' '.join(titre.replace(':', '').replace('—', '').strip().split()[:5])
        page = (_img_counter % 5) + 1
        url = f'https://api.pexels.com/v1/search?query={urllib.parse.quote(query)}&per_page=5&page={page}&orientation=landscape'
        req = urllib.request.Request(url, headers={
            'Authorization': PEXELS_KEY,
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json',
        })
        data = json2.loads(urllib.request.urlopen(req, timeout=15).read())
        if data.get('photos'):
            idx = (_img_counter - 1) % len(data['photos'])
            print(f'  📸 Pexels: OK')
            return data['photos'][idx]['src']['large2x']
    except Exception as e:
        print(f'  ⚠️ Pexels echoue: {e}')

    try:
        import urllib.parse
        keyword = get_keyword(titre)
        query = keyword if keyword else ' '.join(titre.replace(':', '').replace('—', '').strip().split()[:5])
        page = (_img_counter % 10) + 1
        url = f'https://api.unsplash.com/search/photos?query={urllib.parse.quote(query)}&per_page=10&page={page}&orientation=landscape'
        req = urllib.request.Request(url, headers={
            'Authorization': f'Client-ID {UNSPLASH_KEY}',
            'Accept-Version': 'v1',
        })
        data = json2.loads(urllib.request.urlopen(req, timeout=15).read())
        if data.get('results'):
            idx = (_img_counter - 1) % len(data['results'])
            print(f'  📸 Unsplash: OK')
            return data['results'][idx]['urls']['regular']
    except Exception as e:
        print(f'  ⚠️ Unsplash echoue: {e}')

    img = UNSPLASH_POOL[(_img_counter - 1) % len(UNSPLASH_POOL)]
    print(f'  📸 Pool fixe #{(_img_counter - 1) % len(UNSPLASH_POOL)}')
    return img


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
        "max_tokens": 1600,
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
        fimg = re.sub(r'w=\d+', 'w=600', im.group(1)) if im else ''
        cards += f'<a href="/{cat}/{f}" class="card"><div class="card-img-wrap"><img class="card-img" src="{fimg}" alt="{ft}" loading="lazy"/></div><div class="card-body"><div class="card-cat">{emoji} {label}</div><div class="card-title">{ft}</div></div></a>\n'

    subcats = ''
    if cat == 'recettes':
        subcats = '''<div class="subcats">
<button class="subcat active" onclick="filterCat('toutes',this)">🍽️ Toutes</button>
<button class="subcat" onclick="filterCat('rapide',this)">🚀 Rapide</button>
<button class="subcat" onclick="filterCat('pdej',this)">🥐 Petit déjeuner</button>
<button class="subcat" onclick="filterCat('entrees',this)">🥗 Entrées</button>
<button class="subcat" onclick="filterCat('plats',this)">🍽️ Plats</button>
<button class="subcat" onclick="filterCat('desserts',this)">🎂 Desserts</button>
<button class="subcat" onclick="filterCat('pain',this)">🍞 Pain</button>
</div>
<script>
var currentCat="toutes";
function filterCat(c,b){currentCat=c;document.querySelectorAll(".subcat").forEach(function(x){x.classList.remove("active")});b.classList.add("active");document.getElementById("catSearch").value="";applyFilters();}
function detectCat(c){
  var href=(c.getAttribute("href")||"").toLowerCase();
  var title=(c.querySelector(".card-title")||{textContent:""}).textContent.toLowerCase();
  var text=href+" "+title;
  text=text.normalize("NFD").replace(/[\u0300-\u036f]/g,"");
  if(/rapide|express|vite/.test(text))return"rapide";
  if(/petit.dejeuner|breakfast|muffin|pancake|granola|gouter|biscuit/.test(text))return"pdej";
  if(/soupe|veloute|minestrone|bouillon|salade|entree/.test(text))return"entrees";
  if(/lasagne|quiche|pizza|gratin|curry|pates|pasta/.test(text))return"plats";
  if(/gateau|tarte|brownie|cookie|fondant|chocolat|citron|anniversaire|dessert|cake|patisserie/.test(text))return"desserts";
  if(/pain|baguette|brioche|chataigne|sarrasin|galette|mie|machine.a.pain/.test(text))return"pain";
  return"toutes";
}
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
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Lora:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet" media="print" onload="this.media='all'"/>
<noscript><link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Lora:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet"/></noscript>
<link rel="stylesheet" href="/assets/style.css"/>
<script type="application/ld+json">{bc}</script>
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-X0PFTP0TLQ"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-X0PFTP0TLQ');</script>
</head><body>
<div class="top-bar">📚 <a href="https://www.whynottraining.fr/ed790464" rel="nofollow" target="_blank">La Bible des Farines Sans Gluten</a> → <a href="https://www.whynottraining.fr/ed790464" rel="nofollow" target="_blank">Je le veux</a></div>
<header class="site-header"><a href="/" class="logo-wrap"><div class="logo">Le Club<em> Sans Gluten</em></div><span class="logo-sub">Le site sans gluten N°1</span></a><div class="header-search-wrap"><input type="text" class="header-search" placeholder="🔍 Rechercher..." id="headerSearch" autocomplete="off"/><div class="search-results" id="searchResults"></div></div></header>
<nav class="site-nav"><div class="site-nav-inner"><a href="/recettes/">Recettes</a><a href="/sante/">Santé</a><a href="/farines/">Farines</a><a href="/guides/">Conseils</a></div></nav>
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
    <a href="https://www.whynottraining.fr/08c32d2c-1fbf916c-b0fd38be-d95c800f-ee160319-0993e605" rel="nofollow" target="_blank">🎁 Guide gratuit</a>
    <a href="https://www.whynottraining.fr/ed790464" rel="nofollow" target="_blank">📚 La Bible des Farines</a>
    <a href="/a-propos.html">À propos</a>
    <a href="/glossaire.html">Glossaire</a>
  </div>
  <div class="footer-links" style="margin-top:.5rem;font-size:.8rem">
    <a href="/mentions-legales.html">Mentions légales</a>
    <a href="/cgv.html">CGV</a>
  </div>
  <p class="footer-legal">© 2026 Le Club Sans Gluten · Tous droits réservés</p>
</div></footer>
<div id="cookieBanner" style="display:none;position:fixed;bottom:0;left:0;right:0;background:#1a1a1a;color:#fff;padding:1rem 1.5rem;z-index:9999;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:1rem;font-family:var(--sans);font-size:.875rem">
  <p style="margin:0;flex:1">🍪 Ce site utilise des cookies pour mesurer l'audience. <a href="/mentions-legales.html" style="color:var(--gold)">En savoir plus</a></p>
  <div style="display:flex;gap:.75rem">
    <button onclick="acceptCookies()" style="background:var(--gold);color:#1a1a1a;border:none;padding:.5rem 1.2rem;border-radius:6px;font-weight:700;cursor:pointer">Accepter</button>
    <button onclick="refuseCookies()" style="background:transparent;color:#fff;border:1px solid #555;padding:.5rem 1.2rem;border-radius:6px;cursor:pointer">Refuser</button>
  </div>
</div>
<script>
(function(){{if(!localStorage.getItem('cookie_consent'))document.getElementById('cookieBanner').style.display='flex';}})();
function acceptCookies(){{localStorage.setItem('cookie_consent','accepted');document.getElementById('cookieBanner').style.display='none';}}
function refuseCookies(){{localStorage.setItem('cookie_consent','refused');document.getElementById('cookieBanner').style.display='none';}}
</script>"""

    if cat == 'recettes':
        auto_filter = '''<script>
window.addEventListener('load', function() {
  var params = new URLSearchParams(window.location.search);
  var cat = params.get('cat');
  if(cat) {
    var btn = document.querySelector('.subcat[onclick*="' + cat + '"]');
    if(btn) {
      btn.click();
      setTimeout(function(){ window.scrollTo({top:0}); }, 100);
    }
  }
});
</script>'''
        idx += auto_filter

    idx += '\n</body></html>'
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

    try:
        urllib.request.urlopen('https://www.google.com/ping?sitemap=https://leclubsansgluten.com/sitemap.xml', timeout=10)
        print('  ✅ Google pingé')
    except Exception as e:
        print(f'  ⚠️ Ping Google: {e}')

def google_search(query, num=5):
    try:
        import urllib.parse
        q = urllib.parse.quote(query)
        url = f'https://www.google.com/search?q={q}&num={num}&hl=fr'
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'fr-FR,fr;q=0.9',
        })
        html = urllib.request.urlopen(req, timeout=15).read().decode('utf-8', errors='ignore')
        urls = re.findall(r'href="(https://[^"]+)"', html)
        filtered = []
        skip = ['google.', 'youtube.', 'facebook.', 'twitter.', 'instagram.', 'amazon.', 'wikipedia.']
        for u in urls:
            if not any(s in u for s in skip) and u not in filtered:
                filtered.append(u)
            if len(filtered) >= num:
                break
        return filtered
    except Exception as e:
        print(f'  ⚠️ Google search: {e}')
        return []

def fetch_page(url):
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'text/html',
        })
        html = urllib.request.urlopen(req, timeout=10).read().decode('utf-8', errors='ignore')
        text = re.sub(r'<script[^>]*>.*?</script>', ' ', html, flags=re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', ' ', text, flags=re.DOTALL)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text[:3000]
    except Exception as e:
        return ''

def gather_sources(sujet, cat):
    if cat == 'recettes':
        queries = [
            f'recette {sujet} sans gluten ingrédients',
            f'{sujet} sans gluten recette facile',
        ]
    else:
        queries = [
            f'{sujet} sans gluten',
            f'intolérance gluten {sujet}',
        ]
    
    all_content = []
    seen_urls = set()
    
    for query in queries:
        urls = google_search(query, num=5)
        for url in urls[:3]:
            if url in seen_urls:
                continue
            seen_urls.add(url)
            content = fetch_page(url)
            if len(content) > 200:
                all_content.append(f'[SOURCE: {url}]\n{content}')
            if len(all_content) >= 5:
                break
        if len(all_content) >= 5:
            break
    
    return '\n\n'.join(all_content[:5])

def generate_article(cat, index_num):
    label = LABELS[cat]
    emoji = EMOJIS[cat]
    author = AUTHORS[cat]

    # Récupérer les titres existants pour éviter les doublons
    existing_titles = get_existing_titles()
    existing_str = '\n'.join(f'- {t}' for t in existing_titles[-100:]) if existing_titles else 'Aucun article publié encore.'

    sujet_prompt = f"""Tu es expert en alimentation sans gluten. 
Choisis UN sujet NOUVEAU et DIFFERENT pour la categorie {cat} ciblant les femmes françaises 30-55 ans intolérantes au gluten.

Articles DEJA PUBLIES (ne pas répéter ces sujets) :
{existing_str}

Reponds UNIQUEMENT avec le sujet en francais, rien d autre. Exemple: "gateau anniversaire chocolat" ou "symptomes fatigue chronique gluten"
"""
    sujet_result = subprocess.run(
        ['curl','-s','https://api.anthropic.com/v1/messages',
         '-H', f'x-api-key: {API_KEY}',
         '-H', 'anthropic-version: 2023-06-01',
         '-H', 'content-type: application/json',
         '-d', json.dumps({"model":"claude-haiku-4-5-20251001","max_tokens":50,"messages":[{"role":"user","content":sujet_prompt}]})],
        capture_output=True, text=True, timeout=30
    )
    try:
        sujet = json.loads(sujet_result.stdout)['content'][0]['text'].strip()
    except:
        sujet = cat + ' sans gluten'
    
    print(f'  🔍 Sujet choisi: {sujet}')
    print(f'  🌐 Recherche de sources...')
    sources = gather_sources(sujet, cat)
    sources_text = f'\n\nSOURCES TROUVEES SUR INTERNET:\n{sources}' if sources else ''
    
    recette_instruction = ''
    if cat == 'recettes':
        recette_instruction = """
IMPORTANT POUR LES RECETTES:
- Recupere les ingredients et quantites EXACTES des sources trouvees
- Combine les meilleures informations de plusieurs recettes
- Garde les quantites reelles et verifiees
- Reecris completement la preparation dans ton style
"""

    # Temps seulement pour recettes
    temps_tag = '[TEMPS]X min de préparation[/TEMPS]' if cat == 'recettes' else '[TEMPS][/TEMPS]'

    prompt = f"""Tu es un expert SEO et rédacteur spécialisé dans l'alimentation sans gluten pour leclubsansgluten.com.

CATÉGORIE : {cat}
SUJET : {sujet}
AUTEUR : {author['name']} — {author['bio']}
{recette_instruction}
Rédige un article complet 3500 mots minimum avec :
- Introduction répondant immédiatement à l'intention de recherche
- 6+ H2 avec mots-clés intégrés naturellement
- Paragraphes courts (150-200 mots), ton chaleureux d'experte
- 2+ listes ou tableaux avec données chiffrées
- FAQ 4 questions réelles Google
{sources_text}

FORMAT EXACT :
[TITRE]titre 60 car max avec accents[/TITRE]
[SLUG]slug-sans-accents[/SLUG]
[META]meta description 155 car max[/META]
{temps_tag}
[THEMATIQUE]une seule valeur parmi : rapide / pdej / entrees / plats / desserts / pain[/THEMATIQUE]
[FAQ_Q1]Question 1[/FAQ_Q1]
[FAQ_A1]Réponse 1[/FAQ_A1]
[FAQ_Q2]Question 2[/FAQ_Q2]
[FAQ_A2]Réponse 2[/FAQ_A2]
[FAQ_Q3]Question 3[/FAQ_Q3]
[FAQ_A3]Réponse 3[/FAQ_A3]
[FAQ_Q4]Question 4[/FAQ_Q4]
[FAQ_A4]Réponse 4[/FAQ_A4]
[CONTENU]HTML complet (p, h2, h3, ul, li, strong, em uniquement)[/CONTENU]"""

    print(f'  Appel API pour {cat}...')
    t = call_api(prompt)

    titre      = extract('TITRE', t) or 'Article sans gluten'
    slug       = re.sub(r'[^a-z0-9-]', '', extract('SLUG', t).lower().replace(' ','-'))[:60] or f'article-{index_num}'
    meta       = extract('META', t)
    temps      = extract('TEMPS', t) or ''
    thematique = extract('THEMATIQUE', t).strip().lower() or ''
    contenu    = extract('CONTENU', t) or '<p>Article en cours.</p>'
    img        = get_pexels_image(titre, cat)

    faq_html = '<div class="faq-block"><h2>Questions fréquentes</h2>'
    faq_schema_items = []
    for j in range(1, 5):
        q = re.search(r'\[FAQ_Q'+str(j)+r'\](.*?)\[/FAQ_Q'+str(j)+r'\]', t, re.DOTALL)
        a = re.search(r'\[FAQ_A'+str(j)+r'\](.*?)\[/FAQ_A'+str(j)+r'\]', t, re.DOTALL)
        if q and a:
            faq_html += f'<div class="faq-item"><button class="faq-q" onclick="this.parentElement.classList.toggle(\'open\')">{q.group(1).strip()}<span class="faq-icon">+</span></button><div class="faq-a"><p>{a.group(1).strip()}</p></div></div>'
            qt = q.group(1).strip().replace('"',"'")
            at = a.group(1).strip().replace('"',"'")
            faq_schema_items.append(f'{{"@type":"Question","name":"{qt}","acceptedAnswer":{{"@type":"Answer","text":"{at}"}}}}')
    faq_html += '</div>'

    related_links = ''
    try:
        existing = [f for f in os.listdir(cat) if f.endswith('.html') and f != 'index.html' and f != slug+'.html'][:3]
        if existing:
            items = []
            for f in existing:
                fhtml = open(os.path.join(cat, f)).read()
                tm = re.search(r'<title>(.*?) — Le Club', fhtml)
                art_t = tm.group(1) if tm else f.replace('.html','').replace('-',' ').capitalize()
                items.append(f'<a href="/{cat}/{f}" class="related-link">→ {art_t}</a>')
            related_links = '<div class="related-articles"><h3>À lire aussi</h3><div class="related-links">'+''.join(items)+'</div></div>'
    except:
        pass

    cta = '<div class="cta-box"><h3>🎁 Télécharge ton guide de survie GRATUIT</h3><p>Téléchargé par plus de 20 000 femmes intolérantes.</p><a class="cta-btn" href="https://www.whynottraining.fr/08c32d2c-1fbf916c-b0fd38be-d95c800f-ee160319-0993e605" rel="nofollow" target="_blank">Je veux mon guide gratuit →</a></div>' if cat == 'sante' else '<div class="cta-box"><h3>📚 La Bible des Farines Sans Gluten</h3><p>27 farines décryptées, 3 mix magiques, le convertisseur de recettes.</p><a class="cta-btn" href="https://www.whynottraining.fr/ed790464" rel="nofollow" target="_blank">Je veux La Bible des Farines →</a></div>'
    disclaimer = '<div class="disclaimer"><strong>Information médicale :</strong> Cet article est à titre informatif uniquement. Consultez votre médecin.</div>' if cat == 'sante' else ''

    # Carte auteur
    author_card = f'''<div class="author-card">
  <div class="author-avatar">{author['name'][0]}</div>
  <div class="author-info">
    <div class="author-name">{author['name']}</div>
    <div class="author-role">{author['role']}</div>
    <div class="author-bio">{author['bio']}</div>
  </div>
</div>'''

    # Temps affiché seulement pour recettes
    temps_html = f'<span class="article-temps">⏱ {temps}</span>' if temps and cat == 'recettes' else ''

    schema     = f'{{"@context":"https://schema.org","@type":"BlogPosting","headline":"{titre}","description":"{meta}","image":"{img}","datePublished":"{TODAY_ISO}","dateModified":"{TODAY_ISO}","author":{{"@type":"Person","name":"{author["name"]}"}},"publisher":{{"@type":"Organization","name":"Le Club Sans Gluten","url":"https://leclubsansgluten.com"}},"mainEntityOfPage":{{"@type":"WebPage","@id":"https://leclubsansgluten.com/{cat}/{slug}.html"}}}}'
    breadcrumb = f'{{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{{"@type":"ListItem","position":1,"name":"Accueil","item":"https://leclubsansgluten.com/"}},{{"@type":"ListItem","position":2,"name":"{label}","item":"https://leclubsansgluten.com/{cat}/"}},{{"@type":"ListItem","position":3,"name":"{titre}","item":"https://leclubsansgluten.com/{cat}/{slug}.html"}}]}}'
    faq_schema = f'{{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{",".join(faq_schema_items)}]}}' if faq_schema_items else ''

    schemas = f'<script type="application/ld+json">{schema}</script>\n<script type="application/ld+json">{breadcrumb}</script>'
    if faq_schema:
        schemas += f'\n<script type="application/ld+json">{faq_schema}</script>'

    # Popup guide gratuit (fonctionne sur mobile et desktop)
    popup_html = '''<div id="popupGuide" style="display:none;position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.6);z-index:10000;align-items:center;justify-content:center;padding:1rem">
  <div style="background:#fff;border-radius:16px;padding:2rem;max-width:420px;width:100%;text-align:center;position:relative">
    <button onclick="closePopup()" style="position:absolute;top:1rem;right:1rem;background:none;border:none;font-size:1.5rem;cursor:pointer;color:#888">✕</button>
    <div style="font-size:2.5rem;margin-bottom:1rem">🎁</div>
    <h3 style="font-family:var(--serif);font-size:1.3rem;margin-bottom:.75rem">Ton guide de survie OFFERT</h3>
    <p style="color:#666;font-size:.9rem;margin-bottom:1.5rem">Rejoins 20 000 femmes qui vivent sans gluten sans se priver.</p>
    <a href="https://www.whynottraining.fr/08c32d2c-1fbf916c-b0fd38be-d95c800f-ee160319-0993e605" rel="nofollow" target="_blank" style="display:block;background:#c8953a;color:#fff;padding:1rem;border-radius:8px;font-weight:700;text-decoration:none;font-size:1rem">Je veux mon guide gratuit →</a>
  </div>
</div>
<script>
(function(){
  var shown = sessionStorage.getItem('popup_shown');
  if(!shown){
    setTimeout(function(){
      var p = document.getElementById('popupGuide');
      if(p){ p.style.display='flex'; sessionStorage.setItem('popup_shown','1'); }
    }, 8000);
  }
})();
function closePopup(){document.getElementById('popupGuide').style.display='none';}
window.addEventListener('click',function(e){var p=document.getElementById('popupGuide');if(e.target===p)p.style.display='none';});
</script>'''

    html_out = f'''<!DOCTYPE html>
<html lang="fr"><head>
<meta charset="UTF-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>{titre} — Le Club Sans Gluten</title>
<meta name="description" content="{meta}"/>
<meta name="author" content="{author['name']}"/>
<link rel="canonical" href="https://leclubsansgluten.com/{cat}/{slug}.html"/>
<meta property="og:title" content="{titre}"/>
<meta property="og:description" content="{meta}"/>
<meta property="og:image" content="{img}"/>
<meta property="og:type" content="article"/>
<meta name="twitter:card" content="summary_large_image"/>
<meta name="thematique" content="{thematique}"/>
<link rel="preconnect" href="https://fonts.googleapis.com"/>
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin/>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Lora:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet" media="print" onload="this.media='all'"/>
<noscript><link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Lora:ital,wght@0,400;0,700;1,400&display=swap" rel="stylesheet"/></noscript>
<link rel="stylesheet" href="/assets/style.css"/>
{schemas}
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-X0PFTP0TLQ"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-X0PFTP0TLQ');</script>
</head><body>
<div class="top-bar">📚 <a href="https://www.whynottraining.fr/ed790464" rel="nofollow" target="_blank">La Bible des Farines Sans Gluten</a> → <a href="https://www.whynottraining.fr/ed790464" rel="nofollow" target="_blank">Je le veux</a></div>
<header class="site-header"><a href="/" class="logo-wrap"><div class="logo">Le Club<em> Sans Gluten</em></div><span class="logo-sub">Le site sans gluten N°1</span></a><div class="header-search-wrap"><input type="text" class="header-search" placeholder="🔍 Rechercher..." id="headerSearch" autocomplete="off"/><div class="search-results" id="searchResults"></div></div></header>
<nav class="site-nav"><div class="site-nav-inner"><a href="/recettes/">Recettes</a><a href="/sante/">Santé</a><a href="/farines/">Farines</a><a href="/guides/">Conseils</a></div></nav>
<div class="breadcrumb"><a href="/">Accueil</a><span>›</span><a href="/{cat}/">{emoji} {label}</a><span>›</span><span>{titre}</span></div>
<article class="article-wrap">
  <div class="article-header">
    <div class="article-cat-tag">{emoji} {label}</div>
    <h1 class="article-title">{titre}</h1>
    <div class="article-meta">{temps_html}</div>
  </div>
  <img class="article-hero" src="{img}" alt="{titre}" loading="eager" fetchpriority="high"/>
  {disclaimer}
  <div class="article-body">
    {contenu}
  </div>
  {faq_html}
  {cta}
  {related_links}
  {author_card}
</article>
{popup_html}
<button class="back-to-top" id="backToTop" onclick="window.scrollTo({{top:0,behavior:'smooth'}})">↑</button>
<script>window.addEventListener('scroll',function(){{document.getElementById('backToTop').style.display=window.scrollY>600?'flex':'none';}});</script>
<footer class="site-footer"><div class="footer-inner">
  <div class="footer-logo">Le Club <span>Sans Gluten</span></div>
  <div class="footer-links">
    <a href="https://www.whynottraining.fr/08c32d2c-1fbf916c-b0fd38be-d95c800f-ee160319-0993e605" rel="nofollow" target="_blank">🎁 Guide gratuit</a>
    <a href="https://www.whynottraining.fr/ed790464" rel="nofollow" target="_blank">📚 La Bible des Farines</a>
    <a href="/a-propos.html">À propos</a>
    <a href="/glossaire.html">Glossaire</a>
  </div>
  <div class="footer-links" style="margin-top:.5rem;font-size:.8rem">
    <a href="/mentions-legales.html">Mentions légales</a>
    <a href="/cgv.html">CGV</a>
  </div>
  <p class="footer-legal">© 2026 Le Club Sans Gluten · Tous droits réservés</p>
</div></footer>
<div id="cookieBanner" style="display:none;position:fixed;bottom:0;left:0;right:0;background:#1a1a1a;color:#fff;padding:1rem 1.5rem;z-index:9999;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:1rem;font-family:var(--sans);font-size:.875rem">
  <p style="margin:0;flex:1">🍪 Ce site utilise des cookies pour mesurer l'audience. <a href="/mentions-legales.html" style="color:var(--gold)">En savoir plus</a></p>
  <div style="display:flex;gap:.75rem">
    <button onclick="acceptCookies()" style="background:var(--gold);color:#1a1a1a;border:none;padding:.5rem 1.2rem;border-radius:6px;font-weight:700;cursor:pointer">Accepter</button>
    <button onclick="refuseCookies()" style="background:transparent;color:#fff;border:1px solid #555;padding:.5rem 1.2rem;border-radius:6px;cursor:pointer">Refuser</button>
  </div>
</div>
<script>
(function(){{if(!localStorage.getItem('cookie_consent'))document.getElementById('cookieBanner').style.display='flex';}})();
function acceptCookies(){{localStorage.setItem('cookie_consent','accepted');document.getElementById('cookieBanner').style.display='none';}}
function refuseCookies(){{localStorage.setItem('cookie_consent','refused');document.getElementById('cookieBanner').style.display='none';}}
</script>
<script src="/assets/search-index.js"></script>
<script src="/assets/search.js"></script>
</body></html>'''

    os.makedirs(cat, exist_ok=True)
    open(f'{cat}/{slug}.html', 'w').write(html_out)
    print(f'  ✅ {cat}/{slug}.html — {titre}')
    return slug


def build_homepage():
    """Met a jour les sections dynamiques entre les marqueurs DEBUT/FIN."""
    import re as r2
    if not os.path.exists('index.html'):
        return
    html = open('index.html').read()

    DEBUT = '<!-- SECTIONS_AUTO_DEBUT -->'
    FIN   = '<!-- SECTIONS_AUTO_FIN -->'

    if DEBUT not in html or FIN not in html:
        print('  ⚠️ Marqueurs non trouves dans index.html - homepage non modifiee')
        return

    emoji_icons = {'recettes':'🍞','sante':'🌿','farines':'⚖️','guides':'📖'}
    labels = {'recettes':'Recettes','sante':'Santé','farines':'Farines','guides':'Conseils'}

    def get_cards(cat, limit=4):
        if not os.path.exists(cat): return ''
        files = [(os.path.getmtime(os.path.join(cat,f)), f)
                 for f in os.listdir(cat) if f.endswith('.html') and f != 'index.html']
        files.sort(reverse=True)
        out = ''
        for _, f in files[:limit]:
            fhtml = open(os.path.join(cat, f)).read()
            tm = r2.search(r'<title>(.*?) — Le Club', fhtml)
            title = tm.group(1).strip() if tm else f.replace('-',' ').replace('.html','')
            im = r2.search(r'<img class="article-hero"[^>]+src="([^"]+)"', fhtml)
            if not im: im = r2.search(r'"image":"([^"]+)"', fhtml)
            img = im.group(1) if im else ''
            emoji = emoji_icons.get(cat,'')
            label = labels.get(cat, cat)
            out += ('<a href="/' + cat + '/' + f + '" class="card">'
                    '<div class="card-img-wrap"><img class="card-img" src="' + img + '" alt="' + title + '" loading="lazy"/></div>'
                    '<div class="card-body"><div class="card-cat">' + emoji + ' ' + label + '</div>'
                    '<div class="card-title">' + title + '</div></div></a>\n')
        return out

    all_arts = []
    for cat in ['recettes','sante','farines','guides']:
        if not os.path.exists(cat): continue
        for f in os.listdir(cat):
            if not f.endswith('.html') or f == 'index.html': continue
            all_arts.append((os.path.getmtime(os.path.join(cat,f)), cat, f))
    all_arts.sort(reverse=True)
    derniers_cards = ''
    for _, cat, f in all_arts[:6]:
        fhtml = open(os.path.join(cat, f)).read()
        tm = r2.search(r'<title>(.*?) — Le Club', fhtml)
        title = tm.group(1).strip() if tm else f.replace('-',' ').replace('.html','')
        im = r2.search(r'<img class="article-hero"[^>]+src="([^"]+)"', fhtml)
        if not im: im = r2.search(r'"image":"([^"]+)"', fhtml)
        img = im.group(1) if im else ''
        emoji = emoji_icons.get(cat,'')
        label = labels.get(cat, cat)
        derniers_cards += ('<a href="/' + cat + '/' + f + '" class="card">'
                          '<div class="card-img-wrap"><img class="card-img" src="' + img + '" alt="' + title + '" loading="lazy"/></div>'
                          '<div class="card-body"><div class="card-cat">' + emoji + ' ' + label + '</div>'
                          '<div class="card-title">' + title + '</div></div></a>\n')

    def make_section(cat, nb=4):
        emoji = emoji_icons.get(cat,'')
        label = labels.get(cat, cat)
        cards = get_cards(cat, nb)
        return ('<div class="home-wrap">\n'
                '  <div class="section-head">\n'
                '    <h2 class="section-title">' + emoji + ' ' + label + '</h2>\n'
                '    <a class="section-link" href="/' + cat + '/">Tout voir &rarr;</a>\n'
                '  </div>\n'
                '  <div class="articles-grid">\n' + cards + '  </div>\n'
                '</div>\n')

    derniers = ('<div class="home-wrap">\n'
                '  <div class="section-head">\n'
                '    <h2 class="section-title">🆕 Derniers articles</h2>\n'
                '  </div>\n'
                '  <div class="articles-grid">\n' + derniers_cards + '  </div>\n'
                '</div>\n')

    new_content = (derniers +
                   make_section('sante') +
                   make_section('farines') +
                   make_section('guides'))

    debut_pos = html.find(DEBUT) + len(DEBUT)
    fin_pos = html.find(FIN)
    html = html[:debut_pos] + '\n' + new_content + html[fin_pos:]

    open('index.html', 'w').write(html)
    print('  ✅ Sections auto mises a jour')


def build_search_index():
    import json as json3
    articles = []
    cats_config = {
        'recettes': ('Recettes', '🍞'),
        'sante': ('Santé', '🌿'),
        'farines': ('Farines', '⚖️'),
        'guides': ('Conseils', '📖'),
    }
    for cat, (label, emoji) in cats_config.items():
        if not os.path.exists(cat):
            continue
        for f in os.listdir(cat):
            if not f.endswith('.html') or f == 'index.html':
                continue
            fhtml = open(os.path.join(cat, f)).read()
            tm = re.search(r'<title>(.*?) — Le Club', fhtml)
            title = tm.group(1) if tm else f.replace('-',' ').replace('.html','').capitalize()
            im = re.search(r'<img class="article-hero"[^>]+src="([^"]+)"', fhtml)
            if not im: im = re.search(r'"image":"([^"]+)"', fhtml)
            img = im.group(1) if im else ''
            articles.append({'title':title,'url':f'/{cat}/{f}','cat':label,'emoji':emoji,'img':img})
    
    os.makedirs('assets', exist_ok=True)
    js = 'var SEARCH_INDEX = ' + json3.dumps(articles, ensure_ascii=False, separators=(',',':')) + ';'
    open('assets/search-index.js', 'w', encoding='utf-8').write(js)
    print(f'  ✅ Search index — {len(articles)} articles')


if __name__ == '__main__':
    all_cats = ['recettes','sante','farines','guides']
    total = total_articles()
    cats_today = [all_cats[(total + i) % 4] for i in range(4)]

    print(f'📅 {DATE_FR} — Génération de 4 articles')
    print(f'Catégories : {" / ".join(cats_today)}')

    slugs = []
    for i, cat in enumerate(cats_today):
        print(f'\n--- Article {i+1}/4 : {cat} ---')
        try:
            slug = generate_article(cat, i)
            slugs.append(f'{cat}/{slug}')
            build_index(cat)
        except Exception as e:
            print(f'  Erreur article {i+1}: {e}')

    build_sitemap()
    build_homepage()
    build_search_index()

    with open('_slugs.txt', 'w') as f:
        f.write('\n'.join(slugs))

    print(f'\n✅ Terminé — {len(slugs)}/4 articles créés')
