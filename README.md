# EmojiShift

Aplikasi enkripsi teks berbasis web yang mengubah pesan biasa menjadi deretan emoji menggunakan algoritma cipher Vigenère yang dimodifikasi — dilengkapi noise emoji acak untuk mempersulit analisis.

Dibangun dengan Python (Flask) dan berjalan di browser.

---

## Daftar Isi

1. [Persyaratan](#persyaratan)
2. [Instalasi di Windows](#instalasi-di-windows)
3. [Menjalankan Aplikasi](#menjalankan-aplikasi)
4. [Cara Pakai](#cara-pakai)
5. [Penjelasan Algoritma](#penjelasan-algoritma)
6. [Struktur Project](#struktur-project)

---

## Persyaratan

- Windows 10 atau 11
- Python 3.10 ke atas
- Koneksi internet (hanya saat instalasi, untuk mengunduh dependensi)

---

## Instalasi di Windows

### Langkah 1: Instal Python

1. Buka https://python.org/downloads dan unduh installer Python versi terbaru.
2. Jalankan installer. Pada halaman pertama, centang opsi **"Add Python to PATH"** sebelum klik Install Now.
3. Tunggu hingga selesai, lalu klik Close.
4. Verifikasi instalasi dengan membuka Command Prompt dan ketik:

```
python --version
```

Output yang muncul harus seperti `Python 3.x.x`. Jika muncul error, ulangi langkah instalasi dan pastikan opsi "Add to PATH" dicentang.

### Langkah 2: Ekstrak Project

1. Klik kanan file `emojishift.zip` dan pilih **Extract All**.
2. Pilih lokasi folder tujuan, lalu klik Extract.
3. Buka folder hasil ekstrak. Di dalamnya terdapat folder `emojishift`.

### Langkah 3: Buka Terminal di Folder Project

1. Buka folder `emojishift` di File Explorer.
2. Klik pada address bar di bagian atas, ketik `cmd`, lalu tekan Enter. Command Prompt akan terbuka langsung di folder tersebut.

### Langkah 4: Buat Virtual Environment

Virtual environment memisahkan dependensi project ini dari instalasi Python global di komputer.

```
python -m venv venv
```

Aktifkan virtual environment:

```
venv\Scripts\activate
```

Jika berhasil, nama `(venv)` akan muncul di awal baris prompt.

### Langkah 5: Instal Dependensi

```
pip install -r requirements.txt
```

Tunggu hingga proses unduh dan instalasi selesai.

---

## Menjalankan Aplikasi

Pastikan virtual environment sudah aktif (ada tulisan `(venv)` di prompt), lalu jalankan:

```
python app.py
```

Buka browser dan akses:

```
http://localhost:5000
```

Untuk menghentikan server, tekan `Ctrl + C` di terminal.

---

## Cara Pakai

1. Ketik pesan di kolom **INPUT**.
2. Masukkan password di kolom **PASSWORD**. Password ini berfungsi sebagai kunci enkripsi.
3. Klik tombol **ENCRYPT** untuk mengenkripsi, atau **DECRYPT** untuk mendekripsi.
4. Hasil muncul di bagian **OUTPUT**. Klik **COPY** untuk menyalinnya.

Catatan: password yang digunakan untuk enkripsi harus sama persis saat dekripsi. Jika berbeda, hasil dekripsi akan salah.

---

## Penjelasan Algoritma

### Konsep Dasar

EmojiShift menggabungkan dua mekanisme: **Vigenère Cipher** sebagai dasar enkripsi, dan **noise emoji** sebagai lapisan pengacak tambahan.

### Tabel Emoji

File `all-emoji.json` berisi 125 emoji yang menjadi "alfabet" dari cipher ini, diurutkan berdasarkan ID dari 1 sampai 125. Emoji ini dipilih dari daftar resmi Unicode sehingga dapat ditampilkan di semua platform modern.

Contoh sebagian tabel:

| ID | Emoji | Nama |
|----|-------|------|
| 1  | 😀 | grinning face |
| 2  | 😃 | grinning face with big eyes |
| 3  | 😄 | grinning face with smiling eyes |
| ... | ... | ... |
| 94 | 👿 | angry face with horns |
| 95 | 💀 | skull |

### Ruang Karakter

EmojiShift hanya memproses **printable ASCII** — karakter dari spasi (kode 32) sampai tilde `~` (kode 126), total 95 karakter. Sebelum di-shift, nilai karakter dinormalkan ke rentang 0–94 dengan mengurangi 32. Ini mencegah overflow karena jumlah emoji (125) lebih besar dari rentang yang dipakai (95).

### Proses Enkripsi

Untuk setiap karakter plaintext pada posisi `i`:

```
shift  = ord(password[i % len(password)])
index  = (ord(karakter) - 32 + shift) % 95
output = emoji_table[index]
```

Penjelasan per bagian:

- `ord(karakter) - 32` mengubah karakter menjadi nilai 0–94. Misalnya, `'h'` (kode 104) menjadi 72.
- `shift` adalah nilai numerik karakter password yang bersesuaian. Password berulang dari awal jika pesan lebih panjang dari password.
- Keduanya dijumlahkan lalu mod 95 agar hasilnya selalu dalam rentang 0–94.
- Hasil digunakan sebagai indeks untuk mengambil emoji dari tabel.

Setelah emoji asli ditemukan, ditambahkan **2 noise emoji** di belakangnya. Noise ini bukan acak murni — di-generate dari `SHA-256(password:index:j)` sehingga nilainya deterministik dan hanya bisa diketahui oleh pemegang password yang benar.

Struktur output per karakter:

```
[ emoji_asli | noise_1 | noise_2 ]
```

Sehingga pesan `"suki"` (4 karakter) menghasilkan 12 emoji total.

Contoh langkah demi langkah dengan pesan `"ha"` dan password `"ab"`:

```
Karakter 'h' (posisi 0)
  ord('h') - 32 = 72
  shift = ord('a') = 97
  index = (72 + 97) % 95 = 169 % 95 = 74
  emoji_asli = emoji_table[74]    -> 😦
  noise_1, noise_2 = SHA-256("ab:0:0") % 125, SHA-256("ab:0:1") % 125

Karakter 'a' (posisi 1)
  ord('a') - 32 = 65
  shift = ord('b') = 98
  index = (65 + 98) % 95 = 163 % 95 = 68
  emoji_asli = emoji_table[68]    -> ☹
  noise_1, noise_2 = SHA-256("ab:1:0") % 125, SHA-256("ab:1:1") % 125
```

Output akhir: 6 emoji (2 karakter × 3 emoji per karakter).

### Proses Dekripsi

Karena struktur ciphertext selalu `[asli, noise, noise]` per karakter, dekripsi hanya perlu mengambil emoji pada posisi `0, 3, 6, 9, ...` dan mengabaikan sisanya:

```
emoji  = ciphertext[i * 3]
index  = posisi_emoji_di_tabel
shift  = ord(password[i % len(password)])
karakter = chr((index - shift) % 95 + 32)
```

Operator mod memastikan hasil tidak negatif meskipun pengurangan menghasilkan bilangan di bawah nol.

### Mengapa Noise?

Tanpa noise, panjang ciphertext sama persis dengan panjang plaintext — penyerang bisa langsung tahu jumlah karakter pesan. Dengan 2 noise emoji per karakter, panjang ciphertext selalu 3× panjang plaintext dan tidak memberikan informasi tentang isi pesan.

Selain itu, karena noise di-generate dari password menggunakan SHA-256, tanpa password yang benar tidak ada cara untuk membedakan mana emoji asli dan mana noise hanya dari melihat ciphertext.

### Mengapa Vigenère?

Caesar cipher menggunakan satu angka geser untuk seluruh pesan, sehingga distribusi frekuensi emoji di output tetap terjaga dan mudah dianalisis. Vigenère menggunakan password berupa string, sehingga satu karakter yang sama di plaintext bisa menghasilkan emoji berbeda tergantung posisinya — membuat analisis frekuensi jauh lebih sulit.

---

## Struktur Project

```
emojishift/
├── app.py              server Flask, mendefinisikan endpoint API
├── emojishift.py       library enkripsi dan dekripsi
├── all-emoji.json      database 125 emoji terurut
├── requirements.txt    daftar dependensi Python
├── Procfile            konfigurasi deployment (gunicorn)
└── templates/
    └── index.html      halaman web (HTML, CSS, JavaScript)
```

### Endpoint API

| Method | URL | Fungsi |
|--------|-----|--------|
| GET | `/` | Menampilkan halaman utama |
| POST | `/api/encrypt` | Mengenkripsi teks |
| POST | `/api/decrypt` | Mendekripsi teks |

Request body untuk `/api/encrypt` dan `/api/decrypt`:

```json
{
  "text": "pesan yang akan diproses",
  "password": "kunci_rahasia"
}
```