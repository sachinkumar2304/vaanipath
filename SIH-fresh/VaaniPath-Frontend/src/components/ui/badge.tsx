import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center gap-1 rounded-md border-2 px-3 py-1 text-sm font-semibold transition-colors focus:outline-none focus:ring-3 focus:ring-primary focus:ring-offset-2",
  {
    variants: {
      variant: {
        default: "border-primary/30 bg-primary/10 text-primary",
        secondary: "border-secondary-foreground/30 bg-secondary text-secondary-foreground",
        destructive: "border-destructive/30 bg-destructive/10 text-destructive",
        success: "border-success/30 bg-success/10 text-success",
        warning: "border-warning/30 bg-warning/20 text-warning-foreground",
        info: "border-info/30 bg-info/10 text-info",
        outline: "border-border bg-background text-foreground",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  },
);

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement>, VariantProps<typeof badgeVariants> { }

function Badge({ className, variant, ...props }: BadgeProps) {
  return <div className={cn(badgeVariants({ variant }), className)} {...props} />;
}

export { Badge, badgeVariants };
