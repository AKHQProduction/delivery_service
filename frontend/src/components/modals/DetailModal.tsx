import { usePlatform } from "../../platforms/PlatformProvider";
import { RightModal } from "./RightModal";
import { CenterDetailModal } from "./CenterDetailModal";

interface DetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  children: React.ReactNode;
}

export const DetailModal: React.FC<DetailModalProps> = (props) => {
  const { type } = usePlatform();
  return type === "telegram" ? <RightModal {...props} /> : <CenterDetailModal {...props} />;
};
