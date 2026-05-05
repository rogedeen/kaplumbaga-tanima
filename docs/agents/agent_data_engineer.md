# GÜNCEL VERİ İZOLASYON KURALI:
1. `wildlife-datasets` kütüphanesinden `SeaTurtleIDHeads` verisini çektikten sonra, fotoğrafları say. 
2. Yeterli veriye sahip kaplumbağaları (Örn: minimum 5 fotoğrafı olanları) filtrele.
3. Her kaplumbağa sınıfı için **dinamik %80/%20** ayrımı yap (Örn: 10 foto varsa 8 Train, 2 Test).
4. Verileri fiziksel olarak `/dataset/train/` ve `/dataset/test/` klasörlerine kopyala/taşı. Hiçbir test fotoğrafı train klasörüne sızmamalıdır (Data Leakage kesinlikle yasaktır).
5. İşlemin sonunda `logs/dataset_split_report.md` adında bir rapor oluştur. Bu raporda: "t402: Toplam 10 foto. 8'i Train'e, 2'si Test'e ayrıldı" şeklinde şeffaf bir döküm ver.