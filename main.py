import asyncio
import logging
import os
import re
from io import BytesIO
from pathlib import Path

from aiogram import Bot, Dispatcher, F
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    BotCommand,
    BufferedInputFile,
    CallbackQuery,
    Message,
)
from dotenv import load_dotenv

from bot.keyboards import (
    after_checkup_keyboard,
    after_idea_keyboard,
    after_stats_keyboard,
    hide_menu,
    idea_keyboard,
    job_keyboard,
    note_keyboard,
    panic_keyboard,
    remind_keyboard,
    score_keyboard,
    start_keyboard,
)
from bot.llm import ask_agora, create_llm_client, get_model_name, get_provider_name
from bot.memory import ConversationMemory
from bot.prompts import (
    IDEA_PROMPT,
    JOB_PROMPT,
    MEMORY_EXTRACT_PROMPT,
    PANIC_PROMPT,
    PANIC_PROTOCOL,
    SUMMARY_PROMPT,
    SYSTEM_PROMPT,
)
from bot.storage import Storage
from bot.tts import reminder_worker, synthesize_voice
from bot.voice import transcribe_audio

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger("agora")

HISTORY_LIMIT = int(os.getenv("HISTORY_LIMIT", "30"))
DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
LLM_MODEL = ""

memory = ConversationMemory(limit=HISTORY_LIMIT)
storage = Storage(DATA_DIR / "agora.db")
llm = None
dp = Dispatcher()

START_TEXT = (
    "Привет. Я Агора — личный ассистент.\n\n"
    "Пиши задачу или вопрос — разберем и сделаем следующий шаг.\n"
    "Текст или голос. Команды — кнопками или через /"
)

HELP_TEXT = (
    "Команды\n\n"
    "/checkup — чек-ап состояния\n"
    "/stats — динамика за неделю\n"
    "/insights — паттерны по чек-апам\n"
    "/summary — сводка недели\n"
    "/idea — мысль → три варианта\n"
    "/job — разобрать вакансию\n"
    "/panic — если накрыло\n"
    "/remind — мягкое напоминание о чек-апе\n"
    "/voice — голосовые ответы вкл/выкл\n"
    "/export — выгрузить свои данные\n"
    "/forget — удалить все данные\n"
    "/reset — очистить только диалог\n"
    "/cancel — отменить текущий режим\n\n"
    "Можно просто писать или кидать голосовое."
)

BOT_DESCRIPTION = (
    "Агора — личный ассистент. Помогает с задачами, вопросами и планом на шаг вперед. "
    "Прямо, по делу, с поддержкой если нужно."
)

BOT_SHORT_DESCRIPTION = "Личный ассистент. Пиши задачу — разберем и сделаем шаг."

CHECKUP_FIELDS = (
    ("mood", "Настроение", "0 — дно · 10 — легко"),
    ("anxiety", "Тревога", "0 — спокойно · 10 — накрыло"),
    ("energy", "Энергия", "0 — пусто · 10 — есть силы"),
    ("sleep", "Сон", "0 — плохо · 10 — выспался"),
)

CHECKUP_ORDER = ["mood", "anxiety", "energy", "sleep", "note"]


def _parse_score(text: str) -> int | None:
    match = re.fullmatch(r"\s*([0-9]|10)\s*", text)
    if not match:
        return None
    return int(match.group(1))


def _checkup_prompt(step: str) -> str:
    for key, title, hint in CHECKUP_FIELDS:
        if key == step:
            return f"{title}\n{hint}"
    return ""


def _system_with_memory(user_id: int, base: str = SYSTEM_PROMPT) -> str:
    block = storage.memory_prompt_block(user_id)
    if not block:
        return base
    return f"{base}\n\n{block}"


async def maybe_send_voice(message: Message, text: str) -> None:
    if not message.from_user:
        return
    prefs = storage.get_prefs(message.from_user.id)
    if not prefs.voice_enabled:
        return
    path = await synthesize_voice(text)
    if not path:
        return
    try:
        data = path.read_bytes()
        await message.answer_voice(BufferedInputFile(data, filename="agora.mp3"))
    except Exception:
        logger.exception("Не отправил голосовой ответ")
    finally:
        path.unlink(missing_ok=True)


