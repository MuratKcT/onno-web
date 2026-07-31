# ONNO — SEO + AIGEO Denetimi ve İş Planı

Tarih: 2026-07-31 · Kapsam: `getonno.com`, `muratkct.github.io/onno-web/` (kök, `/lviv/`, `/health-tourism/`)

---

## 0. Tek cümlelik durum

Site teknik olarak sağlam ama **arama motorları ve AI motorları için pratikte görünmez**: marka alan adı boş, para sayfalarına giden tarama yolu yok, içeriğin üçte ikisi CSS ile gizli, hiçbir yerde yapısal veri yok.

---

## 1. BLOKE EDİCİ — bunlar çözülmeden diğer hiçbir iş sonuç vermez

### 1.1 `getonno.com` park edilmiş durumda
Hostinger park sayfası dönüyor ve üstünde şu var:
```
<meta name="robots" content="noindex, nofollow, noarchive, nosnippet">
```
Yani marka alan adı arama motorlarına **"beni indeksleme, linklerimi izleme, snippet gösterme"** diyor. Gerçek site `muratkct.github.io/onno-web/` altında — üçüncü taraf bir alan adının alt klasöründe.

**Sonucu:** Hiçbir otorite ONNO'ya birikmiyor. "getonno" araması markayı bulamıyor. AI motorları bir sağlık aracısı için `github.io` alt klasörünü otoriter kaynak saymaz.

**Yapılacak:** Alan adını GitHub Pages'e yönlendir (repoya `CNAME` dosyası + Hostinger'da DNS kaydı), Pages ayarlarından custom domain + HTTPS aç.

### 1.2 Para sayfalarına tarama yolu yok
- Kök `index.html` → `<meta name="robots" content="noindex">`
- `/lviv/` ve `/health-tourism/` sayfalarına link veren **tek** sayfa o noindex'li kök
- `robots.txt` yok (404), `sitemap.xml` yok (404)

**Sonucu:** Google'ın Lviv sayfasını keşfetmesinin hiçbir yolu yok.

**Yapılacak:** `robots.txt` + `sitemap.xml` ekle; kökten noindex'i kaldır ya da kökü gerçek bir ana sayfaya çevir.

### 1.3 İçeriğin üçte ikisi Google'a görünmüyor
Dil değiştirme şu şekilde çalışıyor:
```css
body.ua .en, body.ua .ru { display: none !important; }
```
Google CSS'i render eder → sadece varsayılan **UA** metnini indeksler. RU ve EN içerik HTML'de var ama gizli; sıralamaya giremez. Ayrıca RU/EN için ayrı URL olmadığından **hreflang kurmak teknik olarak mümkün değil**.

**Sonucu:** Yazılmış içeriğin ~%66'sı SEO açısından boşa gidiyor. Rusça arama yapan Ukraynalı diaspora (hedef kitlenin büyük kısmı) hiçbir sorguda bu sayfayı bulamaz.

**Yapılacak (seçim gerekiyor — bkz. §5 Karar 1):** Dilleri ayrı URL'lere böl (`/lviv/`, `/lviv/ru/`, `/lviv/en/`) ve hreflang ekle.

---

## 2. YÜKSEK ETKİ — AIGEO'nun asıl kaldıracı

### 2.1 Hiçbir sayfada yapısal veri (JSON-LD) yok
AI cevap motorları ve Google AI Overviews varlık tanımını (entity grounding) şemadan çeker. Şu an sıfır.

**Eklenecek:**
| Şema | Nereye | Neden |
|---|---|---|
| `Organization` | tüm sayfalar | ONNO'yu bir varlık olarak tanımlar |
| `MedicalBusiness` / `MedicalClinic` | `/lviv/` | sektör + hizmet alanı sinyali |
| `FAQPage` | `/lviv/` | **13 soru-cevap zaten yazılmış** — en kolay kazanç |
| `Service` | `/lviv/` | implant, hijyen, kron ayrı ayrı |
| `AggregateRating` | `/lviv/` | 4,8 / 98 — gerçek veri, kaynağı belirtilerek |
| `BreadcrumbList` | alt sayfalar | hiyerarşi |

