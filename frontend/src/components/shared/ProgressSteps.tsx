import React from "react";

interface ProgressStepsProps {
  currentStep: number;
  totalSteps: number;
}

export const ProgressSteps: React.FC<ProgressStepsProps> = ({ currentStep, totalSteps }) => {
  return (
    <div className="shrink-0 px-2 py-3">
      <div className="flex items-center justify-between max-w-md mx-auto">
        {Array.from({ length: totalSteps }, (_, i) => i + 1).map((step, idx) => (
          <React.Fragment key={step}>
            <div
              className={`flex h-9 w-9 items-center justify-center rounded-md text-sm font-semibold transition-all ${
                step === currentStep
                  ? "bg-blue-600 text-white"
                  : step < currentStep
                    ? "bg-blue-100 text-blue-700"
                    : "bg-slate-100 text-slate-500"
              }`}
            >
              {step}
            </div>
            {idx < totalSteps - 1 && (
              <div
                className={`mx-2 h-px flex-1 rounded transition-all ${
                  step < currentStep ? "bg-blue-600" : "bg-slate-200"
                }`}
              />
            )}
          </React.Fragment>
        ))}
      </div>
    </div>
  );
};