async def maybe_extract_memory(user_id: int, user_text: str, reply: str) -> None:
    if llm is None:
        return
    # Раз в несколько реплик, чтобы не жечь токены.
    recent = storage.get_messages(user_id, limit=8)
    if len(recent) < 4 or len(recent) % 4 != 0:
        return
    try:
        raw = await ask_agora(
            client=llm,
            system_prompt=MEMORY_EXTRACT_PROMPT,
            history=[],
            user_text=f"Человек: {user_text}\nАгора: {reply}",
            model=LLM_MODEL,
            temperature=0.2,
            max_tokens=300,
        )
    except Exception:
        logger.exception("Не извлек память")
        return
    if not raw or raw.strip().upper() == "NONE":
        return
    for line in raw.splitlines():
        fact = line.strip(" -•\t")
        if len(fact) >= 8:
            storage.add_memory(user_id, fact, source="auto")


async def reply_as_agora(
    message: Message,
    user_text: str,
    *,
    system_prompt: str | None = None,
    use_history: bool = True,
    temperature: float = 0.55,
    max_tokens: int = 1400,
    save_to_memory: bool = True,
    reply_markup=None,
    with_voice: bool = True,
) -> None:
    if not message.from_user:
        return

    user_id = message.from_user.id
    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")

    if llm is None:
        await message.answer("Бот еще запускается. Напиши через секунду.")
        return

    prompt = system_prompt or _system_with_memory(user_id)
    history = memory.get(user_id) if use_history else []
    try:
        reply = await ask_agora(
            client=llm,
            system_prompt=prompt,
            history=history,
            user_text=user_text,
            model=LLM_MODEL,
            temperature=temperature,
            max_tokens=max_tokens,
        )
    except Exception:
        logger.exception("Ошибка ответа модели")
        await message.answer("Связь с нейросетью сбоит. Напиши чуть позже.")
        return

    if save_to_memory:
        memory.add(user_id, "user", user_text)
        memory.add(user_id, "assistant", reply)
        storage.add_message(user_id, "user", user_text)
        storage.add_message(user_id, "assistant", reply)
        await maybe_extract_memory(user_id, user_text, reply)

    await message.answer(reply, reply_markup=reply_markup)
    if with_voice:
        await maybe_send_voice(message, reply)


async def start_checkup(target: Message | CallbackQuery) -> None:
    user = target.from_user
    if not user:
        return
    storage.set_mode(user.id, "checkup_mood", {})
    text = f"Чек-ап\n\n{_checkup_prompt('mood')}"
    markup = score_keyboard()
    if isinstance(target, CallbackQuery):
        await target.message.answer(text, reply_markup=markup)
        await target.answer()
    else:
        await target.answer(text, reply_markup=markup)


async def send_stats(target: Message | CallbackQuery) -> None:
    user = target.from_user
    if not user:
        return
    text = storage.stats_text(user.id, days=7)
    markup = after_stats_keyboard()
    if isinstance(target, CallbackQuery):
        await target.message.answer(text, reply_markup=markup)
        await target.answer()
    else:
        await target.answer(text, reply_markup=markup)


async def send_insights(target: Message | CallbackQuery) -> None:
    user = target.from_user
    if not user:
        return
    text = storage.insights_text(user.id, days=14)
    if isinstance(target, CallbackQuery):
        await target.message.answer(text, reply_markup=after_stats_keyboard())
        await target.answer()
    else:
        await target.answer(text, reply_markup=after_stats_keyboard())


async def send_panic(target: Message | CallbackQuery) -> None:
    user = target.from_user
    if user:
        storage.clear_mode(user.id)
    if isinstance(target, CallbackQuery):
        await target.message.answer(PANIC_PROTOCOL, reply_markup=panic_keyboard())
        await target.answer()
    else:
        await target.answer(PANIC_PROTOCOL, reply_markup=panic_keyboard())


async def send_help(target: Message | CallbackQuery) -> None:
    if isinstance(target, CallbackQuery):
        await target.message.answer(HELP_TEXT, reply_markup=start_keyboard())
        await target.answer()
    else:
        await target.answer(HELP_TEXT, reply_markup=start_keyboard())


