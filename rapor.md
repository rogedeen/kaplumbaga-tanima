# Proje Ar-Ge ve Optimizasyon Süreç Raporu: SeaTurtleID

## 1. Proje Özeti
Bu çalışma kapsamında, deniz kaplumbağalarını kabuk desenlerinden (pullarından) bireysel olarak tanımayı hedefleyen yapay zeka modelinin (SeaTurtleID) Ar-Ge, optimizasyon, hata ayıklama ve MVP (Minimum Viable Product) entegrasyon süreçleri yürütülmüştür. Önceden eğitilmiş ancak 384x384 yüksek çözünürlük entegrasyonunda eğitimi yarım kalan modelin ("latest_384.pth") kurtarılması, eğitimin devam ettirilmesi ve sistemin Full-Stack bir web arayüzüne bağlanması sağlanmıştır.

## 2. Kullanılan Teknolojiler ve Araçlar
Projenin bu fazında aşağıdaki teknoloji yığınından (tech stack) yararlanılmıştır:
* **Yapay Zeka & Derin Öğrenme:** Python, PyTorch, Torchvision, Timm (ConvNeXt-Tiny Omurgası), ArcFace (Metric Learning).
* **Donanım & Bulut Bilişim:** Google Colab (NVIDIA T4 GPU).
* **Full-Stack & Mimari:** NestJS (Backend), React & TailwindCSS (Frontend), Node.js `child_process` (AI Modeli ile API arası köprü).
* **Yazılım Mühendisliği Standartları:** SOLID Prensipleri, Clean Code, Çoklu Ajan Mimarisi (Agentic Workflow).
* **Versiyon Kontrol:** Git & GitHub.

## 3. Geliştirme Aşamaları ve Kriz Yönetimi

### 3.1. Kavramsal İspat (PoC) ve İlk Çıkarım Testleri
Yüksek çözünürlüğe geçerken eğitim doğruluğu %11'lerde kalan `latest_384.pth` dosyası, yerel ortamda `evaluate_model.py` ile test edilmiş ve modelin aslında daha geniş çözünürlükte detayları (kabuk çatlakları vs.) ezberleyerek %57.28 doğruluk oranına ulaştığı keşfedilmiştir. Bu durum projenin PoC aşamasını başarıyla geçtiğini kanıtlamıştır.

### 3.2. Google Colab ile Modelin Yeniden Yüklenmesi (Refuel & Finetune)
Eğitimin yarıda kalmasına sebep olan `CosineAnnealingLR` (Öğrenme Oranı Zamanlayıcısı) terk edilerek yerine **`ReduceLROnPlateau`** algoritması entegre edilmiştir. Bu sayede modelin, doğrulama kaybı (Validation Loss) düşmeyi bıraktığında öğrenme oranını dinamik olarak yarıya indirmesi sağlanmıştır. 

### 3.3. Kritik Veri Seti Hatalarının (CUDA Errors) Çözümü
Eğitim sırasında GPU'nun çökmesine (CUDA device-side assert triggered) neden olan iki büyük veri seti krizi çözülmüştür:
1. **Hayalet Klasör Sorunu:** Google Drive'ın arka planda oluşturduğu `.ipynb_checkpoints` klasörlerinin model tarafından yeni bir sınıf olarak algılanması, özel bir veri yükleyici (Data Loader) mantığı ile engellenmiştir.
2. **Sınıf Uyumsuzluğu (Nükleer Senkronizasyon):** Eğitim setinde 367, test setinde ise 398 farklı kaplumbağa sınıfı olduğu tespit edilmiştir. Doğrulama (Validation) esnasında modelin çökmemesi için Python kodunda dinamik bir filtreleme yapılarak sadece eğitimde var olan 367 sınıf test setinde tutulmuş, diğerleri filtrelenmiştir.

### 3.4. "Amnesia" (Hafıza Kaybı) Bug'ının Giderilmesi
Colab ortamında modelin ağırlıkları yüklenirken katman isimlerindeki uyumsuzluk nedeniyle modelin sıfırdan eğitime başlama hatası tespit edilmiştir. Modelin orijinal mimarisi (BatchNorm, Dropout, Linear katmanları) koda doğrudan entegre edilmiş ve PyTorch'un `strict=True` parametresi ile model beyninin `%100` oranında doğru yüklenmesi zorunlu kılınmıştır.

