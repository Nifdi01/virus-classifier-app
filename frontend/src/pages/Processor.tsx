import { useLayoutEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import apiClient from "../api/client";
import {
  MODEL_OPTIONS,
  type ModelName,
  type BatchPredictResponse,
} from "../types/job";

export default function Processor() {
  const [sequenceText, setSequenceText] = useState(">seq1\n");
  const [file, setFile] = useState<File | null>(null);
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

  function handleFileChange(e: React.ChangeEvent<HTMLInputElement>) {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
    }
  }

  function handleDrop(e: React.DragEvent<HTMLLabelElement>) {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      setFile(e.dataTransfer.files[0]);
    }
  }

  function handleDragOver(e: React.DragEvent<HTMLLabelElement>) {
    e.preventDefault();
  }

  async function handleSubmit() {
    setStatus("submitting");
    setErrorMessage(null);

    try {
      if (file) {
        const formData = new FormData();
        formData.append("file", file);
        formData.append("model_name", modelName);

        try {
          const { data } = await apiClient.post<BatchPredictResponse>(
            "/batch/upload",
            formData,
          );
          setJob(data);
          setStatus("done");
        } catch (err) {
          setErrorMessage(
            err instanceof Error ? err.message : "File upload failed",
          );
          setStatus("error");
        }
      }
    } catch (err) {
      setErrorMessage(
        err instanceof Error ? err.message : "Job failed to submit",
      );
      setStatus("error");
    }
  }

  const isSubmitDisabled =
    status === "submitting" || (!file && sequenceText.trim().length === 0);

  return (
    <div className="mx-auto max-w-2xl px-4 py-8">
      <div className="container mx-auto flex items-center justify-center flex-col">
        <img
          className="lg:w-1/4 md:w-3/6 w-5/6 object-center"
          alt="Nucleotide sequence classifier banner"
          src="/processor.svg"
        />
        <p className="text-3xl mb-5 font-medium text-gray-900">
          Sequence Processor
        </p>
      </div>

      <div className="rounded-xl border border-gray-200 bg-white p-5">
        <p className="text-sm font-medium text-gray-900">Submit a job</p>
        <p className="mt-1 text-xs text-gray-500">
          Paste sequences in FASTA format or upload a file.
        </p>

        <textarea
          ref={textareaRef}
          rows={6}
          placeholder={">seq1\nATGCGTACCTGACTG..."}
          value={sequenceText}
          onChange={(e) => setSequenceText(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={file !== null}
          className="mt-3 w-full rounded border border-gray-300 p-2 font-mono text-sm disabled:bg-gray-100 disabled:text-gray-400"
        />

        <div className="my-6 flex items-center">
          <div className="flex-grow border-t border-gray-200"></div>
          <span className="mx-4 text-xs text-gray-400 font-medium uppercase">
            Or
          </span>
          <div className="flex-grow border-t border-gray-200"></div>
        </div>

        <div className="flex items-center justify-center w-full">
          <label
            htmlFor="dropzone-file"
            onDrop={handleDrop}
            onDragOver={handleDragOver}
            className={`flex flex-col items-center justify-center w-full h-64 border border-dashed rounded-base cursor-pointer hover:bg-neutral-tertiary-medium ${
              file
                ? "bg-indigo-50 border-indigo-500"
                : "bg-neutral-secondary-medium border-default-strong"
            }`}
          >
            <div className="flex flex-col items-center justify-center text-body pt-5 pb-6">
              <svg
                className="w-8 h-8 mb-4"
                aria-hidden="true"
                xmlns="http://www.w3.org/2000/svg"
                width="24"
                height="24"
                fill="none"
                viewBox="0 0 24 24"
              >
                <path
                  stroke="currentColor"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M15 17h3a3 3 0 0 0 0-6h-.025a5.56 5.56 0 0 0 .025-.5A5.5 5.5 0 0 0 7.207 9.021C7.137 9.017 7.071 9 7 9a4 4 0 1 0 0 8h2.167M12 19v-9m0 0-2 2m2-2 2 2"
                />
              </svg>
              <p className="mb-2 text-sm">
                <span className="font-semibold">Click to upload</span> or drag
                and drop
              </p>
              <p className="text-xs text-center px-4">
                {file ? (
                  <span className="text-indigo-600 font-medium">
                    {file.name}
                  </span>
                ) : (
                  "FASTA, FAS, FA or TXT (MAX. 100 sequences)"
                )}
              </p>
            </div>
            <input
              id="dropzone-file"
              type="file"
              accept=".fasta,.fas,.fa,.txt"
              onChange={handleFileChange}
              className="hidden"
            />
          </label>
        </div>

        {file && (
          <div className="mt-2 flex justify-end">
            <button
              onClick={() => setFile(null)}
              className="text-xs text-red-500 hover:text-red-700 font-medium cursor-pointer bg-transparent border-0"
            >
              Remove file
            </button>
          </div>
        )}

        <div className="mt-6 flex items-center justify-between">
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
          disabled={isSubmitDisabled}
          className="mt-4 w-full text-white bg-indigo-500 border-0 py-2 px-6 focus:outline-none hover:bg-indigo-600 rounded text-lg cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
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
            View job {job.task_id.toString().slice(0, 8)}… →
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
