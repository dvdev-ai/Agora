import os
import re
from openai import AsyncOpenAI


def clean_reply(text: str) -> str:
    text = text.replace("**", "").replace("__", "")
    text = re.sub(r"(?<!\w)\*(?!\s)([^*]+)\*(?!\w)", r"\1", text)
    text = text.replace("«", "").replace("»", "")
    text = text.replace("“", "").replace("”", "").replace("„", "")
    text = re.sub(r'[🌿✨🤍🙏😌🤗💫🕊️❤️💕🌸⭐️🌟]+', "", text)

    mantra = (
        r"(?:тихо|спокойно|мирно|без\s+спешки|без\s+давления|"
        r"без\s+анализа|без\s+подвоха|"
        r"все\s+окей|все\s+ок|все\s+хорошо|все\s+будет\s+хорошо|"
        r"вс[её]\s+окей|вс[её]\s+ок|вс[её]\s+хорошо|вс[её]\s+будет\s+хорошо|"
        r"я\s+рядом|я\s+здесь|я\s+тоже\s+здесь|я\s+с\s+тобой|"
        r"просто\s+побудь(?:\s+в\s+этом)?|дыши|беречь?\s+себя|держись|"
        r"ты\s+не\s+один[а]?)"
    )
    for _ in range(8):
        cleaned = re.sub(
            rf"(?:\n+|\s*[.!?…]\s*|\s+){mantra}(?:\s*[.!?…]*)*\s*$",
            "",
            text,
            flags=re.IGNORECASE,
        )
        if cleaned == text:
            break
        text = cleaned
    text = re.sub(
        rf"^(?:{mantra})(?:\s*[.!?…]*)+\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    # Срезаем шаблонный последний абзац «если хочешь разобрать... я тоже здесь».
    therapy_tail = re.compile(
        r"(?:\n\s*){1,2}"
        r"(?:Если хочешь[^\n]{0,220}?(?:я (?:тоже )?здесь|без спешки|без анализа)[^\n]{0,120})"
        r"(?:\n[^\n]{0,80})?\s*$",
        re.IGNORECASE,
    )
    text = therapy_tail.sub("", text)

    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# Все варианты ниже дают именно Qwen (OpenAI-compatible API).
PROVIDERS = {
    # 1) Официальный Qwen / Alibaba Model Studio (DashScope).
    # Бесплатная квота новым аккаунтам (~1M токенов / 90 дней), регион Singapore.
    # Ключ: https://modelstudio.console.alibabacloud.com/ (API Keys)
    "dashscope": {
        "env_key": "DASHSCOPE_API_KEY",
        "base_url": "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
        "default_model": "qwen-plus",
        "help": "https://modelstudio.console.alibabacloud.com/",
    },
    # Китайский endpoint DashScope (иногда дешевле/доступнее).
    "dashscope_cn": {
        "env_key": "DASHSCOPE_API_KEY",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "default_model": "qwen-plus",
        "help": "https://bailian.console.aliyun.com/",
    },
    # 2) SiliconFlow — часто есть бесплатный Qwen3-8B без срока.
    # Ключ: https://cloud.siliconflow.com
    "siliconflow": {
        "env_key": "SILICONFLOW_API_KEY",
        "base_url": "https://api.siliconflow.com/v1",
        "default_model": "Qwen/Qwen3.5-9B",
        "help": "https://cloud.siliconflow.com",
    },
    # 3) Groq — бесплатный Qwen3-32B, но из РФ часто не пускает (нужен VPN).
    "groq": {
        "env_key": "GROQ_API_KEY",
        "base_url": "https://api.groq.com/openai/v1",
        "default_model": "qwen/qwen3-32b",
        "help": "https://console.groq.com/keys",
    },
    # 4) OpenRouter — Qwen есть, но бесплатных Qwen сейчас почти нет (обычно платно).
    "openrouter": {
        "env_key": "OPENROUTER_API_KEY",
        "base_url": "https://openrouter.ai/api/v1",
        "default_model": "qwen/qwen3-30b-a3b",
        "help": "https://openrouter.ai/keys",
    },
}


def _detect_provider() -> str:
    explicit = os.getenv("LLM_PROVIDER", "").strip().lower()
    if explicit:
        if explicit not in PROVIDERS:
            names = ", ".join(PROVIDERS)
            raise RuntimeError(f"Неизвестный LLM_PROVIDER={explicit}. Варианты: {names}")
        return explicit

    # Автовыбор: сначала бесплатные Qwen-пути.
    for name in ("siliconflow", "dashscope", "dashscope_cn", "groq", "openrouter"):
        key_name = PROVIDERS[name]["env_key"]
        if os.getenv(key_name, "").strip():
            return name

    raise RuntimeError(
        "Нет ключа для Qwen. Задай один из: SILICONFLOW_API_KEY / DASHSCOPE_API_KEY / "
        "GROQ_API_KEY / OPENROUTER_API_KEY и при желании LLM_PROVIDER=..."
    )


def _provider_config() -> tuple[str, str, str, str]:
    """Возвращает (provider, api_key, base_url, help_url)."""
    provider = _detect_provider()
    cfg = PROVIDERS[provider]
    api_key = os.getenv(cfg["env_key"], "").strip()
    if not api_key:
        raise RuntimeError(
            f"Не задан {cfg['env_key']} для провайдера {provider}. Ключ: {cfg['help']}"
        )
    return provider, api_key, cfg["base_url"], cfg["help"]


def get_model_name() -> str:
    explicit = os.getenv("LLM_MODEL", "").strip()
    if explicit:
        return explicit
    provider = _detect_provider()
    return PROVIDERS[provider]["default_model"]


def get_provider_name() -> str:
    return _detect_provider()


def create_llm_client() -> AsyncOpenAI:
    provider, api_key, base_url, _ = _provider_config()
    kwargs: dict = {
        "api_key": api_key,
        "base_url": base_url,
    }
    if provider == "openrouter":
        kwargs["default_headers"] = {
            "HTTP-Referer": "https://t.me/agora_psy_bot",
            "X-Title": "Agora Assistant",
        }
    return AsyncOpenAI(**kwargs)


async def ask_agora(
    client: AsyncOpenAI,
    system_prompt: str,
    history: list[dict],
    user_text: str,
    model: str,
    temperature: float = 0.55,
    max_tokens: int = 1400,
) -> str:
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(history)
    messages.append({"role": "user", "content": user_text})

    response = await client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    content = response.choices[0].message.content
    if content and content.strip():
        return clean_reply(content)

    reasoning = getattr(response.choices[0].message, "reasoning_content", None)
    if reasoning and str(reasoning).strip():
        text = str(reasoning).strip()
        for marker in ("Final Answer:", "Итоговый ответ:", "Ответ:"):
            if marker in text:
                return clean_reply(text.split(marker, 1)[1] or text)
        return clean_reply(text)

    return "Напиши еще раз своими словами. Что нужно сделать?"
