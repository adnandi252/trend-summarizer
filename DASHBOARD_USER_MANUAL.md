# Panduan Penggunaan Aplikasi (User Manual) - TrendAI Dashboard

Selamat datang di Panduan Penggunaan Mandiri aplikasi **TrendAI**. Dokumen ini dirancang khusus bagi analis pasar, eksekutif bisnis, dan operator sistem untuk memahami seluruh fitur, elemen antarmuka pengguna (UI), informasi konten, serta alur pengoperasian aplikasi secara detail.

---

## 1. Struktur Navigasi & Setelan Global

Antarmuka TrendAI dibagi menjadi dua bagian navigasi utama: **Sidebar Navigasi Kiri** (untuk beralih halaman secara global) dan **Setelan Workspace Proyek** (untuk mengelola topik riset).

### A. Sidebar Navigasi Kiri
Terletak permanen di sisi kiri layar (sembunyi saat dicetak), berisi menu:
1.  **Dashboard:** Halaman beranda visualisasi KPI, grafik volume tren, dan ringkasan eksekutif gabungan.
2.  **Trend Discovery:** Halaman eksplorasi mendalam (deep dive) per kategori tren dilengkapi form feedback.
3.  **Executive Briefs:** Halaman laporan formal berformat A4 yang siap dicetak fisik atau disimpan ke format PDF.
4.  **Manajemen Berita:** Pusat kendali untuk melakukan scraping berita, memicu analisis AI, memantau log konsol, dan mencari database berita.
5.  **Settings:** Tombol khusus yang memicu jendela pop-up Setelan Workspace.

### B. Jendela Setelan Workspace (Settings Modal)
Diakses dengan mengeklik menu **Settings** pada sidebar. Jendela pop-up ini berfungsi mengelola proyek riset pasar yang aktif.

```
┌────────────────────────────────────────────────────────┐
│               TrendAI Settings & Workspace         [X] │
├────────────────────────────────────────────────────────┤
│ Kelola topik riset pasar, scraping, dan summary AI.    │
│                                                        │
│ ┌────────────────────────────────────────────────────┐ │
│ │ Daftar Proyek Riset Aktif                          │ │
│ ├────────────────────────────────────────────────────┤ │
│ │ FMCG Ritel     │ ramah lingkungan, ritel  │ [Gunakan]│ │
│ │ Tech Indonesia │ AI, startup, digital     │ [Hapus]  │ │
│ └────────────────────────────────────────────────────┘ │
│                                                        │
│  Buat Proyek Baru:                                     │
│  * Nama Proyek : [ FMCG Sustainability           ]     │
│  * Kata Kunci  : [ ramah lingkungan, plastik, esg]     │
│  * Deskripsi   : [ Pemantauan regulasi hijau...  ]     │
│                                                        │
│  [ Simpan Proyek ]                          [ Tutup ]  │
└────────────────────────────────────────────────────────┘
```

*   **Elemen & Item di Jendela Settings:**
    *   **Tabel Daftar Proyek:** Menampilkan seluruh proyek riset yang tersimpan di database.
        *   **Kolom Nama Proyek:** Nama unik riset (misal: *FMCG Ritel*). Jika proyek tersebut sedang aktif, akan muncul badge **"Aktif"** berwarna biru muda di samping namanya.
        *   **Kolom Kata Kunci:** Menampilkan daftar kata kunci yang digunakan untuk scraping.
        *   **Aksi "Gunakan":** Tombol untuk mengaktifkan proyek terpilih secara global. Seluruh halaman akan otomatis memuat data proyek ini.
        *   **Aksi "Hapus":** Tombol merah untuk menghapus proyek beserta seluruh database artikel dan hasil ringkasan terkait.
    *   **Formulir Pembuatan Proyek Baru:**
        *   **Input "Nama Proyek" (Wajib):** Nama pengenal riset pasar (min. 3 karakter).
        *   **Input "Kata Kunci" (Wajib):** Daftar kata kunci pencarian berita dipisahkan dengan tanda koma (maksimal 5 kata kunci).
        *   **Textarea "Deskripsi Proyek" (Opsional):** Keterangan tambahan mengenai ruang lingkup riset.
        *   **Tombol "Simpan Proyek":** Mendaftarkan proyek ke database dan mengaktifkannya secara otomatis.

---

## 2. Panduan Halaman: Dashboard

Halaman utama untuk melihat ringkasan performa dan volume tren terkini dari proyek riset yang sedang aktif.

