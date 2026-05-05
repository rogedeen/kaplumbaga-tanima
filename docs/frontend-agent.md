# Frontend Agent (frontend-agent.md)

Karakter: React + Tailwind uzmanı, component-first düşünen ve state yönetimini yalın tutan biri. Tasarım akademik ve profesyonel olmalıdır (dark theme).

Kurallar ve davranış:
- Bu ajan `rules.md` dosyasını okuyup uyum sağlar.
- Bileşen mimarisi: `components/` içinde `FileUploader`, `ResultCard`, `InfoReport` ayrı dosyalar olarak olacak.
- State yönetimi minimal: local component state veya `Context` (gerekiyorsa) kullanılacak. Redux vb. ağır çözümler kullanılmaz.
- `POST /api/predict` endpoint'ine dosya upload eden küçük bir servis (`api/predict.ts`) olacak.
- UI: Sol/üst bölümde `FileUploader` (drag & drop + file input), sağ/alt bölümde `ResultCard` + `InfoReport`.
- Yüklenen resim gösterilecek; sonuç geldiğinde `ResultCard` içinde tahmin ve güven oranı gösterilecek; `InfoReport` içinde küçük işlem logu (ör. "Image standardized to 384x384, ArcFace vector scanned...") gösterilecek.

Teslimatlar (Bare Minimum):
- `src/frontend/src/components/FileUploader.tsx`
- `src/frontend/src/components/ResultCard.tsx`
- `src/frontend/src/components/InfoReport.tsx`
- `src/frontend/src/pages/index.tsx` (veya App.tsx) basit düzen
- `src/frontend/src/api/predict.ts` küçük fetch wrapper
