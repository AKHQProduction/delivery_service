type ModalButtonsProps = {
  firstButtonText: string;
  handleEditClick: () => void;
  secondButtonText: string;
  onDelete: () => void;
};

export const ModalButtons = ({
  firstButtonText,
  handleEditClick,
  secondButtonText,
  onDelete,
}: ModalButtonsProps) => {
  return (
    <div className="flex gap-3 pt-4">
      <button
        onClick={handleEditClick}
        type="button"
        className="flex-1 py-4 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-2xl transition-colors"
      >
        {firstButtonText}
      </button>
      <button
        onClick={onDelete}
        type="button"
        className="flex-1 py-4 bg-red-50 hover:bg-red-100 text-red-600 font-semibold rounded-2xl transition-colors"
      >
        {secondButtonText}
      </button>
    </div>
  );
};
