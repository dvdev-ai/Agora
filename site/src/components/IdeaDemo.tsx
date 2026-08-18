import { useMemo, useState } from "react";
import { IDEA_SEED_EXAMPLES } from "@/data/content";
import { describeIdeaMode, expandIdeaRich } from "@/lib/ideaEngine";
import { Button } from "@/components/Button";

export function IdeaDemo() {
  const [seed, setSeed] = useState(IDEA_SEED_EXAMPLES[0]);
  const [committed, setCommitted] = useState(IDEA_SEED_EXAMPLES[0]);

  const angles = useMemo(() => expandIdeaRich(committed), [committed]);

  function run(next?: string) {
    const value = (next ?? seed).trim();
    if (value.length < 3) return;
    setSeed(value);
    setCommitted(value);
  }

  return (
    <div className="panel">
      <div className="container panel-grid">
        <div className="stack">
          <div>
            <p className="eyebrow">Демо · /idea</p>
            <h3 className="display" style={{ fontSize: "2rem" }}>
              Куда может потечь мысль
            </h3>
            <p className="muted" style={{ lineHeight: 1.65, marginTop: "0.6rem" }}>
              На сайте — локальный разгон без нейросети. В боте ответ глубже и живее.
              Здесь можно почувствовать сам формат: реалистично / смело / абсурдно.
              {` ${describeIdeaMode()}`}
            </p>
          </div>

          <div className="field">
            <label htmlFor="idea-seed">Твоя мысль</label>
            <textarea
              id="idea-seed"
              value={seed}
              onChange={(e) => setSeed(e.target.value)}
              placeholder="Кинь сырую идею..."
            />
          </div>

          <div className="chip-row">
            {IDEA_SEED_EXAMPLES.map((example) => (
              <button
                key={example}
                type="button"
                className="chip"
                onClick={() => run(example)}
              >
                {example.length > 42 ? `${example.slice(0, 42)}...` : example}
              </button>
            ))}
          </div>

          <div style={{ display: "flex", gap: "0.7rem", flexWrap: "wrap" }}>
            <Button onClick={() => run()} disabled={seed.trim().length < 3}>
              Развернуть
            </Button>
            <Button
              variant="ghost"
              onClick={() => {
                setSeed("");
                setCommitted("");
              }}
            >
              Очистить
            </Button>
          </div>
        </div>

        <div className="idea-angles" aria-live="polite">
          {committed.trim().length >= 3 ? (
            angles.map((angle) => (
              <article key={angle.title} className="idea-angle">
                <h4>{angle.title}</h4>
                <p>{angle.text}</p>
              </article>
            ))
          ) : (
            <p className="muted" style={{ margin: 0, lineHeight: 1.65 }}>
              Напиши мысль слева — появятся три угла реализации.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
