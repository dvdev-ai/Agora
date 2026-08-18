import { PageHero, Reveal, SectionHeading } from "@/components/Reveal";
import { PRINCIPLES, FAQ } from "@/data/content";
import { MANIFESTO } from "@/data/manifesto";
import { TelegramButton, Button } from "@/components/Button";
import { usePageMeta } from "@/hooks/usePageMeta";

export function DialoguePage() {
  usePageMeta("Диалог", "Как Агора слышит: принципы живого разговора без ваты.");
  return (
    <>
      <PageHero
        eyebrow="Диалог"
        title="Как Агора слышит"
        lead="Не роль психолога из рекламы. Близкий умный друг с глубиной: видит нерв, не давит чек-листами и не прячется за мантрами."
      />

      <Reveal as="section" className="section">
        <div className="container">
          <SectionHeading eyebrow="Принципы" title="Что важно в каждом ответе" />
          <div className="principles">
            {PRINCIPLES.map((item) => (
              <article key={item.title} className="principle">
                <h3>{item.title}</h3>
                <p>{item.text}</p>
              </article>
            ))}
          </div>
        </div>
      </Reveal>

      <Reveal as="section" className="section">
        <div className="container">
          <SectionHeading
            eyebrow="Манифест тона"
            title="Правила, которые держат живость"
          />
          <div className="principles">
            {MANIFESTO.map((item) => (
              <article key={item.title} className="principle">
                <h3>{item.title}</h3>
                <p>{item.text}</p>
              </article>
            ))}
          </div>
        </div>
      </Reveal>

      <Reveal as="section" className="section">
        <div className="container">
          <SectionHeading
            eyebrow="Как это ощущается"
            title="Не сессия. Переписка"
            lead="Можно вывалить длинным голосовым. Можно короткой фразой. Агора подстраивается под объем и тон — злость не тушит ватой, выгорание не толкает в подвиг."
          />
          <div className="principles">
            <article className="principle">
              <h3>Сначала понять</h3>
              <p>
                Войти в контекст и назвать, где болит на самом деле. Иногда человек
                говорит про работу, а нерв — в стыде, что «должен быть сильным».
              </p>
            </article>
            <article className="principle">
              <h3>Потом углубить</h3>
              <p>
                Найти слой глубже жалобы. Не чтобы уколоть — чтобы человек сам
                узнал себя и сказал внутри: да, вот оно.
              </p>
            </article>
            <article className="principle">
              <h3>Потом предложить угол</h3>
              <p>
                Не приказ. Мысль вслух: может, путь не ломать все сразу, а сделать
                один маленький шаг, который возвращает ощущение выбора.
              </p>
            </article>
          </div>
        </div>
      </Reveal>

      <Reveal as="section" className="section">
        <div className="container">
          <SectionHeading eyebrow="Честно" title="Чего Агора не делает" />
          <div className="principles">
            <article className="principle">
              <h3>Не ставит диагнозы</h3>
              <p>Это не врач и не клиника. Если нужна медицина — к живому специалисту.</p>
            </article>
            <article className="principle">
              <h3>Не обещает исцеление за вечер</h3>
              <p>
                Можно стать яснее. Нельзя честно обещать, что все решится одной
                перепиской.
              </p>
            </article>
            <article className="principle">
              <h3>Не бросает в кризисе наедине с ботом</h3>
              <p>
                При риске — прямо: 8-800-2000-122, экстренные службы, человек рядом.
              </p>
            </article>
          </div>
        </div>
      </Reveal>

      <Reveal as="section" className="section">
        <div className="container">
          <SectionHeading title="Вопросы" />
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
        <p className="display">Можно просто написать</p>
        <p>Без правильных слов. Как есть.</p>
        <div
          style={{
            display: "flex",
            gap: "0.8rem",
            justifyContent: "center",
            flexWrap: "wrap",
          }}
        >
          <TelegramButton />
          <Button to="/tools" variant="ghost">
            К инструментам
          </Button>
        </div>
      </Reveal>
    </>
  );
}
