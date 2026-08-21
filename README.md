# Mirip Kodi

Mirip Kodi (Similar to Kodi) Adalah Script Mpv Yang Menampilkan Clear Logo, Genre Film atau TV Show dan Jam di Kanan Atas Layar.
Sript ini Juga dapat menampilkan Poster, Rating dan Sinopsis Singkat (Overview) Film atau TV Show Koleksi Anda,
Yang Tampilanya Mirip Dengan Kodi Media Center, ya kita tahu kalau player bawaan Kodi Media Center itu burik. 
Dengan Script ini anda akan merasakan kualitas gambar MPV yang mendukung banyak GLSL Shader dan berbagai macam filter.
Mirip Kodi Juga menyertakan Sript Python Untuk Auto Scrapping Metadada,Poster,Clear logo dll dari TMDB a.k.a https://www.themoviedb.org/

Clear Logo, Genre dan Jam akan muncul saat Mouse Bergerak dan akan menghilang dengan sendirinya. Default 10 detik.
![Spring Clear Logo](Screenshoot/Spring_Clear_Logo.png)

Poster Rating dan Sinopsis akan muncul saat Right Clik (Klik Kanan Pada Mouse) dan akan hilang jika Klik Kanan Kedua Kalinya.
![Spring Poster](Screenshoot/Spring_Poster.png)

# Mirip-Kodi (Media Library Scanner)

Skrip otomatis berbasis Python untuk memindai direktori film (Movies) dan serial TV (TV Series), mengunduh metadata resmi dari TMDB (The Movie Database), serta mengunduh sekaligus menajamkan gambar poster dan clearlogo secara otomatis.

Setelah instalasi, skrip ini dapat dijalankan langsung dari terminal sebagai perintah global sistem (`scan_movies`).

## Fitur Utama

* Pemindaian otomatis folder Film dan Serial TV secara rekursif.
* Mengunduh metadata resmi TMDB dan menyimpannya dalam format `metadata.json`.
* Pencarian sinopsis otomatis dalam bahasa Indonesia (`id-ID`) dengan fallback bahasa Inggris (`en-US`).
* Mengunduh poster film serta gambar logo jernih (`clearlogo.png`).
* Pemrosesan gambar otomatis (kompresi ukuran dan penajaman logo) menggunakan Pillow.

## Persyaratan Sistem

Sebelum menjalankan skrip ini, pastikan sistem Anda memenuhi kebutuhan berikut:
* **Sistem Operasi**: Linux / Unix-based (Skrip membaca path direktori media eksternal `/run/media/...`).
* **Python**: Versi 3.x atau yang terbaru.

### Dependensi Python

Skrip ini memerlukan library pihak ketiga **Pillow** untuk memproses gambar. Instal melalui terminal Anda:

```bash
pip install Pillow
```

## Konfigurasi Lingkungan (.bashrc)

Skrip ini memerlukan otentikasi ke API TMDB agar dapat berfungsi. Disarankan menggunakan **TMDB Read Access Token (v4 auth)** yang dimasukkan ke dalam file `.bashrc` Anda.

### Cara Mendapatkan Token TMDB (Gratis):
1. Buka situs resmi [The Movie Database (TMDB)](https://themoviedb.org) dan masuk ke akun Anda (buat akun baru jika belum punya).
2. Klik ikon profil Anda di pojok kanan atas, lalu pilih **Settings**.
3. Pada menu sebelah kiri, klik tab **API**.
4. Klik tautan **Create** di bawah bagian "Request an API Key", lalu pilih jenis aplikasi **Developer**.
5. Isi formulir informasi aplikasi yang diminta (Anda bisa mengisi nama proyek dengan `Mirip-Kodi` dan URL dengan tautan GitHub Anda).
6. Setelah menyetujui persyaratan, API Key Anda akan langsung dibuat.
7. Cari bagian **API Read Access Token (v4 auth)** yang berupa teks kode sangat panjang, lalu salin (copy) seluruh kode tersebut.

### Memasukkan Token ke Sistem:
Jalankan perintah berikut di terminal untuk memasukkan token Anda secara otomatis ke dalam konfigurasi sistem Linux:

```bash
# Tambahkan Token TMDB ke .bashrc
echo 'export TMDB_TOKEN="isi_read_access_token_v4_anda_di_sini"' >> ~/.bashrc

# Muat ulang konfigurasi terminal agar langsung aktif
source ~/.bashrc
```

*Catatan: Pastikan Anda mengganti `"isi_read_access_token_v4_anda_di_sini"` dengan kode token panjang yang sudah Anda salin dari dasbor TMDB sebelum menekan Enter.*

## Cara Instalasi (`.local/bin`)

Agar skrip dapat dipanggil langsung dari mana saja di terminal tanpa mengetik ekstensi `.py`, ikuti langkah pemasangan berikut:

1. **Clone Repositori ini:**
   ```bash
   git clone https://github.com/thecimot/Mirip-Kodi
   cd Mirip-Kodi
   ```

2. **Buat Folder Bin Lokal & Pindahkan File:**
   ```bash
   mkdir -p ~/.local/bin
   cp scan_movies ~/.local/bin/
   ```

3. **Berikan Hak Akses Eksekusi:**
   ```bash
   chmod +x ~/.local/bin/scan_movies
   ```

4. **Daftarkan ke PATH Sistem (Jika belum):**
   Pastikan baris berikut sudah ada di bagian bawah file `~/.bashrc` Anda:
   ```bash
   export PATH="HOME/.local/bin:PATH"
   ```
   Jangan lupa jalankan `source ~/.bashrc` setelah menambahkannya.

## Cara Penggunaan

Setelah langkah instalasi di atas selesai, Anda bisa langsung menjalankan pemindaian dari folder mana saja di terminal cukup dengan mengetik:

```bash
scan_movies
```

## Lisensi

Proyek ini dilisensikan di bawah **MIT License** - Lihat isi file kode untuk detail hak cipta oleh Hartono (2026).
