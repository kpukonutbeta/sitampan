# Apa itu token.json?

File `token.json` adalah "**Kunci Sesungguhnya**" (Refresh Token) yang membuktikan bahwa akun Google Anda **telah mengizinkan** aplikasi SITAMPAN ini mengakses Google Drive Anda.

Ini adalah alurnya:
1. `credentials.json` adalah **Kartu Identitas Aplikasi** (berisi nama aplikasi "SITAMPAN Uploader" dan Client ID-nya). Saat Django mencoba mengakses Drive, ia menggunakan file ini untuk bilang ke Google: *"Hai Google, saya aplikasi SITAMPAN Uploader milik si fulan"*.
2. Karena aplikasi ini **belum tahu** akun Google Drive mana yang mau di-_upload_-in file, ia memunculkan layar Login di Browser Anda (OAuth Consent Screen). Anda login pakai email `@gmail.com`.
3. Setelah Anda meng-klik **Allow / Izinkan**, Google akan mengirim balik sebuah kode unik ke aplikasi SITAMPAN.
4. Python/Django akan mengambil kode tersebut dan menyimpannya secara permanen ke dalam **file bernama `token.json`**.
5. Untuk ke depannya (besok, lusa, minggu depan), setiap kali ada dokumen baru yang di-upload, aplikasi tidak perlu lagi memunculkan layar login, karena ia sudah punya `token.json` yang berfungsi seperti "Kunci Cadangan Rahasia" untuk mengakses Drive Anda kapan saja di *background*.

**Jadi, Anda TIDAK PERLU membuat atau mengunduh `token.json` secara manual. File ini akan DIBUAT OTOMATIS oleh program kita sesaat setelah Anda berhasil Sign-in di browser untuk pertama kalinya!**
