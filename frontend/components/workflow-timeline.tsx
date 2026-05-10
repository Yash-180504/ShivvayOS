import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { WorkflowEventRecord } from "@/types/workflow";

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleString();
}

export function WorkflowTimeline({ events }: { events: WorkflowEventRecord[] }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Execution Timeline</CardTitle>
      </CardHeader>
      <CardContent>
        <ol className="space-y-3">
          {events.map((event) => (
            <li key={event.id} className="rounded-md border p-3">
              <div className="text-sm font-medium">{event.event_type}</div>
              <div className="text-xs text-muted-foreground">{formatDate(event.timestamp)}</div>
              <p className="mt-1 text-sm">{event.message}</p>
            </li>
          ))}
        </ol>
      </CardContent>
    </Card>
  );
}
