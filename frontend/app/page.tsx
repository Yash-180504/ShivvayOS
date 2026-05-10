import { GoalSubmissionForm } from "@/components/goal-submission-form";
import { WorkflowRunsTable } from "@/components/workflow-runs-table";
import { workflowApi } from "@/lib/api/client";

export default async function DashboardPage() {
  const runs = await workflowApi.listWorkflows().catch(() => []);

  return (
    <div className="space-y-6">
      <header>
        <h1 className="text-2xl font-semibold">ShivvayOS Workflow Dashboard</h1>
        <p className="text-sm text-muted-foreground">Monitor autonomous workflows and execution outcomes.</p>
      </header>
      <GoalSubmissionForm />
      <WorkflowRunsTable runs={runs} />
    </div>
  );
}
