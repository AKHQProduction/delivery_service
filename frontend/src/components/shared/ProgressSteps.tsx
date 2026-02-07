import React from "react";

interface ProgressStepsProps {
  currentStep: number;
  totalSteps: number;
}

export const ProgressSteps: React.FC<ProgressStepsProps> = ({ currentStep, totalSteps }) => {
  return (
    <div className="px-6 py-6 shrink-0">
      <div className="flex items-center justify-between max-w-md mx-auto">
        {Array.from({ length: totalSteps }, (_, i) => i + 1).map((step, idx) => (
          <React.Fragment key={step}>
            <div
              className={`w-12 h-12 rounded-full flex items-center justify-center font-bold transition-all ${
                step === currentStep
                  ? "bg-indigo-600 text-white scale-110"
                  : step < currentStep
                    ? "bg-indigo-200 text-indigo-700"
                    : "bg-gray-200 text-gray-500"
              }`}
            >
              {step}
            </div>
            {idx < totalSteps - 1 && (
              <div
                className={`flex-1 h-1 mx-2 rounded transition-all ${
                  step < currentStep ? "bg-indigo-600" : "bg-gray-200"
                }`}
              />
            )}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
};
