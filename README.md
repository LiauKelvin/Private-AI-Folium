# 🌿 Virtual-Assistant-AI-Folium (Folium AI)

<p align="center">
  <img src="https://github.com/LiauKelvin/Private-AI-Folium/blob/main/.asset_AI/AI_ICON.png?raw=true" alt="Folium AI Icon" width="150">
  <img src="https://github.com/LiauKelvin/Private-AI-Folium/blob/main/.asset_AI/Ollama%20picture.webp?raw=true" alt="Folium AI Icon" width="150">
  <img src="https://github.com/LiauKelvin/Private-AI-Folium/blob/main/.asset_AI/gradio.png?raw=true" alt="Folium AI Icon" width="150">
</p>

## 📖 Tentang Program
**Folium AI** adalah sebuah Sistem Informasi *Virtual Assistant* berbasis Kecerdasan Buatan (AI) yang dirancang khusus dapat berjalan pada perangkat pribadi untuk kebutuhan personal dengan mengedepankan **privasi dan kedaulatan data**. 

Berjalan 100% secara lokal (*offline*) menggunakan platform **Ollama** serta UI dari **Gradio**, dengan mengadopsi arsitektur *Retrieval-Augmented Generation* (RAG), aplikasi ini memungkinkan pengguna untuk berinteraksi, bertanya, dan mencari informasi dari dokumen pribadi tanpa perlu mengirimkan data ke *server* atau *cloud* internet. Semua pemrosesan teks dan *embedding* dokumen terjadi secara aman di dalam perangkat pengguna sendiri.

### ✨ Fitur Utama:
*   **100% Local & Private:** Tidak memerlukan koneksi internet, berjalan secara lokal untuk menjamin kerahasiaan dokumen pribadi.
*   **Integrasi Ollama:** Menggunakan ekosistem *Local LLM* yang efisien dan cepat.
*   **Interaksi Dokumen (RAG):** Membaca dan menjawab pertanyaan berdasarkan dokumen spesifik yang diunggah pengguna (*users*).
*   **Antarmuka Pengguna Sederhana:** Tersedia dalam bentuk aplikasi (*executable*) yang mudah digunakan oleh pengguna non-teknis.

---

## 💻 Prasyarat Sistem
Sebelum menginstal aplikasi, pastikan perangkat Anda memenuhi spesifikasi berikut:
*   **Sistem Operasi:** Windows 10/11 (Untuk versi `.exe`).
*   **RAM:** Minimal 8 GB (Direkomendasikan 16 GB untuk kelancaran model LLM).
*   **Penyimpanan:** Ruang kosong yang cukup untuk mengunduh model Ollama (bervariasi tergantung model, misal: ~4.7 GB untuk Llama 3) serta aplikasi Ollama itu sendiri yang berkisar ~1.7 GB.

---

## 🛠️ Cara Instalasi untuk Developer (Pengembang)
Bagian ini ditujukan bagi pengembang yang ingin melihat, memodifikasi, atau menjalankan *source code* secara langsung menggunakan Python.

