import apiClient from "./client";

import type {
  BatchPredictResponse,
  ModelName,
  PredictResponse,
  JobListResponse,
} from "../types/job";

export async function predictSinlge(
  sequence: string,
  modelName: ModelName,
): Promise<PredictResponse> {
  const { data } = await apiClient.post<PredictResponse>("/predict", {
    sequence,
    model_name: modelName,
  });
  return data;
}

export async function submitBatch(
  sequences: string[],
  modelName: ModelName,
): Promise<BatchPredictResponse> {
  const { data } = await apiClient.post<BatchPredictResponse>(
    "/batch/predict",
    {
      sequences,
      model_name: modelName,
    },
  );
  console.log(data);
  return data;
}

export async function fetchBatchStatus(
  taskId: string,
): Promise<BatchPredictResponse> {
  const { data } = await apiClient.get<BatchPredictResponse>(
    `/batch/predict/${taskId}`,
  );
  return data;
}

export function pollBatchStatus(
  taskId: string,
  onUpdate: (res: BatchPredictResponse) => void,
  intervalMs = 2000,
): () => void {
  let cancelled = false;

  const tick = async () => {
    if (cancelled) return;
    try {
      const res = await fetchBatchStatus(taskId);
      onUpdate(res);
      if (res.status === "SUCCESS" || res.status === "FAILURE") return;
    } catch {
      // just retry on next click
    }
    if (!cancelled) setTimeout(tick, intervalMs);
  };
  tick();
  return () => {
    cancelled = true;
  };
}

export async function fetchJobs(
  limit = 50,
  offset = 0,
): Promise<JobListResponse> {
  const { data } = await apiClient.get<JobListResponse>("/batch", {
    params: { limit, offset },
  });
  return data;
}

export function parseSequencesFromFasta(text: string): string[] {
  return text
    .split(/^>/m)
    .filter((block) => block.trim().length > 0)
    .map((block) => block.split("\n").slice(1).join("").trim().toUpperCase());
}
