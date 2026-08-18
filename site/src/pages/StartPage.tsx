import { PageHero, Reveal, SectionHeading } from "@/components/Reveal";
import { START_STEPS } from "@/data/content";
import { TelegramButton, Button } from "@/components/Button";
import { usePageMeta } from "@/hooks/usePageMeta";

export function StartPage() {
  usePageMeta("Начать", "Как открыть Агору в Telegram и начать разговор.");
  return (
    <>
      <PageHero
        eyebrow="Начать"
        title="Три шага до разговора"
        lead="Без регистрации на сайте. Просто Telegram и готовность сказать как есть."
      />

      <Reveal as="section" className="section">
        <div className="container">
          <div className="steps">
            {START_STEPS.map((step) => (
              <article key={step.n} className="step">
                <div className="step__n">{step.n}</div>
                <div>
                  <h3>{step.title}</h3>
                  <p>{step.text}</p>
                </div>
              </article>
            ))}
          </div>
        </div>
      </Reveal>

      <Reveal as="section" className="section">
        <div className="container">
          <SectionHeading
            eyebrow="Если не знаешь, с чего"
            title="Можно начать с любой фразы"
            lead="«Мне тяжело», «хожу кругами», «накрыло», «есть мысль, но не знаю куда ее деть». Этого достаточно."
          />
          <div style={{ display: "flex", gap: "0.8rem", flexWrap: "wrap" }}>
            <TelegramButton>Открыть @agora_mind_bot</TelegramButton>
            <Button to="/tools" variant="ghost">
              Сначала демо
            </Button>
          </div>
        </div>
      </Reveal>

      <Reveal as="section" className="cta-band container">
        <p className="display">Агора</p>
        <p>Душевный разговор. Разберем, что происходит.</p>
        <TelegramButton>Написать сейчас</TelegramButton>
      </Reveal>
    </>
  );
}
