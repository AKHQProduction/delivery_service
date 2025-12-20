import { useEffect, useState, useRef, useCallback } from "react";
import { PageHeader } from "../components/ui/pageHeader";
import { SearchBar } from "../components/ui/searchBar";
import { EmployeeCard } from "../components/ui/employeeCard";
import { EmployeeDetailModal } from "../components/modals/detailsModals/EmployeeDetailModal";
import { RightModal } from "../components/modals/RightModal";
import { useEmployees } from "../hooks/useEmployees";
import { reverseRoleMap } from "../utils/dataMap";
import { type Employee } from "../types/entities/Employee";

export const EmployeePage = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedEmployee, setSelectedEmployee] = useState<Employee | null>(
    null
  );
  const [isModalOpen, setIsModalOpen] = useState(false);
  const { getEmployees, deleteEmployees, updateEmployee, employees, loadMoreEmployees, loadingMore, hasMore } =
    useEmployees();
  const debounceRef = useRef<NodeJS.Timeout | null>(null);
  const observerRef = useRef<IntersectionObserver | null>(null);
  const loadMoreRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    getEmployees();
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
  }, [searchTerm]);

  const handleObserver = useCallback(
    (entries: IntersectionObserverEntry[]) => {
      const [entry] = entries;
      if (entry.isIntersecting && hasMore && !loadingMore) {
        loadMoreEmployees();
      }
    },
    [hasMore, loadingMore, loadMoreEmployees]
  );

  useEffect(() => {
    if (observerRef.current) {
      observerRef.current.disconnect();
    }

    observerRef.current = new IntersectionObserver(handleObserver, {
      root: null,
      rootMargin: "100px",
      threshold: 0,
    });

    if (loadMoreRef.current) {
      observerRef.current.observe(loadMoreRef.current);
    }

    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, [handleObserver]);

  const handleEmployeeClick = (employee: Employee) => {
    setSelectedEmployee(employee);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setTimeout(() => setSelectedEmployee(null), 300);
  };

  const handleSave = (updatedEmployee: Employee) => {
    const reverseRole = reverseRoleMap[updatedEmployee.role];
    updateEmployee(
      updatedEmployee.user_id,
      updatedEmployee.full_name,
      reverseRole
    );
    window.location.reload();
  };

  const handleDelete = () => {
    console.log("Delete employee:", selectedEmployee);
    deleteEmployees(selectedEmployee!.user_id);
    window.location.reload();
    handleCloseModal();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <PageHeader title="Персонал" />

      <div className="px-6 pb-4">
        <SearchBar
          placeholder="Пошук працівників"
          searchTerm={searchTerm}
          setSearchTerm={setSearchTerm}
        />
      </div>

      {employees.length === 0 ? (
        <div className="flex flex-col items-center justify-center mt-20">
          <p className="text-gray-500 text-lg font-medium">
            {searchTerm ? "Працівників не знайдено" : "Працівники відсутні"}
          </p>
          {searchTerm && (
            <p className="text-gray-400 text-sm mt-2">
              Спробуйте інший пошуковий запит
            </p>
          )}
        </div>
      ) : (
        <div className="px-6 pb-24">
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {employees.map((employee) => (
              <EmployeeCard
                key={employee.user_id}
                employee={employee}
                onClick={() => handleEmployeeClick(employee)}
              />
            ))}
          </div>

          <div ref={loadMoreRef} className="py-4 flex justify-center">
            {loadingMore && (
              <div className="flex items-center gap-2 text-gray-500">
                <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                <span>Завантаження...</span>
              </div>
            )}
          </div>
        </div>
      )}

      <RightModal isOpen={isModalOpen} onClose={handleCloseModal}>
        {selectedEmployee && (
          <EmployeeDetailModal
            employee={selectedEmployee}
            onClose={handleCloseModal}
            onDelete={handleDelete}
            onSave={handleSave}
          />
        )}
      </RightModal>
    </div>
  );
};