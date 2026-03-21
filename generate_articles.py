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
DESCS  = {
    'recettes': 'Recettes sans gluten testées et approuvées par notre communauté de 100 000 membres.',
    'sante':    'Symptômes, diagnostics, conseils santé pour vivre mieux sans gluten. Articles vérifiés.',
    'farines':  "Comparatifs complets des farines sans gluten. Guides d'utilisation pratiques.",
    'guides':   'Guides pratiques pour bien vivre sans gluten : débuter, voyager, cuisiner avec un petit budget.'
}
# Images de fallback Unsplash variées par thème
IMAGES_FALLBACK = {
    'recettes': [
        'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=1200&q=80',
        'https://images.unsplash.com/photo-1547592180-85f173990554?w=1200&q=80',
        'https://images.unsplash.com/photo-1490645935967-10de6ba17061?w=1200&q=80',
        'https://images.unsplash.com/photo-1565299543923-37dd37887442?w=1200&q=80',
        'https://images.unsplash.com/photo-1519676867240-f03562e64548?w=1200&q=80',
        'https://images.unsplash.com/photo-1574894709920-11b28e7367e3?w=1200&q=80',
        'https://images.unsplash.com/photo-1568571780765-9276ac8b75a2?w=1200&q=80',
        'https://images.unsplash.com/photo-1606313564200-e75d5e30476c?w=1200&q=80',
    ],
    'sante': [
        'https://images.unsplash.com/photo-1540420773420-3366772f4999?w=1200&q=80',
        'https://images.unsplash.com/photo-1505576399279-565b52d4ac71?w=1200&q=80',
        'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=1200&q=80',
        'https://images.unsplash.com/photo-1490645935967-10de6ba17061?w=1200&q=80',
        'https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=1200&q=80',
        'https://images.unsplash.com/photo-1544126592-807ade215a0b?w=1200&q=80',
    ],
    'farines': [
        'https://images.unsplash.com/photo-1612200606649-1e95b16fcf2c?w=1200&q=80',
        'https://images.unsplash.com/photo-1585478259715-4c6d5047b7c1?w=1200&q=80',
        'https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=1200&q=80',
        'https://images.unsplash.com/photo-1558636508-e0969431e67f?w=1200&q=80',
        'https://images.unsplash.com/photo-1556909211-36987daf7b4d?w=1200&q=80',
    ],
    'guides': [
        'https://images.unsplash.com/photo-1499636136210-6f4ee915583e?w=1200&q=80',
        'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=1200&q=80',
        'https://images.unsplash.com/photo-1503676260728-1c00da094a0b?w=1200&q=80',
        'https://images.unsplash.com/photo-1482575832494-771f74bf6857?w=1200&q=80',
        'https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=1200&q=80',
        'https://images.unsplash.com/photo-1542838132-92c53300491e?w=1200&q=80',
    ],
}

# Compteur global pour varier les fallbacks
_fallback_counter = 0

# Compteur global pour varier les images
_img_counter = 0

# Pool d'images Unsplash de fallback variées par thème
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

def get_pexels_image(titre, cat):
    """Cherche une photo Pexels. Si echec, utilise Unsplash avec compteur."""
    global _img_counter
    _img_counter += 1
    import urllib.request, urllib.parse, json as json2

    # Essai Pexels
    try:
        query = ' '.join(titre.replace(':', '').replace('—', '').strip().split()[:5])
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
            img_url = data['photos'][idx]['src']['large2x']
            print(f'  📸 Pexels: OK')
            return img_url
    except Exception as e:
        print(f'  ⚠️ Pexels echoue, fallback Unsplash: {e}')

    # Fallback : recherche Unsplash par titre
    try:
        import urllib.parse
        query = ' '.join(titre.replace(':', '').replace('—', '').strip().split()[:5])
        page = (_img_counter % 10) + 1
        url = f'https://api.unsplash.com/search/photos?query={urllib.parse.quote(query)}&per_page=10&page={page}&orientation=landscape'
        req = urllib.request.Request(url, headers={
            'Authorization': f'Client-ID {UNSPLASH_KEY}',
            'Accept-Version': 'v1',
        })
        data = json2.loads(urllib.request.urlopen(req, timeout=15).read())
        if data.get('results'):
            idx = (_img_counter - 1) % len(data['results'])
            img_url = data['results'][idx]['urls']['regular']
            print(f'  📸 Unsplash: OK')
            return img_url
    except Exception as e:
        print(f'  ⚠️ Unsplash echoue aussi: {e}')

    # Dernier recours : pool fixe
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

CATÉGORIE : {cat}

Choisis un sujet précis longue traîne pour {cat}, ciblant les femmes françaises 30-55 ans intolérantes au gluten. Sujet non redondant.

Rédige un article complet 3500 mots minimum avec :
- Introduction répondant immédiatement à l'intention de recherche
- 6+ H2 avec mots-clés intégrés naturellement
- Paragraphes courts (150-200 mots), ton chaleureux d'experte
- 2+ listes ou tableaux avec données chiffrées
- FAQ 4 questions réelles Google

