interface Props {
  label?: string;
  title: string;
  accent?: string;
  subtitle?: string;
}

export function PageHeader({ label, title, accent, subtitle }: Props) {
  return (
    <header className="mb-10 animate-reveal-up">
      {label && <p className="mesh-label mb-4">{label}</p>}
      <h1 className="mesh-hero-title">
        {title}
        {accent && (
          <>
            <br />
            <span className="mesh-hero-accent">{accent}</span>
          </>
        )}
      </h1>
      {subtitle && (
        <p className="mt-4 text-sm max-w-xl" style={{ color: "var(--mesh-muted)" }}>
          {subtitle}
        </p>
      )}
    </header>
  );
}
