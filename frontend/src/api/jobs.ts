import apiClient from "./client";

import type {
  BatchPredictResponse,
  ModelName,
  PredictResponse,
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

export function parseSequencesFromFasta(text: string): string[] {
  return text
    .split(/^>/m)
    .filter((block) => block.trim().length > 0)
    .map((block) => block.split("\n").slice(1).join("").trim().toUpperCase());
}
