import { PageHero, Reveal } from "@/components/Reveal";
import { SiteMap } from "@/components/SiteMap";
import { PRIVACY } from "@/data/content";
import { TelegramButton, Button } from "@/components/Button";
import { usePageMeta } from "@/hooks/usePageMeta";

export function PrivacyPage() {
  usePageMeta("Приватность", "Как устроены сайт и бот Агора с точки зрения данных.");
  return (
    <>
      <PageHero
        eyebrow="Приватность"
        title="Коротко и по делу"
        lead="Сайт — витрина. Бот — переписка в Telegram. Демо на сайте никуда не уходят из браузера."
      />

      <Reveal as="section" className="section">
        <div className="container">
          {PRIVACY.map((block) => (
            <article key={block.title} className="privacy-block">
              <h2>{block.title}</h2>
              {block.paragraphs.map((p) => (
                <p key={p}>{p}</p>
              ))}
            </article>
          ))}
        </div>
      </Reveal>

      <SiteMap />

      <Reveal as="section" className="cta-band container">
        <p className="display">Остались вопросы</p>
        <p>Напиши прямо в бота — там живой диалог.</p>
        <div
          style={{
            display: "flex",
            gap: "0.8rem",
            justifyContent: "center",
            flexWrap: "wrap",
          }}
        >
          <TelegramButton />
          <Button to="/" variant="ghost">
            На главную
          </Button>
        </div>
      </Reveal>
    </>
  );
}
