import { useLayoutEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { submitBatch, parseSequencesFromFasta } from "../api/jobs";
import {
  MODEL_OPTIONS,
  type ModelName,
  type BatchPredictResponse,
} from "../types/job";

export default function Processor() {
  const [sequenceText, setSequenceText] = useState(">seq1\n");
  const [modelName, setModelName] = useState<ModelName>("hyenadna");
  const [status, setStatus] = useState<
    "idle" | "submitting" | "done" | "error"
  >("idle");
  const [job, setJob] = useState<BatchPredictResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const textareaRef = useRef<HTMLTextAreaElement | null>(null);
  const pendingCursorRef = useRef<number | null>(null);

  useLayoutEffect(() => {
    if (pendingCursorRef.current !== null && textareaRef.current) {
      const pos = pendingCursorRef.current;
      textareaRef.current.setSelectionRange(pos, pos);
      pendingCursorRef.current = null;
    }
  }, [sequenceText]);

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key !== "Enter") return;
    e.preventDefault();

    const textarea = e.currentTarget;
    const { selectionStart, selectionEnd, value } = textarea;
    const before = value.slice(0, selectionStart);
    const after = value.slice(selectionEnd);

    const lastLine = before.slice(before.lastIndexOf("\n") + 1);
    const isHeaderLine = lastLine.trim().startsWith(">");
    const hasContent = lastLine.trim().length > 0;

    let insertion = "\n";

    if (hasContent && !isHeaderLine) {
      const existingHeaders = (before.match(/^>/gm) || []).length;
      insertion = `\n>seq${existingHeaders + 1}\n`;
    }

    const newValue = before + insertion + after;
    pendingCursorRef.current = before.length + insertion.length;
    setSequenceText(newValue);
  }

  async function handleSubmit() {
    setStatus("submitting");
    setErrorMessage(null);
    try {
      const sequences = parseSequencesFromFasta(sequenceText);
      if (sequences.length === 0) {
        throw new Error("Enter at least on sequence in fasta format");
      }
      const res = await submitBatch(sequences, modelName);
      setJob(res);
      setStatus("done");
    } catch (err) {
      setErrorMessage(
        err instanceof Error ? err.message : "Job failed to submit",
      );
      setStatus("error");
    }
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-8">
      <div className="rounded-xl border border-gray-200 bg-white p-5">
        <p className="text-sm font-medium text-gray-900">Submit a job</p>
        <p className="mt-1 text-xs text-gray-500">
          Paste sequences in FASTA format (max 100 per batch).
        </p>

        <textarea
          rows={6}
          placeholder={">seq1\nATGCGTACCTGACTG..."}
          value={sequenceText}
          onChange={(e) => setSequenceText(e.target.value)}
          onKeyDown={handleKeyDown}
          className="mt-3 w-full rounded border border-gray-300 p-2 font-mono text-sm"
        />

        <div className="mt-3 flex items-center justify-between">
          <label className="text-xs text-gray-500">Model</label>
          <select
            value={modelName}
            onChange={(e) => setModelName(e.target.value as ModelName)}
            className="rounded border border-gray-300 px-2 py-1 text-sm"
          >
            {MODEL_OPTIONS.map((m) => (
              <option key={m.value} value={m.value}>
                {m.label}
              </option>
            ))}
          </select>
        </div>

        <button
          onClick={handleSubmit}
          disabled={status === "submitting" || sequenceText.trim().length === 0}
          className="mt-4 w-full rounded bg-gray-900 py-2 text-sm font-medium text-white hover:bg-gray-800 disabled:opacity-40"
        >
          {status === "submitting" ? "Submitting…" : "Run job"}
        </button>
      </div>

      {status === "done" && job && (
        <div className="mt-4 flex items-center justify-between rounded bg-green-50 px-4 py-3">
          <span className="text-sm text-green-800">Job submitted</span>
          <Link
            to={`/history/${job.task_id}`}
            className="text-sm font-medium text-green-800 underline"
          >
            View job {job.task_id.slice(0, 8)}… →
          </Link>
        </div>
      )}

      {status === "error" && errorMessage && (
        <div className="mt-4 rounded bg-red-50 px-4 py-3 text-sm text-red-800">
          {errorMessage}
        </div>
      )}
    </div>
  );
}
