import { useState } from "react";
import { Modal } from "../modals/Modal";
import {
  importClientsFromXlsx,
  previewImportXlsx,
  type ColumnMapping,
  type ImportResult,
  type PreviewResult,
} from "../../services/api/clientApi";
import { ProgressSteps } from "../shared/ProgressSteps";
import { UploadStep } from "./import/UploadStep";
import { ColumnMappingStep } from "./import/ColumnMappingStep";
import { ImportResultStep } from "./import/ImportResultStep";
import { autoMatchColumns, REQUIRED_SYSTEM_FIELDS } from "./import/constants";

interface ImportClientsModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export const ImportClientsModal: React.FC<ImportClientsModalProps> = ({ isOpen, onClose, onSuccess }) => {
  const [step, setStep] = useState<1 | 2 | 3>(1);
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState("");
  const [preview, setPreview] = useState<PreviewResult | null>(null);
  const [mapping, setMapping] = useState<ColumnMapping>({});
  const [firstRowIsHeader, setFirstRowIsHeader] = useState(true);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ImportResult | null>(null);

  const resetState = () => {
    setStep(1);
    setFile(null);
    setError("");
    setPreview(null);
    setMapping({});
    setFirstRowIsHeader(true);
    setLoading(false);
    setResult(null);
  };

  const handleClose = () => {
    resetState();
    onClose();
  };

  const isMappingValid = REQUIRED_SYSTEM_FIELDS.every((f) =>
    Object.values(mapping).includes(f),
  );

  const handlePreview = async () => {
    if (!file) return;
    setError("");
    setLoading(true);
    try {
      const data = await previewImportXlsx(file);
      setPreview(data);
      const autoMapping = autoMatchColumns(data.columns);
      setMapping(autoMapping);
      setStep(2);
    } catch (err: unknown) {
      if (err && typeof err === "object" && "response" in err) {
        const response = (err as { response: { status: number } }).response;
        if (response.status === 422) {
          setError("Невірний формат файлу. Підтримується лише .xlsx");
        } else {
          setError("Помилка завантаження. Спробуйте ще раз");
        }
      } else {
        setError("Помилка завантаження. Спробуйте ще раз");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleImport = async () => {
    if (!file || !isMappingValid) return;
    setError("");
    setLoading(true);
    try {
      const originalHeaders = firstRowIsHeader && preview
        ? preview.columns.map((c) => c.header ?? `Стовпець ${c.index}`)
        : undefined;

      const data = await importClientsFromXlsx(
        file,
        mapping,
        firstRowIsHeader,
        originalHeaders,
      );
      setResult(data);
      setStep(3);
      onSuccess();
    } catch (err: unknown) {
      if (err && typeof err === "object" && "response" in err) {
        const response = (err as { response: { status: number } }).response;
        if (response.status === 422) {
          setError("Невірний маппінг колонок");
        } else {
          setError("Помилка імпорту. Спробуйте ще раз");
        }
      } else {
        setError("Помилка імпорту. Спробуйте ще раз");
      }
    } finally {
      setLoading(false);
    }
  };

  const modalSize = step === 2 ? "3xl" as const : "md" as const;

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="Імпорт клієнтів" size={modalSize}>
      <div className="space-y-4 pb-4">
        {step < 3 && <ProgressSteps currentStep={step} totalSteps={2} />}

        {step === 1 && (
          <>
            <UploadStep
              file={file}
              onFileChange={setFile}
              error={error}
              onError={setError}
            />
            <button
              type="button"
              onClick={handlePreview}
              disabled={!file || loading}
              className="w-full py-3 bg-linear-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-white font-semibold rounded-xl transition-colors flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  Завантаження...
                </>
              ) : (
                "Далі"
              )}
            </button>
          </>
        )}

        {step === 2 && preview && (
          <>
            <ColumnMappingStep
              columns={preview.columns}
              mapping={mapping}
              onMappingChange={setMapping}
              firstRowIsHeader={firstRowIsHeader}
              onFirstRowIsHeaderChange={setFirstRowIsHeader}
              totalRows={preview.total_rows}
            />

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

            <div className="flex gap-3">
              <button
                type="button"
                onClick={() => { setStep(1); setError(""); }}
                className="flex-1 py-3 border border-gray-300 text-gray-700 font-semibold rounded-xl hover:bg-gray-50 transition-colors"
              >
                Назад
              </button>
              <button
                type="button"
                onClick={handleImport}
                disabled={!isMappingValid || loading}
                className="flex-1 py-3 bg-linear-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-white font-semibold rounded-xl transition-colors flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? (
                  <>
                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    Імпорт...
                  </>
                ) : (
                  "Імпортувати"
                )}
              </button>
            </div>
          </>
        )}

        {step === 3 && result && (
          <>
            <ImportResultStep result={result} />
            <button
              type="button"
              onClick={handleClose}
              className="w-full py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-xl transition-colors"
            >
              Закрити
            </button>
          </>
        )}
      </div>
    </Modal>
  );
};