async def send_summary(target: Message | CallbackQuery) -> None:
    user = target.from_user
    if not user or llm is None:
        return
    msg = target if isinstance(target, Message) else target.message
    await msg.bot.send_chat_action(chat_id=msg.chat.id, action="typing")

    mem = storage.list_memory(user.id, limit=12)
    checkups = storage.get_checkups(user.id, days=7)
    recent = storage.get_messages(user.id, limit=20)
    payload_parts = []
    if mem:
        payload_parts.append(
            "Память:\n" + "\n".join(f"- {m.content}" for m in reversed(mem))
        )
    if checkups:
        payload_parts.append(
            "Чек-апы:\n"
            + "\n".join(
                f"- {c.created_at} {c.mood}/{c.anxiety}/{c.energy}/{c.sleep}"
                + (f" · {c.note}" if c.note else "")
                for c in checkups
            )
        )
    if recent:
        payload_parts.append(
            "Диалог:\n"
            + "\n".join(f"{m['role']}: {m['content']}" for m in recent[-12:])
        )
    if not payload_parts:
        text = "Пока мало материала для сводки. Поговори или пройди /checkup."
        if isinstance(target, CallbackQuery):
            await target.message.answer(text)
            await target.answer()
        else:
            await target.answer(text)
        return

    try:
        reply = await ask_agora(
            client=llm,
            system_prompt=SUMMARY_PROMPT,
            history=[],
            user_text="\n\n".join(payload_parts),
            model=LLM_MODEL,
            temperature=0.55,
            max_tokens=1200,
        )
    except Exception:
        logger.exception("Ошибка summary")
        reply = "Сейчас не собрал сводку. Попробуй чуть позже."

    if isinstance(target, CallbackQuery):
        await target.message.answer(reply)
        await target.answer()
    else:
        await target.answer(reply)
    await maybe_send_voice(msg, reply)


async def start_job(target: Message | CallbackQuery, body: str = "") -> None:
    user = target.from_user
    if not user:
        return
    msg = target if isinstance(target, Message) else target.message
    if body and len(body) >= 20:
        storage.clear_mode(user.id)
        await reply_as_agora(
            msg,
            body,
            system_prompt=JOB_PROMPT,
            use_history=False,
            temperature=0.4,
            max_tokens=1600,
            save_to_memory=False,
        )
        if isinstance(target, CallbackQuery):
            await target.answer()
        return
    storage.set_mode(user.id, "job_wait", {})
    text = (
        "Вакансия\n\n"
        "Пришли текст вакансии, офер или переписку.\n"
        "Разберу риски и набросаю короткий ответ."
    )
    if isinstance(target, CallbackQuery):
        await target.message.answer(text, reply_markup=job_keyboard())
        await target.answer()
    else:
        await target.answer(text, reply_markup=job_keyboard())


async def start_idea(target: Message | CallbackQuery, body: str = "") -> None:
    user = target.from_user
    if not user:
        return
    msg = target if isinstance(target, Message) else target.message
    if body and len(body) >= 3:
        storage.clear_mode(user.id)
        await reply_as_agora(
            msg,
            body,
            system_prompt=IDEA_PROMPT,
            use_history=False,
            temperature=0.95,
            max_tokens=1800,
            save_to_memory=False,
            reply_markup=after_idea_keyboard(),
        )
        if isinstance(target, CallbackQuery):
            await target.answer()
        return
    storage.set_mode(user.id, "idea_wait", {})
    text = (
        "Идея\n\n"
        "Кинь мысль как есть — сырую, странную, недоделанную.\n"
        "Разверну в три варианта: реалистично, смело и абсурдно."
    )
    if isinstance(target, CallbackQuery):
        await target.message.answer(text, reply_markup=idea_keyboard())
        await target.answer()
    else:
        await target.answer(text, reply_markup=idea_keyboard())


async def finish_checkup(
    user_id: int, draft: dict, note: str, target: Message | CallbackQuery
) -> None:
    storage.add_checkup(
        user_id=user_id,
        mood=int(draft["mood"]),
        anxiety=int(draft["anxiety"]),
        energy=int(draft["energy"]),
        sleep=int(draft["sleep"]),
        note=note,
    )
    storage.clear_mode(user_id)
    if note:
        storage.add_memory(user_id, f"В чек-апе отметил: {note}", source="checkup")
    text = (
        "Записал чек-ап\n\n"
        f"Настроение {draft['mood']} · тревога {draft['anxiety']}\n"
        f"Энергия {draft['energy']} · сон {draft['sleep']}"
    )
    markup = after_checkup_keyboard()
    if isinstance(target, CallbackQuery):
        await target.message.edit_text(text, reply_markup=markup)
        await target.answer("Готово")
    else:
        await target.answer(text, reply_markup=markup)


