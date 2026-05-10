import { Badge } from "@/components/ui/badge";
import type { TaskStatus } from "@/types/workflow";

const styles: Record<TaskStatus, string> = {
  queued: "bg-gray-100 text-gray-700",
  running: "bg-blue-100 text-blue-700",
  blocked: "bg-amber-100 text-amber-700",
  completed: "bg-emerald-100 text-emerald-700",
  failed: "bg-red-100 text-red-700",
};

export function StatusBadge({ status }: { status: TaskStatus }) {
  return <Badge className={styles[status]}>{status}</Badge>;
}
