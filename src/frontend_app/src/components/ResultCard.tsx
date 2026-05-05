import React from 'react';

type Props = {
  imageUrl?: string;
  prediction?: string;
  confidence?: number;
};

export default function ResultCard({ imageUrl, prediction, confidence }: Props) {
  const hasResult = prediction !== undefined;

  return (
    <div className="bg-slate-800/40 backdrop-blur-xl border border-slate-700/50 rounded-2xl overflow-hidden shadow-2xl">
      <div className="p-6 border-b border-slate-700/50">
        <h2 className="text-xl font-bold text-white flex items-center gap-2">
          <span className="w-2 h-6 bg-blue-500 rounded-full"></span>
          Analiz Sonuçları
        </h2>
      </div>

      <div className="p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Image Preview */}
          <div className="aspect-square bg-slate-900/50 rounded-xl border border-slate-700/30 overflow-hidden flex items-center justify-center relative group">
            {imageUrl ? (
              <img src={imageUrl} alt="Analiz" className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105" />
            ) : (
              <div className="text-slate-600 text-center p-4">
                <svg className="w-12 h-12 mx-auto mb-2 opacity-20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <p className="text-sm font-medium">Görüntü Bekleniyor</p>
              </div>
            )}
          </div>

          {/* Metrics */}
          <div className="flex flex-col justify-center space-y-4">
            <div className={`p-4 rounded-xl border transition-all duration-300 ${hasResult ? 'bg-emerald-500/10 border-emerald-500/20' : 'bg-slate-900/30 border-slate-700/30'}`}>
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-widest block mb-1">Tahmin Edilen Sınıf</span>
              <span className={`text-2xl font-black ${hasResult ? 'text-emerald-400' : 'text-slate-600'}`}>
                {prediction ?? 'N/A'}
              </span>
            </div>

            <div className={`p-4 rounded-xl border transition-all duration-300 ${hasResult ? 'bg-blue-500/10 border-blue-500/20' : 'bg-slate-900/30 border-slate-700/30'}`}>
              <span className="text-xs font-semibold text-slate-500 uppercase tracking-widest block mb-1">Güven Oranı</span>
              <div className="flex items-end gap-2">
                <span className={`text-3xl font-black ${hasResult ? 'text-blue-400' : 'text-slate-600'}`}>
                  {confidence !== undefined ? `${(confidence * 100).toFixed(1)}%` : '0.0%'}
                </span>
                {hasResult && (
                  <div className="mb-1 w-full bg-slate-700 h-1.5 rounded-full overflow-hidden">
                    <div 
                      className="bg-blue-500 h-full rounded-full transition-all duration-1000 ease-out"
                      style={{ width: `${confidence * 100}%` }}
                    ></div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
