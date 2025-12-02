import { useEffect, useState } from "react";
import { PageHeader } from "../components/ui/pageHeader";
import { SearchBar } from "../components/ui/searchBar";
import { EmployeeCard } from "../components/ui/employeeCard";
import { EmployeeDetailModal } from "../components/features/employeeDetailModal";
import { RightModal } from "../components/ui/rightModal";
import { useEmployees } from "../hooks/useEmployees";
import { reverseRoleMap } from "../utils/dataMap";
import { type Employee } from "../types/entities/Employee";

export const EmployeePage = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedEmployee, setSelectedEmployee] = useState<Employee | null>(
    null
  );
  const [isModalOpen, setIsModalOpen] = useState(false);
  const { getEmployees, deleteEmployees, updateEmployee, employees } =
    useEmployees();

  useEffect(() => {
    getEmployees();
  }, []);

  const employeesList = employees.filter((employee) =>
    employee.full_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

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
      <SearchBar
        placeholder="Пошук працівників..."
        searchTerm={searchTerm}
        setSearchTerm={setSearchTerm}
      />

      {employeesList.length === 0 ? (
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
