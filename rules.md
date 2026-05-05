# PROJE ANAYASASI (Global Rules)

1. **SOLID ve Clean Code:** Yazılan her kod parçası SOLID prensiplerine harfiyen uymalıdır. Fonksiyonlar tek bir iş yapmalı (Single Responsibility), sınıflar genişlemeye açık değişime kapalı olmalıdır (Open/Closed).
2. **Mimari Kararlar:** Backend için NestJS ve Supabase, Frontend için React, Model için Python/PyTorch kullanılacaktır. Stack dışına çıkılamaz.
3. **Loglama Zorunluluğu (CRITICAL):** Her ajan, işlemlerini `logs/` dizinindeki kendi log dosyasına (örn: `logs/agent_backend_log.md`) **SÜREKLİ EKLEYEREK (Append)** yazmak zorundadır. Dosyanın üstüne yazmak (overwrite) KESİNLİKLE YASAKTIR.
   - Log formatı: `[Tarih-Saat] - Yapılan İşlem - Varsa Alınan Hata - Çözüm/Sonraki Adım`.
   - Örnek: `[14:00] - Veritabanı şeması oluşturuldu. [14:05] - HATA: Relation bulunamadı. Çözüm: Foreign key düzeltilip migration tekrar çalıştırıldı.`
4. **Hiyerarşi ve İletişim:** 
   - İcracı ajanlar (Backend, Frontend, Model vb.) kendi başlarına yeni mimari karar alamazlar. Tıkandıklarında `agent_manager.md`'ye danışırlar.
   - Yazılan her kod, merge edilmeden veya tamamlandı sayılmadan önce `agent_reviewer.md` tarafından denetlenmek zorundadır.
5. **Bağımsızlık:** Ajanlar birbirinin dosyalarını değiştiremez. (Örn: Frontend ajanı, backend controller dosyasını editleyemez).