import type { CeleryStatus } from "../types/job";

const STYLES: Record<CeleryStatus, string> = {
  SUCCESS: "bg-green-100 text-green-800",
  FAILURE: "bg-red-100 text-red-800",
  PROGRESS: "bg-amber-100 text-amber-800",
  PENDING: "bg-gray-100 text-gray-700",
};

const LABELS: Record<CeleryStatus, string> = {
  SUCCESS: "complete",
  FAILURE: "failed",
  PROGRESS: "running",
  PENDING: "queued",
};

export default function StatusBadge({ status }: { status: CeleryStatus }) {
  return (
    <span
      className={`inline-block rounded px-2 py-0.5 text-xs font-medium ${STYLES[status]}`}
    >
      {LABELS[status]}
    </span>
  );
}