### 3.5. Ağırlaştırılmış Eğitim (Data Augmentation) ve Yeni Rekor
Model, eğitim sırasında `RandomResizedCrop` ve `ColorJitter` gibi ağır veri artırma teknikleri ve ArcFace'in marj (ceza) sistemleri ile zorlu koşullarda eğitilmiştir. 30 Epochluk (Toplamda 120 Epoch) eğitim sonucunda elde edilen `best_384.pth` modeli, temiz verilerle yapılan nihai testte **%58.04** doğruluk (Accuracy) ve **0.54** Güven Skoru (Confidence) ile projenin rekorunu kırmıştır.

## 4. Çoklu Ajan (Multi-Agent) Orkestrasyonu ve Karakterizasyon
Modern yazılım geliştirme pratikleri kapsamında yapay zeka ajanları (AI Agents) modüler bir ekosistem olarak yönetilmiş ve her birine `.md` uzantılı dosyalarla spesifik roller (karakterizasyon) atanmıştır:

* **Ana Kurallar Anayasası (`rules.md`):** Tüm ajanların uyması zorunlu olan temel standartlar dosyasıdır. Kodların spagetti koda dönüşmesini engellemek, DRY (Don't Repeat Yourself) ve KISS (Keep It Simple, Stupid) prensiplerine uymak, Türkçe açıklayıcı yorum satırları kullanmak bu dosyada zorunlu kılınmıştır.
* **Manager Agent (Yönetici Ajan):** Projenin genel mimarisini denetleyen, alt ajanlara (sub-agents) iş dağıtan ve MVP'nin baştan uca entegrasyonunu sağlayan ana orkestratör rolündedir.
* **Backend Ajanı (`backend-agent.md`):** NestJS uzmanı "Kıdemli Mimar" olarak karakterize edilmiştir. Görevi; Controller, Service ve Module ayrımlarını kusursuz yapmak, Python yapay zeka köprüsünü kurmak ve özellikler "Single Responsibility (SRP)" ve "Dependency Inversion (DIP)" gibi SOLID kurallarına tam uyumlu, genişletilebilir API'ler yazmaktır.
* **Frontend Ajanı (`frontend-agent.md`):** React ve TailwindCSS uzmanı UI/UX geliştiricisi olarak tanımlanmıştır. Bileşen tabanlı (component-based) bir yaklaşımla tasarımları bölmüş; dosya yükleme (FileUploader) ile sonuç gösterme (ResultCard) mantıklarını birbirinden tamamen izole ederek Clean Code standartlarına sadık kalmıştır.
* **Jüri ve Test Ajanı (`test-agent.md`):** Geliştirilen mimarinin ve kod bloklarının akademik denetimini yapan "Kalite Güvence (QA)" simülatörüdür. Kodların SOLID prensiplerine ne derece uyduğunu bağımsız bir gözle test etmiş, hata yönetimi akışlarını denetlemiş ve projenin resmi raporlamasına altlık oluşturmuştur.

## 5. Versiyon Kontrolü (Git) Krizinin Çözümü
Projenin GitHub'a push edilmesi sırasında 10.000'den fazla veri seti fotoğrafı ve devasa `.pth` (model) dosyalarının yüklenmeye çalışılması krizi yaşanmıştır. Kriz anında işlem durdurulmuş, `.gitignore` dosyası güncellenmiş ve `git rm -r --cached` komutları ile Git hafızası temizlenerek sadece hafif kaynak kodların (Source Code) depoya aktarılması sağlanmıştır.

## 6. Sonuç
Laboratuvar aşaması tamamlanan yapay zeka motoru, tasarlanan Full-Stack mimarinin ve alt ajanların kusursuz çalışması sayesinde ürünleştirilmiştir. Sistem şu an dışarıdan aldığı bir deniz kaplumbağası fotoğrafını 384x384 piksel formatına standardize edip ArcFace vektör uzayında tarayabilmekte, %58 doğrulukla kimlik tespiti yapıp sonucu ve güven oranını web arayüzünde canlı olarak sunabilmektedir.