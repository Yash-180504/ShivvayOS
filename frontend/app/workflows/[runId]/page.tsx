import Link from "next/link";
import { notFound } from "next/navigation";

import { StatusBadge } from "@/components/status-badge";
import { TaskExecutionsTable } from "@/components/task-executions-table";
import { WorkflowSummaryCard } from "@/components/workflow-summary-card";
import { WorkflowTimeline } from "@/components/workflow-timeline";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { workflowApi } from "@/lib/api/client";

type WorkflowDetailPageProps = {
  params: Promise<{ runId: string }>;
};

function formatDate(dateString: string | null): string {
  if (!dateString) return "-";
  return new Date(dateString).toLocaleString();
}

export default async function WorkflowDetailPage({ params }: WorkflowDetailPageProps) {
  const { runId } = await params;

  const [workflow, timeline] = await Promise.all([
    workflowApi.getWorkflow(runId).catch(() => null),
    workflowApi.getTimeline(runId).catch(() => []),
  ]);

  if (!workflow) {
    notFound();
  }

  return (
    <div className="space-y-6">
      <Link href="/" className="text-sm text-primary underline-offset-4 hover:underline">
        Back to dashboard
      </Link>

      <Card>
        <CardHeader>
          <CardTitle>Workflow Metadata</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          <div>
            <div className="text-xs text-muted-foreground">Run ID</div>
            <div className="text-sm font-medium">{workflow.workflow.id}</div>
          </div>
          <div>
            <div className="text-xs text-muted-foreground">Status</div>
            <StatusBadge status={workflow.workflow.status} />
          </div>
          <div>
            <div className="text-xs text-muted-foreground">Started</div>
            <div className="text-sm">{formatDate(workflow.workflow.started_at)}</div>
          </div>
          <div>
            <div className="text-xs text-muted-foreground">Completed</div>
            <div className="text-sm">{formatDate(workflow.workflow.completed_at)}</div>
          </div>
          <div className="sm:col-span-2 lg:col-span-3">
            <div className="text-xs text-muted-foreground">Goal</div>
            <div className="text-sm font-medium">{workflow.workflow.goal}</div>
          </div>
        </CardContent>
      </Card>

      <WorkflowSummaryCard summary={workflow.executive_summary} />
      <TaskExecutionsTable tasks={workflow.tasks} />
      <WorkflowTimeline events={timeline.length ? timeline : workflow.timeline} />
    </div>
  );
}
