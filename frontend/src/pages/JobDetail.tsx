import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { fetchBatchStatus, pollBatchStatus } from "../api/jobs";
import type { BatchPredictResponse } from "../types/job";
import StatusBadge from "../components/StatusBadge";

export default function JobDetail() {
  const { jobId } = useParams<{ jobId: string }>();
  const [job, setJob] = useState<BatchPredictResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [expandedRow, setExpandedRow] = useState<number | null>(null);

  useEffect(() => {
    if (!jobId) return;
    let cancel: (() => void) | undefined;

    fetchBatchStatus(jobId)
      .then((res) => {
        setJob(res);
        if (res.status === "PENDING" || res.status === "PROGRESS") {
          cancel = pollBatchStatus(jobId, setJob);
        }
      })
      .catch((err) => setErrorMessage(err.message));

    return () => cancel?.();
  }, [jobId]);

  if (errorMessage) {
    return (
      <p className="mx-auto max-w-2xl px-4 py-8 text-sm text-red-600">
        {errorMessage}
      </p>
    );
  }
  if (!job) {
    return (
      <p className="mx-auto max-w-2xl px-4 py-8 text-sm text-gray-400">
        Loading…
      </p>
    );
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-8">
      <Link
        to="/history"
        className="mb-3 inline-block text-sm text-gray-500 hover:underline"
      >
        ← Back to history
      </Link>

      <div className="rounded-xl border border-gray-200 bg-white p-5">
        <div className="mb-3 flex items-center justify-between">
          <p className="text-sm font-medium text-gray-900">
            Job {job.task_id.slice(0, 8)}…
          </p>
          <StatusBadge status={job.status} />
        </div>

        {job.status === "PROGRESS" && job.progress && (
          <div className="mb-4">
            <div className="h-2 w-full overflow-hidden rounded bg-gray-100">
              <div
                className="h-full bg-gray-900 transition-all"
                style={{
                  width: `${
                    job.progress.total > 0
                      ? (job.progress.current / job.progress.total) * 100
                      : 0
                  }%`,
                }}
              />
            </div>
            <p className="mt-1 text-xs text-gray-500">
              {job.progress.current} / {job.progress.total} sequences
            </p>
          </div>
        )}

        {job.status === "PENDING" && (
          <p className="text-sm text-gray-500">
            Waiting for a worker to pick this up…
          </p>
        )}

        {job.status === "FAILURE" && (
          <p className="text-sm text-red-600">
            Job failed. Check the worker logs.
          </p>
        )}

        {job.status === "SUCCESS" && job.results && (
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-gray-500">
                <th className="pb-1 font-medium">#</th>
                <th className="pb-1 font-medium">Influenza type</th>
                <th className="pb-1 font-medium">Length</th>
                <th className="pb-1 font-medium">Model</th>
                <th className="pb-1 text-right font-medium">Confidence</th>
              </tr>
            </thead>
            <tbody>
              {job.results.map((r) => {
                const isExpanded = expandedRow === r.sequence_index;
                return (
                  <>
                    <tr
                      key={r.sequence_index}
                      onClick={() =>
                        setExpandedRow(isExpanded ? null : r.sequence_index)
                      }
                      className="cursor-pointer border-t border-gray-100 hover:bg-gray-50"
                    >
                      <td className="py-1.5 font-mono">{r.sequence_index}</td>
                      <td className="py-1.5">{r.influenza_type}</td>
                      <td className="py-1.5">{r.sequence_length} bp</td>
                      <td className="py-1.5 text-gray-500">{r.model_used}</td>
                      <td className="py-1.5 text-right">
                        {(r.confidence * 100).toFixed(1)}%
                      </td>
                    </tr>
                    {isExpanded && (
                      <tr
                        key={`${r.sequence_index}-detail`}
                        className="border-t border-gray-50 bg-gray-50"
                      >
                        <td colSpan={5} className="px-2 py-2">
                          <div className="flex flex-wrap gap-2">
                            {Object.entries(r.scores)
                              .sort(([, a], [, b]) => b - a)
                              .map(([cls, score]) => (
                                <span
                                  key={cls}
                                  className="rounded bg-white px-2 py-1 text-xs text-gray-600 ring-1 ring-gray-200"
                                >
                                  {cls}: {(score * 100).toFixed(1)}%
                                </span>
                              ))}
                          </div>
                        </td>
                      </tr>
                    )}
                  </>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
