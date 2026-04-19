import { useState } from "react";
import { generateOrdersPdfLink } from "../services/api/ordersApi";
import { usePlatform } from "../platforms/usePlatform";

type DocType = "ORDER_LIST" | "STATISTICS";
type RoutingMode = "NONE" | "OPTIMIZED";

interface PreviewPdfArgs {
  deliveryDateIso: string;
  timeSlotId?: string | null;
  docType?: DocType;
  routingMode?: RoutingMode;
}

export const useOrdersPdfPreview = (
  onError?: (message: string) => void,
) => {
  const { files } = usePlatform();
  const [loading, setLoading] = useState(false);

  const previewPdf = async ({
    deliveryDateIso,
    timeSlotId,
    docType = "ORDER_LIST",
    routingMode = "OPTIMIZED",
  }: PreviewPdfArgs) => {
    if (!deliveryDateIso || loading) return;
    setLoading(true);
    try {
      const { file_id } = await generateOrdersPdfLink(
        deliveryDateIso,
        docType,
        timeSlotId ?? undefined,
        routingMode,
      );
      const baseUrl = import.meta.env.VITE_API_URL;
      files.openLink(
        `${baseUrl}/v1/orders/export/pdf/download/${file_id}?inline=true`,
      );
    } catch {
      onError?.("Не вдалося сформувати документ");
    } finally {
      setLoading(false);
    }
  };

  return { previewPdf, loading };
};
