# ONNO — getonno.com

Sağlık turizmi + dijital altyapı hizmeti broker'ı. Tek marka, çok bacak; **subfolder** mimarisi (subdomain değil — SEO otoritesi tek domainde toplansın).

## Yapı

```
/
├── index.html              # Geçici ana sayfa / hub (yönlendirme)
├── health-tourism/
│   └── index.html          # Türkiye sağlık turizmi (Clinic Support) — EN / TR / PL
├── lviv/
│   └── index.html          # Ukrayna / Lviv diş tedavisi — UA / RU / EN
├── assets/
│   ├── onno-logo.svg       # Nav/hub logosu (beyaz üst-alt kırpılmış, şeffaf)
│   └── onno.svg            # Orijinal kare logo (Canva final kaynağı)
└── onno-project-log.md     # Proje devir notu / karar geçmişi
```

İki landing page **ayrı sayfalar** olarak duruyor (birleştirilmedi); tek repo/site altında toplandı.

## Marka

- Renk: turkuaz `#11DDDD` + gri `#6D6D6D`
- Logo: `onno.svg` (kilitli, kullanıcı onaylı)
- İletişim: Telegram öncelikli (Lviv bacağı)

## Açık işler (öncelik sırası)

1. `lviv/index.html` placeholder'ları: `REPLACE_TELEGRAM`, `REPLACE@getonno.com`, `[YEARS]`, `[PATIENTS]`, gerçek testimonials.
2. Ölü CSS temizliği (Lviv'de kullanılmayan calculator/booking stilleri).
3. Chat widget → gerçek n8n webhook (şu an sahte JS yanıtları).
4. Ana sayfa (`/`) tasarımı + `/tech-support` bacağı.

Ayrıntı için `onno-project-log.md`.