```
┌────────────────────────────────────────────────────────────────────────┐
│ Dasbor Analisis Tren  [Periode: Semua Periode v] [Proyek: FMCG Ritel v]│
│ Menganalisis 24 artikel dari berbagai sumber industri.                 │
├────────────────────────────────────────────────────────────────────────┤
│ ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐       │
│ │ ARTIKEL DIPROSES │  │   SUMBER DATA    │  │  KATEGORI TREN   │       │
│ │   24 Artikel     │  │  8 Portal Unik   │  │   3 Kluster AI   │       │
│ └──────────────────┘  └──────────────────┘  └──────────────────┘       │
├────────────────────────────────────────────────────────────────────────┤
│ ┌──────────────────────────────────────────────┐  ┌──────────────────┐ │
│ │ [✨] RINGKASAN EKSEKUTIF         Diperbarui. │  │ KARTU WAWASAN    │ │
│ ├──────────────────────────────────────────────┤  ├──────────────────┤ │
│ │ Sustainability: Tren ramah lingkungan ritel  │  │ [Sustainability] │ │
│ │ meningkat sebesar 20% didukung regulasi baru.│  │ Regulasi Hijau   │ │
│ │                                              │  │ Pembersih Plastik│ │
│ │ ┌──────────────────┐    ┌──────────────────┐ │  │ 5 portal sumber  │ │
│ │ │ PELUANG UTAMA    │    │ PERILAKU / RISIKO│ │  ├──────────────────┤ │
│ │ │ Substitusi kertas│    │ Konsumen menolak │ │  │ [Digital Market] │ │
│ │ └──────────────────┘    └──────────────────┘ │  │ Belanja Online   │ │
│ ├──────────────────────────────────────────────┤  │ 4 portal sumber  │ │
│ │ VOLUME ARTIKEL PER KATEGORI TREN             │  │                  │ │
│ │ * Sustainability     [==========] 12 Artikel │  │ [Lihat Semua]    │ │
│ │ * Digital Marketing  [=====     ]  6 Artikel │  │                  │ │
│ └──────────────────────────────────────────────┘  └──────────────────┘ │
└────────────────────────────────────────────────────────────────────────┘
```

### A. Fitur & Fungsi Halaman
*   Memberikan ringkasan eksekutif instan hasil olahan AI dari kumpulan berita terunduh.
*   Memantau volume perhatian media terhadap topik tren tertentu.
*   Memungkinkan penyaringan data berdasarkan kurun waktu analisis mingguan.

### B. Daftar Elemen & Item UI
1.  **Header Dasbor:**
    *   **Dropdown "Periode Analisis":** Terletak di kanan atas. Digunakan untuk menyaring visualisasi data dasbor berdasarkan periode mingguan analisis historis (contoh: *2026-07-07 s/d 2026-07-14* atau *Semua Periode*).
    *   **Dropdown "Project Selector" (Pilih Proyek):** Tombol pilih cepat untuk berpindah proyek riset aktif tanpa perlu membuka modal setelan.
    *   **Label Deskripsi Sinyal:** Teks dinamis di bawah judul (contoh: *"Menganalisis 24 artikel dari berbagai sumber industri."*).
2.  **Baris Indikator Metrik (KPI Cards):**
    *   **Artikel Diproses:** Total dokumen artikel berita yang lolos verifikasi data dan masuk ke database proyek.
    *   **Sumber Data:** Jumlah portal media berita unik (domain web seperti *detik.com*, *kompas.com*, dll.) yang menjadi sumber artikel.
    *   **Kategori Tren:** Jumlah kluster pengelompokan topik AI yang aktif (default: 3 kluster).
3.  **Panel Ringkasan Eksekutif (Executive Summary Card):**
    *   **Badge Judul:** Teks *"RINGKASAN EKSEKUTIF"* dengan ikon bintang kecerdasan buatan.
    *   **Indikator Waktu:** Teks *"Diperbarui [HH:MM]"* di sisi kanan panel yang menunjukkan jam terakhir visualisasi dasbor diperbarui.
    *   **Area Teks Narasi AI:** Kumpulan paragraf ringkasan yang dihasilkan model LLM untuk masing-masing kategori tren (*Sustainability*, *Digital Marketing*, *Consumer Shift*). Nama kategori tren ditebalkan dan diwarnai sesuai identitas visualnya.
    *   **Kotak Peluang Utama:** Panel hijau muda yang menyoroti satu peluang pasar terbaik berdasarkan data berita terkini.
    *   **Kotak Perilaku / Risiko Kunci:** Panel merah/oranye muda yang merangkum pergeseran perilaku konsumen atau risiko pasar utama.
