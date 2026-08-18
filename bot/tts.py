import asyncio
import logging
import tempfile
from pathlib import Path

logger = logging.getLogger("agora.tts")


async def synthesize_voice(text: str, voice: str = "ru-RU-DmitryNeural") -> Path | None:
    """Синтез речи через edge-tts. Возвращает путь к mp3 или None."""
    clean = " ".join(text.split())
    if len(clean) < 3:
        return None
    # Не озвучиваем гигантские простыни целиком — берем первые ~900 символов.
    if len(clean) > 900:
        clean = clean[:900].rsplit(" ", 1)[0] + "..."

    try:
        import edge_tts
    except ImportError:
        logger.exception("edge-tts не установлен")
        return None

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tmp_path = Path(tmp.name)
    tmp.close()

    try:
        communicate = edge_tts.Communicate(clean, voice=voice)
        await communicate.save(str(tmp_path))
        if tmp_path.stat().st_size < 100:
            tmp_path.unlink(missing_ok=True)
            return None
        return tmp_path
    except Exception:
        logger.exception("Ошибка синтеза речи")
        tmp_path.unlink(missing_ok=True)
        return None


async def reminder_worker(bot, storage, interval_sec: int = 60) -> None:
    """Мягкие напоминания о чек-апе раз в сутки в выбранный час (MSK)."""
    while True:
        try:
            due = storage.list_due_reminders()
            for user_id in due:
                try:
                    await bot.send_message(
                        user_id,
                        "Мягкое напоминание про чек-ап.\n"
                        "Если есть минута — /checkup. Если нет — просто пропусти.",
                    )
                    storage.mark_reminded(user_id)
                except Exception:
                    logger.exception("Не отправил напоминание user_id=%s", user_id)
        except Exception:
            logger.exception("Сбой цикла напоминаний")
        await asyncio.sleep(interval_sec)
