# -*- coding: utf-8 -*-
"""
ONNO fiyat ureticisi — tek kaynak: pricing.json

  python tools/pricing.py build    site + sema + llms + karsilastirma yeniden uretilir, n8n blogu basilir
  python tools/pricing.py check    uretilen dosyalar pricing.json ile tutuyor mu, dogrular
  python tools/pricing.py n8n      sadece n8n blogunu basar

Tasarim notu: hicbir yerde eski degeri okuyup yenisiyle degistirmiyoruz.
Bolgeler yapidan bulunur ve icerigi komple yeniden yazilir. Boylece
"eski degeri bul, yenisiyle degistir" zincirinden dogan hatalar imkansiz.
"""
import io, json, os, re, sys, hashlib

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG = os.path.join(ROOT, 'pricing.json')

# n8n Code node'undaki degisken adlari — uretilen blok mevcut kodla birebir uyusmali
VARNAME = {'standard': 'STD', 'comfort': 'CMF'}

# Gece sayisi tabloda rakamla yaziliyor; ua/ru cekim sorunundan kacinmak icin
# kisaltma kullaniyoruz (2 ноч. / 6 ноч.), tam kelime cekimi gerektirirdi.
NIGHTS_WORD = {'ua': 'ноч.', 'ru': 'ноч.', 'en': 'nights'}

PAGES = {'ua': 'lviv/index.html', 'ru': 'lviv/ru/index.html', 'en': 'lviv/en/index.html'}
CMP = {'ua': 'lviv/implant-price/index.html',
       'ru': 'lviv/ru/implant-price/index.html',
       'en': 'lviv/en/implant-price/index.html'}


def load():
    return json.load(io.open(CFG, encoding='utf-8'))


# ── hesap ────────────────────────────────────────────────────────────────
def package(cfg, tr, tier_id):
    """tedavi + (transfer x ziyaret) + (gece x otel) + marj, en yakin 5'e yuvarli."""
    lg, r = cfg['logistics'], cfg['meta']['roundTo']
    tier = next(t for t in cfg['tiers'] if t['id'] == tier_id)
    visits = tr.get('visits', cfg['defaults']['visits'])
    nights = tr.get('nights', cfg['defaults']['nights'])
    total = (tr['price']
             + lg['transfer'][tier['transfer']] * visits
             + sum(nights) * lg['hotelPerNight']
             + cfg['margin'][tier_id])
    return int(round(total / r) * r)


def site_tier(cfg):
    return next(t for t in cfg['tiers'] if t.get('showOnSite'))


