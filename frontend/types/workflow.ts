export type TaskStatus = "queued" | "running" | "blocked" | "completed" | "failed";

export type WorkflowRunListItem = {
  id: string;
  goal: string;
  status: TaskStatus;
  started_at: string;
  completed_at: string | null;
  created_at: string;
};

export type TaskExecutionRecord = {
  id: string;
  workflow_run_id: string;
  task_type: string;
  assigned_agent: string;
  status: TaskStatus;
  started_at: string | null;
  completed_at: string | null;
  output_json: Record<string, unknown> | null;
  confidence_score: number | null;
  error_code: string | null;
  error_message: string | null;
  failed_at: string | null;
};

export type WorkflowEventRecord = {
  id: string;
  workflow_run_id: string;
  event_type: string;
  timestamp: string;
  message: string;
};

export type WorkflowRunDetailResponse = {
  workflow: WorkflowRunListItem;
  executive_summary: Record<string, unknown> | null;
  tasks: TaskExecutionRecord[];
  timeline: WorkflowEventRecord[];
};

export type RunWorkflowRequest = {
  goal: string;
};

export type RunWorkflowResponse = {
  run_id: string;
};
