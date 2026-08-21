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

# Nama Program Anda

Penjelasan singkat tentang apa yang dilakukan oleh program ini.

## Persyaratan Sistem

Sebelum memulai, pastikan sistem Anda sudah terinstal:
* [Git](https://git-scm.com)
* [Node.js](https://nodejs.org) (atau sesuaikan dengan bahasa pemrograman Anda)

## Cara Instalasi

Buka terminal Anda dan jalankan perintah-perintah berikut secara berurutan:

1. **Clone repositori ini:**
   ```bash
   git clone https://github.com
   ```

2. **Masuk ke folder proyek:**
   ```bash
   cd nama-repo
   ```

3. **Install dependensi:**
   ```bash
   npm install
   ```

## Konfigurasi Lingkungan (.bashrc)

Program ini membutuhkan konfigurasi variabel lingkungan di dalam file `.bashrc`. Anda bisa menambahkannya secara otomatis dengan menjalankan perintah ini di terminal:

```bash
echo 'export API_KEY="isi_api_key_di_sini"' >> ~/.bashrc
echo 'export DB_HOST="localhost"' >> ~/.bashrc
source ~/.bashrc
```

*Catatan: Ganti `"isi_api_key_di_sini"` dengan nilai yang sesuai sebelum menjalankan perintah.*

## Cara Menjalankan Program

Setelah semua langkah di atas selesai, jalankan program dengan perintah:

```bash
npm start
```
