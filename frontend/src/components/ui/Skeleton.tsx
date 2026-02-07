import React from "react";

interface SkeletonProps {
  className?: string;
}

const SkeletonBlock: React.FC<SkeletonProps> = ({ className = "" }) => (
  <div className={`animate-shimmer rounded-xl ${className}`} />
);

export const ClientCardSkeleton: React.FC = () => (
  <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
    <div className="flex items-start gap-4">
      <div className="flex-1 min-w-0">
        <SkeletonBlock className="h-6 w-3/4 mb-3" />
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <SkeletonBlock className="w-4 h-4 rounded-full" />
            <SkeletonBlock className="h-5 w-32 rounded-lg" />
          </div>
          <div className="flex items-center gap-2">
            <SkeletonBlock className="w-4 h-4 rounded-full" />
            <SkeletonBlock className="h-5 w-40 rounded-lg" />
          </div>
        </div>
      </div>
    </div>
  </div>
);

export const ProductCardSkeleton: React.FC = () => (
  <div className="bg-white rounded-2xl p-5 shadow-sm">
    <SkeletonBlock className="h-6 w-3/4 mb-2" />
    <SkeletonBlock className="h-4 w-1/2 mb-3" />
    <SkeletonBlock className="h-8 w-20" />
  </div>
);

export const EmployeeCardSkeleton: React.FC = () => (
  <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100 flex items-center gap-4">
    <SkeletonBlock className="w-12 h-12 rounded-full" />
    <div>
      <SkeletonBlock className="h-5 w-36 mb-2" />
      <SkeletonBlock className="h-4 w-24" />
    </div>
  </div>
);

export const OrderCardSkeleton: React.FC = () => (
  <div className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
    <div className="space-y-2.5">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <SkeletonBlock className="w-9 h-9 rounded-full" />
          <SkeletonBlock className="h-5 w-32" />
        </div>
        <SkeletonBlock className="h-7 w-16" />
      </div>
      <div className="flex items-center gap-3">
        <SkeletonBlock className="w-9 h-9 rounded-full" />
        <SkeletonBlock className="h-5 w-40" />
      </div>
      <div className="flex items-center gap-3">
        <SkeletonBlock className="w-9 h-9 rounded-full" />
        <SkeletonBlock className="h-5 w-24" />
      </div>
    </div>
  </div>
);

export const SettingsItemSkeleton: React.FC = () => (
  <div className="flex items-center gap-2">
    <SkeletonBlock className="flex-1 h-12 rounded-xl" />
    <SkeletonBlock className="w-10 h-10 rounded-xl" />
  </div>
);
