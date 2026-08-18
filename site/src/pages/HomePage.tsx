import { Hero } from "@/components/Hero";
import { FeatureRail } from "@/components/FeatureRail";
import { Reveal, SectionHeading } from "@/components/Reveal";
import { TelegramButton, Button } from "@/components/Button";
import { FAQ, PRINCIPLES } from "@/data/content";
import { MetricsStrip } from "@/components/MetricsStrip";
import { AtmosphereMarquee } from "@/components/AtmosphereMarquee";
import { DialogueSamples } from "@/components/DialogueSamples";
import { usePageMeta } from "@/hooks/usePageMeta";

export function HomePage() {
  usePageMeta();
  return (
    <>
      <Hero />
      <MetricsStrip />
      <AtmosphereMarquee />

      <FeatureRail />

      <DialogueSamples />

      <Reveal as="section" className="section">
        <div className="container">
          <SectionHeading
            eyebrow="Тон"
            title="Живой разговор без ваты"
            lead="Агора звучит как близкий умный друг: входит в нерв проблемы, а не заканчивает ответ пустыми мантрами."
          />
          <div className="principles">
            {PRINCIPLES.slice(0, 2).map((item) => (
              <article key={item.title} className="principle">
                <h3>{item.title}</h3>
                <p>{item.text}</p>
              </article>
            ))}
          </div>
          <div style={{ marginTop: "1.5rem" }}>
            <Button to="/dialogue" variant="ghost">
              Больше о диалоге
            </Button>
          </div>
        </div>
      </Reveal>

      <Reveal as="section" className="section">
        <div className="container">
          <SectionHeading
            eyebrow="Попробовать здесь"
            title="Демо без Telegram"
            lead="На сайте можно пройти чек-ап и развернуть идею локально. Полный живой ответ — уже в боте."
          />
          <div style={{ display: "flex", gap: "0.8rem", flexWrap: "wrap" }}>
            <Button to="/tools">Открыть инструменты</Button>
            <TelegramButton variant="ghost">Сразу в бота</TelegramButton>
          </div>
        </div>
      </Reveal>

      <Reveal as="section" className="section">
        <div className="container">
          <SectionHeading eyebrow="Коротко" title="Частые вопросы" />
          <div className="faq">
            {FAQ.map((item) => (
              <details key={item.q}>
                <summary>{item.q}</summary>
                <p>{item.a}</p>
              </details>
            ))}
          </div>
        </div>
      </Reveal>

      <Reveal as="section" className="cta-band container">
        <p className="display">Агора</p>
        <p>Когда тяжело держать все в голове — можно выговорить.</p>
        <TelegramButton>Открыть бота</TelegramButton>
      </Reveal>
    </>
  );
}
