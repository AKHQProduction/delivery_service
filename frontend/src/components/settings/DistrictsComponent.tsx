import { useState } from "react";
import {
  useDistrictsSettings,
  type District,
} from "../../hooks/settings/useDistrictsSettings";

interface NewDistrict {
  id: string;
  name: string;
  isNew: boolean;
}

export const DistrictsComponent = () => {
  const { districts, addDistrict, updateDistrictById, deleteDistrictById } =
    useDistrictsSettings();
  const [editedDistricts, setEditedDistricts] = useState<
    Record<string, Partial<District>>
  >({});
  const [newDistricts, setNewDistricts] = useState<NewDistrict[]>([]);

  const handleFieldChange = (districtId: string, value: string) => {
    setEditedDistricts((prev) => {
      const originalDistrict = districts?.find(
        (d) => d?.district_id === districtId
      );
      return {
        ...prev,
        [districtId]: {
          ...originalDistrict,
          ...prev[districtId],
          name: value,
        },
      };
    });
  };

  const handleNewDistrictChange = (tempId: string, value: string) => {
    setNewDistricts((prev) =>
      prev.map((district) =>
        district.id === tempId ? { ...district, name: value } : district
      )
    );
  };

  const handleSaveExisting = async (districtId: string) => {
    try {
      const changes = editedDistricts[districtId];
      if (changes?.name) {
        await updateDistrictById(districtId, changes.name);
        setEditedDistricts((prev) => {
          const updated = { ...prev };
          delete updated[districtId];
          return updated;
        });
      }
    } catch (error) {
      console.error("Error saving changes:", error);
    }
  };

  const handleSaveNew = async (tempId: string) => {
    try {
      const newDistrict = newDistricts.find((d) => d.id === tempId);
      if (newDistrict && newDistrict.name.trim()) {
        await addDistrict(newDistrict.name);
        setNewDistricts((prev) => prev.filter((d) => d.id !== tempId));
      }
    } catch (error) {
      console.error("Error creating district:", error);
    }
  };

  const handleDeleteNew = (tempId: string) => {
    setNewDistricts((prev) => prev.filter((d) => d.id !== tempId));
  };

  const handleAddNewDistrict = () => {
    const tempId = `temp-${Date.now()}`;
    setNewDistricts((prev) => [
      ...prev,
      {
        id: tempId,
        name: "",
        isNew: true,
      },
    ]);
  };

  const getDistrictValue = (district: District) => {
    const edited = editedDistricts[district.district_id];
    if (edited && "name" in edited) {
      return edited.name;
    }
    return district.name;
  };

  const isDistrictEdited = (districtId: string) => {
    const edited = editedDistricts[districtId];
    if (!edited) return false;

    const originalDistrict = districts?.find((d) => d?.district_id === districtId);
    const originalName = originalDistrict?.name || "";
    const editedName = edited.name || "";

    // Only show as edited if value differs from original AND is not empty
    return editedName !== originalName && editedName.trim() !== "";
  };

  const isNewDistrictValid = (district: NewDistrict) => {
    return district.name.trim() !== "";
  };

  const validDistricts = (districts || []).filter(
    (district): district is District =>
      district !== null &&
      district !== undefined &&
      district.district_id !== null
  );

  return (
    <div className="bg-white rounded-xl shadow-sm p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-gray-900">Райони доставки</h2>
      </div>

      <div className="space-y-3">
        {validDistricts.map((district) => {
          const currentName = getDistrictValue(district) || "";

          return (
            <div key={district.district_id} className="flex items-center gap-2">
              <input
                type="text"
                placeholder="Назва району"
                value={currentName}
                onChange={(e) =>
                  handleFieldChange(district.district_id, e.target.value)
                }
                className="flex-1 min-w-0 px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />

              {isDistrictEdited(district.district_id) ? (
                <button
                  onClick={() => handleSaveExisting(district.district_id)}
                  className="w-10 h-10 flex-shrink-0 flex items-center justify-center rounded-xl bg-green-500 hover:bg-green-600 text-white transition-colors"
                  aria-label="Зберегти район"
                >
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    strokeWidth={2}
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                </button>
              ) : (
                <button
                  onClick={async () => {
                    try {
                      await deleteDistrictById(district.district_id);
                    } catch (error) {
                      console.error("Error deleting district:", error);
                    }
                  }}
                  className="w-10 h-10 flex-shrink-0 flex items-center justify-center rounded-xl hover:bg-red-50 text-red-500 transition-colors"
                  aria-label="Видалити район"
                >
                  <svg
                    className="w-5 h-5"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                    strokeWidth={2}
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                    />
                  </svg>
                </button>
              )}
            </div>
          );
        })}

        {newDistricts.map((district) => (
          <div key={district.id} className="flex items-center gap-2">
            <input
              type="text"
              placeholder="Назва району"
              value={district.name}
              onChange={(e) =>
                handleNewDistrictChange(district.id, e.target.value)
              }
              className="flex-1 min-w-0 px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
            <button
              onClick={() => handleSaveNew(district.id)}
              disabled={!isNewDistrictValid(district)}
              className={`w-10 h-10 flex-shrink-0 flex items-center justify-center rounded-xl transition-colors ${
                isNewDistrictValid(district)
                  ? "bg-green-500 hover:bg-green-600 text-white"
                  : "bg-gray-200 text-gray-400 cursor-not-allowed"
              }`}
              aria-label="Зберегти новий район"
            >
              <svg
                className="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                strokeWidth={2}
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M5 13l4 4L19 7"
                />
              </svg>
            </button>
            <button
              onClick={() => handleDeleteNew(district.id)}
              className="w-10 h-10 flex-shrink-0 flex items-center justify-center rounded-xl hover:bg-red-200 bg-red-100 text-red-500 transition-colors"
              aria-label="Скасувати"
            >
              <svg
                className="w-5 h-5"
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
        ))}

        {validDistricts.length === 0 && newDistricts.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            <p>Райони доставки не додані</p>
            <p className="text-sm mt-1">
              Натисніть "+ Додати район" щоб створити новий
            </p>
          </div>
        )}

        <button
          onClick={handleAddNewDistrict}
          className="text-indigo-600 hover:text-indigo-700 text-sm font-medium transition-colors"
        >
          + Додати район
        </button>
      </div>
    </div>
  );
};
