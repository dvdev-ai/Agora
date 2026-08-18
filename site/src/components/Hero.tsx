import { TelegramButton, Button } from "@/components/Button";

export function Hero() {
  return (
    <section className="hero container">
      <div className="hero__copy">
        <p className="hero__brand">Агора</p>
        <h1>Разговор, в котором становится яснее</h1>
        <p className="hero__lead">
          Душевный собеседник в Telegram. Пиши как есть — найдем, где затык, и
          разберем, что с этим можно сделать.
        </p>
        <div className="hero__actions">
          <TelegramButton />
          <Button to="/tools" variant="ghost">
            Инструменты
          </Button>
        </div>
      </div>

      <div className="hero__visual" aria-hidden="true">
        <div className="orb">
          <img src="/assets/agora-icon.png" alt="" />
        </div>
      </div>
    </section>
  );
}
