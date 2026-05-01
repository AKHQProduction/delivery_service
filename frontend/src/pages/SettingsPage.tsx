import { EmptyState } from "../components/ui/EmptyState";
import { useTGSettings } from "../hooks/settings/useTGSettings";
import { usePlatform } from "../platforms/usePlatform";

export const SettingsPage = () => {
  const { settings, updateSetting } = useTGSettings();
  const { features, type } = usePlatform();

  return (
    <div className="min-h-screen bg-slate-50 px-4 pb-28 pt-6 sm:px-6 md:px-8 md:pb-10">
      <div>
        <h1 className="text-2xl font-semibold leading-8 text-slate-950">Налаштування</h1>
        <p className="mt-1 text-sm text-slate-500">Параметри платформи та поведінки застосунку</p>
      </div>

      <div className="mt-4 grid gap-4 lg:grid-cols-[minmax(0,1fr)_20rem]">
        <section className="rounded-lg border border-slate-200 bg-white">
          <div className="border-b border-slate-200 px-4 py-4 sm:px-5">
            <h2 className="text-base font-semibold text-slate-950">Платформа</h2>
            <p className="mt-1 text-sm text-slate-500">
              Доступні параметри залежать від середовища запуску.
            </p>
          </div>

          <div className="p-4 sm:p-5">
            {features.fullscreen ? (
              <SettingRow
                title="Повноекранний режим"
                description="Відкривати застосунок на весь екран у Telegram."
                checked={settings.fullscreen}
                onChange={(checked) => updateSetting("fullscreen", checked)}
              />
            ) : (
              <EmptyState
                title="Налаштування наразі відсутні"
                description="Для поточної платформи немає доступних параметрів."
                icon={<SettingsIcon className="h-7 w-7" />}
              />
            )}
          </div>
        </section>

        <aside className="rounded-lg border border-slate-200 bg-white p-4 sm:p-5">
          <p className="text-sm font-semibold text-slate-950">Поточне середовище</p>
          <div className="mt-4 rounded-md border border-blue-100 bg-blue-50 px-3 py-3">
            <p className="text-xs font-medium uppercase text-blue-600">Платформа</p>
            <p className="mt-1 text-lg font-semibold text-slate-950">
              {type === "telegram" ? "Telegram" : "Web"}
            </p>
          </div>
          <p className="mt-3 text-sm leading-5 text-slate-500">
            Ця сторінка показує лише технічні налаштування інтерфейсу. Налаштування магазину
            знаходяться в окремому розділі.
          </p>
        </aside>
      </div>
    </div>
  );
};

const SettingRow = ({
  title,
  description,
  checked,
  onChange,
}: {
  title: string;
  description: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
}) => (
  <label className="relative flex cursor-pointer items-center justify-between gap-4 rounded-lg border border-slate-200 bg-white px-4 py-4 pr-20">
    <span className="min-w-0">
      <span className="block text-sm font-semibold text-slate-950">{title}</span>
      <span className="mt-1 block text-sm leading-5 text-slate-500">{description}</span>
    </span>
    <input
      type="checkbox"
      className="peer sr-only"
      checked={checked}
      onChange={(event) => onChange(event.target.checked)}
    />
    <span className="absolute right-4 top-1/2 h-7 w-12 -translate-y-1/2 rounded-full bg-slate-200 transition-colors peer-checked:bg-blue-600 peer-focus-visible:outline peer-focus-visible:outline-2 peer-focus-visible:outline-offset-2 peer-focus-visible:outline-blue-600" />
    <span className="absolute right-10 top-1/2 h-5 w-5 -translate-y-1/2 rounded-full bg-white shadow-sm transition-transform peer-checked:translate-x-5" />
  </label>
);

const SettingsIcon = ({ className }: { className?: string }) => (
  <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth={2}
      d="M10.5 6h3m-7.6 2.2 2.1-2.1m8 0 2.1 2.1M6 12H3m18 0h-3m-9.9 5.9-2.1-2.1m12.2 0-2.1 2.1M10.5 18h3M12 9.25A2.75 2.75 0 1 1 12 14.75 2.75 2.75 0 0 1 12 9.25Z"
    />
  </svg>
);