async def advance_checkup_score(
    user_id: int,
    draft: dict,
    step: str,
    score: int,
    target: Message | CallbackQuery,
) -> None:
    draft[step] = score
    next_step = CHECKUP_ORDER[CHECKUP_ORDER.index(step) + 1]
    if next_step == "note":
        storage.set_mode(user_id, "checkup_note", draft)
        text = "Что сильнее всего выбило сегодня?\nОдной фразой или пропусти."
        markup = note_keyboard()
    else:
        storage.set_mode(user_id, f"checkup_{next_step}", draft)
        text = _checkup_prompt(next_step)
        markup = score_keyboard()
    if isinstance(target, CallbackQuery):
        await target.message.edit_text(text, reply_markup=markup)
        await target.answer(f"{score}")
    else:
        await target.answer(text, reply_markup=markup)


async def handle_checkup_step(message: Message, text: str) -> bool:
    if not message.from_user:
        return False
    user_id = message.from_user.id
    mode, draft = storage.get_mode(user_id)
    if not mode.startswith("checkup_"):
        # Старый режим checkin_* тоже поддержим.
        if mode.startswith("checkin_"):
            mode = "checkup_" + mode[len("checkin_") :]
            storage.set_mode(user_id, mode, draft)
        else:
            return False

    lowered = text.lower().strip()
    if lowered in {"/cancel", "cancel", "отмена"}:
        storage.clear_mode(user_id)
        await message.answer("Чек-ап отменен.")
        return True

    step = mode.replace("checkup_", "", 1)
    if step not in CHECKUP_ORDER:
        storage.clear_mode(user_id)
        return False

    if step != "note":
        score = _parse_score(text)
        if score is None:
            await message.answer(
                "Выбери цифру на кнопках или напиши от 0 до 10.",
                reply_markup=score_keyboard(),
            )
            return True
        await advance_checkup_score(user_id, draft, step, score, message)
        return True

    note = "" if lowered in {"пропустить", "skip", "-", "нет"} else text.strip()
    await finish_checkup(user_id, draft, note, message)
    return True


async def handle_job_pending(message: Message, text: str) -> bool:
    if not message.from_user:
        return False
    user_id = message.from_user.id
    mode, _ = storage.get_mode(user_id)
    if mode != "job_wait":
        return False
    lowered = text.lower().strip()
    if lowered in {"/cancel", "cancel", "отмена"}:
        storage.clear_mode(user_id)
        await message.answer("Ок, отменил.")
        return True
    if len(text) < 20:
        await message.answer(
            "Маловато текста. Пришли описание целиком.",
            reply_markup=job_keyboard(),
        )
        return True
    storage.clear_mode(user_id)
    await reply_as_agora(
        message,
        text,
        system_prompt=JOB_PROMPT,
        use_history=False,
        temperature=0.4,
        max_tokens=1600,
        save_to_memory=False,
    )
    return True


async def handle_idea_pending(message: Message, text: str) -> bool:
    if not message.from_user:
        return False
    user_id = message.from_user.id
    mode, _ = storage.get_mode(user_id)
    if mode != "idea_wait":
        return False
    lowered = text.lower().strip()
    if lowered in {"/cancel", "cancel", "отмена"}:
        storage.clear_mode(user_id)
        await message.answer("Ок, отменил.")
        return True
    if len(text) < 3:
        await message.answer(
            "Совсем коротко. Кинь мысль чуть шире.",
            reply_markup=idea_keyboard(),
        )
        return True
    storage.clear_mode(user_id)
    await reply_as_agora(
        message,
        text,
        system_prompt=IDEA_PROMPT,
        use_history=False,
        temperature=0.95,
        max_tokens=1800,
        save_to_memory=False,
        reply_markup=after_idea_keyboard(),
    )
    return True