> Not: `AggregateRating`'i klinik adı vermeden kullanmak Google politikası açısından tartışmalı. Puanın kime ait olduğu belirsizse yapılandırılmış veri yerine sadece görsel rozet olarak bırakmak daha güvenli. §5 Karar 2.

### 2.2 Sayfada hiç fiyat yok
Diş turizmi araması fiyat odaklıdır: *"ціна імпланта Львів"*, *"dental implant Ukraine cost"*, *"скільки коштує коронка"*. Sayfada **tek bir rakam yok**. Umi botunun EUR fiyat haritası var ama sayfa sessiz.

**Sonucu:** En yüksek niyetli sorguların hiçbirine sayfa cevap veremiyor → LLM'in alıntılayacağı bir şey yok.

**Yapılacak:** Bot'taki yaklaşık EUR aralıklarını sayfaya bir fiyat tablosu olarak taşı + mevcut hekim onayı disclaimer'ı. Bu aynı zamanda AIGEO'da en çok alıntılanan içerik tipidir (tablo + net rakam).

### 2.3 Görsellerde alt metni yok
8 görselin 7'sinde `alt` boş — **6 öncesi/sonrası vaka fotoğrafı dahil**. Bunlar sayfanın en özgün, en alıntılanabilir varlıkları ve şu an makinelere hiçbir şey söylemiyorlar.

### 2.4 Eksik temel etiketler
| Etiket | Durum |
|---|---|
| `rel="canonical"` | 3 sayfada da **yok** |
| `og:image` | **yok** → link paylaşımında görsel çıkmıyor |
| `twitter:card` | **yok** |
| `<h1>` sayısı | `/lviv/` ve `/health-tourism/`'de **3'er tane** (dil başına bir) |

CSS'i render etmeyen AI tarayıcıları (GPTBot, ClaudeBot, PerplexityBot çoğunlukla etmez) üç rakip h1 ve iç içe geçmiş üç dil görüyor.

---

## 3. ORTA ÖNCELİK

- **`llms.txt` yok.** ONNO'nun ne olduğunu, hangi sayfaların ne cevapladığını düz metin olarak veren dosya. Ucuz, hızlı, AI motorları için doğrudan yem.
- **`/health-tourism/` marka uyumsuzluğu.** Başlık hâlâ *"Clinic Support — Premium Health Tourism in Turkey"*. ONNO adı geçmiyor.
- **İçerik derinliği yok.** Tek landing page. AIGEO, belirli bir soruyu kapsamlı cevaplayan sayfaları alıntılar. Şu an cevaplanacak niş soru yok.
- **Dış varlık sinyali sıfır.** ONNO hiçbir yerde geçmiyor — dizin, profil, bahsedilme yok. LLM'ler tek kaynaktan sentez yapmaz.

---

## 4. STRATEJİK GERİLİM — açıkça not edilmeli

**"Klinik kimliğini gizle" kuralı yerel SEO'yu doğrudan öldürüyor.**

Diş turizminde sıralama yerel varlık sinyalleriyle olur: isimli klinik, adres, Google Business Profile, o yere bağlı yorumlar. ONNO bunların hiçbirine bilerek sahip değil. Dolayısıyla:

- ❌ `стоматологія Львів` gibi yerel sorgularda ONNO **yarışamaz** — burada uğraşmak boşa emek.
- ✅ Aracı/lojistik açısında yarışabilir ve orada rakip neredeyse yok:
  - *"лікування зубів в Україні для тих, хто живе за кордоном"*
  - *"dental treatment Ukraine from Poland / Germany"*
  - *"скільки коштує імплант в Україні vs Польщі"* (fiyat karşılaştırması)
  - *"як приїхати на лікування зубів з-за кордону"* (süreç, sınır, belgeler)

Bu ikinci küme aynı zamanda **AIGEO için ideal**: karşılaştırma ve süreç soruları LLM'lerin en çok alıntı ürettiği sorgu tipi.

**Öneri:** SEO hedefini "Lviv'de diş kliniği" değil, **"yurt dışındaki Ukraynalı için Ukrayna'da tedavi lojistiği"** olarak konumlandır.

---

## 5. KARAR GEREKTİREN 3 NOKTA

