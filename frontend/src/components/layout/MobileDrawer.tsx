import { type RouteConfig } from "../../config/roles.config";

interface MobileDrawerProps {
  isOpen: boolean;
  routes: RouteConfig[];
  userName: string;
  userRole: string;
  activePath: string;
  onClose: () => void;
  onNavigate: (path: string) => void;
}

export const MobileDrawer = ({
  isOpen,
  routes,
  userName,
  userRole,
  activePath,
  onClose,
  onNavigate,
}: MobileDrawerProps) => {
  return (
    <div
      className={`fixed inset-0 z-[10000] transition-[visibility] duration-300 md:hidden ${
        isOpen ? "visible pointer-events-auto" : "invisible pointer-events-none"
      }`}
    >
      <button
        type="button"
        className={`absolute inset-0 bg-slate-950/45 transition-opacity duration-300 ease-out ${
          isOpen ? "opacity-100" : "opacity-0"
        }`}
        onClick={onClose}
        aria-label="Закрити меню фоном"
        tabIndex={isOpen ? 0 : -1}
      />
      <aside
        className={`relative flex h-full w-[82vw] max-w-sm flex-col border-r border-slate-200 bg-white shadow-xl transition-transform duration-300 ease-out ${
          isOpen ? "translate-x-0" : "-translate-x-full"
        }`}
      >
        <div className="flex items-center justify-between border-b border-slate-200 px-5 py-5">
          <h2 className="text-lg font-semibold text-slate-950">Water Delivery</h2>
          <button
            type="button"
            onClick={onClose}
            className="rounded-md p-2 text-slate-500 hover:bg-slate-100 hover:text-slate-950"
            aria-label="Закрити меню"
          >
            <CloseIcon className="h-5 w-5" />
          </button>
        </div>

        <nav className="flex-1 space-y-1 px-3 py-4">
          {routes.map((route) => {
            const isActive =
              activePath === route.path ||
              (route.path !== "/" && activePath.startsWith(route.path));
            return (
              <button
                key={route.path}
                type="button"
                onClick={() => onNavigate(route.path)}
                className={`flex w-full items-center gap-3 rounded-md px-3 py-3 text-left text-sm font-medium ${
                  isActive
                    ? "bg-blue-50 text-blue-700"
                    : "text-slate-700 hover:bg-slate-100 hover:text-slate-950"
                }`}
              >
                <img
                  src={route.icon}
                  alt={route.label}
                  className={`h-5 w-5 object-contain ${isActive ? "opacity-100" : "opacity-70"}`}
                />
                <span>{route.label}</span>
              </button>
            );
          })}
        </nav>

        <div className="border-t border-slate-200 p-4">
          <div className="flex items-center gap-3 rounded-lg border border-slate-200 p-3">
            <span className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-100 font-semibold text-blue-700">
              {userName?.[0] ?? "?"}
            </span>
            <div className="min-w-0">
              <p className="truncate text-sm font-semibold text-slate-950">{userName}</p>
              <p className="text-xs text-slate-500">{userRole}</p>
            </div>
          </div>
        </div>
      </aside>
    </div>
  );
};

export const MenuIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M4 7h16M4 12h16M4 17h10"
    />
  </svg>
);

const CloseIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18 18 6M6 6l12 12" />
  </svg>
);