@dp.message(CommandStart())
async def cmd_start(message: Message) -> None:
    if message.from_user:
        storage.clear_mode(message.from_user.id)
    await message.answer(START_TEXT, reply_markup=hide_menu())
    await message.answer("Быстрые действия:", reply_markup=start_keyboard())


@dp.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await message.answer(HELP_TEXT, reply_markup=start_keyboard())


@dp.message(Command("reset"))
async def cmd_reset(message: Message) -> None:
    if message.from_user:
        memory.clear(message.from_user.id)
        storage.clear_mode(message.from_user.id)
    await message.answer("Чистый лист диалога. Что случилось?")


@dp.message(Command("cancel"))
async def cmd_cancel(message: Message) -> None:
    if message.from_user:
        storage.clear_mode(message.from_user.id)
    await message.answer("Ок, отменил.")


@dp.message(Command("panic"))
async def cmd_panic(message: Message) -> None:
    await send_panic(message)


@dp.message(Command("checkup"))
@dp.message(Command("checkin"))
async def cmd_checkup(message: Message) -> None:
    await start_checkup(message)


@dp.message(Command("stats"))
async def cmd_stats(message: Message) -> None:
    await send_stats(message)


@dp.message(Command("insights"))
async def cmd_insights(message: Message) -> None:
    await send_insights(message)


@dp.message(Command("summary"))
async def cmd_summary(message: Message) -> None:
    await send_summary(message)


@dp.message(Command("job"))
async def cmd_job(message: Message) -> None:
    text = (message.text or "").strip()
    payload = text.split(maxsplit=1)
    body = payload[1].strip() if len(payload) > 1 else ""
    await start_job(message, body=body)


@dp.message(Command("idea"))
async def cmd_idea(message: Message) -> None:
    text = (message.text or "").strip()
    payload = text.split(maxsplit=1)
    body = payload[1].strip() if len(payload) > 1 else ""
    await start_idea(message, body=body)


@dp.message(Command("remind"))
async def cmd_remind(message: Message) -> None:
    if not message.from_user:
        return
    prefs = storage.get_prefs(message.from_user.id)
    status = (
        f"Сейчас напоминания {'вкл' if prefs.remind_enabled else 'выкл'}"
        + (f" · около {prefs.remind_hour}:00 МСК" if prefs.remind_enabled else "")
    )
    await message.answer(
        f"{status}\n\nВыбери час мягкого напоминания о чек-апе:",
        reply_markup=remind_keyboard(),
    )


@dp.message(Command("voice"))
async def cmd_voice(message: Message) -> None:
    if not message.from_user:
        return
    parts = (message.text or "").split()
    prefs = storage.get_prefs(message.from_user.id)
    arg = parts[1].lower() if len(parts) > 1 else ""
    if arg in {"on", "вкл", "1", "yes"}:
        prefs.voice_enabled = True
        storage.set_prefs(message.from_user.id, prefs)
        await message.answer("Голосовые ответы включены. Буду дублировать голосом.")
        return
    if arg in {"off", "выкл", "0", "no"}:
        prefs.voice_enabled = False
        storage.set_prefs(message.from_user.id, prefs)
        await message.answer("Голосовые ответы выключены.")
        return
    # toggle
    prefs.voice_enabled = not prefs.voice_enabled
    storage.set_prefs(message.from_user.id, prefs)
    state = "включены" if prefs.voice_enabled else "выключены"
    await message.answer(
        f"Голосовые ответы {state}.\n"
        "Можно явно: /voice on или /voice off"
    )


@dp.message(Command("export"))
async def cmd_export(message: Message) -> None:
    if not message.from_user:
        return
    payload = storage.export_text(message.from_user.id)
    data = payload.encode("utf-8")
    await message.answer_document(
        BufferedInputFile(data, filename="agora-export.txt"),
        caption="Твои данные из Агоры.",
    )


@dp.message(Command("forget"))
async def cmd_forget(message: Message) -> None:
    if not message.from_user:
        return
    storage.set_mode(message.from_user.id, "forget_confirm", {})
    await message.answer(
        "Точно удалить все данные: чек-апы, память, сообщения, настройки?\n"
        "Напиши: удалить все\n"
        "Или /cancel"
    )


