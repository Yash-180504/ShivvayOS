import { cn } from "@/lib/utils";

type BadgeProps = {
  className?: string;
  children: React.ReactNode;
};

export function Badge({ className, children }: BadgeProps) {
  return <span className={cn("inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium", className)}>{children}</span>;
}
