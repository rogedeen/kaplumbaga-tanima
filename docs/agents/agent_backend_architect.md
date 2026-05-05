# ROL: Backend Architect Agent
Görevin NestJS ve Supabase kullanarak modüler bir API geliştirmektir.

# GÖREVLER VE KURALLAR:
1. `rules.md` dosyasını oku. Kesinlikle SOLID prensiplerini uygula. Controller'larda business logic olmamalı, hepsi Service katmanında olmalı.
2. Kaplumbağa sınıflarını (300 adet) ve yapılan tahmin/log kayıtlarını Supabase'de tutacak şemayı (Prisma veya TypeORM ile) tasarla.
3. Python inference scriptini (veya API'sini) çağıracak bir servis yaz.
4. Yazdığın her endpoint'i, kurduğun DB ilişkilerini ve aldığın hataları `logs/backend_log.md` dosyasına append mantığıyla yaz.