4.  **Grafik Batang Volume Kategori (Trending Topics Chart):**
    *   Menampilkan grafik batang horizontal berwarna yang menunjukkan jumlah artikel per kategori tren. Berguna untuk membandingkan kategori mana yang sedang mendapat sorotan media paling masif.
5.  **Kartu Wawasan Tren (Latest Insights Column):**
    *   Terletak di kolom kanan dasbor. Menampilkan daftar kartu pratinjau wawasan per kategori tren.
    *   Setiap kartu menampilkan **Badge Kategori** (dengan warna identitas), **Tanggal Rilis Terakhir**, **Judul Peluang Riset**, **Kutipan Singkat Ringkasan**, jumlah portal berita pendukung, dan chip kata kunci utama.
    *   Jika salah satu kartu diklik, pengguna langsung diarahkan ke halaman **Trend Discovery** untuk kategori tersebut.
    *   **Tombol "Lihat Semua Tren":** Tombol di bagian bawah kolom untuk menavigasi ke halaman eksplorasi tren penuh.

---

## 3. Panduan Halaman: Trend Discovery (Eksplorasi Tren)

Halaman eksplorasi mendalam (deep dive) untuk mengkaji wawasan taktis, kata kunci, dan artikel pendukung dari satu kategori tren secara spesifik.

```
┌────────────────────────────────────────────────────────────────────────┐
│ Ringkasan Tren: Sustainability                   [Proyek: FMCG Ritel v]│
├────────────────────────────────────────────────────────────────────────┤
│ [KATEGORI TREN] Pembaruan: 14 Juli 2026                                │
│ Sustainability                                                         │
│ ┌──────────────────────────────────┐  ┌──────────────────────────────┐ │
│ │ JUMLAH ARTIKEL                   │  │ KATA KUNCI UTAMA             │ │
│ │   12 Artikel                     │  │ keberlanjutan, esg, ramah    │ │
│ │ [x] 4 portal sumber              │  │ Topik dominan dalam klaster  │ │
│ └──────────────────────────────────┘  └──────────────────────────────┘ │
├────────────────────────────────────────────────────────────────────────┤
│ ┌──────────────────────────────────────────────┐  ┌──────────────────┐ │
│ │ [✨] Ringkasan Analisis             NARASI AI│  │ KATEGORI TERKAIT │ │
│ ├──────────────────────────────────────────────┤  ├──────────────────┤ │
│ │ **Executive Brief**                          │  │ [Digital Market] │ │
│ │ 1. Tren Utama: Peningkatan kesadaran produk  │  │ 6 Artikel    [>] │ │
│ │ 2. Ringkasan: Retailer mulai mengurangi...   │  ├──────────────────┤ │
│ │                                              │  │ [Consumer Shift] │ │
│ │ Kata Kunci Strategis     Peluang Pasar       │  │ 6 Artikel    [>] │ │
│ │ [keberlanjutan]          * Substitusi Kertas │  └──────────────────┘ │
│ │ [ramah lingkungan]       * Kemasan Organik   │                       │
│ └──────────────────────────────────────────────┘                       │
├────────────────────────────────────────────────────────────────────────┤
│ ARTIKEL PENDUKUNG                                                      │
│ ┌────────────────────────────────────────────────────────────────────┐ │
│ │ JUDUL ARTIKEL              │ SUMBER      │ TANGGAL     │ AKSI      │ │
│ ├────────────────────────────┼─────────────┼─────────────┼───────────┤ │
│ │ Retailer Terapkan ESG...   │ Kompas      │ 13 Jul 2026 │ [Baca]    │ │
│ │ Kantong Plastik Dilarang...│ Detik       │ 12 Jul 2026 │ [Baca]    │ │
│ └────────────────────────────┴─────────────┴─────────────┴───────────┘ │
├────────────────────────────────────────────────────────────────────────┤
│ EVALUASI RINGKASAN TREN                                                │
│ Bagaimana kualitas analisis AI untuk kategori tren ini?                │
│ Rating Ulasan: [ Sangat Baik v ]                                       │
│ Masukan/Komentar:                                                      │
│ [ Tulis ulasan atau koreksi informasi di sini...                   ]   │
│ [ Kirim Feedback ]                                                     │
└────────────────────────────────────────────────────────────────────────┘
```

