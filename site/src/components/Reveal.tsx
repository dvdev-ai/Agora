import { useReveal } from "@/hooks/useMotion";
import { cn } from "@/lib/utils";

export function Reveal({
  children,
  className,
  as: Tag = "div",
}: {
  children: React.ReactNode;
  className?: string;
  as?: "div" | "section" | "article" | "ul" | "li";
}) {
  const { ref, visible } = useReveal<HTMLElement>();
  return (
    <Tag ref={ref as never} className={cn("reveal", visible && "is-visible", className)}>
      {children}
    </Tag>
  );
}

export function PageHero({
  eyebrow,
  title,
  lead,
}: {
  eyebrow?: string;
  title: string;
  lead: string;
}) {
  return (
    <div className="page-hero container">
      {eyebrow ? <p className="eyebrow">{eyebrow}</p> : null}
      <h1>{title}</h1>
      <p className="lead">{lead}</p>
    </div>
  );
}

export function SectionHeading({
  eyebrow,
  title,
  lead,
}: {
  eyebrow?: string;
  title: string;
  lead?: string;
}) {
  return (
    <div style={{ marginBottom: "1.8rem" }}>
      {eyebrow ? <p className="eyebrow">{eyebrow}</p> : null}
      <h2 className="display" style={{ fontSize: "clamp(2rem, 4vw, 2.8rem)" }}>
        {title}
      </h2>
      {lead ? <p className="lead">{lead}</p> : null}
    </div>
  );
}
