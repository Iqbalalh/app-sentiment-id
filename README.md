# App Sentiment ID

Alat analisis sentimen ulasan aplikasi berbahasa Indonesia. App Sentiment ID
mengumpulkan ulasan publik dari **Google Play Store**, **Apple App Store**, dan
komentar **TikTok**, lalu mengklasifikasikannya menjadi *positif*, *netral*,
atau *negatif* menggunakan model transformer multibahasa.

Kategori: **NLP — Analisis Sentimen** (sentiment analysis / opinion mining).

Proyek bersifat generik: aplikasi yang dianalisis cukup ditentukan lewat berkas
`.env`, tanpa mengubah kode. Setiap platform berjalan terisolasi sehingga data
dan hasil satu platform tidak bercampur dengan platform lain.

## Fitur

- Tiga sumber data: Play Store, App Store (RSS resmi Apple), dan TikTok.
- Pembersihan data sebelum analisis: membuang komentar kosong, komentar tanpa
  teks (emoji/simbol saja), dan **komentar duplikat (indikasi spam/buzzer)** —
  dengan pelacakan berapa komentar di-scrap, dipakai, dan dibuang.
- Preprocessing Bahasa Indonesia: *case folding*, pembersihan, normalisasi slang
  (kamus alay), penghapusan stopword dengan negasi dipertahankan, dan stemming
  (Sastrawi).
- Klasifikasi tiga kelas berbasis transformer dengan probabilitas per label.
- Keluaran siap pakai: CSV berlabel, diagram distribusi, pie chart, word cloud,
  dan peringkat kata dominan.
- Laporan analisis naratif (Markdown) per platform **dan gabungan**: faktor
  pemicu opini negatif/positif, pemetaan aspek (login, error, performa, dll.),
  kata/frasa dominan, kutipan representatif, dan kesimpulan akhir.
- Satu entrypoint (`main.py`) menjalankan seluruh alur end-to-end dengan
  progress bar pada tahap preprocessing dan klasifikasi.

## Struktur Proyek

```
.
├── main.py              # entrypoint utama: jalankan seluruh pipeline + laporan
├── report.py            # entrypoint: buat laporan analisis dari output yang ada
├── config.py            # konfigurasi terpusat, dibaca dari .env
├── setup_resources.py   # unduh kamus normalisasi ke resources/
├── requirements.txt
├── .env.example         # template konfigurasi
│
├── scrapers/            # pengambil data per platform (independen)
│   ├── playstore.py
│   ├── appstore.py
│   └── tiktok.py
│
├── sentiment/           # mesin analisis (dipakai bersama)
│   ├── cleaning.py      # buang komentar kosong/spam/duplikat + lacak provenance
│   ├── preprocessing.py # case folding → cleansing → tokenizing → normalisasi → filtering → stemming
│   ├── model.py         # klasifikasi transformer
│   ├── pipeline.py      # orkestrasi: data → preprocessing → klasifikasi → visualisasi
│   ├── insight.py       # ekstraksi aspek, kata kunci, kutipan representatif
│   └── report.py        # susun laporan analisis (per platform + gabungan)
│
├── runners/             # runner per platform (dipakai main.py / bisa berdiri sendiri)
│   ├── playstore.py
│   ├── appstore.py
│   └── tiktok.py
│
├── resources/           # kamus & berkas unduhan        (dibuat otomatis)
├── data/                # data mentah hasil scraping     (dibuat otomatis)
└── output/<platform>/   # hasil analisis & grafik        (dibuat otomatis)
```

Direktori `resources/`, `data/`, dan `output/` dibuat otomatis saat dijalankan
dan diabaikan oleh Git.

## Instalasi

Disarankan memakai virtual environment (Python 3.9+).

```bash
pip install -r requirements.txt
python setup_resources.py              # unduh kamus normalisasi ke resources/
python -m playwright install chromium  # hanya bila ingin scraping TikTok
```

Lalu siapkan konfigurasi:

```bash
cp .env.example .env                   # Windows: copy .env.example .env
```

Buka `.env` dan isi sesuai aplikasi yang ingin dianalisis.

## Konfigurasi (.env)

| Variabel             | Keterangan                                                        |
| -------------------- | ----------------------------------------------------------------- |
| `APP_NAME`           | Nama tampilan aplikasi, dipakai pada judul grafik.                |
| `PLAYSTORE_APP_ID`   | ID paket dari URL Play Store, mis. `id.go.bpn.sentuh`.            |
| `PLAYSTORE_LANG`     | Kode bahasa ulasan (default `id`).                                |
| `PLAYSTORE_COUNTRY`  | Kode negara (default `id`).                                       |
| `APPSTORE_APP_ID`    | ID numerik dari URL App Store, mis. `1287142144`.                |
| `APPSTORE_COUNTRY`   | Storefront App Store (default `id`).                              |
| `TIKTOK_MS_TOKEN`    | `msToken` dari cookie browser saat login TikTok.                  |
| `TIKTOK_VIDEO_IDS`   | Daftar id video, dipisahkan koma.                                 |
| `MODEL_NAME`         | (opsional) model Hugging Face untuk klasifikasi.                  |

