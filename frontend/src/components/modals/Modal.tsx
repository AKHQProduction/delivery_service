import { usePlatform } from "../../platforms/usePlatform";
import { BottomModal } from "./BottomModal";
import { CenterModal } from "./CenterModal";

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  size?: "md" | "lg" | "xl" | "2xl" | "3xl" | "4xl" | "5xl";
}

export const Modal: React.FC<ModalProps> = ({ size, ...rest }) => {
  const { type } = usePlatform();
  return type === "telegram" ? <BottomModal {...rest} /> : <CenterModal {...rest} size={size} />;
};
