import base64
import os
from io import BytesIO

from openai import AsyncOpenAI

from bot.llm import get_provider_name

ASR_MODELS = {
    "dashscope": "qwen3-asr-flash",
    "dashscope_cn": "qwen3-asr-flash",
    "groq": "whisper-large-v3",
    "siliconflow": "FunAudioLLM/SenseVoiceSmall",
    "openrouter": "openai/whisper-large-v3",
}


def get_asr_model() -> str:
    explicit = os.getenv("ASR_MODEL", "").strip()
    if explicit:
        return explicit
    return ASR_MODELS.get(get_provider_name(), "qwen3-asr-flash")


async def transcribe_audio(
    client: AsyncOpenAI,
    audio_bytes: bytes,
    filename: str = "voice.ogg",
) -> str:
    provider = get_provider_name()
    model = get_asr_model()

    if provider in {"dashscope", "dashscope_cn"}:
        return await _transcribe_dashscope(client, audio_bytes, model)
    return await _transcribe_whisper(client, audio_bytes, model, filename)


async def _transcribe_dashscope(
    client: AsyncOpenAI,
    audio_bytes: bytes,
    model: str,
) -> str:
    b64 = base64.b64encode(audio_bytes).decode("ascii")
    response = await client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_audio",
                        "input_audio": {
                            "data": f"data:audio/ogg;base64,{b64}",
                        },
                    }
                ],
            }
        ],
        extra_body={
            "asr_options": {
                "enable_itn": True,
            }
        },
        max_tokens=1024,
    )
    content = response.choices[0].message.content
    return (content or "").strip()


async def _transcribe_whisper(
    client: AsyncOpenAI,
    audio_bytes: bytes,
    model: str,
    filename: str,
) -> str:
    buf = BytesIO(audio_bytes)
    buf.name = filename
    result = await client.audio.transcriptions.create(
        model=model,
        file=buf,
        language="ru",
    )
    return (getattr(result, "text", None) or "").strip()
