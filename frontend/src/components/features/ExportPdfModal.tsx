import { useState, useEffect } from "react";
import { Modal } from "../modals/Modal";
import { DateInput } from "../shared/DateInput";
import { generateOrdersPdfLink } from "../../services/api/ordersApi";
import { getAllTimeSlots } from "../../services/api/settingsApi";
import { useUserShopStore } from "../../context/useUserShopStore";
import { usePlatform } from "../../platforms/PlatformProvider";

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

const getPrintUrl = (fileId: string): string => {
  const baseUrl = import.meta.env.VITE_API_URL;
  return `${baseUrl}/v1/orders/export/pdf/print/${fileId}`;
};

export const ExportPdfModal: React.FC<ExportPdfModalProps> = ({ isOpen, onClose }) => {
  const { files } = usePlatform();
  const [exportDate, setExportDate] = useState(() => {
    const today = new Date();
    return today.toISOString().split("T")[0];
  });
  const [exportError, setExportError] = useState(false);
  const [docType, setDocType] = useState<DocType>("ORDER_LIST");
  const [selectedTimeSlotId, setSelectedTimeSlotId] = useState("");
  const [routingMode, setRoutingMode] = useState<RoutingMode>("NONE");
  const [timeSlots, setTimeSlots] = useState<TimeSlot[]>([]);
  const [exporting, setExporting] = useState(false);

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

  const handlePrintPdf = async () => {
    if (!exportDate) {
      setExportError(true);
      return;
    }
    setExportError(false);
    setExporting(true);
    try {
      const { file_id } = await generateOrdersPdfLink(
        exportDate,
        docType,
        selectedTimeSlotId || undefined,
        routingMode,
      );
      const printUrl = getPrintUrl(file_id);

      files.openLink(printUrl);
    } catch {
      setExportError(true);
    } finally {
      setExporting(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Сформувати документ">
      <div className="space-y-4">
        {/* Date picker */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Дата доставки</label>
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
          <label className="block text-sm font-medium text-gray-700 mb-2">Тип документа</label>
          <div className="grid grid-cols-2 gap-2">
            <button
              type="button"
              onClick={() => setDocType("ORDER_LIST")}
              className={`px-4 py-3 rounded-xl font-medium text-sm transition-colors ${
                docType === "ORDER_LIST"
                  ? "bg-indigo-600 text-white"
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              }`}
            >
              Список замовлень
            </button>
            <button
              type="button"
              onClick={() => setDocType("STATISTICS")}
              className={`px-4 py-3 rounded-xl font-medium text-sm transition-colors ${
                docType === "STATISTICS"
                  ? "bg-indigo-600 text-white"
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              }`}
            >
              Статистика
            </button>
          </div>
        </div>

        {/* Time slot selector */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Часовий проміжок</label>
          <select
            title="Часовий слот"
            value={selectedTimeSlotId}
            onChange={(e) => setSelectedTimeSlotId(e.target.value)}
            className="w-full px-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
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
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Маршрутизація
              {!shopHasAddress && (
                <span className="text-xs text-gray-400 ml-1">(додайте адресу магазину)</span>
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
                  className={`px-3 py-3 rounded-xl font-medium text-sm transition-colors disabled:cursor-not-allowed ${
                    routingMode === option.value && shopHasAddress
                      ? "bg-indigo-600 text-white"
                      : "bg-gray-100 text-gray-700 hover:bg-gray-200 disabled:hover:bg-gray-100"
                  }`}
                >
                  {option.label}
                </button>
              ))}
            </div>
          </div>
        )}

        {exportError && <p className="text-red-500 text-sm text-center">Помилка формування документа</p>}

        {/* Action buttons */}
        <div className="flex gap-3 pt-2">
          <button
            type="button"
            onClick={handlePrintPdf}
            disabled={exporting}
            className="flex-1 py-3 bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold rounded-xl transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z"
              />
            </svg>
            Друк
          </button>
          <button
            type="button"
            onClick={handleExportPdf}
            disabled={exporting}
            className="flex-1 py-3 bg-linear-to-r from-amber-500 to-orange-500 hover:from-amber-600 hover:to-orange-600 text-white font-semibold rounded-xl transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
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
