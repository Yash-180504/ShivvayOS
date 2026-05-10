"use client";

import { FormEvent, useState } from "react";
import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { workflowApi } from "@/lib/api/client";

export function GoalSubmissionForm() {
  const router = useRouter();
  const [goal, setGoal] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!goal.trim()) return;

    setIsSubmitting(true);
    setError(null);
    try {
      const response = await workflowApi.runWorkflow({ goal: goal.trim() });
      router.push(`/workflows/${response.run_id}`);
    } catch (submissionError) {
      setError(submissionError instanceof Error ? submissionError.message : "Failed to submit workflow goal");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Submit Business Goal</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={onSubmit} className="flex flex-col gap-3 sm:flex-row sm:items-center">
          <Input
            placeholder="Example: Improve company revenue through channel optimization"
            value={goal}
            onChange={(event) => setGoal(event.target.value)}
          />
          <Button type="submit" disabled={isSubmitting || !goal.trim()}>
            {isSubmitting ? "Launching..." : "Run Workflow"}
          </Button>
        </form>
        {error ? <p className="mt-3 text-sm text-red-600">{error}</p> : null}
      </CardContent>
    </Card>
  );
}
