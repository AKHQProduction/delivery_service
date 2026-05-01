import React, { useRef } from "react";

interface UploadStepProps {
  file: File | null;
  onFileChange: (file: File | null) => void;
  error: string;
  onError: (error: string) => void;
}

export const UploadStep: React.FC<UploadStepProps> = ({ file, onFileChange, error, onError }) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [dragging, setDragging] = React.useState(false);

  const validateAndSetFile = (selected: File) => {
    onError("");
    if (!selected.name.endsWith(".xlsx")) {
      onError("Підтримується лише формат .xlsx");
      return;
    }
    onFileChange(selected);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0];
    if (!selected) {
      onFileChange(null);
      return;
    }
    validateAndSetFile(selected);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped) {
      validateAndSetFile(dropped);
    }
  };

  return (
    <div className="space-y-4">
      <a
        href="https://docs.google.com/spreadsheets/d/1hoWFYZpfd8rlt3oDpfMLQpdPtQQeCStnxUjeyzyk-rc/edit?gid=814068555#gid=814068555"
        target="_blank"
        rel="noopener noreferrer"
        className="group flex items-center gap-3 rounded-md border border-blue-100 bg-blue-50 px-4 py-3 transition-colors hover:bg-blue-100"
      >
        <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-blue-100 transition-colors group-hover:bg-blue-200">
          <svg className="h-5 w-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
        </div>
        <div className="min-w-0">
          <p className="text-sm font-medium text-blue-700">Завантажити шаблон</p>
          <p className="text-xs text-blue-500">Google Sheets (.xlsx)</p>
        </div>
      </a>

      <div
        onClick={() => fileInputRef.current?.click()}
        onDrop={handleDrop}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={(e) => { e.preventDefault(); setDragging(false); }}
        className={`relative cursor-pointer rounded-md border-2 border-dashed p-6 text-center transition-colors ${
          dragging
            ? "border-blue-400 bg-blue-50"
            : file
              ? "border-blue-300 bg-blue-50"
              : "border-slate-200 bg-slate-50 hover:border-blue-300 hover:bg-blue-50/50"
        }`}
      >
        <input
          title="import file"
          ref={fileInputRef}
          type="file"
          accept=".xlsx"
          onChange={handleFileChange}
          className="hidden"
        />
        {file ? (
          <div className="flex items-center justify-center gap-3">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-md bg-emerald-100">
              <svg className="h-5 w-5 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <div className="text-left min-w-0">
              <p className="truncate text-sm font-medium text-slate-900">{file.name}</p>
              <p className="text-xs text-slate-500">{(file.size / 1024).toFixed(1)} KB</p>
            </div>
          </div>
        ) : (
          <>
            <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-md bg-slate-100">
              <svg className="h-6 w-6 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
              </svg>
            </div>
            <p className="text-sm font-medium text-slate-700">Натисніть або перетягніть файл</p>
            <p className="mt-1 text-xs text-slate-400">Підтримується лише .xlsx</p>
          </>
        )}
      </div>

      {error && (
        <div className="flex items-center gap-3 rounded-md border border-red-100 bg-red-50 px-4 py-3 text-red-600">
          <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-red-100">
            <svg className="h-4 w-4 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          <p className="text-sm font-medium">{error}</p>
        </div>
      )}
    </div>
  );
};
