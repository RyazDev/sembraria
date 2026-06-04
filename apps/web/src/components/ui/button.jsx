import * as React from "react";
import { cn } from "@/lib/utils";

const variantClasses = {
  default: "bg-sembriaia-action text-white hover:bg-[#00B248] shadow-sm",
  primary: "bg-sembriaia-primary text-white hover:bg-[#154a18] shadow-sm",
  outline:
    "border border-input bg-background hover:bg-accent hover:text-accent-foreground",
  ghost: "hover:bg-accent hover:text-accent-foreground",
  destructive: "bg-sembriaia-alert text-white hover:bg-[#b02525]",
  link: "text-sembriaia-water underline-offset-4 hover:underline",
  secondary:
    "bg-white border border-sembriaia-primary text-sembriaia-primary hover:bg-sembriaia-primary hover:text-white",
};

const sizeClasses = {
  default: "h-10 px-4 py-2",
  sm: "h-9 rounded-md px-3",
  lg: "h-12 rounded-lg px-8 text-base",
  xl: "h-14 rounded-full px-10 text-base font-semibold",
  icon: "h-10 w-10",
};

const Button = React.forwardRef(
  ({ className, variant = "default", size = "default", asChild, children, ...props }, ref) => {
    if (asChild && React.isValidElement(children)) {
      return React.cloneElement(children, {
        ...props,
        ref,
        className: cn(
          "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sembriaia-action focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
          variantClasses[variant],
          sizeClasses[size],
          children.props.className,
          className
        ),
      });
    }
    return (
      <button
        ref={ref}
        className={cn(
          "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-sembriaia-action focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
          variantClasses[variant],
          sizeClasses[size],
          className
        )}
        {...props}
      >
        {children}
      </button>
    );
  }
);
Button.displayName = "Button";

export { Button };
