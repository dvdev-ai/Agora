import { ATMOSPHERE_LINES } from "@/data/samples";

export function AtmosphereMarquee() {
  const line = [...ATMOSPHERE_LINES, ...ATMOSPHERE_LINES];
  return (
    <div className="marquee" aria-hidden="true">
      <div className="marquee__track">
        {line.map((item, index) => (
          <span key={`${item}-${index}`}>{item}</span>
        ))}
      </div>
    </div>
  );
}