### A. Fitur & Fungsi Halaman
*   Menyajikan narasi analisis AI berstruktur formal 4 poin (Tren Utama, Ringkasan, Sentimen Pasar, dan Rekomendasi).
*   Menyediakan daftar kata kunci strategis dan daftar peluang pasar taktis.
*   Menyajikan bukti berita otentik (artikel pendukung) untuk diverifikasi oleh analis.
*   Mengakomodasi umpan balik manusia (human-in-the-loop) untuk evaluasi performa AI.

### B. Daftar Elemen & Item UI
1.  **Header Eksplorasi:**
    *   **Judul Halaman:** Menampilkan nama kategori tren yang sedang dibuka (*Sustainability*, *Digital Marketing*, atau *Consumer Behavior Shift*).
    *   **Dropdown Proyek Aktif:** Memilih proyek riset aktif.
2.  **Section Banner Tren Hero:**
    *   **Badge Kategori Tren:** Tag warna khusus penanda kategori.
    *   **Label Waktu Pembaruan:** Tanggal publikasi berita terbaru yang ada di dalam klaster tren ini.
    *   **Kartu Metrik Kiri (Jumlah Artikel):** Total artikel di dalam klaster dan jumlah portal sumber unik.
    *   **Kartu Metrik Kanan (Kata Kunci Utama):** Tiga kata kunci dominan di dalam klaster.
3.  **Panel Ringkasan Analisis:**
    *   **Area Teks Narasi AI:** Ringkasan eksekutif berstruktur 4 poin utama:
        1.  *Tren Utama:* Konteks gambaran tren di pasar.
        2.  *Ringkasan:* Rangkuman informasi berita pendukung.
        3.  *Sentimen Pasar:* Analisis sentimen konsumen/industri.
        4.  *Rekomendasi:* Langkah strategis yang disarankan.
    *   **Kolom Kata Kunci Strategis:** Daftar kata dasar penting yang paling mewakili dokumen di klaster ini.
    *   **Kolom Peluang Pasar:** Daftar rekomendasi inovasi produk atau ceruk pasar baru berdasarkan analisis berita.
4.  **Panel Kategori Terkait (Related Nodes):**
    *   Berada di kolom kanan. Berisi tautan cepat ke kategori tren lainnya dalam proyek yang sama, lengkap dengan jumlah artikel masing-masing kategori dan ikon chevron (`>`).
5.  **Tabel Artikel Pendukung (Supporting Sources):**
    *   Menampilkan seluruh berita yang masuk ke dalam klaster tren ini.
    *   **Kolom Judul:** Judul berita asli.
    *   **Kolom Sumber:** Nama portal media penerbit berita (diberi badge abu-abu).
    *   **Kolom Tanggal:** Tanggal terbit berita diformat secara lokal (*dd mmm yyyy*).
    *   **Aksi "Baca":** Tombol tautan eksternal yang akan membuka halaman situs berita asli di tab peramban baru.
6.  **Formulir Evaluasi Ringkasan Tren (Feedback Form):**
    *   **Dropdown "Rating Ulasan":** Pilihan nilai kepuasan analis (*Sangat Baik*, *Cukup Baik*, *Perlu Perbaikan*).
    *   **Textarea "Masukan/Komentar":** Kolom input teks bebas untuk menulis catatan, saran, atau koreksi fakta terhadap hasil ringkasan AI.
    *   **Tombol "Kirim Feedback":** Tombol untuk menyimpan umpan balik ke database SQLite proyek.

---

## 4. Panduan Halaman: Executive Briefs (Laporan Eksekutif)

Halaman laporan formal berformat A4 digital yang dirancang untuk diunduh sebagai berkas PDF atau dicetak langsung untuk dibagikan kepada jajaran direksi/eksekutif.

