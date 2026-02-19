import { useEffect, useState, useRef } from "react";
import { PageHeader } from "../components/ui/PageHeader";
import { SearchBar } from "../components/ui/SearchBar";
import { EmployeeCard } from "../components/ui/EmployeeCard";
import { EmployeeDetailModal } from "../components/modals/detailsModals/EmployeeDetailModal";
import { DetailModal } from "../components/modals/DetailModal";
import { useEmployees } from "../hooks/useEmployees";
import { reverseRoleMap } from "../utils/dataMap";
import { type Employee } from "../types/entities/Employee";
import { useInfiniteScroll } from "../hooks/useInfiniteScroll";
import { EmployeeCardSkeleton } from "../components/ui/Skeleton";

export const EmployeePage = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedEmployee, setSelectedEmployee] = useState<Employee | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const {
    getEmployees,
    deleteEmployees,
    updateEmployee,
    employees,
    loadMoreEmployees,
    loading,
    loadingMore,
    hasMore,
  } = useEmployees();
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const { sentinelRef } = useInfiniteScroll({
    onLoadMore: loadMoreEmployees,
    hasMore,
    isLoading: loadingMore,
  });

  useEffect(() => {
    getEmployees();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    debounceRef.current = setTimeout(() => {
      getEmployees(searchTerm);
    }, 100);

    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchTerm]);

  const handleEmployeeClick = (employee: Employee) => {
    setSelectedEmployee(employee);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setTimeout(() => setSelectedEmployee(null), 300);
  };

  const handleSave = async (updatedEmployee: Employee) => {
    if (!updatedEmployee?.user_id) return;

    const reverseRole = reverseRoleMap[updatedEmployee.role];
    await updateEmployee(updatedEmployee.user_id, updatedEmployee.full_name, reverseRole);
    const refreshedEmployees = await getEmployees(searchTerm);

    if (refreshedEmployees) {
      const updatedSelectedEmployee = refreshedEmployees.find(
        (emp: Employee) => emp?.user_id === updatedEmployee.user_id,
      );
      if (updatedSelectedEmployee) {
        setSelectedEmployee(updatedSelectedEmployee);
      }
    }
  };

  const handleDelete = async () => {
    if (selectedEmployee) {
      await deleteEmployees(selectedEmployee.user_id);
      handleCloseModal();
      getEmployees(searchTerm);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 md:bg-white">
      <PageHeader title="Персонал" />

      <div className="px-6 pb-4 md:px-8">
        <SearchBar
          placeholder="Пошук працівників"
          searchTerm={searchTerm}
          setSearchTerm={setSearchTerm}
        />
      </div>

      {loading && employees.length === 0 ? (
        <div className="px-6 pb-24 md:pb-8 md:px-8">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {Array.from({ length: 8 }).map((_, i) => (
              <EmployeeCardSkeleton key={i} />
            ))}
          </div>
        </div>
      ) : employees.length === 0 ? (
        <div className="flex flex-col items-center justify-center mt-20">
          <svg
            className="w-16 h-16 mx-auto mb-4 text-gray-300"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M10 6H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V8a2 2 0 00-2-2h-5m-4 0V5a2 2 0 114 0v1m-4 0a2 2 0 104 0m-5 8a2 2 0 100-4 2 2 0 000 4zm0 0c1.306 0 2.417.835 2.83 2M9 14a3.001 3.001 0 00-2.83 2M15 11h3m-3 4h2"
            />
          </svg>
          <p className="text-gray-500 text-lg font-medium">
            {searchTerm ? "Працівників не знайдено" : "Працівники відсутні"}
          </p>
          {searchTerm && (
            <p className="text-gray-400 text-sm mt-2">Спробуйте інший пошуковий запит</p>
          )}
        </div>
      ) : (
        <div className="px-6 pb-24 md:pb-8 md:px-8">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {employees.map((employee) => (
              <EmployeeCard
                key={employee.user_id}
                employee={employee}
                onClick={() => handleEmployeeClick(employee)}
              />
            ))}
          </div>

          <div ref={sentinelRef} className="py-4 flex justify-center">
            {loadingMore && (
              <div className="flex items-center gap-2 text-gray-500">
                <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                    fill="none"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  />
                </svg>
                <span>Завантаження...</span>
              </div>
            )}
          </div>
        </div>
      )}

      <DetailModal isOpen={isModalOpen} onClose={handleCloseModal}>
        {selectedEmployee && (
          <EmployeeDetailModal
            employee={selectedEmployee}
            onClose={handleCloseModal}
            onDelete={handleDelete}
            onSave={handleSave}
          />
        )}
      </DetailModal>
    </div>
  );
};
