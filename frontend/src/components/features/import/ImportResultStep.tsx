import React from "react";
import { type ImportResult } from "../../../services/api/clientApi";
import { usePlatform } from "../../../platforms/PlatformProvider";

interface ImportResultStepProps {
  result: ImportResult;
}

const getErrorReportUrl = (fileId: string): string => {
  const baseUrl = import.meta.env.VITE_API_URL;
  return `${baseUrl}/v1/clients/export/errors/${fileId}`;
};

export const ImportResultStep: React.FC<ImportResultStepProps> = ({ result }) => {
  const { files } = usePlatform();

  const handleDownloadErrors = () => {
    if (result.error_file_id) {
      const url = getErrorReportUrl(result.error_file_id);
      files.download(url, result.error_filename ?? "import_errors.xlsx");
    }
  };

  return (
    <div className="space-y-2">
      <div className="flex items-center gap-3 px-4 py-3 bg-green-50 border border-green-100 text-green-700 rounded-xl">
        <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center shrink-0">
          <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <p className="text-sm font-medium">Імпортовано: {result.imported}</p>
      </div>
      {result.skipped > 0 && result.error_file_id && (
        <div className="px-4 py-3 bg-amber-50 border border-amber-100 text-amber-700 rounded-xl space-y-3">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-full bg-amber-100 flex items-center justify-center shrink-0">
              <svg className="w-4 h-4 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01M12 3a9 9 0 100 18 9 9 0 000-18z" />
              </svg>
            </div>
            <p className="text-sm font-medium">Пропущено: {result.skipped}</p>
          </div>
          <button
            type="button"
            onClick={handleDownloadErrors}
            className="w-full py-2.5 bg-amber-100 hover:bg-amber-200 text-amber-800 font-medium text-sm rounded-lg transition-colors flex items-center justify-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            Завантажити звіт помилок
          </button>
        </div>
      )}
    </div>
  );
};
