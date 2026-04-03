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
        className="flex items-center gap-3 px-4 py-3 bg-indigo-50 border border-indigo-100 rounded-xl hover:bg-indigo-100 transition-colors group"
      >
        <div className="w-9 h-9 rounded-full bg-indigo-100 group-hover:bg-indigo-200 flex items-center justify-center shrink-0 transition-colors">
          <svg className="w-5 h-5 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
        </div>
        <div className="min-w-0">
          <p className="text-sm font-medium text-indigo-700">Завантажити шаблон</p>
          <p className="text-xs text-indigo-500">Google Sheets (.xlsx)</p>
        </div>
      </a>

      <div
        onClick={() => fileInputRef.current?.click()}
        onDrop={handleDrop}
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={(e) => { e.preventDefault(); setDragging(false); }}
        className={`relative border-2 border-dashed rounded-xl p-6 text-center cursor-pointer transition-colors ${
          dragging
            ? "border-indigo-400 bg-indigo-50"
            : file
              ? "border-indigo-300 bg-indigo-50"
              : "border-gray-200 bg-gray-50 hover:border-indigo-300 hover:bg-indigo-50/50"
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
            <div className="w-10 h-10 rounded-xl bg-green-100 flex items-center justify-center shrink-0">
              <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <div className="text-left min-w-0">
              <p className="text-sm font-medium text-gray-800 truncate">{file.name}</p>
              <p className="text-xs text-gray-500">{(file.size / 1024).toFixed(1)} KB</p>
            </div>
          </div>
        ) : (
          <>
            <div className="w-12 h-12 rounded-full bg-gray-100 flex items-center justify-center mx-auto mb-3">
              <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
              </svg>
            </div>
            <p className="text-sm font-medium text-gray-700">Натисніть або перетягніть файл</p>
            <p className="text-xs text-gray-400 mt-1">Підтримується лише .xlsx</p>
          </>
        )}
      </div>

      {error && (
        <div className="flex items-center gap-3 px-4 py-3 bg-red-50 border border-red-100 text-red-600 rounded-xl">
          <div className="w-8 h-8 rounded-full bg-red-100 flex items-center justify-center shrink-0">
            <svg className="w-4 h-4 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          <p className="text-sm font-medium">{error}</p>
        </div>
      )}
    </div>
  );
};
