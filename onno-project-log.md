# ONNO — Proje Log (Claude Code Devir Notu)
_Son güncelleme: 23 Temmuz 2026_

## Konum ve Amaç
getonno.com — sağlık turizmi + dijital altyapı hizmeti broker'ı. Tek marka, üç bacak:

1. **Sağlık Turizmi** (`/health-tourism` veya subfolder) — mevcut `klinikdestek` sitesi taşınacak.
2. **Teknik Destek** (`/tech-support`) — Google Maps'ten n8n ile klinik verisi toplanacak, otomatik site analizi + email taslağı ile warm outreach.
3. **Ukrayna / Lviv Diş Bacağı** — bu oturumda tasarlandı, dosya hazır: `onno-lviv-ua.html`

**Mimari karar:** Subdomain değil, **subfolder**. Gerekçe: SEO otoritesi bölünmesin, tek domain gücü birikensin. Ton UI'da ayrışır, URL yapısında değil.

## Bu Oturumda Netleşen Kararlar

- **Marka rengi:** Turkuaz `#11DDDD` + Gri `#6D6D6D` (üç renkten iki renge indirildi — nötr/profesyonel ton için bilinçli sadeleşme, turuncu kaldırıldı).
- **Logo:** Kilitli, kullanıcı onaylı — `onno.svg` (Canva'dan gelen final, split-panel gri/turkuaz, gerçek vektör path, font bağımsız).
- **Ukrayna bacağı dil sırası:** UA (varsayılan) → RU → EN.
- **Vasha Usmishka veri modeli:** `relationship_type: "own"` — partner klinik şemasıyla aynı yapıda ama `commission_rate: 0`, `campaign_owner: "self"`. n8n segmentasyon pipeline'ına tek şema ile entegre edilecek.
- **Fiyatlandırma:** Sabit tablo/hesaplayıcı YOK. Her şey asistan (n8n webhook) üzerinden — statik rakam bayatlar, asistan güncel kalır.
- **Transfer+Konaklama:** Detaysız teaser blok. Sınır kapısı/güzergah bilgisi sitede yok, asistanla görüşmede paylaşılıyor.
- **İletişim kanalı:** WhatsApp değil **Telegram** öncelikli (Ukraynalı diaspora için daha doğal, mevcut Viber/n8n altyapısıyla da örtüşüyor).

## Üretilen Dosyalar
- `/mnt/user-data/outputs/onno-logo-final.svg` — ilk logo denemesi (artık geçersiz, final Canva'dan geldi)
- `onno.svg` (kullanıcı yüklemesi) — **kullanılacak final logo**
- `onno-lviv-ua.html` — Ukrayna/Lviv diş bacağı, tam landing sayfası (nav, hero, trust bar, hizmetler, why-Lviv, süreç, "kimler gelebilir" şeffaflık bloğu, testimonials-placeholder, FAQ, CTA, footer, chat widget iskeleti)

## Claude Code'da Yapılacaklar (öncelik sırasıyla)

1. **Placeholder doldurma** — `onno-lviv-ua.html` içinde:
   - `REPLACE_TELEGRAM` (18 yer) → gerçek Telegram linki
   - `REPLACE@getonno.com` → gerçek email
   - `[YEARS]`, `[PATIENTS]` → Vasha Usmishka'nın gerçek deneyim yılı / hasta sayısı (uydurulmadı, bilerek boş bırakıldı)
   - Testimonials bölümü → gerçek hasta yorumlarıyla değiştirilmeden **yayına alınmamalı**
2. **Ölü CSS temizliği** — eski calculator/booking-form stilleri (`.calc-section`, `.booking-wrap`, `.bstep` vb.) kullanılmıyor ama dosyada duruyor, temizlenebilir.
3. **Chat widget → gerçek n8n webhook** — şu an sahte JS yanıtları var (`chatReplies` objesi), gerçek asistana bağlanacak.
4. **Site iskeleti** — ana sayfa + `/health-tourism` (klinikdestek taşınacak) + `/tech-support` (henüz yok) + Ukrayna bacağı bu sayfa üzerinden.
5. **Google Maps scraping pipeline** (n8n, Places API veya Apify) — henüz kurulmadı, teknik destek bacağı için gerekli.

## Kilitli, Geri Dönülmeyecek Kararlar
- Logo ve renk paleti (turkuaz + gri)
- Subfolder mimarisi (subdomain değil)
- Fiyatlandırmanın asistan üzerinden yönetilmesi (statik tablo yok)
