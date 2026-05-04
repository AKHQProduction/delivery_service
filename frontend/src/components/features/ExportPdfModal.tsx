import { useState, useEffect } from "react";
import { Modal } from "../modals/Modal";
import { DateInput } from "../shared/DateInput";
import { generateOrdersPdfLink } from "../../services/api/ordersApi";
import { getAllTimeSlots } from "../../services/api/settingsApi";
import { useUserShopStore } from "../../context/useUserShopStore";
import { usePlatform } from "../../platforms/usePlatform";
import { useOrdersPdfPreview } from "../../hooks/useOrdersPdfPreview";
import { formatLocalDateKey } from "../../utils/dateUtils";

type DocType = "ORDER_LIST" | "STATISTICS";
type RoutingMode = "NONE" | "OPTIMIZED";

interface TimeSlot {
  time_slot_id: string;
  start_time: string;
  end_time: string;
  label?: string;
}

interface ExportPdfModalProps {
  isOpen: boolean;
  onClose: () => void;
}

const getDownloadUrl = (fileId: string): string => {
  const baseUrl = import.meta.env.VITE_API_URL;
  return `${baseUrl}/v1/orders/export/pdf/download/${fileId}`;
};

export const ExportPdfModal: React.FC<ExportPdfModalProps> = ({ isOpen, onClose }) => {
  const { files } = usePlatform();
  const currentDate = useUserShopStore((s) => s.currentDate);
  const todayKey = currentDate ?? formatLocalDateKey();
  const [exportDate, setExportDate] = useState(() => {
    return todayKey;
  });
  const [exportError, setExportError] = useState(false);
  const [docType, setDocType] = useState<DocType>("ORDER_LIST");
  const [selectedTimeSlotId, setSelectedTimeSlotId] = useState("");
  const [routingMode, setRoutingMode] = useState<RoutingMode>("NONE");
  const [timeSlots, setTimeSlots] = useState<TimeSlot[]>([]);
  const [exporting, setExporting] = useState(false);

  const { previewPdf, loading: previewLoading } = useOrdersPdfPreview(
    () => setExportError(true),
  );

  const shop = useUserShopStore((s) => s.shop);
  const shopHasAddress = !!(shop?.street && shop?.house);

  useEffect(() => {
    if (!isOpen) return;
    getAllTimeSlots()
      .then((data) => setTimeSlots(data as TimeSlot[]))
      .catch(() => console.error("Failed to fetch time slots"));
  }, [isOpen]);

  const handleExportPdf = async () => {
    if (!exportDate) {
      setExportError(true);
      return;
    }
    setExportError(false);
    setExporting(true);
    try {
      const { file_id, filename } = await generateOrdersPdfLink(
        exportDate,
        docType,
        selectedTimeSlotId || undefined,
        routingMode,
      );
      const downloadUrl = getDownloadUrl(file_id);

      files.download(downloadUrl, filename);
    } catch {
      setExportError(true);
    } finally {
      setExporting(false);
    }
  };

  const handlePreviewPdf = () => {
    if (!exportDate) {
      setExportError(true);
      return;
    }
    setExportError(false);
    previewPdf({
      deliveryDateIso: exportDate,
      timeSlotId: selectedTimeSlotId || undefined,
      docType,
      routingMode,
    });
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Сформувати документ">
      <div className="space-y-4 pb-1">
        {/* Date picker */}
        <div>
          <label className="mb-2 block text-sm font-medium text-slate-700">Дата доставки</label>
          <DateInput
            title="export date"
            value={exportDate}
            onChange={(value) => {
              setExportDate(value);
              setExportError(false);
            }}
            error={exportError}
          />
        </div>

        {/* Doc type selector */}
        <div>
          <label className="mb-2 block text-sm font-medium text-slate-700">Тип документа</label>
          <div className="grid grid-cols-2 gap-2">
            <button
              type="button"
              onClick={() => setDocType("ORDER_LIST")}
              className={`rounded-md px-4 py-3 text-sm font-medium transition-colors ${
                docType === "ORDER_LIST"
                  ? "bg-blue-600 text-white"
                  : "bg-slate-100 text-slate-700 hover:bg-slate-200"
              }`}
            >
              Список замовлень
            </button>
            <button
              type="button"
              onClick={() => setDocType("STATISTICS")}
              className={`rounded-md px-4 py-3 text-sm font-medium transition-colors ${
                docType === "STATISTICS"
                  ? "bg-blue-600 text-white"
                  : "bg-slate-100 text-slate-700 hover:bg-slate-200"
              }`}
            >
              Статистика
            </button>
          </div>
        </div>

        {/* Time slot selector */}
        <div>
          <label className="mb-2 block text-sm font-medium text-slate-700">Часовий проміжок</label>
          <select
            title="Часовий слот"
            value={selectedTimeSlotId}
            onChange={(e) => setSelectedTimeSlotId(e.target.value)}
            className="h-12 w-full rounded-md border border-slate-300 bg-white px-4 text-sm font-medium text-slate-950 focus:border-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-100"
          >
            <option value="">Усі проміжки</option>
            {timeSlots.map((slot) => (
              <option key={slot.time_slot_id} value={slot.time_slot_id}>
                {slot.label || `${slot.start_time} - ${slot.end_time}`}
              </option>
            ))}
          </select>
        </div>

        {/* Routing mode selector — visible for ORDER_LIST, disabled without shop address */}
        {docType === "ORDER_LIST" && (
          <div className={!shopHasAddress ? "opacity-50" : ""}>
            <label className="mb-2 block text-sm font-medium text-slate-700">
              Маршрутизація
              {!shopHasAddress && (
                <span className="ml-1 text-xs text-slate-400">(додайте адресу магазину)</span>
              )}
            </label>
            <div className="grid grid-cols-2 gap-2">
              {([
                { value: "NONE", label: "Без" },
                { value: "OPTIMIZED", label: "Оптимальний" },
              ] as const).map((option) => (
                <button
                  key={option.value}
                  type="button"
                  disabled={!shopHasAddress}
                  onClick={() => setRoutingMode(option.value)}
                  className={`rounded-md px-3 py-3 text-sm font-medium transition-colors disabled:cursor-not-allowed ${
                    routingMode === option.value && shopHasAddress
                      ? "bg-blue-600 text-white"
                      : "bg-slate-100 text-slate-700 hover:bg-slate-200 disabled:hover:bg-slate-100"
                  }`}
                >
                  {option.label}
                </button>
              ))}
            </div>
          </div>
        )}

        {exportError && (
          <div className="rounded-md border border-red-100 bg-red-50 px-3 py-2 text-sm font-medium text-red-700">
            Помилка формування документа
          </div>
        )}

        {/* Action buttons */}
        <div className="flex gap-3 border-t border-slate-200 pt-4">
          <button
            type="button"
            onClick={handlePreviewPdf}
            disabled={exporting || previewLoading}
            className="flex flex-1 items-center justify-center gap-2 rounded-md bg-slate-100 py-3 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-200 disabled:opacity-50"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
              />
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"
              />
            </svg>
            Переглянути
          </button>
          <button
            type="button"
            onClick={handleExportPdf}
            disabled={exporting}
            className="flex flex-1 items-center justify-center gap-2 rounded-md bg-blue-600 py-3 text-sm font-medium text-white transition-colors hover:bg-blue-700 disabled:opacity-50"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
              />
            </svg>
            {exporting ? "Завантаження..." : "Завантажити"}
          </button>
        </div>
      </div>
    </Modal>
  );
};