```
┌────────────────────────────────────────────────────────────────────────┐
│ Dasbor TrendAI Summarizer                          [ Export PDF ] no-pr│
├────────────────────────────────────────────────────────────────────────┤
│  LAPORAN RINGKASAN TREN INDUSTRI                                       │
│  Laporan Ringkasan Tren Industri                                       │
│  [calendar] Periode: 07 Jul 2026 - 14 Jul 2026   Laporan: 24 artikel   │
│  [verified] Dihasilkan oleh TrendAI              Dihasilkan oleh AI    │
│ ┌────────────────────────────────────────────────────────────────────┐ │
│ │ ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐   │ │
│ │ │ KATA KUNCI AKTIF │  │  KATEGORI TREN   │  │  TOTAL ARTIKEL   │   │ │
│ │ │    18 Kata Kunci │  │   3 Kategori     │  │   24 Artikel     │   │ │
│ │ └──────────────────┘  └──────────────────┘  └──────────────────┘   │ │
│ │                                                                    │ │
│ │  Ringkasan Tren Utama                                              │ │
│ │  * SUSTAINABILITY: Tren kemasan ramah lingkungan...                │ │
│ │  * DIGITAL MARKETING: Brand memanfaatkan influencer...             │ │
│ │                                                                    │ │
│ │  Wawasan Strategis                                                 │ │
│ │  [Sustainability]  12 artikel  - Substitusi Kertas                 │ │
│ │  [Digital Market]   6 artikel  - Kampanye Video Pendek             │ │
│ │                                                                    │ │
│ │  Rekomendasi Strategis              DISTRIBUSI ARTIKEL PER KATEGORI│ │
│ │  01. Substitusi Kertas              Sustainability      [50%] 12   │ │
│ │  02. Kampanye Video                 Digital Marketing   [25%]  6   │ │
│ └────────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────┘
```

### A. Fitur & Fungsi Halaman
*   Menyajikan rangkuman komparatif seluruh tren dalam satu halaman A4 yang rapi.
*   Memiliki fungsi ekspor cepat ke bentuk fisik atau cetak digital PDF (`window.print()`).
*   Menyajikan rekomendasi taktis terurut tingkat kepentingannya.

### B. Daftar Elemen & Item UI
1.  **Top Navigation (No-Print):**
    *   **Dropdown Project Selector:** Berpindah proyek aktif secara cepat.
    *   **Tombol "Export PDF" / "Cetak":** Tombol biru berikon unduh untuk membuka dialog cetak peramban. Seluruh elemen non-laporan (sidebar, header, tombol cetak) akan otomatis disembunyikan dalam cetakan.
2.  **Laporan Kartu A4 (A4 Card Container):**
    *   Memiliki rasio lebar-tinggi standar A4 (210mm x 297mm) dengan warna latar belakang putih bersih dan bayangan lembut di layar monitor.
    *   **Header Laporan:**
        *   Judul resmi *"Laporan Ringkasan Tren Industri"*.
        *   **Periode Tanggal:** Rentang tanggal terbit berita paling awal hingga paling akhir yang dianalisis dalam laporan ini.
        *   Badge Laporan: Keterangan jumlah artikel terindeks (contoh: *"Laporan: 24 artikel terindeks"*).
3.  **Indikator Utama Laporan (Tiga Kotak KPI):**
    *   **Kata Kunci Teridentifikasi:** Jumlah kata unik penting dari seluruh klaster tren.
    *   **Kategori Tren:** Jumlah kategori tren aktif.
    *   **Total Artikel:** Total database artikel pendukung yang dianalisis.
4.  **Area Ringkasan Tren Utama:**
    *   Kompilasi gabungan seluruh ringkasan generatif dari kategori tren aktif. Ditampilkan dalam format paragraf mengalir yang dibatasi garis tepi vertikal biru tebal di sisi kiri (`executive-accent`).
5.  **Section Wawasan Strategis:**
    *   Daftar kartu wawasan per kategori tren yang berisi: **Badge Kategori**, **Volume Artikel**, **Judul Peluang Teratas**, **Ringkasan Narasi Dua Kalimat**, serta **Chip Kata Kunci Kluster**.
6.  **Section Rekomendasi & Distribusi:**
    *   **Kolom Kiri - Rekomendasi Strategis:** Daftar bernomor bulat besar (`01`, `02`, dst.) berisi usulan aksi nyata bagi bisnis (diambil dari peluang pasar hasil analisis AI).
    *   **Kolom Kanan - Distribusi Artikel:** Diagram batang horizontal mini yang menampilkan persentase distribusi artikel di setiap kategori tren (misal: *Sustainability 50%, Digital Marketing 25%, Consumer Shift 25%*).
7.  **Footer Laporan:**
    *   Mencantumkan cap tanda tangan digital *"Dihasilkan oleh TrendAI"*, hak cipta tahun berjalan, dan penanda halaman resmi laporan.

---

## 5. Halaman: Manajemen Berita (Control Center)

Pusat administrasi data aplikasi. Halaman ini berfungsi sebagai ruang kendali bagi analis untuk memicu scraping, memicu analisis model AI, dan mengelola basis data berita.

