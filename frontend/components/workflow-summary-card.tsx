import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function WorkflowSummaryCard({ summary }: { summary: Record<string, unknown> | null }) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Executive Summary</CardTitle>
      </CardHeader>
      <CardContent>
        {summary ? (
          <pre className="whitespace-pre-wrap break-words rounded-md bg-muted p-3 text-sm">
            {JSON.stringify(summary, null, 2)}
          </pre>
        ) : (
          <p className="text-sm text-muted-foreground">No executive summary available.</p>
        )}
      </CardContent>
    </Card>
  );
}
