import React, { useState, useCallback } from 'react';
import FileUploader from './components/FileUploader';
import ResultCard from './components/ResultCard';
import InfoReport from './components/InfoReport';
import { predictImage } from './api/predict';

interface InferenceResult {
  turtleId: string | null;
  confidence: number;
  findings: string[];
  warnings: string[];
  ok: boolean;
}

const App: React.FC = () => {
  const [preview, setPreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<InferenceResult | null>(null);
  const [logs, setLogs] = useState<string[]>([]);

  const handleFile = useCallback(async (file: File) => {
    // Reset state
    const objectUrl = URL.createObjectURL(file);
    setPreview(objectUrl);
    setResult(null);
    setLogs(['[System] Görüntü analize hazırlanıyor...']);

    setLoading(true);
    try {
      setLogs((prev) => [...prev, '[API] Sunucuya yükleniyor...']);
      const response: InferenceResult = await predictImage(file);
      
      setResult(response);
      
      if (response.ok) {
        setLogs((prev) => [
          ...prev, 
          '[Model] Analiz başarıyla tamamlandı.',
          `[Result] Tahmin: ${response.turtleId || 'Bilinmiyor'}`,
          `[Confidence] %${(response.confidence * 100).toFixed(2)}`
        ]);
      } else {
        setLogs((prev) => [...prev, `[Warning] ${response.warnings.join(', ')}`]);
      }
    } catch (err: any) {
      setLogs((prev) => [...prev, `[Error] Beklenmeyen hata: ${err.message}`]);
    } finally {
      setLoading(false);
    }
  }, []);

  return (
    <div className="min-h-screen bg-[#0f172a] text-slate-200 font-sans selection:bg-emerald-500/30">
      {/* Background Decor */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-[10%] -left-[10%] w-[40%] h-[40%] bg-emerald-500/10 blur-[120px] rounded-full"></div>
        <div className="absolute -bottom-[10%] -right-[10%] w-[40%] h-[40%] bg-blue-500/10 blur-[120px] rounded-full"></div>
      </div>

      <div className="relative z-10 max-w-6xl mx-auto px-6 py-12">
        <header className="text-center mb-16">
          <div className="inline-block px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-medium mb-4 tracking-wider uppercase">
            Graduation Project • AI Research
          </div>
          <h1 className="text-5xl md:text-6xl font-extrabold tracking-tight text-white mb-6">
            SeaTurtle<span className="text-emerald-500">ID</span>
          </h1>
          <p className="text-lg text-slate-400 max-w-2xl mx-auto leading-relaxed">
            Derin Öğrenme ve ArcFace Metrik Öğrenme tabanlı, 367 farklı deniz kaplumbağasını 
            tanımlayabilen akademik araştırma aracı.
          </p>
        </header>

        <main className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Sol Panel: Upload */}
          <div className="lg:col-span-5 space-y-6">
            <div className="bg-slate-800/40 backdrop-blur-xl border border-slate-700/50 rounded-2xl p-6 shadow-2xl">
              <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <span className="w-2 h-6 bg-emerald-500 rounded-full"></span>
                Görüntü Yükleme
              </h2>
              <FileUploader onFile={handleFile} />
              
              {loading && (
                <div className="mt-6 flex flex-col items-center justify-center p-8 bg-slate-900/50 rounded-xl border border-slate-700/30">
                  <div className="w-10 h-10 border-4 border-emerald-500/20 border-t-emerald-500 rounded-full animate-spin mb-4"></div>
                  <p className="text-emerald-400 font-medium animate-pulse">Model Inference Devam Ediyor...</p>
                </div>
              )}
            </div>
          </div>

          {/* Sağ Panel: Results & Logs */}
          <div className="lg:col-span-7 space-y-6">
            <ResultCard 
              imageUrl={preview ?? undefined} 
              prediction={result?.turtleId ?? undefined} 
              confidence={result?.confidence} 
            />
            
            <InfoReport logs={logs} />
          </div>
        </main>

        <footer className="mt-24 pt-8 border-t border-slate-800/50 text-center">
          <p className="text-slate-500 text-sm italic">
            &copy; 2026 SeaTurtleID - Deep Learning Infrastructure
          </p>
        </footer>
      </div>
    </div>
  );
};

export default App;