```
┌────────────────────────────────────────────────────────────────────────┐
│ Manajemen Berita               [Proyek: FMCG Ritel v]      Pusat Data  │
├────────────────────────────────────────────────────────────────────────┤
│ ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐       │
│ │ TOTAL ARTIKEL    │  │ ARTIKEL HARI INI │  │ KATEGORI UTAMA   │       │
│ │   24 Artikel     │  │   5  [+100%]     │  │ Sustainability   │       │
│ └──────────────────┘  └──────────────────┘  └──────────────────┘       │
├────────────────────────────────────────────────────────────────────────┤
│ ┌──────────────────────────┐┌──────────────────────────┐┌──────────────┐ │
│ │ 1. TARIK ARTIKEL BERITA  ││ 2. ANALISIS KLASTER TREN ││ LOG PIPELINE │ │
│ ├──────────────────────────┤├──────────────────────────┤├──────────────┤ │
│ │ Batas Berita/Kueri: [5 v]││ Model AI: [Groq API v]   ││ status: completed│
│ │ Waktu Terbit: [Semua v]  ││ Model ID: [test-1   v]   ││ [12:00] Start│ │
│ │                          ││ Tanggal Mulai: [      ]  ││ [12:01] Pre- │ │
│ │ [ Mulai Tarik Berita ]   ││ Tanggal Akhir: [      ]  ││ [12:02] Done │ │
│ │                          ││ [ Mulai Analisis Tren ]  ││              │ │
│ └──────────────────────────┘└──────────────────────────┘└──────────────┘ │
├────────────────────────────────────────────────────────────────────────┤
│ DAFTAR ARTIKEL BERITA TERUNDUH                          [Refresh]      │
│ [ Cari judul... ]  [ Semua Kategori v ]  [ Tanggal:   s/d   ] [Reset]  │
│ ┌────────────────────────────────────────────────────────────────────┐ │
│ │ JUDUL ARTIKEL              │ SUMBER      │ TANGGAL     │ KATEGORI  │ │
│ ├────────────────────────────┼─────────────┼─────────────┼───────────┤ │
│ │ Retailer Terapkan ESG...   │ Kompas      │ 13 Jul 2026 │ Sustain   │ │
│ └────────────────────────────┴─────────────┴─────────────┴───────────┘ │
│ Menampilkan 1-10 dari 24 artikel                [Sebelumnya] [Selanjutnya]│
└────────────────────────────────────────────────────────────────────────┘
```

### A. Fitur & Fungsi Halaman
*   Melakukan scraping berita otomatis dari Google News berdasarkan kata kunci proyek.
*   Menjalankan pemrosesan bahasa alami (NLP) dan pemodelan AI secara terfokus pada rentang tanggal berita tertentu.
*   Menyediakan konsol log real-time untuk memantau berjalannya proses latar belakang.
*   Menyediakan fungsi pencarian, penyaringan tanggal, dan pembaca artikel utuh dari database lokal.

### B. Daftar Elemen & Item UI
1.  **Header & Kartu KPI Manajemen Berita:**
    *   **Dropdown Proyek Aktif:** Memilih proyek riset aktif.
    *   **KPI Total Artikel Terunduh:** Jumlah keseluruhan artikel yang berhasil dikumpulkan dalam proyek ini.
    *   **KPI Artikel Baru Hari Ini:** Jumlah berita yang terbit pada tanggal hari ini. Dilengkapi dengan **Badge Persentase Pertumbuhan** (warna hijau jika naik dibanding kemarin, merah jika turun, abu-abu jika stabil).
    *   **KPI Kategori Utama:** Nama kategori tren yang memiliki jumlah artikel terbanyak dalam 7 hari terakhir.
2.  **Panel 1: Tarik Artikel Berita (Scraper Control):**
    *   **Dropdown "Batas Berita per Kata Kunci":** Menentukan batas maksimal artikel yang diunduh per satu kata kunci pencarian (Pilihan: 3, 5, 10, 15, atau 20 artikel).
    *   **Dropdown "Rentang Waktu Terbit (Google News)":** Memfilter berita di Google News berdasarkan waktu terbitnya (Pilihan: *Semua Waktu*, *24 Jam Terakhir*, *7 Hari Terakhir*, atau *30 Hari Terakhir*).
    *   **Tombol "Mulai Tarik Berita" (Biru):** Menjalankan scraping berita di latar belakang. Tombol akan otomatis nonaktif (disabled) jika sistem sedang memproses tugas lain.
