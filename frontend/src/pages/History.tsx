import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { fetchJobs } from "../api/jobs";
import type { JobSummary } from "../types/job";
import StatusBadge from "../components/StatusBadge";

const PAGE_SIZE = 10;

function formatBytes(bytes: number | null): string {
  if (bytes === null) return "-";
  if (bytes < 1024) return `${bytes} B`;

  return `${(bytes / 1024).toFixed(1)} KB`;
}

export default function History() {
  const [jobs, setJobs] = useState<JobSummary[]>([]);
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);
  const [loading, setLoading] = useState(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    setLoading(true);

    fetchJobs(PAGE_SIZE, offset)
      .then((res) => {
        if (!mounted) return;
        setJobs(res.jobs);
        setTotal(res.total);
      })
      .catch((err) => mounted && setErrorMessage(err.message))
      .finally(() => mounted && setLoading(false));
    return () => {
      mounted = false;
    };
  }, [offset]);
  const canPrev = offset > 0;
  const canNext = offset + PAGE_SIZE < total;

  return (
    <div className="mx-auto max-w-3xl px-4 py-8">
      <div className="mb-3 flex items-center justify-between">
        <p className="text-sm font-medium text-gray-900">Job history</p>
        {!loading && <p className="text-xs text-gray-400">{total} total</p>}
      </div>

      {loading && <p className="text-sm text-gray-400">Loading…</p>}
      {errorMessage && <p className="text-sm text-red-600">{errorMessage}</p>}

      {!loading && !errorMessage && (
        <>
          <div className="overflow-hidden rounded border border-gray-200">
            <table className="w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-3 py-2 text-left font-medium text-gray-700">
                    Job ID
                  </th>
                  <th className="px-3 py-2 text-left font-medium text-gray-700">
                    Submitted
                  </th>
                  <th className="px-3 py-2 text-left font-medium text-gray-700">
                    Model
                  </th>
                  <th className="px-3 py-2 text-left font-medium text-gray-700">
                    Sequences
                  </th>
                  <th className="px-3 py-2 text-left font-medium text-gray-700">
                    File size
                  </th>
                  <th className="px-3 py-2 text-left font-medium text-gray-700">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody>
                {jobs.map((job) => (
                  <tr
                    key={job.task_id}
                    className="border-t border-gray-100 hover:bg-gray-50"
                  >
                    <td className="px-3 py-2">
                      <Link
                        to={`/history/${job.task_id}`}
                        className="font-mono text-blue-600 hover:underline"
                      >
                        {job.task_id.slice(0, 8)}…
                      </Link>
                    </td>
                    <td className="px-3 py-2 text-gray-500">
                      {new Date(job.submitted_at).toLocaleString()}
                    </td>
                    <td className="px-3 py-2 text-gray-500">
                      {job.model_name}
                    </td>
                    <td className="px-3 py-2">{job.sequence_count}</td>
                    <td className="px-3 py-2">
                      {formatBytes(job.file_size_bytes)}
                    </td>
                    <td className="px-3 py-2">
                      <StatusBadge status={job.status} />
                    </td>
                  </tr>
                ))}
                {jobs.length === 0 && (
                  <tr>
                    <td
                      colSpan={6}
                      className="px-3 py-6 text-center text-gray-400"
                    >
                      No jobs yet.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>

          {total > PAGE_SIZE && (
            <div className="mt-3 flex items-center justify-between text-sm">
              <button
                onClick={() =>
                  setOffset((o: number) => Math.max(0, o - PAGE_SIZE))
                }
                disabled={!canPrev}
                className="rounded border border-gray-300 px-3 py-1 text-gray-700 disabled:opacity-40"
              >
                ← Prev
              </button>
              <span className="text-gray-400">
                {offset + 1}–{Math.min(offset + PAGE_SIZE, total)} of {total}
              </span>
              <button
                onClick={() => setOffset((o: number) => o + PAGE_SIZE)}
                disabled={!canNext}
                className="rounded border border-gray-300 px-3 py-1 text-gray-700 disabled:opacity-40"
              >
                Next →
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
