import React from "react";

interface SkeletonProps {
  className?: string;
}

export const SkeletonBlock: React.FC<SkeletonProps> = ({ className = "" }) => (
  <div className={`animate-shimmer rounded-md bg-slate-100 ${className}`} />
);

export const ClientCardSkeleton: React.FC = () => (
  <div className="rounded-lg border border-slate-200 bg-white p-4">
    <div className="flex items-start gap-4">
      <SkeletonBlock className="h-10 w-10 shrink-0 rounded-full" />
      <div className="flex-1 min-w-0">
        <SkeletonBlock className="mb-3 h-5 w-2/3" />
        <SkeletonBlock className="mb-2 h-4 w-40" />
        <SkeletonBlock className="h-4 w-56 max-w-full" />
      </div>
    </div>
  </div>
);

export const ProductCardSkeleton: React.FC = () => (
  <div className="rounded-lg border border-slate-200 bg-white p-4">
    <SkeletonBlock className="mb-3 h-5 w-3/4" />
    <SkeletonBlock className="mb-4 h-4 w-1/2" />
    <SkeletonBlock className="h-7 w-24" />
  </div>
);

export const EmployeeCardSkeleton: React.FC = () => (
  <div className="flex items-center gap-4 rounded-lg border border-slate-200 bg-white p-4">
    <SkeletonBlock className="w-12 h-12 rounded-full" />
    <div>
      <SkeletonBlock className="h-5 w-36 mb-2" />
      <SkeletonBlock className="h-4 w-24" />
    </div>
  </div>
);

export const OrderCardSkeleton: React.FC = () => (
  <div className="rounded-lg border border-slate-200 bg-white p-4">
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <SkeletonBlock className="h-10 w-10 rounded-full" />
          <SkeletonBlock className="h-5 w-32" />
        </div>
        <SkeletonBlock className="h-5 w-16" />
      </div>
      <SkeletonBlock className="h-4 w-full" />
      <SkeletonBlock className="h-4 w-3/4" />
    </div>
  </div>
);

export const SettingsItemSkeleton: React.FC = () => (
  <div className="flex items-center gap-2">
    <SkeletonBlock className="flex-1 h-12 rounded-xl" />
    <SkeletonBlock className="w-10 h-10 rounded-xl" />
  </div>
);

export const SummaryCardsSkeleton: React.FC<{ count?: number }> = ({ count = 4 }) => (
  <div className="mt-4 grid grid-cols-2 gap-2 md:grid-cols-[repeat(4,minmax(0,1fr))]">
    {Array.from({ length: count }).map((_, index) => (
      <div key={index} className="rounded-lg border border-slate-200 bg-white p-4">
        <SkeletonBlock className="h-4 w-20" />
        <SkeletonBlock className="mt-3 h-8 w-24" />
      </div>
    ))}
  </div>
);

export const TableSkeleton: React.FC<{ columns?: number; rows?: number }> = ({
  columns = 5,
  rows = 6,
}) => (
  <section className="hidden overflow-hidden rounded-lg border border-slate-200 bg-white lg:block">
    <div className="overflow-x-auto">
      <table className="min-w-full table-fixed divide-y divide-slate-200 text-sm">
        <thead className="bg-white">
          <tr>
            {Array.from({ length: columns }).map((_, index) => (
              <th key={index} className="px-4 py-4">
                <SkeletonBlock className={index === 0 ? "h-4 w-4" : "h-4 w-20"} />
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-200">
          {Array.from({ length: rows }).map((_, rowIndex) => (
            <tr key={rowIndex}>
              {Array.from({ length: columns }).map((_, columnIndex) => (
                <td key={columnIndex} className="px-4 py-4">
                  <SkeletonBlock
                    className={
                      columnIndex === 0
                        ? "h-4 w-4"
                        : columnIndex === columns - 1
                          ? "ml-auto h-8 w-16"
                          : "h-4 w-full max-w-[12rem]"
                    }
                  />
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
    <div className="flex items-center justify-between border-t border-slate-200 px-5 py-3">
      <SkeletonBlock className="h-4 w-32" />
      <SkeletonBlock className="h-9 w-28" />
    </div>
  </section>
);

export const SidePanelSkeleton: React.FC = () => (
  <aside className="hidden rounded-lg border border-slate-200 bg-white p-6 xl:block">
    <div className="flex items-center gap-3">
      <SkeletonBlock className="h-12 w-12 rounded-full" />
      <div className="flex-1">
        <SkeletonBlock className="h-5 w-40" />
        <SkeletonBlock className="mt-2 h-4 w-28" />
      </div>
    </div>
    <div className="mt-6 space-y-4">
      {Array.from({ length: 4 }).map((_, index) => (
        <div key={index} className="flex items-center justify-between gap-4 border-t border-slate-200 pt-4">
          <SkeletonBlock className="h-4 w-20" />
          <SkeletonBlock className="h-4 w-32" />
        </div>
      ))}
    </div>
    <div className="mt-8 grid grid-cols-2 gap-3">
      <SkeletonBlock className="h-11 w-full" />
      <SkeletonBlock className="h-11 w-full" />
    </div>
  </aside>
);

export const InlineListSkeleton: React.FC<{ rows?: number; variant?: "client" | "product" }> = ({
  rows = 2,
  variant = "product",
}) => (
  <div className="space-y-2">
    {Array.from({ length: rows }).map((_, index) => (
      <div key={index} className="rounded-md border border-slate-200 bg-white p-3">
        <div className="flex items-center gap-3">
          {variant === "client" && <SkeletonBlock className="h-8 w-8 rounded-full" />}
          <div className="min-w-0 flex-1">
            <SkeletonBlock className="h-4 w-2/3" />
            <SkeletonBlock className="mt-2 h-3 w-28" />
          </div>
          <SkeletonBlock className="h-8 w-16" />
        </div>
      </div>
    ))}
  </div>
);

export const FormSkeleton: React.FC<{ fields?: number }> = ({ fields = 4 }) => (
  <div className="flex min-h-full flex-col">
    <div className="space-y-4 pb-24">
      {Array.from({ length: fields }).map((_, index) => (
        <div key={index} className="space-y-2">
          <SkeletonBlock className="h-4 w-28" />
          <SkeletonBlock className="h-12 w-full" />
        </div>
      ))}
    </div>
    <div className="sticky bottom-0 -mx-6 mt-auto flex gap-3 border-t border-slate-200 bg-white px-6 py-4">
      <SkeletonBlock className="h-12 flex-1" />
      <SkeletonBlock className="h-12 flex-1" />
    </div>
  </div>
);
