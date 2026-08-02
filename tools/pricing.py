# -*- coding: utf-8 -*-
"""
ONNO fiyat ureticisi — tek kaynak: pricing.json

  python tools/pricing.py build    site + sema + llms + karsilastirma yeniden uretilir, n8n blogu basilir
  python tools/pricing.py check    uretilen dosyalar pricing.json ile tutuyor mu, dogrular
  python tools/pricing.py n8n      sadece n8n blogunu basar

Model
-----
Yazilan sey SERVIS. Paketler servis x katman olarak turetiliyor, kimlik: "<servis>.<katman>".
Hastaya SADECE paket fiyati gosterilir; tedavi/yol/otel/kar kalemleri asla ayri gorunmez.

  lojistik = transfer[katman] x visits + nights x otel + kar[katman]
  paket    = yuvarla5(tedavi x adet + lojistik)

Adet sadece tedaviyi carpar. Iki implant icin iki transfer ve iki kat gece odenmez;
eski surumde bu yanlisti.

Bot fiyat HESAPLAMAZ: katalogdan bir kimlik secer, hesabi JSON Cleaner yapar.
Bilinmeyen kimlik gelirse fiyat hic gosterilmez — yanlis fiyat gosterilmez.

Bolgeler dosyalarda aranip degistirilmez, yapidan bulunup sifirdan yazilir.
Boylece "eski degeri bul, yenisiyle degistir" zincirinden dogan hatalar imkansiz.
"""
import io, json, os, re, sys, hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = os.path.join(ROOT, 'pricing.json')

PAGES = {'ua': 'lviv/index.html', 'ru': 'lviv/ru/index.html', 'en': 'lviv/en/index.html'}
CMP = {'ua': 'lviv/implant-price/index.html',
       'ru': 'lviv/ru/implant-price/index.html',
       'en': 'lviv/en/implant-price/index.html'}

TH = {
 'ua': ('Послуга', 'Пакет «під ключ», від', 'ноч.'),
 'ru': ('Услуга', 'Пакет «под ключ», от', 'ноч.'),
 'en': ('Treatment', 'Turnkey package, from', 'nights'),
}


def load():
    return json.load(io.open(CFG, encoding='utf-8'))


# ── hesap ────────────────────────────────────────────────────────────────
def tier_of(cfg, tid):
    return next(t for t in cfg['tiers'] if t['id'] == tid)


def logistics(cfg, svc, tid):
    """Hastaya asla ayri gosterilmeyen toplam ek."""
    lg, t = cfg['logistics'], tier_of(cfg, tid)
    return (lg['transfer'][t['transfer']] * svc['visits']
            + svc['nights'] * lg['hotelPerNight']
            + cfg['margin'][t['transfer']])


def price(cfg, svc, tid, qty=1):
    r = cfg['meta']['roundTo']
    return int(round((svc['treatment'] * qty + logistics(cfg, svc, tid)) / r) * r)


def site_tier(cfg):
    return next(t for t in cfg['tiers'] if t.get('showOnSite'))


def featured(cfg):
    return next((s for s in cfg['services'] if s.get('featured')), cfg['services'][0])


