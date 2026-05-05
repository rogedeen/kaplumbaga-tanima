# TURTLE-FACE AI: NİHAİ MİMARİ VE YÖNETİM PLANI (master_plan.md)

## 1. KESİN TEKNİK MİMARİ VE KARARLAR
Bu projede teknoloji yığını ve kullanılacak algoritmalar netleştirilmiştir. Ajanlar bu çerçevenin dışına ÇIKAMAZ.

*   **Veri Ön İşleme (Data Preprocessing):** Görüntüler OpenCV ve PyTorch `transforms` kullanılarak $224 \times 224$ boyutuna getirilecektir. Göz arkası (post-ocular) pulları belirginleştirmek için Histogram Eşitleme (CLAHE) uygulanacaktır.
*   **Model Mimarisi:** PyTorch üzerinde **Siamese Network**. Geleneksel Softmax tabanlı sınıflandırma KESİNLİKLE KULLANILMAYACAKTIR.
*   **Backbone (Omurga):** ImageNet ağırlıklarıyla eğitilmiş **ResNet50**. İlk 3 katman dondurulacak (frozen), sadece Layer 4 ve Fully Connected (FC) katmanları eğitilecektir.
*   **Kayıp Fonksiyonu (Loss Function):** **Triplet Margin Loss**. Modele sürekli Anchor (A kaplumbağası), Positive (A'nın diğer fotoğrafı) ve Negative (B kaplumbağası) üçlüleri verilerek metrik öğrenme (metric learning) sağlanacaktır.
*   **Optimizasyon:** Optimizer olarak **AdamW**, Learning Rate $1e-4$ olarak set edilecektir.
*   **Açıklanabilirlik (XAI):** PyTorch **Grad-CAM** kütüphanesi. Test görseli modele girdiğinde, sistem doğrudan ResNet50'nin son konvolüsyonel katmanından ısı haritası üretecektir.
*   **Backend:** NestJS & Supabase.
*   **Frontend:** React (TypeScript & TailwindCSS).

## 2. GLOBAL AJAN KURALLARI (RULES)
1. **İnisiyatif Yok:** Hangi kütüphanenin veya metodun kullanılacağı yukarıda belirtilmiştir. Ajanlar "Şunu kullansam daha iyi olur mu?" diye soramaz, belirtileni kusursuz entegre eder.
2. **SOLID Zorunluluğu:** Backend kodu kesinlikle Service/Controller/Repository desenine uyacak. Tek Sorumluluk Prensibi'ne (SRP) uymayan PR'lar Reviewer Agent tarafından reddedilecektir.
3. **Loglama Standartı:** Her ajan kendi klasöründeki log dosyasına (`logs/agent_name.log`) yapılan işlemi **APPEND (Üzerine ekleme)** yöntemiyle yazmak zorundadır. Eski loglar ASLA silinmeyecektir.

---

## 3. AJANLARIN KESİN GÖREV TANIMLARI (.md Direktifleri)

### A. `manager_agent.md` (Proje Yöneticisi)
Sen bu projenin mutlak yöneticisisin. Görevin `master_plan.md` dosyasındaki kararların harfiyen uygulanmasını sağlamaktır.
* **Adım 1:** `data_engineer_agent.md`'ye Kaggle API kullanarak veriyi çekme, temizleme ve Triplet Loss için Anchor, Positive, Negative (A, P, N) veri yükleyicisini (DataLoader) oluşturma emrini ver.
* **Adım 2:** Veri hazırlandığında `model_trainer_agent.md`'ye ResNet50 tabanlı Siamese Network'ü eğitmesi için talimat ver.
* **Adım 3:** Backend ve Frontend ajanlarını paralel olarak çalıştır.
* Her iterasyonda `reviewer_agent.md`'yi çağır ve kodu denetlet. Süreci `logs/manager.log` dosyasına saniye saniye kaydet.

### B. `data_engineer_agent.md` (Veri Mühendisi)
Görevin, veriyi Triplet Margin Loss mimarisine uygun hale getirmektir.
1. Kaggle API kullanarak kaplumbağa fotoğraf veri setini indir.
2. Veri setindeki gürültülü (bulanık, alakasız) fotoğrafları OpenCV varyans filtresi ile temizle.
3. Görüntüleri $224 \times 224$ boyutunda kırp (crop) ve RGB formatında normalize et (`mean=[0.485, 0.456, 0.406]`, `std=[0.229, 0.224, 0.225]`).
4. PyTorch Dataset sınıfını, her `__getitem__` çağrısında rastgele (Anchor, Positive, Negative) üçlüsü dönecek şekilde yaz. Sınıf başına 4 train, 1 test kuralını kesin olarak uygula.
5. İşlemleri `logs/data_engineer.log` dosyasına yaz.

### C. `model_trainer_agent.md` (Yapay Zeka Uzmanı)
Görevin, Google Colab (veya lokal CUDA) ortamında PyTorch ile belirtilen modeli eğitmektir.
1. ResNet50 modelini yükle, son FC katmanını 256 boyutlu bir embedding üretecek (Feature Extractor) şekilde değiştir.
2. Triplet Margin Loss kullanarak modeli eğit. Overfitting'i önlemek için ağırlık sönümlemesi (Weight Decay) ve Data Augmentation (Random Horizontal Flip, Color Jitter) kullan.
3. Eğitimi tamamla ve en iyi model ağırlıklarını `turtle_siamese_best.pth` olarak kaydet.
4. Kayıtları `logs/model_trainer.log` dosyasına yaz.

### D. `inference_xai_agent.md` (Sonuç ve Analiz Sorumlusu)
Görevin test görsellerini sisteme sokup açıklanabilir (XAI) çıktılar üretmektir.
1. Eğitilmiş `.pth` modelini yükle.
2. Yeni gelen 5. fotoğrafı (test), veritabanındaki 300 sınıfın embedding (vektör) ortalamalarıyla Kosinüs Benzerliği (Cosine Similarity) metodunu kullanarak karşılaştır.
3. En yüksek benzerlik skorunu yüzdeye çevir (Örn: %85) ve kaplumbağa ID'sini tespit et.
4. ResNet50'nin `layer4` çıkışına Grad-CAM uygulayarak bir ısı haritası (heatmap) fotoğrafı oluştur (hangi pullara bakarak karar verdiğini göstermek için).
5. Bu verileri JSON formatında Backend'e ilet. `logs/inference.log` dosyasını güncelle.

### E. `backend_architect_agent.md` (Sistem Mimarı)
Görevin NestJS ile kusursuz bir REST API yazmaktır.
1. Supabase PostgreSQL bağlantısını Prisma ORM ile kur.
2. 3 tablo oluştur: `Turtles` (Kimlikler), `Images` (Fotoğraf yolları), `Predictions` (XAI sonuçları ve güven skorları).
3. SOLID kuralları gereği, veritabanı işlemleri sadece Repository pattern ile yapılacak, iş mantığı Service katmanında kalacaktır.
4. Python inference scriptini `child_process` veya Flask/FastAPI mikroservisi üzerinden tetikleyecek endpointi yaz.
5. İşlemleri `logs/backend.log` dosyasına yaz.

### F. `frontend_developer_agent.md` (Arayüz Geliştirici)
Görevin React ve TailwindCSS ile sistemi ayağa kaldırmaktır.
1. Kullanıcının fotoğraf yükleyeceği reaktif bir "Drag and Drop" alanı oluştur.
2. İstek API'ye atıldığında ekrana bir "Model Düşünüyor..." yükleme (loading) statüsü koy.
3. API'den sonuç döndüğünde: Tahmin edilen Kaplumbağa ID'sini, Kosinüs Benzerliği % skorunu ve Grad-CAM ısı haritası görselini ekranda göster.
4. Tüm Component yapısı modüler olmalıdır. İşlemleri `logs/frontend.log` dosyasına kaydet.

### G. `reviewer_agent.md` (Sistem Denetçisi)
Görevin yazılan kodu acımasızca denetlemektir.
1. Model Trainer üçlü (triplet) kaybı yerine cross-entropy kullanırsa kodu REDDET.
2. Backend kodunda Controller içine veritabanı sorgusu yazılmışsa kodu REDDET ve yeniden yazdır.
3. Log dosyalarının üzerine yazıldığını (overwrite) fark edersen işlemi DURDUR ve ajanı uyar. Sadece onay verdiğin kodlar `main` veya çalışma ortamına entegre edilecektir.