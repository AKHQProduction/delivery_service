import { useState, useEffect } from "react";
import {
  getAllTimeSlots,
  createNewTimeSlot,
  updateTimeSlot,
  deleteTimeSlot,
} from "../../services/api/settingsApi";

interface TimeSlot {
  time_slot_id: string;
  start_time: string;
  end_time: string;
  label?: string;
}

export const useTimeSlotsSettings = () => {
  const [timeSlots, setTimeSlots] = useState<TimeSlot[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isLoaded, setIsLoaded] = useState(false);

  const fetchTimeSlots = async () => {
    try {
      setIsLoading(true);
      const data = (await getAllTimeSlots()) as TimeSlot[];
      setTimeSlots(data);
    } catch (error) {
      console.error("Error fetching time slots:", error);
    } finally {
      setIsLoading(false);
      setIsLoaded(true);
    }
  };

  useEffect(() => {
    fetchTimeSlots();
  }, []);

  const addTimeSlot = async (start_time: Date, end_time: Date, label?: string) => {
    try {
      const newSlot = (await createNewTimeSlot(start_time, end_time, label)) as TimeSlot;
      // Immediately update local state
      setTimeSlots((prev) => [...prev, newSlot]);
      // Optionally refetch to ensure sync
      await fetchTimeSlots();
    } catch (error) {
      console.error("Error adding time slot:", error);
      throw error;
    }
  };

  const updateTimeSlotById = async (
    id: string,
    start_time: Date,
    end_time: Date,
    label?: string,
  ) => {
    try {
      const updatedSlot = (await updateTimeSlot(id, start_time, end_time, label)) as TimeSlot;
      // Immediately update local state
      setTimeSlots((prev) => prev.map((slot) => (slot.time_slot_id === id ? updatedSlot : slot)));
      // Optionally refetch to ensure sync
      await fetchTimeSlots();
    } catch (error) {
      console.error("Error updating time slot:", error);
      throw error;
    }
  };

  const deleteTimeSlotById = async (id: string) => {
    try {
      await deleteTimeSlot(id);
      // Immediately update local state
      setTimeSlots((prev) => prev.filter((slot) => slot.time_slot_id !== id));
      // Optionally refetch to ensure sync
      await fetchTimeSlots();
    } catch (error) {
      console.error("Error deleting time slot:", error);
      throw error;
    }
  };

  return {
    timeSlots,
    addTimeSlot,
    updateTimeSlotById,
    deleteTimeSlotById,
    isLoading,
    isLoaded,
    refetch: fetchTimeSlots,
  };
};
