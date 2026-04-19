import { usePlatform } from "../../platforms/usePlatform";
import { RightModal } from "./RightModal";
import { CenterDetailModal } from "./CenterDetailModal";

interface DetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
  size?: "xl" | "2xl" | "3xl" | "4xl" | "5xl";
}

export const DetailModal: React.FC<DetailModalProps> = ({ size, ...props }) => {
  const { type } = usePlatform();
  return type === "telegram" ? <RightModal {...props} /> : <CenterDetailModal {...props} size={size} />;
};
