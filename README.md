# Агора

Telegram-бот: личный ассистент. Помогает с задачами, вопросами и коротким планом. Отвечает **Qwen**.

Провайдеры Qwen (на выбор): SiliconFlow, DashScope, Groq, OpenRouter. Подробно — в [QWEN.md](QWEN.md).

## Что умеет

- прямые рабочие ответы: разобрать вопрос, набросать текст, предложить шаг
- поддержка, если человеку тяжело — коротко и без театра
- расшифровывает голосовые
- `/checkup` и `/stats` — состояние и динамика за неделю
- `/insights` — паттерны по чек-апам
- `/summary` — сводка недели
- `/remind` — мягкие напоминания
- `/voice` — голосовые ответы
- `/export` / `/forget` — контроль данных
- `/idea` — мысль → три варианта
- `/job` — разбор вакансии (команда, без кнопки)
- `/panic` — короткий антикризисный протокол (команда, без кнопки)
- память последних реплик в чате
- `/start`, `/help`, `/reset`, `/cancel`

## Что нужно

1. Telegram-бот у [@BotFather](https://t.me/BotFather) → токен
2. Ключ к **Qwen** — см. [QWEN.md](QWEN.md)

Рекомендация для РФ без VPN: **SiliconFlow** + модель `Qwen/Qwen3.5-9B`.
Официальный Qwen с пробной квотой: **DashScope**.
Сильный бесплатный Qwen: **Groq** (часто нужен VPN).

## Сервер

Хватит самого дешевого VPS:

- 1 CPU
- 512 MB–1 GB RAM
- Ubuntu 22.04+

Ориентир: Timeweb / Aeza / Hetzner Cloud CX22 / FirstVDS — от ~150–300 руб/мес.

Бот легкий: сам Python + polling к Telegram. GPU не нужен, модель сидит у OpenRouter/Groq.

## Быстрый старт на сервере

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip git
cd /opt
# загрузи папку проекта сюда
cd agora-psychologist-bot

python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
nano .env   # вставь TELEGRAM_BOT_TOKEN и OPENROUTER_API_KEY
```

Запуск:

```bash
python main.py
```

Или через Docker:

```bash
cp .env.example .env
# заполни .env
docker compose up -d --build
docker compose logs -f
```

Чтобы бот не падал после выхода из SSH:

```bash
# вариант без Docker
sudo apt install -y tmux
tmux new -s agora
source .venv/bin/activate
python main.py
# Ctrl+B, потом D — отключиться, бот продолжит работать
```

Или systemd (проще надолго):

```bash
sudo nano /etc/systemd/system/agora.service
```

```ini
[Unit]
Description=Agora Telegram psychologist bot
After=network.target

[Service]
Type=simple
WorkingDirectory=/opt/agora-psychologist-bot
EnvironmentFile=/opt/agora-psychologist-bot/.env
ExecStart=/opt/agora-psychologist-bot/.venv/bin/python /opt/agora-psychologist-bot/main.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now agora
sudo systemctl status agora
```

## Локальный сайт

Полноценный фронт в `site/` (Vite + React + TypeScript).

```bash
cd site
npm install
npm run dev
```

Открой http://127.0.0.1:5173

Подробнее: [site/README.md](site/README.md)

## Имя в BotFather

Предложение:

- имя: `Агора`
- username: например `agora_mind_bot`
- описание: `Агора — личный ассистент. Помогает с задачами, вопросами и планом на шаг вперед. Можно текстом и голосовыми.`
- короткое описание: `Личный ассистент. Пиши задачу — разберем и сделаем шаг.`
- аватар: загрузи `assets/agora-icon.png` через `/setuserpic` у @BotFather

## Важно

При кризисе — к живой помощи. Это не медицина и не терапия.
