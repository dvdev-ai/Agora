# Как подключить именно Qwen

Все провайдеры ниже отдают **Qwen**. В `.env` ставишь `LLM_PROVIDER=...` и свой ключ.

## 1. SiliconFlow — начни с него

- Сайт: https://cloud.siliconflow.com
- Плюсы: много версий Qwen, OpenAI-compatible API, из РФ обычно заходит
- Для диалога бери текстовый Chat, не VL
- `.env`:

```env
LLM_PROVIDER=siliconflow
SILICONFLOW_API_KEY=sk-...
LLM_MODEL=Qwen/Qwen3.5-9B
```

Посильнее (если хватит баланса): `Qwen/Qwen3.6-27B`

## 2. Официальный Alibaba (DashScope / Model Studio)

- Intl: https://modelstudio.console.alibabacloud.com/
- CN: https://bailian.console.aliyun.com/
- Плюсы: настоящий Qwen от разработчика, новичкам дают бесплатную квоту (~1M токенов / 90 дней)
- Минусы: после квоты уже платно; регистрация иногда капризная
- `.env` (Singapore / intl):

```env
LLM_PROVIDER=dashscope
DASHSCOPE_API_KEY=sk-...
LLM_MODEL=qwen-plus
```

Если intl не открывается — тот же ключ с CN-консоли:

```env
LLM_PROVIDER=dashscope_cn
DASHSCOPE_API_KEY=sk-...
LLM_MODEL=qwen-plus
```

Другие модели: `qwen-turbo`, `qwen-max`, `qwen2.5-72b-instruct` — смотри список в консоли.

## 3. Groq

- https://console.groq.com/keys
- Плюсы: сильный **бесплатный** `qwen/qwen3-32b`, очень быстрый
- Минусы: из РФ часто не пускает без VPN
- `.env`:

```env
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_...
LLM_MODEL=qwen/qwen3-32b
```

## 4. OpenRouter

- https://openrouter.ai/keys
- Плюсы: удобно, много версий Qwen
- Минусы: бесплатных Qwen сейчас почти нет — обычно копейки, но уже не zero
- `.env`:

```env
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-...
LLM_MODEL=qwen/qwen3-30b-a3b
```

## Что выбрать по ситуации

| Цель | Куда идти |
|---|---|
| Бесплатно и без VPN | SiliconFlow |
| Официальный Qwen + пробная квота | DashScope |
| Самый сильный бесплатный Qwen | Groq + VPN |
| Не жалко чуть денег | OpenRouter |

Бот сам подхватит провайдера по ключу в `.env`.