@dp.callback_query(F.data.startswith("cu:") | F.data.startswith("ci:"))
async def on_checkup_callback(query: CallbackQuery) -> None:
    if not query.from_user or not query.data:
        return
    user_id = query.from_user.id
    mode, draft = storage.get_mode(user_id)
    parts = query.data.split(":")
    if len(parts) < 2:
        await query.answer()
        return
    action = parts[1]

    if action == "cancel":
        storage.clear_mode(user_id)
        await query.message.edit_text("Чек-ап отменен.")
        await query.answer()
        return

    if action == "skip":
        if not mode.endswith("_note"):
            await query.answer("Сейчас не тот шаг", show_alert=False)
            return
        await finish_checkup(user_id, draft, "", query)
        return

    if action == "score" and len(parts) == 3:
        if not (mode.startswith("checkup_") or mode.startswith("checkin_")):
            await query.answer("Чек-ап уже закрыт", show_alert=False)
            return
        step = mode.split("_", 1)[1]
        if step not in {"mood", "anxiety", "energy", "sleep"}:
            await query.answer("Сейчас нужна заметка текстом", show_alert=False)
            return
        try:
            score = int(parts[2])
        except ValueError:
            await query.answer()
            return
        if score < 0 or score > 10:
            await query.answer()
            return
        await advance_checkup_score(user_id, draft, step, score, query)
        return

    await query.answer()


@dp.callback_query(F.data.startswith("panic:"))
async def on_panic_callback(query: CallbackQuery) -> None:
    if not query.data:
        return
    action = query.data.split(":", 1)[1]
    if action == "ok":
        await query.message.answer("Хорошо. Если захочешь разобрать — просто напиши.")
        await query.answer()
    elif action in {"checkup", "checkin"}:
        await start_checkup(query)
    elif action == "help":
        await query.message.answer(
            "Живая помощь\n\n"
            "8-800-2000-122 — бесплатно, круглосуточно\n"
            "112 — экстренные службы\n"
            "Или позвони человеку, которому доверяешь."
        )
        await query.answer()
    else:
        await query.answer()


@dp.callback_query(F.data.startswith("job:"))
async def on_job_callback(query: CallbackQuery) -> None:
    if not query.from_user or not query.data:
        return
    if query.data == "job:cancel":
        storage.clear_mode(query.from_user.id)
        await query.message.edit_text("Разбор вакансии отменен.")
        await query.answer()
        return
    await query.answer()


@dp.callback_query(F.data.startswith("idea:"))
async def on_idea_callback(query: CallbackQuery) -> None:
    if not query.from_user or not query.data:
        return
    if query.data == "idea:cancel":
        storage.clear_mode(query.from_user.id)
        await query.message.edit_text("Идею отменил.")
        await query.answer()
        return
    await query.answer()


@dp.callback_query(F.data.startswith("remind:"))
async def on_remind_callback(query: CallbackQuery) -> None:
    if not query.from_user or not query.data:
        return
    prefs = storage.get_prefs(query.from_user.id)
    action = query.data.split(":", 1)[1]
    if action == "off":
        prefs.remind_enabled = False
        storage.set_prefs(query.from_user.id, prefs)
        await query.message.edit_text("Напоминания выключены.")
        await query.answer()
        return
    try:
        hour = int(action)
    except ValueError:
        await query.answer()
        return
    prefs.remind_enabled = True
    prefs.remind_hour = hour
    prefs.last_reminded_date = ""
    storage.set_prefs(query.from_user.id, prefs)
    await query.message.edit_text(
        f"Ок. Буду мягко напоминать около {hour}:00 по МСК.\n"
        "Выключить: /remind → Выключить"
    )
    await query.answer()


@dp.callback_query(F.data.startswith("nav:"))
async def on_nav_callback(query: CallbackQuery) -> None:
    if not query.data:
        return
    action = query.data.split(":", 1)[1]
    if action == "stats":
        await send_stats(query)
    elif action in {"checkup", "checkin"}:
        await start_checkup(query)
    elif action == "insights":
        await send_insights(query)
    elif action == "summary":
        await send_summary(query)
    elif action == "panic":
        await send_panic(query)
    elif action == "job":
        await start_job(query)
    elif action == "idea":
        await start_idea(query)
    elif action == "help":
        await send_help(query)
    else:
        await query.answer()


