import { usePlatform } from "../../platforms/PlatformProvider";
import { BottomModal } from "./BottomModal";
import { CenterModal } from "./CenterModal";

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
}

export const Modal: React.FC<ModalProps> = (props) => {
  const { type } = usePlatform();
  return type === "telegram" ? <BottomModal {...props} /> : <CenterModal {...props} />;
};
