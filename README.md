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

Skrip ini memerlukan otentikasi ke API TMDB agar dapat berfungsi. Anda harus memasukkan salah satu dari **TMDB Token** atau **TMDB API Key** ke dalam file `.bashrc` Anda.

Jalankan perintah berikut di terminal untuk menambahkannya secara otomatis (pilih salah satu atau isi keduanya):

```bash
# Tambahkan Token TMDB (Disarankan)
echo 'export TMDB_TOKEN="isi_bearer_token_tmdb_anda"' >> ~/.bashrc

# ATAU Tambahkan API Key TMDB
echo 'export TMDB_API_KEY="isi_api_key_tmdb_anda"' >> ~/.bashrc

# Muat ulang konfigurasi terminal
source ~/.bashrc
```

*Catatan: Ganti `"isi_bearer_token_tmdb_anda"` atau `"isi_api_key_tmdb_anda"` dengan kredensial asli dari akun developer TMDB Anda sebelum menjalankan perintah.*

## Cara Instalasi (`.local/bin`)

Agar skrip dapat dipanggil langsung dari mana saja di terminal tanpa mengetik ekstensi `.py`, ikuti langkah pemasangan berikut:

1. **Clone Repositori ini:**
   ```bash
   git clone https://github.com
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

