# PROJE TANIMI VE DURUM RAPORU (SeaTurtleID)

## 1. Proje Özeti ve Amacı
Bu proje, deniz kaplumbağalarını tıpkı insan parmak izi gibi benzersiz olan yüz profillerinden (post-ocular pullarından) tanımayı amaçlayan otonom bir web platformudur. Sistem, **ArcFace Metrik Öğrenme** kullanarak 367 farklı kaplumbağa sınıfını yüksek doğrulukla ayırt edebilir.

## 2. Mimari Durum (Refactoring Sonrası)
Proje, "Senior Full-Stack Mimarı" denetiminde akademik jüri standartlarına uygun şekilde refactor edilmiştir:

*   **SOLID Uyumluluk:** Tüm backend servisleri `SRP` ve `DIP` prensiplerine göre modüler hale getirilmiştir.
*   **Bağımsız Inference:** Python inference motoru, NestJS backend'inden soyutlanmış (IInferenceEngine) ve bağımsız bir "Inference Engine" olarak kurgulanmıştır.
*   **Premium UI:** Frontend, araştırma projesi ciddiyetine uygun, modern ve şık bir "Dark Research Tool" tasarımına kavuşturulmuştur.

## 3. Güncel Teknoloji Yığını (Tech Stack)
*   **AI:** Python, PyTorch, ArcFace, ConvNeXt-Tiny.
*   **Backend:** NestJS (TypeScript), Prisma ORM.
*   **Database:** Supabase (PostgreSQL).
*   **Frontend:** React, Tailwind CSS, Vite.
*   **Inference:** `child_process` üzerinden otonom Python-Node.js köprüsü.

## 4. Ajan Rolleri ve Denetim
Proje boyunca görev alan ajanlar:
*   **Manager Agent:** Süreç orkestrasyonu.
*   **Reviewer Agent:** Kod kalitesi ve SOLID denetimi.
*   **Senior Architect (Current):** Refactoring ve akademik raporlama.

## 5. Proje İlerleme Durumu
- [x] Ar-Ge Fazı: Model eğitimi (367 sınıf, ArcFace).
- [x] Backend Fazı: NestJS API ve Python entegrasyonu.
- [x] Frontend Fazı: Premium UI ve Drag-and-Drop uploader.
- [x] Kalite Fazı: SOLID refactoring ve akademik rapor hazırlığı.
- [x] Yayılım Fazı: GitHub entegrasyonu ve dokümantasyon.

---
**Durum:** Hazır / Sunuma Hazır
**Sürüm:** v1.0.0 (Refactored)