def fingerprint(cfg):
    core = json.dumps({k: cfg[k] for k in ('logistics', 'margin', 'tiers', 'services')},
                      sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(core.encode('utf-8')).hexdigest()[:8]


# ── site fiyat tablosu ───────────────────────────────────────────────────
def rewrite_table(cfg, path, lang):
    s = io.open(path, encoding='utf-8').read()
    t = site_tier(cfg)
    hs, hp, nw = TH[lang]
    rows = ''
    for svc in cfg['services']:
        rows += ('          <tr>\n'
                 '            <th scope="row"><span class="%s">%s</span></th>\n'
                 '            <td class="pr-pkg">€%d <small class="pr-n">· %d %s</small></td>\n'
                 '          </tr>\n'
                 % (lang, svc['name'][lang], price(cfg, svc, t['id']), svc['nights'], nw))
    table = ('<table class="price-table">\n'
             '          <thead>\n'
             '            <tr><th scope="col">%s</th>'
             '<th scope="col" class="price-head-pkg">%s</th></tr>\n'
             '          </thead>\n'
             '          <tbody>\n%s        </tbody>\n        </table>' % (hs, hp, rows))
    a = s.index('<table class="price-table">')
    b = s.index('</table>', a) + len('</table>')
    s = s[:a] + table + s[b:]
    io.open(path, 'w', encoding='utf-8').write(s)
    return len(cfg['services'])


# ── JSON-LD ──────────────────────────────────────────────────────────────
DESC = {
 'ua': 'Пакет «під ключ» від {p} € — {inc}. {n} ночей у Львові.',
 'ru': 'Пакет «под ключ» от {p} € — {inc}. {n} ночей во Львове.',
 'en': 'Turnkey package from {p} € — {inc}. {n} nights in Lviv.',
}


def rewrite_schema(cfg, path, lang):
    s = io.open(path, encoding='utf-8').read()
    m = re.search(r'<script type="application/ld\+json">(.*?)</script>', s, re.S)
    d = json.loads(m.group(1))
    cat = next((n for n in d['@graph'] if n.get('@type') == 'OfferCatalog'), None)
    if cat is None:
        return 0
    org = {'@id': [n for n in d['@graph'] if n['@type'] == 'Organization'][0]['@id']}
    t = site_tier(cfg)
    items = []
    for k, svc in enumerate(cfg['services'], 1):
        p = price(cfg, svc, t['id'])
        items.append({
            '@type': 'Offer',
            'itemOffered': {'@type': 'Service', 'name': svc['name'][lang], 'provider': org},
            'priceSpecification': {'@type': 'PriceSpecification',
                                   'priceCurrency': cfg['meta']['currency'],
                                   'minPrice': p, 'valueAddedTaxIncluded': True},
            'description': DESC[lang].format(p=p, inc=t['includes'][lang], n=svc['nights']),
            'position': k,
        })
    cat['itemListElement'] = items
    cat['numberOfItems'] = len(items)
    new = ('<script type="application/ld+json">\n'
           + json.dumps(d, ensure_ascii=False, indent=2) + '\n</script>')
    s = s[:m.start()] + new + s[m.end():]
    io.open(path, 'w', encoding='utf-8').write(s)
    return len(items)


# ── llms.txt / llms-full.txt ─────────────────────────────────────────────
def rewrite_llms(cfg, fname, euro):
    path = os.path.join(ROOT, fname)
    s = io.open(path, encoding='utf-8').read()
    t = site_tier(cfg)
    f = (lambda v: '€%d' % v) if euro else (lambda v: '%d' % v)
    block = ('| Package | Price, from | Nights in Lviv |\n|---|---|---|\n'
             + ''.join('| %s | %s | %d |\n' % (s2['name']['en'], f(price(cfg, s2, t['id'])), s2['nights'])
                       for s2 in cfg['services']))
    m = re.search(r'\| (?:Treatment|Package) \|.*?\n(?:\|.*\n)+', s)
    assert m, fname + ': fiyat tablosu bulunamadi'
    s = s[:m.start()] + block + s[m.end():]
    io.open(path, 'w', encoding='utf-8').write(s)
    return len(cfg['services'])


# ── data-pv isaretli rakamlar ────────────────────────────────────────────
def pv_values(cfg, euro_first):
    svc = featured(cfg)
    std = price(cfg, svc, site_tier(cfg)['id'])
    cmf = price(cfg, svc, next(t['id'] for t in cfg['tiers'] if not t.get('showOnSite')))
    f = (lambda v: '€%d' % v) if euro_first else (lambda v: '%d €' % v)
    return {'base': f(svc['treatment']), 'pkg': f(std), 'pkgCmf': f(cmf),
            'addon': f(std - svc['treatment']),
            'saving': f(cfg['comparison']['polandMin'] - std)}


def rewrite_pv(path, vals):
    s = io.open(path, encoding='utf-8').read()
    n = 0
    for key, val in vals.items():
        s, k = re.subn(r'(<span data-pv="%s">)[^<]*(</span>)' % key,
                       lambda m: m.group(1) + val + m.group(2), s)
        n += k
    io.open(path, 'w', encoding='utf-8').write(s)
    return n


# ── n8n blogu ────────────────────────────────────────────────────────────
def n8n_block(cfg):
    t_std = site_tier(cfg)
    t_cmf = next(t for t in cfg['tiers'] if not t.get('showOnSite'))
    a = ['// ===== ONNO PAKET KATALOGU  %s · hash %s =====' % (cfg['meta']['updated'], fingerprint(cfg)),
         '// tools/pricing.py tarafindan uretildi. ELLE DEGISTIRME.',
         '// Bot fiyat hesaplamaz: bir kimlik secer, hesap burada yapilir.',
         '//   t = tedavi (adetle carpilir), l = lojistik (carpilmaz)',
         'const PKG = {']
    for svc in cfg['services']:
        for t in (t_std, t_cmf):
            a.append('  "%s.%s": { t: %d, l: %d, n: %d },'
                     % (svc['id'], t['id'], svc['treatment'], logistics(cfg, svc, t['id']), svc['nights']))
    a.append('};')
    a.append('const r5 = (x) => Math.round(x / %d) * %d;' % (cfg['meta']['roundTo'], cfg['meta']['roundTo']))
    a.append('const pkgPrice = (id, qty) => { const p = PKG[id]; '
             'return p ? r5(p.t * (qty || 1) + p.l) : null; };')
    a.append('')
    a.append('// --- ajana verilecek katalog metni (buffer node) ---')
    a.append('const pricesText = [')
    a.append('  "ONNO PACKAGE CATALOGUE — pick ONE id. Prices are turnkey and already include '
             'the transfer from Warsaw, accommodation and coordination. Never invent a price; '
             'never add anything up yourself.",')
    for svc in cfg['services']:
        a.append('  "- %s.%s | %s | from %d EUR | %d nights | %s",'
                 % (svc['id'], t_std['id'], svc['name']['en'],
                    price(cfg, svc, t_std['id']), svc['nights'], svc['botDesc']))
    a.append('  "Add \\".%s\\" instead of \\".%s\\" if the patient asks for a private car transfer."'
             % (t_cmf['id'], t_std['id']))
    a.append('].join("\\n");')
    return '\n'.join(a)


# ── komutlar ─────────────────────────────────────────────────────────────
def cmd_build():
    cfg = load()
    t = site_tier(cfg)
    print('pricing.json %s · hash %s · %d hizmet · site katmani: %s\n'
          % (cfg['meta']['updated'], fingerprint(cfg), len(cfg['services']), t['label']['en']))
    offer = pv_values(cfg, euro_first=False)
    for lang, rel in PAGES.items():
        p = os.path.join(ROOT, rel)
        print('%-34s tablo %d, sema %d, kart %d' %
              (rel, rewrite_table(cfg, p, lang), rewrite_schema(cfg, p, lang), rewrite_pv(p, offer)))
    for f, euro in (('llms.txt', False), ('llms-full.txt', True)):
        print('%-34s tablo %d' % (f, rewrite_llms(cfg, f, euro)))
    cmpv = pv_values(cfg, euro_first=True)
    for lang, rel in CMP.items():
        print('%-34s %d rakam' % (rel, rewrite_pv(os.path.join(ROOT, rel), cmpv)))
    print('\n' + '=' * 72)
    print(n8n_block(cfg))
    print('=' * 72)


def cmd_check():
    cfg = load()
    t = site_tier(cfg)
    bad = []
    exp = [str(price(cfg, s, t['id'])) for s in cfg['services']]
    for lang, rel in PAGES.items():
        s = io.open(os.path.join(ROOT, rel), encoding='utf-8').read()
        if re.findall(r'<td class="pr-pkg">€(\d+)', s) != exp:
            bad.append('%s: tablo tutmuyor' % rel)
        if '<td class="pr-base"' in s:
            bad.append('%s: eski "sadece tedavi" sutunu duruyor' % rel)
        j = json.loads(re.search(r'application/ld\+json">(.*?)</script>', s, re.S).group(1))
        cat = next((n for n in j['@graph'] if n.get('@type') == 'OfferCatalog'), None)
        if cat and [o['priceSpecification']['minPrice'] for o in cat['itemListElement']] != [int(x) for x in exp]:
            bad.append('%s: OfferCatalog tutmuyor' % rel)
    for f in ('llms.txt', 'llms-full.txt'):
        txt = io.open(os.path.join(ROOT, f), encoding='utf-8').read()
        for s2 in cfg['services']:
            p = price(cfg, s2, t['id'])
            if not re.search(r'\|\s*%s\s*\|\s*€?%d\s*\|' % (re.escape(s2['name']['en']), p), txt):
                bad.append('%s: "%s" tutmuyor' % (f, s2['name']['en'])); break
    v = pv_values(cfg, euro_first=True)
    for lang, rel in CMP.items():
        s = io.open(os.path.join(ROOT, rel), encoding='utf-8').read()
        for k in ('pkg', 'saving'):
            if ('<span data-pv="%s">%s</span>' % (k, v[k])) not in s:
                bad.append('%s: data-pv="%s" tutmuyor' % (rel, k))
    print('SONUC:', 'TUTARLI' if not bad else 'SORUN VAR')
    for b in bad:
        print('  -', b)
    return 1 if bad else 0


if __name__ == '__main__':
    c = sys.argv[1] if len(sys.argv) > 1 else 'build'
    if c == 'build':
        cmd_build()
    elif c == 'check':
        sys.exit(cmd_check())
    elif c == 'n8n':
        print(n8n_block(load()))
    else:
        print(__doc__)
