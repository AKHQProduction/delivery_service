import { useState, useEffect } from "react";
import {
  getAllDistricts,
  createDistrict,
  updateDistrict,
  deleteDistrict,
} from "../../services/api/settingsApi";

export interface District {
  district_id: string;
  name: string;
}

export const useDistrictsSettings = () => {
  const [districts, setDistricts] = useState<District[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const fetchDistricts = async () => {
    try {
      setIsLoading(true);
      const data = await getAllDistricts();
      setDistricts(data);
    } catch (error) {
      console.error("Error fetching districts:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDistricts();
  }, []);

  const addDistrict = async (name: string) => {
    try {
      const newDistrict = await createDistrict(name);
      setDistricts((prev) => [...prev, newDistrict]);
      await fetchDistricts();
    } catch (error) {
      console.error("Error adding district:", error);
      throw error;
    }
  };

  const updateDistrictById = async (id: string, name: string) => {
    try {
      const updatedDistrict = await updateDistrict(id, name);
      setDistricts((prev) =>
        prev.map((district) =>
          district.district_id === id ? updatedDistrict : district
        )
      );
      await fetchDistricts();
    } catch (error) {
      console.error("Error updating district:", error);
      throw error;
    }
  };

  const deleteDistrictById = async (id: string) => {
    try {
      await deleteDistrict(id);
      setDistricts((prev) =>
        prev.filter((district) => district.district_id !== id)
      );
      await fetchDistricts();
    } catch (error) {
      console.error("Error deleting district:", error);
      throw error;
    }
  };

  return {
    districts,
    addDistrict,
    updateDistrictById,
    deleteDistrictById,
    isLoading,
    refetch: fetchDistricts,
  };
};
