export type ModelName =
  "hyenadna" | "random_forest" | "xgb" | "logistic_regression";

export type CeleryStatus = "PENDING" | "PROGRESS" | "SUCCESS" | "FAILURE";

export interface BatchProgress {
  current: number;
  total: number;
}

export interface PredictResponse {
  influenza_type: string;
  confidence: number;
  scores: Record<string, number>;
  sequence_length: number;
  model_used: string;
}

export interface PredictionResult extends PredictResponse {
  sequence_index: number;
}

export interface BatchPredictResponse {
  task_id: string;
  status: CeleryStatus;
  progress?: BatchProgress | null;
  results?: PredictionResult[] | null;
}

export interface JobSummary {
  task_id: string;
  submitted_at: string;
  sequence_count: number;
  file_size_bytes: number | null;
  model_name: ModelName;
  status: CeleryStatus;
}

export interface JobListResponse {
  jobs: JobSummary[];
  total: number;
}

export const MODEL_OPTIONS: { value: ModelName; label: string }[] = [
  { value: "hyenadna", label: "HyenaDNA" },
  { value: "random_forest", label: "Random Forest" },
  { value: "xgb", label: "XGBoost" },
  { value: "logistic_regression", label: "Logistic Regression" },
];
