import type {
  RunWorkflowRequest,
  WorkflowEventRecord,
  WorkflowRunDetailResponse,
  WorkflowRunListItem,
  RunWorkflowResponse,
  TaskExecutionRecord,
} from "@/types/workflow";

const PUBLIC_API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
const INTERNAL_API_BASE_URL = process.env.INTERNAL_API_BASE_URL ?? PUBLIC_API_BASE_URL;

function getApiBaseUrl(): string {
  return typeof window === "undefined" ? INTERNAL_API_BASE_URL : PUBLIC_API_BASE_URL;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${getApiBaseUrl()}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
    cache: "no-store",
  });

  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as { error_message?: string } | null;
    throw new Error(payload?.error_message ?? `Request failed with ${response.status}`);
  }

  return (await response.json()) as T;
}

export const workflowApi = {
  listWorkflows: () => request<WorkflowRunListItem[]>("/api/v1/workflows"),
  getWorkflow: (runId: string) => request<WorkflowRunDetailResponse>(`/api/v1/workflows/${runId}`),
  getTimeline: (runId: string) => request<WorkflowEventRecord[]>(`/api/v1/workflows/${runId}/timeline`),
  getTask: (taskId: string) => request<TaskExecutionRecord>(`/api/v1/tasks/${taskId}`),
  runWorkflow: (payload: RunWorkflowRequest) =>
    request<RunWorkflowResponse>("/api/v1/workflows/run", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
};
