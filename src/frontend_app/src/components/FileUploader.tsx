import React, { useRef, useState } from 'react';

type Props = {
  onFile: (file: File) => void;
};

export default function FileUploader({ onFile }: Props) {
  const inputRef = useRef<HTMLInputElement | null>(null);
  const [isDragging, setIsDragging] = useState(false);

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onFile(e.dataTransfer.files[0]);
    }
  };

  const handleFile = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) onFile(e.target.files[0]);
  };

  return (
    <div
      onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
      className={`
        relative group cursor-pointer
        bg-slate-900/50 rounded-xl p-10 border-2 border-dashed 
        transition-all duration-300 ease-in-out
        flex flex-col items-center justify-center text-center
        ${isDragging ? 'border-emerald-500 bg-emerald-500/5' : 'border-slate-700 hover:border-slate-600'}
      `}
      onClick={() => inputRef.current?.click()}
    >
      <div className={`
        w-16 h-16 rounded-full flex items-center justify-center mb-4
        transition-all duration-300
        ${isDragging ? 'bg-emerald-500 text-white animate-bounce' : 'bg-slate-800 text-slate-400 group-hover:bg-slate-700 group-hover:text-emerald-400'}
      `}>
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4" />
        </svg>
      </div>
      
      <p className="text-lg font-semibold text-white mb-1">Görüntü Seçin</p>
      <p className="text-sm text-slate-500">veya dosyayı buraya sürükleyin</p>
      
      <div className="mt-6 flex gap-2">
        <span className="px-2 py-1 bg-slate-800 rounded text-[10px] font-bold text-slate-400 border border-slate-700 uppercase tracking-tight">JPG</span>
        <span className="px-2 py-1 bg-slate-800 rounded text-[10px] font-bold text-slate-400 border border-slate-700 uppercase tracking-tight">PNG</span>
        <span className="px-2 py-1 bg-slate-800 rounded text-[10px] font-bold text-slate-400 border border-slate-700 uppercase tracking-tight">WEBP</span>
      </div>

      <input ref={inputRef} type="file" accept="image/*" onChange={handleFile} className="hidden" />
    </div>
  );
}
