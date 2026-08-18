import { useMemo, useState } from "react";
import { CHECKUP_LABELS } from "@/data/content";
import { useLocalStorageState } from "@/hooks/useMotion";
import {
  createCheckupId,
  DemoCheckup,
  formatScore,
  summarizeCheckups,
} from "@/lib/utils";
import { Button } from "@/components/Button";
import { cn } from "@/lib/utils";

type StepKey = (typeof CHECKUP_LABELS)[number]["key"] | "note" | "done";

const ORDER: StepKey[] = ["mood", "anxiety", "energy", "sleep", "note", "done"];

export function CheckupDemo() {
  const [items, setItems] = useLocalStorageState<DemoCheckup[]>(
    "agora.demo.checkups",
    []
  );
  const [step, setStep] = useState<StepKey>("mood");
  const [draft, setDraft] = useState<Partial<DemoCheckup>>({});
  const [note, setNote] = useState("");

  const summary = useMemo(() => summarizeCheckups(items), [items]);
  const meta = CHECKUP_LABELS.find((x) => x.key === step);

  function pickScore(value: number) {
    if (!meta) return;
    const nextDraft = { ...draft, [meta.key]: value };
    setDraft(nextDraft);
    const idx = ORDER.indexOf(step);
    setStep(ORDER[idx + 1]);
  }

  function saveNote(skip = false) {
    const entry: DemoCheckup = {
      id: createCheckupId(),
      createdAt: new Date().toISOString(),
      mood: Number(draft.mood ?? 5),
      anxiety: Number(draft.anxiety ?? 5),
      energy: Number(draft.energy ?? 5),
      sleep: Number(draft.sleep ?? 5),
      note: skip ? "" : note.trim(),
    };
    setItems((prev) => [...prev, entry].slice(-30));
    setDraft({});
    setNote("");
    setStep("done");
  }

  function resetFlow() {
    setDraft({});
    setNote("");
    setStep("mood");
  }

  function clearAll() {
    setItems([]);
    resetFlow();
  }

  return (
    <div className="panel">
      <div className="container panel-grid">
        <div className="stack">
          <div>
            <p className="eyebrow">Демо · локально в браузере</p>
            <h3 className="display" style={{ fontSize: "2rem" }}>
              Чек-ап
            </h3>
            <p className="muted" style={{ lineHeight: 1.65, marginTop: "0.6rem" }}>
              Как в боте: четыре шкалы и короткая заметка. Данные остаются только
              в твоем браузере.
            </p>
          </div>

          {meta ? (
            <div className="stack">
              <div>
                <strong>{meta.title}</strong>
                <div className="muted" style={{ marginTop: "0.25rem" }}>
                  {meta.hint}
                </div>
              </div>
              <div className="score-grid" role="group" aria-label={meta.title}>
                {Array.from({ length: 11 }, (_, n) => (
                  <button
                    key={n}
                    type="button"
                    className={cn(
                      "score-btn",
                      draft[meta.key] === n && "is-active"
                    )}
                    onClick={() => pickScore(n)}
                  >
                    {n}
                  </button>
                ))}
              </div>
              <Button variant="quiet" onClick={resetFlow}>
                Сначала
              </Button>
            </div>
          ) : null}

          {step === "note" ? (
            <div className="stack">
              <div className="field">
                <label htmlFor="checkup-note">Что сильнее всего выбило сегодня?</label>
                <textarea
                  id="checkup-note"
                  value={note}
                  onChange={(e) => setNote(e.target.value)}
                  placeholder="Одной фразой или пропусти"
                />
              </div>
              <div style={{ display: "flex", gap: "0.7rem", flexWrap: "wrap" }}>
                <Button onClick={() => saveNote(false)}>Сохранить</Button>
                <Button variant="ghost" onClick={() => saveNote(true)}>
                  Пропустить
                </Button>
              </div>
            </div>
          ) : null}

          {step === "done" ? (
            <div className="stack">
              <p style={{ margin: 0, lineHeight: 1.6 }}>
                Записал. Можно пройти еще раз или посмотреть динамику справа.
              </p>
              <div style={{ display: "flex", gap: "0.7rem", flexWrap: "wrap" }}>
                <Button onClick={resetFlow}>Еще чек-ап</Button>
                <Button variant="ghost" onClick={clearAll}>
                  Очистить демо
                </Button>
              </div>
            </div>
          ) : null}
        </div>

        <div>
          <div className="stats-box">
            <div className="stats-line">
              <span>Записей</span>
              <strong>{summary.count}</strong>
            </div>
            <div className="stats-line">
              <span>Настроение</span>
              <strong>{summary.count ? formatScore(summary.mood) : "—"}</strong>
            </div>
            <div className="stats-line">
              <span>Тревога</span>
              <strong>{summary.count ? formatScore(summary.anxiety) : "—"}</strong>
            </div>
            <div className="stats-line">
              <span>Энергия</span>
              <strong>{summary.count ? formatScore(summary.energy) : "—"}</strong>
            </div>
            <div className="stats-line">
              <span>Сон</span>
              <strong>{summary.count ? formatScore(summary.sleep) : "—"}</strong>
            </div>
          </div>
          <p className="note">{summary.trend}</p>

          <div className="history-list">
            {[...items].reverse().slice(0, 5).map((item) => (
              <div key={item.id} className="history-item">
                <strong>
                  {item.mood}/{item.anxiety}/{item.energy}/{item.sleep}
                </strong>
                {" · "}
                {new Date(item.createdAt).toLocaleString("ru-RU", {
                  day: "2-digit",
                  month: "short",
                  hour: "2-digit",
                  minute: "2-digit",
                })}
                {item.note ? ` · ${item.note}` : ""}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
