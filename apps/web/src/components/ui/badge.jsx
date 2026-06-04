import * as React from "react";
import { cn } from "@/lib/utils";

const Badge = React.forwardRef(({ className, variant = "default", ...props }, ref) => {
  const variants = {
    default: "bg-sembriaia-action/10 text-sembriaia-action border-sembriaia-action/20",
    secondary: "bg-muted text-foreground border-border",
    success: "bg-sembriaia-action/15 text-sembriaia-action border-sembriaia-action/30",
    warning: "bg-sembriaia-warning/15 text-sembriaia-warning border-sembriaia-warning/30",
    destructive: "bg-sembriaia-alert/15 text-sembriaia-alert border-sembriaia-alert/30",
    info: "bg-sembriaia-water/15 text-sembriaia-water border-sembriaia-water/30",
  };
  return (
    <div
      ref={ref}
      className={cn(
        "inline-flex items-center gap-1 rounded-full border px-2.5 py-0.5 text-xs font-medium",
        variants[variant],
        className
      )}
      {...props}
    />
  );
});
Badge.displayName = "Badge";

export { Badge };
