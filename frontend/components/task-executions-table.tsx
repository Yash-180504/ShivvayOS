import { StatusBadge } from "@/components/status-badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import type { TaskExecutionRecord } from "@/types/workflow";

function formatDate(dateString: string | null): string {
  if (!dateString) return "-";
  return new Date(dateString).toLocaleString();
}

export function TaskExecutionsTable({ tasks }: { tasks: TaskExecutionRecord[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Task Executions</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Task</TableHead>
                <TableHead>Agent</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Started</TableHead>
                <TableHead>Completed</TableHead>
                <TableHead>Failure</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {tasks.map((task) => (
                <TableRow key={task.id}>
                  <TableCell>{task.task_type}</TableCell>
                  <TableCell>{task.assigned_agent}</TableCell>
                  <TableCell><StatusBadge status={task.status} /></TableCell>
                  <TableCell>{formatDate(task.started_at)}</TableCell>
                  <TableCell>{formatDate(task.completed_at)}</TableCell>
                  <TableCell className="text-sm text-red-600">{task.error_message ?? "-"}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </div>
      </CardContent>
    </Card>
  );
}
