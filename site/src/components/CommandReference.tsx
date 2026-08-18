import { FEATURES } from "@/data/content";
import { Reveal, SectionHeading } from "@/components/Reveal";

export function CommandReference() {
  return (
    <Reveal as="section" className="section">
      <div className="container">
        <SectionHeading
          eyebrow="Шпаргалка"
          title="Команды под рукой"
          lead="Их не обязательно учить наизусть. Достаточно помнить, что структура всегда рядом."
        />
        <div className="command-ref">
          {FEATURES.map((feature) => (
            <div key={feature.id} className="command-ref__row">
              <code>{feature.command}</code>
              <div>
                <strong>{feature.title}</strong>
                <p>{feature.teaser}</p>
              </div>
            </div>
          ))}
          <div className="command-ref__row">
            <code>/stats</code>
            <div>
              <strong>Неделя</strong>
              <p>Средние по чек-апам и мягкий тренд за 7 дней.</p>
            </div>
          </div>
          <div className="command-ref__row">
            <code>/insights</code>
            <div>
              <strong>Паттерны</strong>
              <p>Что повторяется в чек-апах: просадки, связки, заметки.</p>
            </div>
          </div>
          <div className="command-ref__row">
            <code>/remind</code>
            <div>
              <strong>Пинг</strong>
              <p>Мягкое напоминание о чек-апе — без давления.</p>
            </div>
          </div>
          <div className="command-ref__row">
            <code>/voice</code>
            <div>
              <strong>Голос наружу</strong>
              <p>Ответы голосом: on / off / toggle.</p>
            </div>
          </div>
          <div className="command-ref__row">
            <code>/export · /forget</code>
            <div>
              <strong>Данные</strong>
              <p>Выгрузить или стереть все, что бот о тебе помнит.</p>
            </div>
          </div>
          <div className="command-ref__row">
            <code>/reset</code>
            <div>
              <strong>Заново</strong>
              <p>Очистить диалог и начать с чистого листа.</p>
            </div>
          </div>
          <div className="command-ref__row">
            <code>/cancel</code>
            <div>
              <strong>Отмена</strong>
              <p>Выйти из текущего режима: чек-ап, идея, вакансия.</p>
            </div>
          </div>
        </div>
      </div>
    </Reveal>
  );
}