3.  **Panel 2: Analisis Kluster Tren AI (Analyzer Control):**
    *   **Dropdown "Model Generative AI":** Memilih mesin perangkum (Pilihan: *Groq API* untuk model cloud berkecepatan tinggi, atau *Model T5 Lokal* untuk pemrosesan offline tanpa internet).
    *   **Dropdown "Model ID" (Hanya muncul jika memilih Groq API):** Memilih model kecerdasan buatan spesifik (Pilihan: *test-1 Model* atau model Llama).
    *   **Input Kalender "Tanggal Mulai" & "Tanggal Akhir" (Opsional):** Membatasi artikel yang akan dimasukkan ke model AI berdasarkan rentang tanggal terbitnya. Sangat berguna untuk melakukan analisis tren mingguan secara presisi.
    *   **Tombol "Mulai Analisis Tren" (Hijau):** Menjalankan pipeline pembersihan, clustering, dan peringkasan berita di latar belakang.
4.  **Panel 3: Log Eksekusi Pipeline (Console Logs Panel):**
    *   **Badge Status Proyek:** Menampilkan status terkini proyek (`completed`, `failed`, `scraping`, `processing`, atau `draft`) dengan penanda warna dinamis (hijau untuk sukses, merah untuk gagal, kuning berkedip untuk sedang berjalan).
    *   **Kotak Konsol Terminal Hitam (`pipeline-console`):** Menampilkan log output teks detail dari server backend. Teks akan bergeser otomatis ke bawah (auto-scroll) dan memiliki kode warna:
        *   *Hijau:* Berhasil menyelesaikan suatu tahapan pipeline (contoh log berikon `✓`).
        *   *Merah:* Terjadi kegagalan proses (contoh log berikon `❌` atau kata `GAGAL`).
        *   *Kuning:* Peringatan atau skip berita (contoh log berikon `⚠`).
        *   *Putih/Abu:* Informasi proses berjalan biasa.
5.  **Panel 4: Daftar Artikel Berita Terunduh (Database Toolbar & Table):**
    *   **Tombol "Refresh" (Putih berikon putar):** Memuat ulang daftar artikel dari database tanpa me-refresh seluruh halaman web.
    *   **Input Pencarian "Cari judul/sumber...":** Menyaring artikel di tabel berdasarkan kecocokan kata pada judul artikel atau nama portal media berita.
    *   **Dropdown Kategori:** Menyaring artikel berdasarkan kategori trennya (*Sustainability*, *Digital Marketing*, *Consumer Shift*, atau *Belum Diklasifikasi*).
    *   **Filter Tanggal "s/d":** Dua kolom input kalender untuk menyaring baris artikel di tabel berdasarkan tanggal terbit berita.
    *   **Tombol "Reset" (Merah):** Membersihkan seluruh input filter tanggal secara instan.
    *   **Tabel Hasil Artikel:**
        *   **Kolom Judul:** Judul berita lengkap (dapat diklik untuk membuka sumber asli berita).
        *   **Kolom Sumber:** Portal berita penerbit.
        *   **Kolom Tanggal:** Tanggal berita diterbitkan.
        *   **Kolom Kategori Tren:** Badge berwarna biru jika sudah terklasifikasi oleh AI, atau abu-abu jika berstatus *Belum Diklasifikasi*.
        *   **Tombol Aksi "Lihat Konten" (Biru):** Tombol interaktif untuk membuka **Jendela Pop-Up Modal Detail Artikel**.
    *   **Kontrol Pagination:** Tombol **Sebelumnya** dan **Selanjutnya** untuk beralih halaman (10 artikel per halaman).

### C. Jendela Pop-up Detail Artikel (Article Modal)
Terbuka ketika pengguna mengeklik tombol **Lihat Konten** pada tabel artikel terunduh. Jendela ini digunakan untuk memvalidasi teks asli berita secara cepat.

```
┌────────────────────────────────────────────────────────┐
│ Kantong Plastik Mulai Dilarang di Ritel Jakarta    [X] │
│ Sumber: Kompas | Tanggal: 13 Juli 2026, 10:00          │
├────────────────────────────────────────────────────────┤
│ Kategori Klaster AI: [ Sustainability ]                │
│                                                        │
│ KONTEN BERITA RAW/CLEAN:                               │
│ ┌────────────────────────────────────────────────────┐ │
│ │ Pemerintah Provinsi DKI Jakarta resmi menerapkan   │ │
│ │ larangan penggunaan kantong plastik sekali pakai   │ │
│ │ di seluruh pusat perbelanjaan dan ritel modern...  │ │
│ └────────────────────────────────────────────────────┘ │
│                                                        │
│ [ Buka Sumber Asli ]                         [ Tutup ]  │
└────────────────────────────────────────────────────────┘
```

