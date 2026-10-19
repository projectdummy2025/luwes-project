# Arsitektur Sistem — Luwesin Studio

Dokumen ini menjelaskan batas arsitektur, landasan evaluasi, dan alur kerja penyuntingan esai bahasa Indonesia pada **Luwesin Studio**.

---

## 1. Masalah Pokok & Batas Konseptual

### 1.1 Keterbatasan Deteksi AI
Model deteksi teks AI komersial (seperti GPTZero, Turnitin, Copyleaks, dan Originality.ai) bekerja dengan memperkirakan kemungkinan token (perpleksitas) dan pola statistik bahasa. Detektor memiliki keterbatasan mendasar:
- **Bias Penutur Non-Asli / Bahasa Terjemahan**: Teks terstruktur atau kosakata formal kerap keliru diklasifikasikan sebagai teks mesin.
- **Hukum Goodhart**: Menargetkan metrik proksi (seperti varians panjang kalimat atau penghapusan frasa tertentu) justru merusak keterbacaan, keutuhan argumen, dan tata bahasa baku.
- **Bukan Bukti Kepengarangan**: Skor detektor bukan pembuktian apakah teks ditulis oleh manusia. Luwesin Studio tidak menjanjikan lolos detektor secara mutlak dan memperlakukan skor detektor semata sebagai sinyal sekunder.

### 1.2 Tolok Ukur Keberhasilan
Keberhasilan sistem diukur melalui **Rubrik Mutu Esai Bahasa Indonesia (Skala 1–5)**:
1. **Kesetiaan Sumber (*Faithfulness*)**: Fakta, angka, nama, urutan argumen, dan relasi logika tidak hilang atau ditambah.
2. **Keluwesan Diksi (*Diction*)**: Kosakata esai Indonesia yang wajar dan aktif, tanpa terjemahan harfiah (*calque*).
3. **Kohesi Alur (*Coherence*)**: Gagasan mengalir antarkalimat dan antarparagraf tanpa ketergantungan pada transisi mekanis.
4. **Struktur Retorika (*Structure*)**: Bentuk kalimat bervariasi secara alami sesuai isi argumen; bebas dari daftar tiga poin yang dipaksakan.
5. **Kesesuaian Laras (*Register*)**: Nada formal/akademik/profesional yang konsisten sesuai tujuan tulisan.

---

## 2. Arsitektur Komponen

```text
Frontend (Vite + React)
  |-- EditorCard (Input & Output)
  |-- ScoreMeter (Linting Gaya & Ukuran Dokumen)
  \-- useHumanizer (State & API Service)
         |
         v
Backend (FastAPI - Port 8035)
  |-- main.py (REST API: /api/config, /api/analyze, /api/humanize, /api/evaluate)
  |-- engine.py (Prompt esai Indonesia, chunking, pembersihan output, guardrail lokal)
  |-- evaluation.py (Rubrik 5 dimensi, pairwise judge mitigasi bias posisi, parsing ketat)
  \-- config.py (Pengaturan lingkungan dan penyedia model)
```

---

## 3. Alur Kerja Penyuntingan

### 3.1 Mode Cepat (Fast Mode)
1. Teks sumber dipecah menjadi chunk terikat paragraf (ambang 500 kata) tanpa memotong tengah kalimat.
2. Setiap chunk dikirim ke model target dengan direktif penyuntingan esai bahasa Indonesia (verba aktif, hubungan logis alami, rasio panjang 0.85x–1.15x).
3. Artefak pemformatan (markdown bold/italic, pagar kode, pembuka generik) dibersihkan via `cleanOutput`.
4. Sistem memverifikasi rasio panjang, keutuhan paragraf, dan penanda fakta sebelum draf dikembalikan.

### 3.2 Mode Mendalam (Deep Mode)
1. Draf hasil Pass 1 diaudit secara lokal terhadap kemunculan pola klise dan guardrail penyuntingan.
2. Chunk yang bermasalah dikirim untuk perbaikan terfokus dengan menyertakan teks sumber asli dan daftar masalah terukur.
3. Hasil perbaikan hanya diterima bila guardrail lulus dan jumlah masalah gaya berkurang dibandingkan draf pertama; jika tidak, draf pertama dipertahankan.

---

## 4. Evaluasi & AI Judge

Modul `evaluation.py` menyediakan evaluasi *pairwise* independen:
- Menguji dua draf kandidat terhadap sumber secara buta (*blind evaluation*).
- Menjalankan urutan ganda (A vs B dan B vs A) untuk memitigasi bias posisi (*position bias*).
- Menghasilkan status `consistent` jika pilihan konsisten di kedua arah, atau `uncertain` bila terdapat pertentangan.
