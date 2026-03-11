# Panduan Mendapatkan credentials.json untuk Google Drive API

Ikuti langkah-langkah berikut untuk mendapatkan file kredensial OAuth 2.0 Anda:

1. Buka [Google Cloud Console](https://console.cloud.google.com).
2. Pastikan Anda sudah membuat Project atau pilih Project yang sudah ada di bagian atas kiri layar.

### Langkah A: Mengaktifkan API
3. Di menu sebelah kiri (ikon garis tiga/hamburger), pilih **APIs & Services** > **Library**.
4. Cari **Google Drive API** dan klik **Enable** (Aktifkan).

### Langkah B: Konfigurasi Layar Persetujuan (OAuth consent screen)
5. Di menu kiri, pilih **APIs & Services** > **OAuth consent screen**.
6. Pilih **External** lalu klik **Create**.
7. Isi form:
   - **App name**: misal "SITAMPAN Uploader"
   - **User support email**: Pilih email Anda
   - **Developer contact information**: Isi dengan email Anda
8. Klik **Save and Continue** melewati halaman *Scopes*.
9. Di halaman **Test users**, ini **sangat penting**:
   - Klik **ADD USERS**
   - Masukkan alamat email Gmail pribadi Anda (email yang sama yang folder Drive-nya akan dipakai)
   - Klik Add, lalu **Save and Continue**.
10. Selesaikan dan kembali ke Dashboard.

### Langkah C: Membuat Kredensial
11. Buka kembali menu kiri, pilih **APIs & Services** > **Credentials**.
12. Klik tombol **+ CREATE CREDENTIALS** di bagian atas, lalu pilih **OAuth client ID**.
13. Di bagian **Application type**, pilih **Desktop App**.
14. Beri nama bebas (misal: "SITAMPAN Desktop Client"), lalu klik **Create**.
15. Akan muncul jendela pop-up dengan Client ID Anda, klik tombol **DOWNLOAD JSON**.
16. File yang terunduh biasanya bernama panjang (seperti `client_secret_xxx...json`).
17. Ganti nama file tersebut menjadi tepat **`credentials.json`**.
18. Pindahkan/taruh file `credentials.json` ini di dalam folder `sitampan` di komputer Anda (satu folder dengan file `manage.py` dan `.env`).