FORMAT EXACT :
[TITRE]titre 60 car max avec accents[/TITRE]
[SLUG]slug-sans-accents[/SLUG]
[META]meta description 155 car max[/META]
[TEMPS]X min[/TEMPS]
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
    temps      = extract('TEMPS', t) or '8 min'
    thematique = extract('THEMATIQUE', t).strip().lower() or ''
    contenu    = extract('CONTENU', t) or '<p>Article en cours.</p>'
    # Chercher une vraie photo Pexels en lien avec le titre
    img = get_pexels_image(titre, cat)

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

    cta = '<div class="cta-box"><h3>🎁 Télécharge ton guide de survie GRATUIT</h3><p>Téléchargé par plus de 20 000 femmes intolérantes.</p><a class="cta-btn" href="https://www.whynottraining.fr/08c32d2c-1fbf916c-b0fd38be-d95c800f-ee160319-0993e605" target="_blank">Je veux mon guide gratuit →</a></div>' if cat == 'sante' else '<div class="cta-box"><h3>📚 La Bible des Farines Sans Gluten</h3><p>27 farines décryptées, 3 mix magiques, le convertisseur de recettes.</p><a class="cta-btn" href="https://www.whynottraining.fr/ed790464" target="_blank">Je veux La Bible des Farines →</a></div>'
    disclaimer = '<div class="disclaimer"><strong>Information médicale :</strong> Cet article est à titre informatif uniquement. Consultez votre médecin.</div>' if cat == 'sante' else ''

    schema     = f'{{"@context":"https://schema.org","@type":"BlogPosting","headline":"{titre}","description":"{meta}","image":"{img}","datePublished":"{TODAY_ISO}","dateModified":"{TODAY_ISO}","author":{{"@type":"Organization","name":"Le Club Sans Gluten"}},"publisher":{{"@type":"Organization","name":"Le Club Sans Gluten","url":"https://leclubsansgluten.com"}},"mainEntityOfPage":{{"@type":"WebPage","@id":"https://leclubsansgluten.com/{cat}/{slug}.html"}}}}'
    breadcrumb = f'{{"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[{{"@type":"ListItem","position":1,"name":"Accueil","item":"https://leclubsansgluten.com/"}},{{"@type":"ListItem","position":2,"name":"{label}","item":"https://leclubsansgluten.com/{cat}/"}},{{"@type":"ListItem","position":3,"name":"{titre}","item":"https://leclubsansgluten.com/{cat}/{slug}.html"}}]}}'
    faq_schema = f'{{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{",".join(faq_schema_items)}]}}' if faq_schema_items else ''

    html = open('template.html').read()
    # Injecter la thématique dans un meta tag
    html = html.replace('</head>', f'<meta name="thematique" content="{thematique}"/>\n</head>', 1)
    for k, v in [('[TITRE_SEO]',titre),('[TITRE_ARTICLE]',titre),('[SLUG]',slug),
                 ('[META_DESCRIPTION]',meta),('[CATEGORIE]',cat),('[CATEGORIE_LABEL]',label),
                 ('[CATEGORIE_EMOJI]',emoji),('[DATE_PUBLICATION]',DATE_FR),('[TEMPS_LECTURE]',temps),
                 ('[IMAGE_URL]',img),('[CTA_BOX]',cta),('[DISCLAIMER]',disclaimer),
                 ('[FAQ_BLOCK]',faq_html),('[MAILLAGE_INTERNE]',related_links),('[CONTENU_ARTICLE]',contenu)]:
        html = html.replace(k, v)

    schemas = f'<script type="application/ld+json">{schema}</script>\n<script type="application/ld+json">{breadcrumb}</script>'
    if faq_schema:
        schemas += f'\n<script type="application/ld+json">{faq_schema}</script>'
    html = html.replace('<script type="application/ld+json">[SCHEMA_JSON]</script>', schemas)

    os.makedirs(cat, exist_ok=True)
    open(f'{cat}/{slug}.html', 'w').write(html)
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

    labels = {'recettes':'Recettes','sante':'Sante','farines':'Farines','guides':'Conseils'}
    emojis = {'recettes':'Recettes','sante':'Sante','farines':'Farines','guides':'Conseils'}
    emoji_icons = {'recettes':'🍞','sante':'🌿','farines':'⚖️','guides':'📖'}

    def get_cards(cat, limit=4):
        if not os.path.exists(cat): return ''
        files = [(os.path.getmtime(os.path.join(cat,f)), f)
                 for f in os.listdir(cat) if f.endswith('.html') and f != 'index.html']
        files.sort(reverse=True)
        out = ''
        for _, f in files[:limit]:
            fhtml = open(os.path.join(cat, f)).read()
            tm = r2.search(r'<title>(.*?)[—\-]', fhtml)
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

    # Derniers articles
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
        tm = r2.search(r'<title>(.*?)[—\-]', fhtml)
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

    # Remplacer entre les marqueurs
    debut_pos = html.find(DEBUT) + len(DEBUT)
    fin_pos = html.find(FIN)
    html = html[:debut_pos] + '\n' + new_content + html[fin_pos:]

    open('index.html', 'w').write(html)
    print('  ✅ Sections auto mises a jour')


def build_search_index():
    """Génère l'index de recherche pour le moteur de recherche du site."""
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