**Karar 1 — Dil mimarisi.** Üç seçenek:
- **(a)** Ayrı URL'ler + hreflang → SEO açısından doğru olan, en çok iş
- **(b)** Sadece UA'da kal, RU/EN'i widget'ta bırak → en az iş, RU pazarı feda
- **(c)** Şimdilik UA + RU ayır, EN sonra → dengeli

**Karar 2 — `AggregateRating` şeması.** Klinik adı verilmeden 4,8/98 puanını yapısal veriye koymak politika riski taşır. Koyalım mı, yoksa sadece görsel rozet mi kalsın?

**Karar 3 — Fiyat şeffaflığı.** Yaklaşık EUR aralıklarını sayfaya koymak SEO/AIGEO için en yüksek getirili tek hamle. Ama fiyatı sayfaya koymak, botla başlayan konuşmanın bir kısmını da götürür. Kabul mü?

---

## 6. İŞ PLANI — sıralı fazlar

### Faz 0 — Altyapı (bloke edici, önce bu)
| # | İş | Süre |
|---|---|---|
| 0.1 | `CNAME` dosyası + Hostinger DNS → getonno.com'u Pages'e bağla | 30 dk + DNS yayılımı |
| 0.2 | Pages'te custom domain + "Enforce HTTPS" | 10 dk |
| 0.3 | `robots.txt` (AI tarayıcılarına açık, sitemap bildirimli) | 10 dk |
| 0.4 | `sitemap.xml` | 15 dk |
| 0.5 | Kök sayfadan `noindex`i kaldır / gerçek ana sayfaya çevir | 30 dk |
| 0.6 | Google Search Console + Bing Webmaster doğrulama, sitemap gönderimi | 20 dk |

### Faz 1 — Sayfa içi teknik temel
| # | İş | Süre |
|---|---|---|
| 1.1 | `canonical` — 3 sayfa | 15 dk |
| 1.2 | `og:image` üret (1200×630) + og/twitter etiketleri | 45 dk |
| 1.3 | 6 vaka görseline + hero'ya açıklayıcı `alt` | 20 dk |
| 1.4 | h1 sayısını düzelt | 20 dk |
| 1.5 | `/health-tourism/` başlık + meta'yı ONNO markasına çek | 20 dk |

### Faz 2 — AIGEO çekirdeği (asıl kaldıraç)
| # | İş | Süre |
|---|---|---|
| 2.1 | `Organization` + `MedicalBusiness` JSON-LD | 45 dk |
| 2.2 | `FAQPage` JSON-LD — 13 soru zaten hazır | 30 dk |
| 2.3 | `Service` şemaları (implant / hijyen / kron / transfer) | 30 dk |
| 2.4 | **Fiyat tablosu bölümü** — botun EUR haritası + disclaimer | 2 sa |
| 2.5 | `llms.txt` + `llms-full.txt` | 45 dk |

### Faz 3 — Dil mimarisi *(Karar 1'e bağlı)*
| # | İş | Süre |
|---|---|---|
| 3.1 | Dilleri ayrı URL'lere böl | 3-4 sa |
| 3.2 | `hreflang` + dil bazlı canonical | 1 sa |
| 3.3 | Dil bazlı title/description/OG | 1 sa |

### Faz 4 — İçerik derinliği (sürekli iş)
Aracı/lojistik açısına odaklı, her biri tek bir soruyu kapsamlı cevaplayan sayfalar:
1. Ukrayna vs Polonya vs Almanya diş fiyatı karşılaştırması *(en yüksek AIGEO getirisi)*
2. Yurt dışından tedaviye gelme rehberi — sınır, belge, süre
3. İmplant süreci: kaç ziyaret, ne kadar sürer, aradaki bakım
4. Uzaktan takip nasıl işler

### Faz 5 — Dış varlık sinyali
Marka bahsi ve dizin kaydı — LLM'lerin tek kaynaktan sentez yapmaması için gerekli. Kapsam ayrıca netleştirilecek.

---

## 7. Sırayla ne yapılmalı — özet

1. **Faz 0'ı bugün bitir.** Bunlar olmadan yapılan her SEO işi rafta kalır.
2. **Faz 2.4 (fiyat) + 2.2 (FAQ şeması)** en yüksek getirili iki tekil iş.
3. Faz 3'e Karar 1 verildikten sonra gir.
4. Faz 4 sürekli; ilk yazı fiyat karşılaştırması olmalı.
