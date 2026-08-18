import { FEATURES } from "@/data/content";
import { Reveal } from "@/components/Reveal";
import { TelegramButton, Button } from "@/components/Button";

export function FeatureRail() {
  return (
    <Reveal as="section" className="section">
      <div className="container">
        <p className="eyebrow">Что умеет</p>
        <h2 className="display" style={{ fontSize: "clamp(2rem, 4vw, 2.8rem)" }}>
          Не кабинет. Переписка.
        </h2>
        <p className="lead">
          Пиши как есть. Если нужна структура — есть короткие команды.
        </p>

        <ul className="rail" style={{ marginTop: "2rem" }}>
          {FEATURES.map((feature) => (
            <li key={feature.id} className="rail__item">
              <div className="rail__command">{feature.command}</div>
              <div>
                <h3 className="rail__title">{feature.title}</h3>
                <p className="rail__text">{feature.teaser}</p>
              </div>
            </li>
          ))}
        </ul>

        <div style={{ display: "flex", gap: "0.8rem", flexWrap: "wrap", marginTop: "1.8rem" }}>
          <TelegramButton />
          <Button to="/dialogue" variant="ghost">
            Как устроен диалог
          </Button>
        </div>
      </div>
    </Reveal>
  );
}
