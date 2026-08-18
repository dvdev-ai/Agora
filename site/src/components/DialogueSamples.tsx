import { useState } from "react";
import { DIALOGUE_SAMPLES } from "@/data/samples";
import { Reveal } from "@/components/Reveal";
import { cn } from "@/lib/utils";

export function DialogueSamples() {
  const [active, setActive] = useState(DIALOGUE_SAMPLES[0].id);
  const current =
    DIALOGUE_SAMPLES.find((item) => item.id === active) ?? DIALOGUE_SAMPLES[0];

  return (
    <Reveal as="section" className="section">
      <div className="container">
        <p className="eyebrow">Примеры тона</p>
        <h2 className="display" style={{ fontSize: "clamp(2rem, 4vw, 2.8rem)" }}>
          Как это может звучать
        </h2>
        <p className="lead">
          Не скрипт. Ориентир по духу: глубже сюжета, без ваты и без приказа.
        </p>

        <div className="chip-row" style={{ marginTop: "1.4rem" }}>
          {DIALOGUE_SAMPLES.map((sample) => (
            <button
              key={sample.id}
              type="button"
              className={cn("chip", active === sample.id && "is-active-chip")}
              onClick={() => setActive(sample.id)}
            >
              {sample.title}
            </button>
          ))}
        </div>

        <div className="sample-thread">
          <div className="sample-bubble sample-bubble--user">
            <span>Ты</span>
            <p>{current.user}</p>
          </div>
          <div className="sample-bubble sample-bubble--agora">
            <span>Агора</span>
            <p>{current.agora}</p>
          </div>
        </div>
      </div>
    </Reveal>
  );
}
