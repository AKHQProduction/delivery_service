import React from "react";

interface FormNavigationButtonsProps {
  currentStep: number;
  totalSteps: number;
  canProceed: boolean;
  onBack: () => void;
  onNext: () => void;
  onSubmit: () => void;
  submitLabel?: string;
  nextLabel?: string;
  backLabel?: string;
}

export const FormNavigationButtons: React.FC<FormNavigationButtonsProps> = ({
  currentStep,
  totalSteps,
  canProceed,
  onBack,
  onNext,
  onSubmit,
  submitLabel = "Створити",
  nextLabel = "Далі",
  backLabel = "Назад",
}) => {
  const isLastStep = currentStep === totalSteps;
  const isFirstStep = currentStep === 1;

  return (
    <div className="px-6 py-4 border-t border-gray-200 shrink-0 flex gap-3">
      {!isFirstStep && (
        <button
          onClick={onBack}
          type="button"
          className="flex-1 py-3 border-2 border-gray-300 rounded-xl font-bold text-gray-700 hover:bg-gray-50 transition-all"
        >
          {backLabel}
        </button>
      )}
      <button
        onClick={isLastStep ? onSubmit : onNext}
        disabled={!canProceed}
        type="button"
        className={`${isFirstStep ? 'w-full' : 'flex-1'} py-3 rounded-xl font-bold transition-all ${
          canProceed
            ? "bg-indigo-600 hover:bg-indigo-700 text-white"
            : "bg-gray-300 text-gray-500 cursor-not-allowed"
        }`}
      >
        {isLastStep ? submitLabel : nextLabel}
      </button>
    </div>
  );
};