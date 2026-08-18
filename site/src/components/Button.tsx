import { Link } from "react-router-dom";
import { BOT_URL } from "@/data/content";
import { cn } from "@/lib/utils";

type ButtonProps = {
  children: React.ReactNode;
  href?: string;
  to?: string;
  onClick?: () => void;
  variant?: "primary" | "ghost" | "quiet";
  className?: string;
  type?: "button" | "submit";
  disabled?: boolean;
  external?: boolean;
};

export function Button({
  children,
  href,
  to,
  onClick,
  variant = "primary",
  className,
  type = "button",
  disabled,
  external,
}: ButtonProps) {
  const classes = cn("btn", `btn-${variant}`, className);

  if (to) {
    return (
      <Link className={classes} to={to} onClick={onClick}>
        {children}
      </Link>
    );
  }

  if (href) {
    return (
      <a
        className={classes}
        href={href}
        onClick={onClick}
        {...(external || href.startsWith("http")
          ? { target: "_blank", rel: "noopener noreferrer" }
          : {})}
      >
        {children}
      </a>
    );
  }

  return (
    <button className={classes} type={type} onClick={onClick} disabled={disabled}>
      {children}
    </button>
  );
}

export function TelegramButton({
  children = "Написать Агоре",
  variant = "primary",
}: {
  children?: React.ReactNode;
  variant?: "primary" | "ghost";
}) {
  return (
    <Button href={BOT_URL} variant={variant} external>
      {children}
    </Button>
  );
}
