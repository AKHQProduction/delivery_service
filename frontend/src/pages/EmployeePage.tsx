import { useEffect, useState, useRef } from "react";
import { SearchBar } from "../components/ui/SearchBar";
import { EmployeeCard } from "../components/ui/EmployeeCard";
import { EmployeeDetailModal } from "../components/modals/detailsModals/EmployeeDetailModal";
import { DetailModal } from "../components/modals/DetailModal";
import { Modal } from "../components/modals/Modal";
import { InviteLinkModal } from "../components/modals/InviteLinkModal";
import { InviteUserForm } from "../components/forms/employees/InviteUserForm";
import { useEmployees } from "../hooks/useEmployees";
import { reverseRoleMap } from "../utils/dataMap";
import { type Employee } from "../types/entities/Employee";
import { useInfiniteScroll } from "../hooks/useInfiniteScroll";
import { EmployeeCardSkeleton } from "../components/ui/Skeleton";

export const EmployeePage = () => {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedEmployee, setSelectedEmployee] = useState<Employee | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isInviteModalOpen, setIsInviteModalOpen] = useState(false);
  const [inviteLink, setInviteLink] = useState<string | null>(null);
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

  const roleCounts = employees.reduce<Record<string, number>>((acc, employee) => {
    acc[employee.role] = (acc[employee.role] ?? 0) + 1;
    return acc;
  }, {});

  return (
    <div className="min-h-screen bg-slate-50 px-4 pb-28 pt-6 sm:px-6 md:px-8 md:pb-10">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <h1 className="text-2xl font-semibold leading-8 text-slate-950">Персонал</h1>
          <p className="mt-1 text-sm text-slate-500">Працівники магазину та їхні ролі</p>
        </div>
        <button
          type="button"
          onClick={() => setIsInviteModalOpen(true)}
          className="inline-flex h-12 items-center justify-center gap-2 rounded-md bg-blue-600 px-4 text-sm font-medium text-white hover:bg-blue-700 lg:w-auto"
        >
          <PlusIcon className="h-4 w-4" />
          Запросити
        </button>
      </div>

      <div className="mt-4 grid grid-cols-3 gap-2">
        <SummaryCard label="Усього" value={employees.length} />
        <SummaryCard label="Менеджери" value={roleCounts.MANAGER ?? 0} />
        <SummaryCard label="Кур'єри" value={roleCounts.COURIER ?? 0} />
      </div>

      <div className="mt-4 rounded-lg border border-slate-200 bg-white p-4">
        <SearchBar
          placeholder="Пошук працівників"
          searchTerm={searchTerm}
          setSearchTerm={setSearchTerm}
        />
      </div>

      {loading && employees.length === 0 ? (
        <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-3">
          {Array.from({ length: 8 }).map((_, i) => (
            <EmployeeCardSkeleton key={i} />
          ))}
        </div>
      ) : employees.length === 0 ? (
        <div className="mt-4 rounded-lg border border-slate-200 bg-white p-10 text-center">
          <svg
            className="mx-auto mb-4 h-14 w-14 text-slate-300"
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
          <p className="text-lg font-semibold text-slate-950">
            {searchTerm ? "Працівників не знайдено" : "Працівники відсутні"}
          </p>
          {searchTerm && (
            <p className="mt-1 text-sm text-slate-500">Спробуйте інший пошуковий запит</p>
          )}
        </div>
      ) : (
        <div className="mt-4">
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 xl:grid-cols-3">
            {employees.map((employee) => (
              <EmployeeCard
                key={employee.user_id}
                employee={employee}
                onClick={() => handleEmployeeClick(employee)}
              />
            ))}
          </div>

          <div ref={sentinelRef} className="flex justify-center py-4">
            {loadingMore && (
              <div className="flex items-center gap-2 text-slate-500">
                <svg className="h-5 w-5 animate-spin" viewBox="0 0 24 24">
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

      <Modal
        isOpen={isInviteModalOpen}
        onClose={() => setIsInviteModalOpen(false)}
        title="Запросити працівника"
      >
        <InviteUserForm
          onClose={() => setIsInviteModalOpen(false)}
          onInviteCreated={(link) => {
            setIsInviteModalOpen(false);
            setInviteLink(link);
          }}
        />
      </Modal>

      {inviteLink && <InviteLinkModal link={inviteLink} onClose={() => setInviteLink(null)} />}
    </div>
  );
};

const SummaryCard = ({ label, value }: { label: string; value: number }) => (
  <div className="rounded-lg border border-slate-200 bg-white p-4">
    <p className="text-sm font-medium text-slate-500">{label}</p>
    <p className="mt-2 text-2xl font-semibold text-slate-950">{value}</p>
  </div>
);

const PlusIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 5v14m7-7H5" />
  </svg>
);
