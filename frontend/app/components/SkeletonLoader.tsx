"use client";

export function VideoCardSkeleton() {
  return (
    <div className="overflow-hidden rounded-[var(--radius-2xl)] glass-panel">
      <div className="aspect-video skeleton" />

      <div className="space-y-4 p-5">
        <div className="h-5 w-3/4 rounded-[var(--radius-sm)] skeleton" />
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-full skeleton" />
          <div className="flex-1 space-y-2">
            <div className="h-3.5 w-36 rounded-[var(--radius-sm)] skeleton" />
            <div className="h-3 w-24 rounded-[var(--radius-sm)] skeleton" />
          </div>
        </div>
        <div className="grid grid-cols-2 border-y border-[var(--border)]">
          <div className="border-r border-[var(--border)] py-3 pr-3">
            <div className="mb-2 h-3 w-16 rounded-[var(--radius-sm)] skeleton" />
            <div className="h-3 w-12 rounded-[var(--radius-sm)] skeleton" />
          </div>
          <div className="py-3 pl-3">
            <div className="mb-2 h-3 w-16 rounded-[var(--radius-sm)] skeleton" />
            <div className="h-3 w-20 rounded-[var(--radius-sm)] skeleton" />
          </div>
        </div>
        <div className="flex gap-1.5">
          <div className="h-7 w-16 rounded-full skeleton" />
          <div className="h-7 w-20 rounded-full skeleton" />
          <div className="h-7 w-24 rounded-full skeleton" />
        </div>
        <div className="hairline" />
        <div className="overflow-hidden rounded-[var(--radius-md)] bg-[var(--bg-input)] px-3 py-2">
          <div className="mb-2 h-4 w-24 rounded-[var(--radius-sm)] skeleton" />
          {[1, 2, 3].map((i) => (
            <div key={i} className="flex gap-3 border-t border-[var(--border-subtle)] py-2 first:border-t-0">
              <div className="h-3 w-10 rounded-[var(--radius-sm)] skeleton" />
              <div className="h-3 flex-1 rounded-[var(--radius-sm)] skeleton" />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export function ComparisonSkeleton() {
  return (
    <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
      <VideoCardSkeleton />
      <VideoCardSkeleton />
    </div>
  );
}
