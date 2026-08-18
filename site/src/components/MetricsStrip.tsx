import { HOME_METRICS } from "@/data/samples";
import { Reveal } from "@/components/Reveal";

export function MetricsStrip() {
  return (
    <Reveal as="section" className="section-tight">
      <div className="container metrics">
        {HOME_METRICS.map((metric) => (
          <div key={metric.label} className="metric">
            <div className="metric__label">{metric.label}</div>
            <div className="metric__value">{metric.value}</div>
            <div className="metric__hint">{metric.hint}</div>
          </div>
        ))}
      </div>
    </Reveal>
  );
}
