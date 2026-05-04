# 🌿 Virtual-Assistant-AI-Folium (Folium AI)

<p align="center">
  <img src="https://github.com/LiauKelvin/Private-AI-Folium/blob/main/.asset_AI/AI_ICON.png?raw=true" alt="Folium AI Icon" width="150">
  <img src="https://github.com/LiauKelvin/Private-AI-Folium/blob/main/.asset_AI/Ollama%20picture.webp?raw=true" alt="Folium AI Icon" width="150">
  <img src="https://github.com/LiauKelvin/Private-AI-Folium/blob/main/.asset_AI/gradio.png?raw=true" alt="Folium AI Icon" width="150">
</p>

## 📖 Tentang Program
**Folium AI** adalah sebuah Sistem Informasi *Virtual Assistant* berbasis Kecerdasan Buatan (AI) yang dirancang khusus untuk kebutuhan personal dengan mengedepankan **privasi dan kedaulatan data**. 

Berjalan 100% secara lokal (*offline*) menggunakan platform **Ollama** dan mengadopsi arsitektur *Retrieval-Augmented Generation* (RAG), aplikasi ini memungkinkan pengguna untuk berinteraksi, bertanya, dan mencari informasi dari dokumen pribadi tanpa perlu mengirimkan data ke *server* atau *cloud* internet. Semua pemrosesan teks dan *embedding* dokumen terjadi secara aman di dalam perangkat pengguna.

### ✨ Fitur Utama:
*   **100% Local & Private:** Tidak memerlukan koneksi internet, menjamin kerahasiaan dokumen pribadi.
*   **Integrasi Ollama:** Menggunakan ekosistem *Local LLM* yang efisien dan cepat.
*   **Interaksi Dokumen (RAG):** Membaca dan menjawab pertanyaan berdasarkan dokumen spesifik yang diunggah pengguna.
*   **Antarmuka Pengguna Sederhana:** Tersedia dalam bentuk aplikasi (*executable*) yang mudah digunakan oleh pengguna non-teknis.

---

## 💻 Prasyarat Sistem
Sebelum menginstal aplikasi, pastikan perangkat Anda memenuhi spesifikasi berikut:
*   **Sistem Operasi:** Windows 10/11 (Untuk versi `.exe`).
*   **RAM:** Minimal 8 GB (Direkomendasikan 16 GB untuk kelancaran model LLM).
*   **Penyimpanan:** Ruang kosong yang cukup untuk mengunduh model Ollama (bervariasi tergantung model, misal: ~4.7 GB untuk Llama 3).

---

## 🛠️ Cara Instalasi untuk Developer (Perancang)
Bagian ini ditujukan bagi pengembang yang ingin melihat, memodifikasi, atau menjalankan *source code* secara langsung menggunakan Python.

![Instalasi Developer](https://github.com/LiauKelvin/Private-AI-Folium/blob/main/.asset_AI/img_inst_dev.png?raw=true)

**Langkah-langkah Instalasi:**
1.  **Instalasi Ollama:** Unduh dan instal platform Ollama beserta Model AI yang diinginkan melalui situs resmi [ollama.com](https://ollama.com).
2.  **Instalasi Python:** Pastikan **Python 3.12.8** telah terinstal di perangkat Anda. Anda dapat mengunduhnya melalui situs resmi [python.org](https://www.python.org).
3.  **Clone Repository:** Unduh folder *file* proyek ini melalui tautan GitHub:
    ```bash
    git clone [https://github.com/LiauKelvin/Private-AI-Folium.git](https://github.com/LiauKelvin/Private-AI-Folium.git)
    cd Private-AI-Folium
    ```
4.  **Instal Dependencies:** Instal semua *library* Python yang diperlukan menggunakan perintah berikut di terminal:
    ```bash
    pip install -r requirements.txt
    ```
5.  **Jalankan Aplikasi:** Eksekusi program utama untuk menjalankan Sistem AI:
    ```bash
    python app.py
    ```

---

## 🚀 Cara Instalasi untuk Pengguna (*User*)
Bagian ini ditujukan bagi pengguna akhir yang ingin langsung menggunakan aplikasi tanpa perlu berurusan dengan *coding* atau *environment* Python.

![Instalasi Pengguna](https://github.com/LiauKelvin/Private-AI-Folium/blob/main/.asset_AI/img_inst_user.png?raw=true)

**Langkah-langkah Instalasi:**
1.  **Instalasi Ollama:** Unduh dan instal platform Ollama beserta Model AI yang dibutuhkan melalui situs resmi [ollama.com](https://ollama.com). *(Wajib dilakukan agar aplikasi memiliki "otak" untuk berpikir).*
2.  **Unduh Aplikasi:** Buka halaman *Release* pada tautan GitHub berikut dan unduh *file* **Folium_AI.exe** (ukuran file sekitar 135 MB): 
    [Download Folium_AI.exe v1.0.0](https://github.com/LiauKelvin/Private-AI-Folium/releases/tag/v1.0.0)
3.  **Jalankan Aplikasi:** Klik ganda (*double-click*) pada *file* `Folium_AI.exe` yang telah diunduh pada sistem operasi Anda untuk mulai berinteraksi dengan *Virtual Assistant*.

---

## 🤝 Penutup & Kontribusi
Terima kasih telah menggunakan **Private-AI-Folium**. Proyek ini dikembangkan sebagai bagian dari penelitian rancang bangun sistem informasi *Virtual Assistant* yang memprioritaskan keamanan data pengguna. 

Jika Anda menemukan *bug* (kesalahan program) atau memiliki saran pengembangan fitur baru, jangan ragu untuk membuka *Issue* atau mengirimkan *Pull Request* di *repository* ini. Dukungan dan masukan Anda sangat berarti untuk pengembangan *Local AI* yang lebih baik ke depannya!

---
*Dibuat dengan ☕ dan dedikasi untuk Privasi Data.*

***

### 💡 Tips Tambahan untuk Repositorimu:
