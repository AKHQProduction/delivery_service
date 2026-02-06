import { useState } from "react";
import { useTimeSlotsSettings } from "../../hooks/settings/useTimeSlotsSettings";
import { TimeInput } from "../ui/TimeInput";

interface NewSlot {
  id: string;
  label: string;
  start_time: string;
  end_time: string;
  isNew: boolean;
}

interface TimeSlot {
  time_slot_id: string;
  start_time: string;
  end_time: string;
  label: string;
}

export const TimeSlotsComponent = () => {
  const { timeSlots, updateTimeSlotById, addTimeSlot, deleteTimeSlotById } =
    useTimeSlotsSettings();
  const [editedSlots, setEditedSlots] = useState<
    Record<string, Partial<TimeSlot>>
  >({});
  const [newSlots, setNewSlots] = useState<NewSlot[]>([]);

  const handleFieldChange = (
    slotId: string,
    field: "label" | "start_time" | "end_time",
    value: string | Date,
  ) => {
    setEditedSlots((prev) => {
      const originalSlot = timeSlots?.find((s) => s?.time_slot_id === slotId);
      return {
        ...prev,
        [slotId]: {
          ...originalSlot,
          ...prev[slotId],
          [field]: value,
        },
      };
    });
  };

  const handleNewSlotChange = (
    tempId: string,
    field: "label" | "start_time" | "end_time",
    value: string,
  ) => {
    setNewSlots((prev) =>
      prev.map((slot) =>
        slot.id === tempId ? { ...slot, [field]: value } : slot,
      ),
    );
  };

  const parseTimeToDate = (timeString: string): Date => {
    if (/^\d{2}:\d{2}:\d{2}$/.test(timeString)) {
      const [hours, minutes, seconds] = timeString.split(":");
      const date = new Date();
      date.setHours(parseInt(hours), parseInt(minutes), parseInt(seconds), 0);
      return date;
    }

    if (/^\d{2}:\d{2}$/.test(timeString)) {
      const [hours, minutes] = timeString.split(":");
      const date = new Date();
      date.setHours(parseInt(hours), parseInt(minutes), 0, 0);
      return date;
    }

    return new Date();
  };

  const handleSaveExisting = async (slotId: string) => {
    try {
      const changes = editedSlots[slotId];
      const originalSlot = timeSlots?.find((s) => s?.time_slot_id === slotId);

      if (originalSlot && changes) {
        const startTime = parseTimeToDate(
          changes.start_time || originalSlot.start_time,
        );

        const endTime = parseTimeToDate(
          changes.end_time || originalSlot.end_time,
        );

        await updateTimeSlotById(
          slotId,
          startTime,
          endTime,
          changes.label !== undefined ? changes.label : originalSlot.label,
        );

        setEditedSlots((prev) => {
          const updated = { ...prev };
          delete updated[slotId];
          return updated;
        });
      }
    } catch (error) {
      console.error("Error saving changes:", error);
    }
  };

  const handleSaveNew = async (tempId: string) => {
    try {
      const newSlot = newSlots.find((s) => s.id === tempId);
      if (newSlot) {
        const [startHours, startMinutes] = newSlot.start_time.split(":");
        const [endHours, endMinutes] = newSlot.end_time.split(":");

        const startDate = new Date();
        startDate.setHours(parseInt(startHours), parseInt(startMinutes), 0, 0);

        const endDate = new Date();
        endDate.setHours(parseInt(endHours), parseInt(endMinutes), 0, 0);

        await addTimeSlot(startDate, endDate, newSlot.label);
        setNewSlots((prev) => prev.filter((s) => s.id !== tempId));
      }
    } catch (error) {
      console.error("Error creating timeslot:", error);
    }
  };

  const handleDeleteNew = (tempId: string) => {
    setNewSlots((prev) => prev.filter((s) => s.id !== tempId));
  };

  const handleAddNewSlot = () => {
    const tempId = `temp-${Date.now()}`;
    setNewSlots((prev) => [
      ...prev,
      {
        id: tempId,
        label: "",
        start_time: "",
        end_time: "",
        isNew: true,
      },
    ]);
  };

  const formatTimeValue = (timeString: string): string => {
    if (!timeString) return "";

    if (/^\d{2}:\d{2}$/.test(timeString)) {
      return timeString;
    }

    if (/^\d{2}:\d{2}:\d{2}$/.test(timeString)) {
      return timeString.slice(0, 5);
    }

    return "";
  };

  const getSlotValue = (slot: TimeSlot, field: keyof TimeSlot) => {
    const edited = editedSlots[slot.time_slot_id];

    if (edited && field in edited) {
      const value = edited[field as keyof typeof edited];

      if (value && typeof value === "object" && "toTimeString" in value) {
        return (value as Date).toTimeString().slice(0, 5);
      }
      return value;
    }

    return slot[field];
  };
  const isSlotEdited = (slotId: string) => {
    return editedSlots[slotId] !== undefined;
  };

  const isNewSlotValid = (slot: NewSlot) => {
    return slot.start_time !== "" && slot.end_time !== "";
  };

  // Filter out null/undefined slots and provide safe defaults
  const validTimeSlots = (timeSlots || []).filter(
    (slot): slot is TimeSlot =>
      slot !== null && slot !== undefined && slot.time_slot_id !== null,
  );

  return (
    <div className="pb-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-800">Часові проміжки</h3>
      </div>

      <div className="space-y-3">
        {validTimeSlots.map((slot) => {
          const currentLabel = (getSlotValue(slot, "label") || "") as string;
          const startTimeValue = formatTimeValue(
            getSlotValue(slot, "start_time") as string,
          );
          const endTimeValue = formatTimeValue(
            getSlotValue(slot, "end_time") as string,
          );

          return (
            <div key={slot.time_slot_id} className="flex items-center gap-2">
              <input
                type="text"
                placeholder="Назва"
                value={currentLabel}
                onChange={(e) =>
                  handleFieldChange(slot.time_slot_id, "label", e.target.value)
                }
                className="flex-1 min-w-0 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
              />
              <TimeInput
                value={startTimeValue}
                onChange={(value) => {
                  handleFieldChange(slot.time_slot_id, "start_time", value);
                }}
              />
              <TimeInput
                value={endTimeValue}
                onChange={(value) => {
                  handleFieldChange(slot.time_slot_id, "end_time", value);
                }}
              />

              {isSlotEdited(slot.time_slot_id) ? (
                <button
                  onClick={() => handleSaveExisting(slot.time_slot_id)}
                  className="w-8 h-8 flex-shrink-0 flex items-center justify-center rounded-lg bg-green-500 hover:bg-green-600 text-white transition-colors"
                  aria-label="Save timeslot"
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
                      await deleteTimeSlotById(slot.time_slot_id);
                    } catch (error) {
                      console.error("Error deleting timeslot:", error);
                    }
                  }}
                  className="w-8 h-8 flex-shrink-0 flex items-center justify-center rounded-lg hover:bg-red-50 text-red-500 transition-colors"
                  aria-label="Delete timeslot"
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
              )}
            </div>
          );
        })}

        {newSlots.map((slot) => (
          <div key={slot.id} className="flex items-center gap-2">
            <input
              type="text"
              placeholder="Назва"
              value={slot.label}
              onChange={(e) =>
                handleNewSlotChange(slot.id, "label", e.target.value)
              }
              className="flex-1 min-w-0 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-sm"
            />
            <TimeInput
              value={slot.start_time}
              onChange={(value) =>
                handleNewSlotChange(slot.id, "start_time", value)
              }
            />
            <TimeInput
              value={slot.end_time}
              onChange={(value) =>
                handleNewSlotChange(slot.id, "end_time", value)
              }
            />
            {isNewSlotValid(slot) ? (
              <button
                onClick={() => handleSaveNew(slot.id)}
                className="w-8 h-8 flex-shrink-0 flex items-center justify-center rounded-lg bg-green-500 hover:bg-green-600 text-white transition-colors"
                aria-label="Save new timeslot"
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
                onClick={() => handleDeleteNew(slot.id)}
                className="w-8 h-8 flex-shrink-0 flex items-center justify-center rounded-lg hover:bg-red-50 text-red-500 transition-colors"
                aria-label="Cancel new timeslot"
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
            )}
          </div>
        ))}

        {validTimeSlots.length === 0 && newSlots.length === 0 && (
          <p className="text-gray-400 text-sm text-center py-4">
            Немає таймслотів. Натісніть "Додати таймслот" щоб створити.
          </p>
        )}

        <button
          onClick={handleAddNewSlot}
          className="text-indigo-600 hover:text-indigo-700 text-sm font-medium transition-colors "
        >
          + Додати таймслот
        </button>
      </div>
    </div>
  );
};
