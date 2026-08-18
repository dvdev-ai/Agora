# Агора · сайт

Локальный продакшен-лендинг и витрина Telegram-бота **Агора**.

## Стек

- Vite
- React 19
- TypeScript
- React Router

## Запуск

```bash
cd site
npm install
npm run dev
```

Открой http://127.0.0.1:5173

## Сборка

```bash
npm run build
npm run preview
```

## Что внутри

- Главная: герой, тон, примеры диалога, FAQ
- `/tools` — описание команд + интерактивные демо `/checkup` и `/idea`
- `/dialogue` — принципы разговора
- `/privacy` — приватность
- `/start` — как начать в Telegram

Демо чек-ина хранится в `localStorage` браузера и не уходит на сервер.
