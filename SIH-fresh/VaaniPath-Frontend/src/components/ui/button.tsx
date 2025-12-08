import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-base font-medium transition-colors focus-visible:outline-none focus-visible:ring-3 focus-visible:ring-primary focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 disabled:cursor-not-allowed [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90 active:bg-primary/95 shadow-sm",
        destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90 active:bg-destructive/95 shadow-sm",
        outline: "border-2 border-primary bg-background text-primary hover:bg-primary/5 active:bg-primary/10",
        secondary: "border-2 border-secondary-foreground/20 bg-secondary text-secondary-foreground hover:bg-secondary/80 active:bg-secondary/90",
        ghost: "hover:bg-accent/10 hover:text-accent-foreground active:bg-accent/20",
        link: "text-primary underline-offset-4 hover:underline focus-visible:ring-offset-0",
        success: "bg-success text-success-foreground hover:bg-success/90 active:bg-success/95 shadow-sm",
        warning: "bg-warning text-warning-foreground hover:bg-warning/90 active:bg-warning/95 shadow-sm",
      },
      size: {
        default: "h-11 min-h-[44px] px-4 py-2",
        sm: "h-10 min-h-[40px] px-3 text-sm",
        lg: "h-12 min-h-[48px] px-6 text-lg",
        icon: "h-11 w-11 min-h-[44px] min-w-[44px]",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  },
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
  VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";
    return <Comp className={cn(buttonVariants({ variant, size, className }))} ref={ref} {...props} />;
  },
);
Button.displayName = "Button";

export { Button, buttonVariants };
