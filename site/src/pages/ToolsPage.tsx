import { PageHero, Reveal, SectionHeading } from "@/components/Reveal";
import { CheckupDemo } from "@/components/CheckupDemo";
import { IdeaDemo } from "@/components/IdeaDemo";
import { CommandReference } from "@/components/CommandReference";
import { FEATURES } from "@/data/content";
import { TelegramButton, Button } from "@/components/Button";
import { usePageMeta } from "@/hooks/usePageMeta";

export function ToolsPage() {
  usePageMeta(
    "Инструменты",
    "Команды Агоры, демо чек-апа и разгон идей — локально на сайте."
  );

  return (
    <>
      <PageHero
        eyebrow="Инструменты"
        title="Структура, когда она нужна"
        lead="Можно просто писать. А можно опереться на короткие команды — здесь их можно потрогать руками."
      />

      <CommandReference />

      <Reveal as="section" className="section-tight">
        <div className="container feature-deep">
          {FEATURES.map((feature) => (
            <article key={feature.id} className="feature-block">
              <p className="feature-block__cmd">{feature.command}</p>
              <h2>{feature.title}</h2>
              <p>{feature.body}</p>
              <ul>
                {feature.beats.map((beat) => (
                  <li key={beat}>{beat}</li>
                ))}
              </ul>
            </article>
          ))}
        </div>
      </Reveal>

      <Reveal as="section" className="section">
        <div className="container" style={{ marginBottom: "1.5rem" }}>
          <SectionHeading
            eyebrow="Интерактив"
            title="Чек-ап на сайте"
            lead="Пройди поток как в боте. История сохранится локально в браузере."
          />
        </div>
        <CheckupDemo />
      </Reveal>

      <Reveal as="section" className="section">
        <div className="container" style={{ marginBottom: "1.5rem" }}>
          <SectionHeading
            eyebrow="Интерактив"
            title="Разгон идеи"
            lead="Формат /idea: три угла. В боте это делает модель, здесь — локальный набросок."
          />
        </div>
        <IdeaDemo />
      </Reveal>

      <Reveal as="section" className="cta-band container">
        <p className="display">Дальше — в Telegram</p>
        <p>Там живой ответ, голос и память диалога.</p>
        <div
          style={{
            display: "flex",
            gap: "0.8rem",
            justifyContent: "center",
            flexWrap: "wrap",
          }}
        >
          <TelegramButton />
          <Button to="/start" variant="ghost">
            Как начать
          </Button>
        </div>
      </Reveal>
    </>
  );
}