*   **Elemen & Item di Jendela Modal:**
    *   **Judul Artikel:** Judul lengkap berita.
    *   **Metadata:** Nama media sumber, tanggal terbit, dan jam publikasi berita.
    *   **Badge Kategori Klaster AI:** Menampilkan nama kategori hasil prediksi KMeans.
    *   **Kotak Konten Berita (`modal-article-body`):** Kotak gelap berfont monospaced (`JetBrains Mono`) untuk menampilkan teks lengkap berita secara utuh dari database SQLite (mendukung scroll vertikal).
    *   **Tombol "Buka Sumber Asli" (Biru):** Membuka URL berita asli di tab baru peramban.
    *   **Tombol "Tutup" (Abu-abu) & Tombol Silang `[X]`:** Menutup pop-up modal dan kembali ke tabel manajemen berita.

---

## 6. Panduan Alur Pengoperasian Mandiri (Step-by-Step Operator Guide)

Berikut adalah panduan praktis skenario pengoperasian aplikasi sehari-hari oleh analis:

### Skenario A: Membuat Proyek Riset Baru
1.  Buka aplikasi di peramban web.
2.  Klik tombol **Settings** di bagian bawah sidebar kiri.
3.  Di dalam formulir **Buat Proyek Baru**, ketik nama proyek (misal: *Ritel Digital Indonesia*).
4.  Masukkan kata kunci pencarian yang relevan (misal: *belanja online ritel, shopee tokopedia Indonesia, digitalisasi UMKM*) dipisahkan koma.
5.  Isi deskripsi proyek (misal: *Memantau tren belanja online pasca pandemi*).
6.  Klik **Simpan Proyek**. Proyek baru akan langsung aktif dan muncul di dropdown header halaman.

### Skenario B: Menarik Berita & Memantau Log Eksekusi
1.  Masuk ke halaman **Manajemen Berita** melalui sidebar navigasi.
2.  Pastikan proyek aktif yang Anda inginkan terpilih pada dropdown header.
3.  Pada panel **1. Tarik Artikel Berita**, pilih batas berita per kata kunci (disarankan: *5 Artikel* atau *10 Artikel* untuk akurasi optimal).
4.  Pilih rentang waktu terbit berita di Google News (misal: *7 Hari Terakhir* untuk pemantauan mingguan).
5.  Klik tombol **Mulai Tarik Berita**.
6.  Perhatikan panel **Log Eksekusi Pipeline** di sebelah kanan. Status proyek akan berubah menjadi `scraping` (kuning berkedip). Konsol akan mulai menulis log secara real-time:
    - *"Menghubungi Google News RSS..."*
    - *"Mendekode rujukan URL Google News..."*
    - *"Mengunduh teks lengkap dari [Nama Media]..."*
    - *"✓ Berhasil menyimpan N artikel ke database SQLite..."*
7.  Tunggu hingga status proyek kembali menjadi `draft`, yang menandakan proses penarikan berita selesai.

### Skenario C: Menjalankan Analisis AI & Menghasilkan Laporan
1.  Pada halaman **Manajemen Berita**, pergilah ke panel **2. Analisis Kluster Tren AI**.
2.  Pilih **Model Generative AI** (disarankan: *Groq API* untuk analisis mendalam dengan model *test-1*).
3.  (Opsional) Jika Anda ingin membuat laporan mingguan yang spesifik, isi **Tanggal Mulai** dan **Tanggal Akhir** analisis (misal: kurun waktu Senin s/d Minggu minggu lalu). Jika dikosongkan, AI akan memproses seluruh berita yang telah diunduh.
4.  Klik tombol **Mulai Analisis Tren**.
5.  Pantau log di konsol terminal. Sistem akan menjalankan tiga langkah berurutan:
    - *Langkah 1/3:* NLP Preprocessing (membersihkan teks, tokenisasi, dan stemming cepat menggunakan bantuan Stem Cache JSON).
    - *Langkah 2/3:* KMeans Clustering dan pemetaan greedy ke 3 kategori tren target.
    - *Langkah 3/3:* Ekstraksi kalimat TextRank dan pengiriman kueri ringkasan ke Groq AI Cloud.
6.  Tunggu hingga status proyek berubah menjadi `completed` (badge hijau) dan konsol menulis pesan sukses: *"STATUS: SELURUH PROSES ANALISIS SELESAI!"*.
7.  Daftar artikel terklasifikasi akan langsung muncul di tabel bawah dengan badge kategori tren yang sesuai.
8. Pindah ke halaman lain untuk melihat hasil analisis
