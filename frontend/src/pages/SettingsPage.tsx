import { PageHeader } from "../components/ui/PageHeader";
import { useTGSettings } from "../hooks/settings/useTGSettings";

export const SettingsPage = () => {
  const { settings, updateSetting } = useTGSettings();

  return (
    <div className="min-h-screen bg-gray-50 lg:bg-white">
      <PageHeader title="Налаштування" />

      <div className="px-6 pb-24 lg:pb-8 lg:px-8">
        <div className="space-y-6 mt-4">
          {/* Fullscreen Section */}
          <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
            <h3 className="text-lg font-semibold mb-4 text-gray-800">Повноекранний режим</h3>
            <label className="flex items-center justify-between cursor-pointer">
              <span className="text-gray-700">На весь екран</span>
              <div className="relative">
                <input
                  type="checkbox"
                  className="sr-only peer"
                  checked={settings.fullscreen}
                  onChange={(e) => updateSetting("fullscreen", e.target.checked)}
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-500"></div>
              </div>
            </label>
          </div>
        </div>
      </div>
    </div>
  );
};