@dp.message(F.voice | F.audio)
async def on_voice(message: Message) -> None:
    file = message.voice or message.audio
    if not file or not message.from_user:
        return
    if llm is None:
        await message.answer("Бот еще запускается.")
        return

    await message.bot.send_chat_action(chat_id=message.chat.id, action="typing")
    try:
        buf = BytesIO()
        await message.bot.download(file, destination=buf)
        audio_bytes = buf.getvalue()
        if not audio_bytes:
            await message.answer("Голосовое не дошло. Кинь еще раз.")
            return
        transcript = await transcribe_audio(
            client=llm,
            audio_bytes=audio_bytes,
            filename="voice.ogg",
        )
    except Exception:
        logger.exception("Ошибка расшифровки голосового")
        await message.answer("Не разобрал голосовое. Напиши текстом.")
        return

    if not transcript:
        await message.answer("Не разобрал. Напиши текстом или запиши еще раз.")
        return

    if await handle_checkup_step(message, transcript):
        return
    if await handle_idea_pending(message, transcript):
        return
    if await handle_job_pending(message, transcript):
        return

    lowered = transcript.lower()
    crisis_markers = ("плохо", "страшно", "накрыло", "паника", "не могу", "умереть")
    if any(m in lowered for m in crisis_markers):
        await reply_as_agora(
            message,
            transcript,
            system_prompt=PANIC_PROMPT,
            use_history=True,
            temperature=0.5,
            max_tokens=700,
        )
        return

    await reply_as_agora(message, transcript)


@dp.message(F.text)
async def on_text(message: Message) -> None:
    if not message.from_user or not message.text:
        return
    user_text = message.text.strip()
    if not user_text:
        return

    mode, _ = storage.get_mode(message.from_user.id)
    if mode == "forget_confirm":
        if user_text.lower() == "удалить все":
            storage.forget_user(message.from_user.id)
            memory.clear(message.from_user.id)
            await message.answer("Все удалил. С чистого листа.")
        else:
            await message.answer("Чтобы подтвердить, напиши точно: удалить все")
        return

    if await handle_checkup_step(message, user_text):
        return
    if await handle_idea_pending(message, user_text):
        return
    if await handle_job_pending(message, user_text):
        return

    await reply_as_agora(message, user_text)


@dp.message()
async def on_other(message: Message) -> None:
    await message.answer("Лучше текст, голос или команда из /help.")


async def setup_bot_profile(bot: Bot) -> None:
    try:
        await bot.set_my_commands(
            [
                BotCommand(command="start", description="Старт"),
                BotCommand(command="checkup", description="Чек-ап"),
                BotCommand(command="stats", description="Неделя"),
                BotCommand(command="insights", description="Паттерны"),
                BotCommand(command="summary", description="Сводка недели"),
                BotCommand(command="idea", description="Идея в 3 варианта"),
                BotCommand(command="remind", description="Напоминание"),
                BotCommand(command="voice", description="Голосовые ответы"),
                BotCommand(command="export", description="Экспорт данных"),
                BotCommand(command="forget", description="Удалить данные"),
                BotCommand(command="help", description="Справка"),
                BotCommand(command="reset", description="Сброс диалога"),
                BotCommand(command="cancel", description="Отмена"),
            ]
        )
        await bot.set_my_description(BOT_DESCRIPTION)
        await bot.set_my_short_description(BOT_SHORT_DESCRIPTION)
    except Exception:
        logger.exception("Не удалось обновить профиль бота, продолжаю без этого")


async def main() -> None:
    global llm, LLM_MODEL

    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        raise RuntimeError("Не задан TELEGRAM_BOT_TOKEN. Создай бота у @BotFather")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    llm = create_llm_client()
    LLM_MODEL = get_model_name()

    session = None
    ssl_verify = os.getenv("TELEGRAM_SSL_VERIFY", "true").strip().lower()
    if ssl_verify in {"0", "false", "no"}:
        session = AiohttpSession()
        session._connector_init["ssl"] = False

    bot = Bot(token=token, session=session)
    await setup_bot_profile(bot)
    me = await bot.get_me()
    logger.info(
        "Агора запущена как @%s | провайдер %s | модель %s | data %s",
        me.username,
        get_provider_name(),
        LLM_MODEL,
        DATA_DIR,
    )
    asyncio.create_task(reminder_worker(bot, storage))
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