![Instalasi Developer](https://github.com/LiauKelvin/Private-AI-Folium/blob/main/.asset_AI/img_inst_dev.png?raw=true)

**Langkah-langkah Instalasi:**
1.  **Instalasi Ollama:** Unduh dan instal platform Ollama beserta Model AI yang diinginkan melalui situs resmi [ollama.com](https://ollama.com).
2.  **Instalasi Python:** Pastikan **Python 3.12.8** telah terinstal di perangkat Anda. Anda dapat mengunduhnya melalui situs resmi [python.org](https://www.python.org).
3.  **Clone Repository:** Unduh folder *file* proyek ini melalui tautan GitHub:
    ```bash
    git clone https://github.com/LiauKelvin/Private-AI-Folium.git
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
3.  **Jalankan Aplikasi:** Klik ganda (*double-click*) pada *file* `Folium_AI.exe` yang telah diunduh pada sistem operasi Anda dan tunggu beberapa saat (~*sekitar 30-60 detik*) untuk mulai berinteraksi dengan *Virtual Assistant* berbasis AI.

---

## 🤖 Model AI Terbaik yang digunakan (Parameter 2.5B - 3.8B)
**Model AI** Adalah  adalah sebuah program komputer yang telah dilatih dengan data dalam jumlah besar agar bisa mengenali pola, memprediksi hasil, atau mengambil keputusan secara mandiri. Layaknya "otak" dari kecerdasan buatan (*Artificial Intelligence*), model ini mempelajari cara menyelesaikan perintah atau tugas tertentu tanpa perlu diprogram secara manual langkah demi langkah.

<div align="center">
  
|No|**Model AI**|**Parameter**|**Dikembangkan Oleh**|
|--|------------|-------------|---------------------|
|1.|Qwen2.5     |3.0B         |Alibaba              |
|2.|Llama3.2    |3.0B         |Meta                 |
|3.|Phi4-Mini   |3.8B         |Microsoft            |

</div>

**Keterangan Model AI yang digunakan:**
*   **Qwen2.5:**  Model dengan pengetahuan luas dan kemampuan pada bidang pemrograman serta matematika yang dikembangkan oleh **Alibaba**, yang memiliki Parameter berkisar antara 0,5 hingga 75 miliar token data.
*   **Llama3.2:** Model dengan kemampuan multibahasa, pencarian, dan peringkasan yang dikembangkan oleh **Meta** dengan Parameter berkisar antara 1 hingga 3 miliar token data.
*   **Phi4-Mini:** Model dengan data sintetis dan situs web yang telah disaring (filter) dengan fokus untuk memperoleh data berkualitas tinggi dengan penalaran yang efektif, dikembangkan oleh **Microsoft**.

### ⬇️ Cara Installasi Model-AI dengan Ollama
1.  **Install Ollama:** Pastikan telah instalasi Platform [Ollama](https://ollama.com/download) telah dilakukan, pengecekan dapat dilakukan pada CMD **(Command Prompt)** dengan perintah:
    ```bash
    Ollama -v
    ```
2.  **Install Model-AI:** Setelah Platform Ollama diinstall, gunakan perintah berikut untuk **instalasi** Model-AI dengan perintah:
    ```bash
    Ollama run <Model-AI>
    ```
    Contoh instalasi **Model-AI** dengan perintah:
    ```bash
    Ollama run qwen2.5:3b
    ```
3.  **Cek Model-AI:** Tunggu Model-AI berhasil untuk terinstall, setelah selesai lakukan pengecekan Model-AI yang telah terinstall dengan perintah:
    ```bash
    Ollama list
    ```
4.  **Selesai:** Setelah terkonfirmasi Model-AI berhasil terinstall, Maka Sistem Informasi **Private-AI-Folium** siap untuk digunakan

---

## 🤝 Penutup & Kontribusi
Terima kasih telah menggunakan **Private-AI-Folium**. Proyek ini dikembangkan sebagai bagian dari penelitian rancang bangun sistem informasi *Virtual Assistant* berbasis AI yang memprioritaskan keamanan data pengguna. 

Jika Anda menemukan *bug* (kesalahan program) atau memiliki saran pengembangan fitur baru, jangan ragu untuk membuka *Issue* atau mengirimkan *Pull Request* di *repository* ini. Dukungan dan masukan Anda akan sangat berarti untuk pengembangan *Local AI* yang lebih baik ke depannya!

---
*Dibuat dengan ☕ dan dedikasi untuk Privasi Data.*

***

### 💡 Tips Tambahan untuk Pengembangan Sistem AI lebih lanjut:
1. **Pengembangan UI:** Sistem dapat dikembangkan kembali untuk tampilan (*interface*) agar lebih mudah untuk digunakan, sistematis, dan sesuai dengan berbagai ukuran tampilan perangkat.
2. **Kompatibilitas OS:** Sistem dapat dikembangkan untuk sesuai dengan berbagai perangkat sistem operasi (*operating system*) seperti Linux, Android, dan Mac OS.
3. **Variasi Dokumen:** Sistem dapat mengelola lebih banyak variasi dokumen selain .pdf seperti .txt, .ppt, .docs, dll.
