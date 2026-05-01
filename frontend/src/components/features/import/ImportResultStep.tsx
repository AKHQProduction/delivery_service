import React from "react";
import { type ImportResult } from "../../../services/api/clientApi";
import { usePlatform } from "../../../platforms/usePlatform";

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
      <div className="flex items-center gap-3 rounded-md border border-emerald-100 bg-emerald-50 px-4 py-3 text-emerald-700">
        <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-emerald-100">
          <svg className="h-4 w-4 text-emerald-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>
        <p className="text-sm font-medium">Імпортовано: {result.imported}</p>
      </div>
      {result.skipped > 0 && result.error_file_id && (
        <div className="space-y-3 rounded-md border border-amber-200 bg-amber-50 px-4 py-3 text-amber-800">
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md bg-amber-100">
              <svg className="h-4 w-4 text-amber-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01M12 3a9 9 0 100 18 9 9 0 000-18z" />
              </svg>
            </div>
            <p className="text-sm font-medium">Пропущено: {result.skipped}</p>
          </div>
          <button
            type="button"
            onClick={handleDownloadErrors}
            className="flex w-full items-center justify-center gap-2 rounded-md bg-amber-100 py-2.5 text-sm font-medium text-amber-800 transition-colors hover:bg-amber-200"
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