Platform yang tidak dipakai cukup dikosongkan variabelnya.

## Penggunaan

### Menjalankan semuanya sekaligus (disarankan)

`main.py` adalah entrypoint utama: ia memastikan resource tersedia, lalu
menjalankan seluruh platform dari awal sampai akhir.

```bash
python main.py                      # analisis semua platform dari data yang ada
python main.py --scrape             # ambil data terbaru semua platform lalu analisis
python main.py --only playstore     # jalankan satu platform saja
python main.py --scrape --sample 1500
```

| Argumen     | Keterangan                                                  |
| ----------- | ----------------------------------------------------------- |
| `--scrape`  | Ambil data terbaru sebelum analisis.                        |
| `--only`    | Jalankan satu platform: `playstore`, `appstore`, `tiktok`.  |
| `--sample`  | Analisis N komentar acak per platform (`0` = seluruhnya).   |

Platform yang belum dikonfigurasi atau belum punya data akan dilewati otomatis,
ditampilkan di bagian ringkasan.

### Menjalankan satu platform secara terpisah

Tiap runner juga bisa dipanggil sendiri lewat `python -m runners.<platform>`,
dengan argumen jumlah data spesifik per platform.

```bash
python -m runners.playstore --scrape --count 3000
python -m runners.appstore  --scrape --pages 10
python -m runners.tiktok    --scrape --count 300
python -m runners.playstore --sample 1500
```

| Argumen     | Berlaku pada        | Keterangan                                  |
| ----------- | ------------------- | ------------------------------------------- |
| `--scrape`  | semua               | Ambil data baru sebelum analisis.           |
| `--count`   | Play Store, TikTok  | Jumlah ulasan / komentar yang diambil.      |
| `--pages`   | App Store           | Maksimal halaman RSS (±50 ulasan/halaman).  |
| `--sample`  | semua               | Analisis N komentar acak (`0` = seluruhnya).|

## Keluaran

Untuk setiap platform, hasil disimpan di `output/<platform>/`:

- `hasil_sentimen_final.csv` — komentar berlabel beserta probabilitas tiap kelas.
- `01_distribusi_sentimen.png` — diagram batang jumlah per sentimen.
- `02_persentase_pie.png` — proporsi sentimen.
- `03_wordcloud_keseluruhan.png`, `04_wordcloud_negatif.png`, `04_wordcloud_positif.png`.
- `05_top_kata.png` — 15 kata dominan pada ulasan negatif dan positif.
- `analisis_<platform>.md` — laporan analisis naratif (lihat di bawah).
- `meta_<platform>.json` — statistik pembersihan (jumlah di-scrap/dipakai/dibuang).

## Laporan Analisis

Selain grafik, sistem menghasilkan laporan teks (Markdown, Bahasa Indonesia)
yang menjelaskan **apa pendapat publik** terhadap aplikasi: cakupan & pembersihan
data (berapa komentar di-scrap, dipakai, dan dibuang), faktor yang membuat opini
negatif, faktor yang membuat opini positif, aspek yang paling sering dibahas
(login, error/bug, performa, tampilan, dll.), kata/frasa dominan, dan kutipan
komentar paling representatif.

Pada laporan gabungan, distribusi sentimen juga disajikan dalam versi
**ternormalisasi** (rata-rata dengan bobot setara antar platform), dan
kesimpulan akhir mengikuti distribusi ternormalisasi ini.

Laporan ini ikut dibuat otomatis saat menjalankan `python main.py`. Untuk
membuatnya ulang dari output yang sudah ada (tanpa menjalankan model):

```bash
python report.py                  # laporan semua platform + laporan gabungan
python report.py --only playstore # satu platform saja
```

Berkas yang dihasilkan:

- `output/<platform>/analisis_<platform>.md` — kesimpulan per platform.
- `output/analisis_gabungan.md` — perbandingan antar platform, kesimpulan tiap
  platform, analisis seluruh data yang digabung, dan **kesimpulan akhir**.

Analisis bersifat *rule-based* (statistik frekuensi + lexicon aspek), sehingga
deterministik dan berjalan offline tanpa API.

## Catatan

- **App Store** memakai feed RSS resmi Apple (tanpa pustaka tambahan). Beberapa
  storefront dapat mengembalikan sedikit atau nol ulasan tergantung ketersediaan.
- **TikTok** menggunakan pustaka tidak resmi (`TikTokApi`) dan dapat gagal
  sewaktu-waktu bila TikTok mengubah sistemnya; `msToken` juga perlu diperbarui
  secara berkala.
- Model bawaan, `cardiffnlp/twitter-xlm-roberta-base-sentiment`, mendukung
  banyak bahasa termasuk Bahasa Indonesia. Unduhan model pertama kali memerlukan
  koneksi internet.