def fingerprint(cfg):
    """n8n blogunun pricing.json ile ayni surumden gelip gelmedigini anlamak icin."""
    core = json.dumps({k: cfg[k] for k in ('logistics', 'margin', 'defaults', 'treatments')},
                      sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(core.encode('utf-8')).hexdigest()[:8]


# ── site fiyat tablosu ───────────────────────────────────────────────────
def rewrite_table(cfg, path, lang):
    s = io.open(path, encoding='utf-8').read()
    tier = site_tier(cfg)
    i = s.index('<tbody>', s.index('id="prices"'))
    j = s.index('</tbody>', i)
    rows = ''
    for tr in cfg['treatments']:
        n = sum(tr.get('nights', cfg['defaults']['nights']))
        rows += ('          <tr>\n'
                 '            <th scope="row"><span class="%s">%s</span></th>\n'
                 '            <td class="pr-base">€%d</td>\n'
                 '            <td class="pr-pkg">€%d <small class="pr-n">· %d %s</small></td>\n'
                 '          </tr>\n'
                 % (lang, tr['label'][lang], tr['price'],
                    package(cfg, tr, tier['id']), n, NIGHTS_WORD[lang]))
    s = s[:i] + '<tbody>\n' + rows + '        ' + s[j:]
    io.open(path, 'w', encoding='utf-8').write(s)
    return len(cfg['treatments'])


# ── JSON-LD OfferCatalog ─────────────────────────────────────────────────
DESC = {
 'ua': 'Орієнтовна ціна: від {b} € лише за лікування, або від {p} € у пакеті «{t}» ({inc}).',
 'ru': 'Ориентировочная цена: от {b} € только за лечение, или от {p} € в пакете «{t}» ({inc}).',
 'en': 'Approximate price: from {b} € for treatment only, or from {p} € in the "{t}" package ({inc}).',
}


def rewrite_schema(cfg, path, lang):
    s = io.open(path, encoding='utf-8').read()
    m = re.search(r'<script type="application/ld\+json">(.*?)</script>', s, re.S)
    d = json.loads(m.group(1))
    tier = site_tier(cfg)
    cat = next((n for n in d['@graph'] if n.get('@type') == 'OfferCatalog'), None)
    if cat is None:
        return 0
    org = {'@id': [n for n in d['@graph'] if n['@type'] == 'Organization'][0]['@id']}
    items = []
    for k, tr in enumerate(cfg['treatments'], 1):
        p = package(cfg, tr, tier['id'])
        items.append({
            '@type': 'Offer',
            'itemOffered': {'@type': 'Service', 'name': tr['label'][lang], 'provider': org},
            'priceSpecification': {'@type': 'PriceSpecification', 'priceCurrency': cfg['meta']['currency'],
                                   'minPrice': tr['price'], 'valueAddedTaxIncluded': True},
            'description': DESC[lang].format(b=tr['price'], p=p,
                                             t=tier['label'][lang], inc=tier['includes'][lang]),
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
    tier = site_tier(cfg)
    head = '| Treatment | Treatment only, from | Package "%s", from |' % tier['label']['en']
    sep = '|---|---|---|'
    body = ''
    for tr in cfg['treatments']:
        p = package(cfg, tr, tier['id'])
        f = (lambda v: '€%d' % v) if euro else (lambda v: '%d' % v)
        body += '| %s | %s | %s |\n' % (tr['label']['en'], f(tr['price']), f(p))
    block = head + '\n' + sep + '\n' + body
    m = re.search(r'\| Treatment \| Treatment only.*?\n(?:\|.*\n)+', s)
    assert m, fname + ': fiyat tablosu bulunamadi'
    s = s[:m.start()] + block + s[m.end():]
    io.open(path, 'w', encoding='utf-8').write(s)
    return len(cfg['treatments'])


# ── karsilastirma sayfasi ────────────────────────────────────────────────
def pv_values(cfg, style='euro-first'):
    """data-pv isaretli rakamlar. Karsilastirma sayfasi '€950', teklif karti '950 €' yazar."""
    tr = next(t for t in cfg['treatments'] if t['id'] == cfg['comparison']['basedOn'])
    tier = site_tier(cfg)
    pkg = package(cfg, tr, tier['id'])
    cmf = package(cfg, tr, 'comfort')
    f = (lambda v: '€%d' % v) if style == 'euro-first' else (lambda v: '%d €' % v)
    return {
        'base': f(tr['price']),
        'pkg': f(pkg),
        'pkgCmf': f(cmf),
        'addon': f(pkg - tr['price']),
        'saving': f(cfg['comparison']['polandMin'] - pkg),
    }


def rewrite_pv(path, vals):
    s = io.open(path, encoding='utf-8').read()
    n = 0
    for key, val in vals.items():
        s, k = re.subn(r'(<span data-pv="%s">)[^<]*(</span>)' % key,
                       lambda m: m.group(1) + val + m.group(2), s)
        n += k
    io.open(path, 'w', encoding='utf-8').write(s)
    return n


def rewrite_comparison(cfg, path, lang):
    """Dinamik rakamlar <span data-pv="..."> ile isaretli; iceriklerini yeniden yazar."""
    s = io.open(path, encoding='utf-8').read()
    tr = next(t for t in cfg['treatments'] if t['id'] == cfg['comparison']['basedOn'])
    tier = site_tier(cfg)
    pkg = package(cfg, tr, tier['id'])
    vals = {
        'base': '€%d' % tr['price'],
        'pkg': '€%d' % pkg,
        'addon': '€%d' % (pkg - tr['price']),
        'saving': '€%d' % (cfg['comparison']['polandMin'] - pkg),
    }
    n = 0
    for key, val in vals.items():
        s, k = re.subn(r'(<span data-pv="%s">)[^<]*(</span>)' % key,
                       lambda m: m.group(1) + val + m.group(2), s)
        n += k
    io.open(path, 'w', encoding='utf-8').write(s)
    return n


# ── n8n blogu ────────────────────────────────────────────────────────────
def n8n_block(cfg):
    fp = fingerprint(cfg)
    lg = cfg['logistics']
    lines = ['ONNO ORIENTATIONAL PRICE LIST — in EUR, per tooth/unit unless noted. '
             'APPROXIMATE only; the final price is set by a dentist after an in-person exam.']
    for tr in cfg['treatments']:
        lines.append('- %s: from %d EUR' % (tr['botLabel'], tr['price']))

    a = ['// ===== PRICING %s · hash %s — pricing.json tarafindan uretildi, ELLE DEGISTIRME =====' %
         (cfg['meta']['updated'], fp),
         '// `buffer clinic and price` node\'unda 1. bolume yapistir:',
         'const pricesText = [']
    for i, l in enumerate(lines):
        a.append('  %s%s' % (json.dumps(l, ensure_ascii=False), ',' if i < len(lines) - 1 else ''))
    a.append('].join("\\n");')
    a.append('')
    a.append("// `JSON Cleaner1` node'unda (HER IKI workflow'da) 3. bolume yapistir:")

    # Taban fiyata gore paket toplami. Cleaner zaten metinden taban rakami cikariyor,
    # o rakamla buradan bakiyor — boylece tedaviye ozel gece sayisi bota da yansiyor.
    pkg, seen = {}, {}
    for tr in cfg['treatments']:
        b = tr['price']
        row = {t['id']: package(cfg, tr, t['id']) for t in cfg['tiers']}
        if b in seen and seen[b] != row:
            raise SystemExit(
                'CAKISMA: "%s" ve "%s" ayni taban fiyati (%d) tasiyor ama paketleri farkli.\n'
                'Bot tabana gore baktigi icin ayirt edemez. Birinin fiyatini veya gecesini degistir.'
                % (seen[b + 0.5], tr['id'], b))
        seen[b], seen[b + 0.5] = row, tr['id']
        pkg[b] = row

    a.append('const PKG = {')
    for b in sorted(pkg):
        a.append('  %d: { std: %d, cmf: %d },' % (b, pkg[b]['standard'], pkg[b]['comfort']))
    a.append('};')
    for t in cfg['tiers']:
        tot = (lg['transfer'][t['transfer']] * cfg['defaults']['visits']
               + sum(cfg['defaults']['nights']) * lg['hotelPerNight']
               + cfg['margin'][t['id']])
        a.append('const ADDON_%s = %d;   // listede olmayan taban icin yedek'
                 % (VARNAME[t['id']], tot))
    a.append('const r5 = (x) => Math.round(x / %d) * %d;' % (cfg['meta']['roundTo'], cfg['meta']['roundTo']))
    a.append('// kullanim: const P = PKG[base] || { std: r5(base+ADDON_STD), cmf: r5(base+ADDON_CMF) };')
    return '\n'.join(a)


# ── komutlar ─────────────────────────────────────────────────────────────
def cmd_build():
    cfg = load()
    tier = site_tier(cfg)
    print('pricing.json %s · hash %s · site katmani: %s\n'
          % (cfg['meta']['updated'], fingerprint(cfg), tier['label']['en']))
    print('%-34s %s' % ('DOSYA', 'SONUC'))
    offer_vals = pv_values(cfg, style='num-first')
    for lang, rel in PAGES.items():
        p = os.path.join(ROOT, rel)
        print('%-34s tablo %d satir, sema %d teklif, kart %d rakam' %
              (rel, rewrite_table(cfg, p, lang), rewrite_schema(cfg, p, lang),
               rewrite_pv(p, offer_vals)))
    for f, euro in (('llms.txt', False), ('llms-full.txt', True)):
        print('%-34s tablo %d satir' % (f, rewrite_llms(cfg, f, euro)))
    for lang, rel in CMP.items():
        p = os.path.join(ROOT, rel)
        print('%-34s %d rakam' % (rel, rewrite_comparison(cfg, p, lang)))
    print('\n' + '=' * 70)
    print(n8n_block(cfg))
    print('=' * 70)


def cmd_check():
    cfg = load()
    tier = site_tier(cfg)
    bad = []
    want = {tr['label']['en']: (tr['price'], package(cfg, tr, tier['id']))
            for tr in cfg['treatments']}
    for lang, rel in PAGES.items():
        s = io.open(os.path.join(ROOT, rel), encoding='utf-8').read()
        got = re.findall(r'<td class="pr-base">€(\d+)</td>\s*'
                         r'<td class="pr-pkg">€(\d+)', s)
        exp = [(str(tr['price']), str(package(cfg, tr, tier['id']))) for tr in cfg['treatments']]
        if got != exp:
            bad.append('%s: tablo pricing.json ile tutmuyor' % rel)
        j = json.loads(re.search(r'application/ld\+json">(.*?)</script>', s, re.S).group(1))
        cat = next((n for n in j['@graph'] if n.get('@type') == 'OfferCatalog'), None)
        if cat and [o['priceSpecification']['minPrice'] for o in cat['itemListElement']] != \
                   [t['price'] for t in cfg['treatments']]:
            bad.append('%s: OfferCatalog tutmuyor' % rel)
    for f in ('llms.txt', 'llms-full.txt'):
        t = io.open(os.path.join(ROOT, f), encoding='utf-8').read()
        for name, (b, p) in want.items():
            if not re.search(r'\|\s*%s\s*\|\s*€?%d\s*\|\s*€?%d\s*\|' % (re.escape(name), b, p), t):
                bad.append('%s: "%s" satiri tutmuyor' % (f, name)); break
    tr = next(t for t in cfg['treatments'] if t['id'] == cfg['comparison']['basedOn'])
    pkg = package(cfg, tr, tier['id'])
    for lang, rel in CMP.items():
        s = io.open(os.path.join(ROOT, rel), encoding='utf-8').read()
        for key, val in (('pkg', pkg), ('saving', cfg['comparison']['polandMin'] - pkg)):
            if ('<span data-pv="%s">€%d</span>' % (key, val)) not in s:
                bad.append('%s: data-pv="%s" tutmuyor' % (rel, key))
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
