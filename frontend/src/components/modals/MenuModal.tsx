import { useEffect, useState } from "react";
import { createPortal } from "react-dom";
import { useTelegram } from "../../hooks/useTelegram";
import { useTGSettings } from "../../hooks/settings/useTGSettings";
import { TimeSlotsComponent } from "../features/settings/TimeSlotsComponent";

export const MenuModal = () => {
  const { isTGWebApp, initDataTG } = useTelegram();
  const { settings, updateSetting } = useTGSettings();
  const [isOpen, setIsOpen] = useState(false);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    if (!isTGWebApp || !initDataTG) return;

    const handleSettingsClick = () => {
      setIsOpen(true);
    };

    initDataTG.SettingsButton.onClick(handleSettingsClick);
    initDataTG.SettingsButton.show();

    return () => {
      initDataTG.SettingsButton.offClick(handleSettingsClick);
      initDataTG.SettingsButton.hide();
    };
  }, [isTGWebApp, initDataTG]);

  useEffect(() => {
    if (isOpen) {
      setIsVisible(true);
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "unset";
    }
    return () => {
      document.body.style.overflow = "unset";
    };
  }, [isOpen]);

  const handleClose = () => {
    setIsVisible(false);
    setTimeout(() => setIsOpen(false), 300);
  };

  if (!isOpen) return null;

  const modalContent = (
    <>
      <div
        className={`fixed inset-0 bg-black transition-opacity duration-300 z-9998 ${
          isVisible ? "opacity-50" : "opacity-0"
        }`}
        onClick={handleClose}
      />

      <div
        className={`fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-white rounded-2xl shadow-2xl transition-all duration-300 z-9999 w-[90%] max-w-md max-h-[80vh] flex flex-col ${
          isVisible ? "opacity-100 scale-100" : "opacity-0 scale-95"
        }`}
      >
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 shrink-0">
          <h2 className="text-xl font-bold">Налаштування</h2>
          <button
            onClick={handleClose}
            className="w-8 h-8 flex items-center justify-center rounded-full hover:bg-gray-100 transition-colors"
            aria-label="Close modal"
          >
            <svg
              className="w-5 h-5 text-gray-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              strokeWidth={2}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        <div className="px-6 py-4 overflow-y-auto flex-1">
          <div className="space-y-6">
            {/* Fullscreen Section */}
            <div className="pb-4 border-b border-gray-100">
              <h3 className="text-lg font-semibold mb-4 text-gray-800">
                Повноекранний режим
              </h3>
              <label className="flex items-center justify-between cursor-pointer">
                <span className="text-gray-700">На весь екран</span>
                <div className="relative">
                  <input
                    type="checkbox"
                    className="sr-only peer"
                    checked={settings.fullscreen}
                    onChange={(e) =>
                      updateSetting("fullscreen", e.target.checked)
                    }
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-500"></div>
                </div>
              </label>
            </div>

            {/* Timeslots Section */}
            <TimeSlotsComponent />
          </div>
        </div>
      </div>
    </>
  );

  return createPortal(modalContent, document.body);
};
