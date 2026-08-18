import json
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from threading import Lock
from typing import Iterator, Optional


MSK = timezone(timedelta(hours=3))


@dataclass
class Checkup:
    mood: int
    anxiety: int
    energy: int
    sleep: int
    note: str
    created_at: str


@dataclass
class MemoryItem:
    id: int
    content: str
    source: str
    created_at: str


@dataclass
class UserPrefs:
    voice_enabled: bool = False
    remind_enabled: bool = False
    remind_hour: int = 21
    last_reminded_date: str = ""


class Storage:
    """SQLite: чек-апы, память, префы, сообщения."""

    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = Lock()
        self._init_db()

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        # Важно: обычный `with sqlite3.connect()` не закрывает файл —
        # только коммитит. Без close() бот течет дескрипторами.
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _now(self) -> str:
        return datetime.now(MSK).isoformat(timespec="seconds")

    def _init_db(self) -> None:
        with self._lock:
            with self._connect() as conn:
                conn.executescript(
                    """
                    CREATE TABLE IF NOT EXISTS checkups (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        mood INTEGER NOT NULL,
                        anxiety INTEGER NOT NULL,
                        energy INTEGER NOT NULL,
                        sleep INTEGER NOT NULL,
                        note TEXT NOT NULL DEFAULT '',
                        created_at TEXT NOT NULL
                    );
                    CREATE INDEX IF NOT EXISTS idx_checkups_user_created
                        ON checkups(user_id, created_at);

                    CREATE TABLE IF NOT EXISTS user_state (
                        user_id INTEGER PRIMARY KEY,
                        mode TEXT NOT NULL DEFAULT '',
                        draft_json TEXT NOT NULL DEFAULT '{}',
                        updated_at TEXT NOT NULL
                    );

                    CREATE TABLE IF NOT EXISTS user_prefs (
                        user_id INTEGER PRIMARY KEY,
                        voice_enabled INTEGER NOT NULL DEFAULT 0,
                        remind_enabled INTEGER NOT NULL DEFAULT 0,
                        remind_hour INTEGER NOT NULL DEFAULT 21,
                        last_reminded_date TEXT NOT NULL DEFAULT ''
                    );

                    CREATE TABLE IF NOT EXISTS user_memory (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        content TEXT NOT NULL,
                        source TEXT NOT NULL DEFAULT 'auto',
                        created_at TEXT NOT NULL
                    );
                    CREATE INDEX IF NOT EXISTS idx_memory_user
                        ON user_memory(user_id, id);

                    CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        role TEXT NOT NULL,
                        content TEXT NOT NULL,
                        created_at TEXT NOT NULL
                    );
                    CREATE INDEX IF NOT EXISTS idx_messages_user
                        ON messages(user_id, id);
                    """
                )
                # Миграция со старой таблицы checkins, если была.
                has_old = conn.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='checkins'"
                ).fetchone()
                if has_old:
                    conn.execute(
                        """
                        INSERT INTO checkups(user_id, mood, anxiety, energy, sleep, note, created_at)
                        SELECT user_id, mood, anxiety, energy, sleep, note, created_at
                        FROM checkins
                        WHERE NOT EXISTS (
                            SELECT 1 FROM checkups c
                            WHERE c.user_id = checkins.user_id
                              AND c.created_at = checkins.created_at
                              AND c.mood = checkins.mood
                        )
                        """
                    )

    def set_mode(self, user_id: int, mode: str, draft: Optional[dict] = None) -> None:
        payload = json.dumps(draft or {}, ensure_ascii=False)
        with self._lock:
            with self._connect() as conn:
                conn.execute(
                    """
                    INSERT INTO user_state(user_id, mode, draft_json, updated_at)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(user_id) DO UPDATE SET
                        mode=excluded.mode,
                        draft_json=excluded.draft_json,
                        updated_at=excluded.updated_at
                    """,
                    (user_id, mode, payload, self._now()),
                )

    def get_mode(self, user_id: int) -> tuple[str, dict]:
        with self._lock:
            with self._connect() as conn:
                row = conn.execute(
                    "SELECT mode, draft_json FROM user_state WHERE user_id=?",
                    (user_id,),
                ).fetchone()
        if not row:
            return "", {}
        try:
            draft = json.loads(row["draft_json"] or "{}")
        except json.JSONDecodeError:
            draft = {}
        if not isinstance(draft, dict):
            draft = {}
        return row["mode"] or "", draft

    def clear_mode(self, user_id: int) -> None:
        self.set_mode(user_id, "", {})

    def add_checkup(
        self,
        user_id: int,
        mood: int,
        anxiety: int,
        energy: int,
        sleep: int,
        note: str = "",
    ) -> None:
        with self._lock:
            with self._connect() as conn:
                conn.execute(
                    """
                    INSERT INTO checkups(user_id, mood, anxiety, energy, sleep, note, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (user_id, mood, anxiety, energy, sleep, note.strip(), self._now()),
                )

    # Обратная совместимость для старых вызовов.
    def add_checkin(self, *args, **kwargs) -> None:
        self.add_checkup(*args, **kwargs)

    def get_checkups(self, user_id: int, days: int = 7) -> list[Checkup]:
        since = (datetime.now(MSK) - timedelta(days=days)).isoformat(timespec="seconds")
        with self._lock:
            with self._connect() as conn:
                rows = conn.execute(
                    """
                    SELECT mood, anxiety, energy, sleep, note, created_at
                    FROM checkups
                    WHERE user_id=? AND created_at>=?
                    ORDER BY created_at ASC
                    """,
                    (user_id, since),
                ).fetchall()
        return [
            Checkup(
                mood=row["mood"],
                anxiety=row["anxiety"],
                energy=row["energy"],
                sleep=row["sleep"],
                note=row["note"] or "",
                created_at=row["created_at"],
            )
            for row in rows
        ]

    def get_checkins(self, user_id: int, days: int = 7) -> list[Checkup]:
        return self.get_checkups(user_id, days=days)

    def stats_text(self, user_id: int, days: int = 7) -> str:
        items = self.get_checkups(user_id, days=days)
        if not items:
            return (
                f"За {days} дн. чек-апов пока нет.\n"
                "Напиши /checkup — займет минуту."
            )

        def avg(field: str) -> float:
            values = [getattr(x, field) for x in items]
            return sum(values) / len(values)

        last = items[-1]
        lines = [
            f"Неделя · {len(items)} чек-апов",
            "",
            f"Среднее · настроение {avg('mood'):.1f} · тревога {avg('anxiety'):.1f}",
            f"          энергия {avg('energy'):.1f} · сон {avg('sleep'):.1f}",
            "",
            f"Последний · {last.mood}/{last.anxiety}/{last.energy}/{last.sleep}",
        ]
        if last.note:
            lines.append(f"Заметка · {last.note}")

        if len(items) >= 3:
            first_half = items[: len(items) // 2]
            second_half = items[len(items) // 2 :]

            def half_avg(part: list[Checkup], field: str) -> float:
                return sum(getattr(x, field) for x in part) / len(part)

            mood_delta = half_avg(second_half, "mood") - half_avg(first_half, "mood")
            anxiety_delta = half_avg(second_half, "anxiety") - half_avg(
                first_half, "anxiety"
            )
            tips = []
            if mood_delta >= 0.7:
                tips.append("настроение чуть выше")
            elif mood_delta <= -0.7:
                tips.append("настроение просело")
            if anxiety_delta >= 0.7:
                tips.append("тревога выросла")
            elif anxiety_delta <= -0.7:
                tips.append("тревога чуть отпустила")
            if tips:
                lines.append("")
                lines.append("Тренд · " + ", ".join(tips))

        return "\n".join(lines)

    def insights_text(self, user_id: int, days: int = 14) -> str:
        items = self.get_checkups(user_id, days=days)
        if len(items) < 3:
            return (
                "Для insights нужно хотя бы 3 чек-апа.\n"
                "Пройди /checkup еще пару раз — и посмотрим паттерны."
            )

        def avg(field: str) -> float:
            return sum(getattr(x, field) for x in items) / len(items)

        notes = [x.note.strip() for x in items if x.note.strip()]
        lines = [
            f"Insights · {days} дн. · {len(items)} чек-апов",
            "",
            f"Фон · настроение {avg('mood'):.1f} · тревога {avg('anxiety'):.1f}",
            f"       энергия {avg('energy'):.1f} · сон {avg('sleep'):.1f}",
        ]

        # Связка сон → настроение / тревога на следующий день (грубо по порядку).
        sleep_mood_pairs = []
        sleep_anxiety_pairs = []
        for i in range(len(items) - 1):
            sleep_mood_pairs.append((items[i].sleep, items[i + 1].mood))
            sleep_anxiety_pairs.append((items[i].sleep, items[i + 1].anxiety))

        def corr_hint(pairs: list[tuple[int, int]], low_label: str, high_label: str) -> str:
            low = [b for a, b in pairs if a <= 4]
            high = [b for a, b in pairs if a >= 7]
            if len(low) < 2 or len(high) < 2:
                return ""
            low_avg = sum(low) / len(low)
            high_avg = sum(high) / len(high)
            if high_avg - low_avg >= 1.0:
                return high_label
            if low_avg - high_avg >= 1.0:
                return low_label
            return ""

        sleep_mood = corr_hint(
            sleep_mood_pairs,
            "после плохого сна настроение чаще ниже",
            "после нормального сна настроение обычно выше",
        )
        sleep_anx = corr_hint(
            sleep_anxiety_pairs,
            "после нормального сна тревога чаще ниже",
            "после плохого сна тревога чаще выше",
        )
        pattern_bits = [x for x in (sleep_mood, sleep_anx) if x]

        # Дни недели с худшей тревогой.
        by_weekday: dict[int, list[int]] = {}
        for item in items:
            try:
                dt = datetime.fromisoformat(item.created_at)
            except ValueError:
                continue
            by_weekday.setdefault(dt.weekday(), []).append(item.anxiety)
        if by_weekday:
            worst_day, vals = max(by_weekday.items(), key=lambda kv: sum(kv[1]) / len(kv[1]))
            day_names = [
                "понедельникам",
                "вторникам",
                "средам",
                "четвергам",
                "пятницам",
                "субботам",
                "воскресеньям",
            ]
            if sum(vals) / len(vals) >= avg("anxiety") + 0.8:
                pattern_bits.append(f"тревога заметнее по {day_names[worst_day]}")

        if pattern_bits:
            lines.append("")
            lines.append("Паттерны")
            for bit in pattern_bits:
                lines.append(f"· {bit}")
        else:
            lines.append("")
            lines.append("Явных паттернов пока мало — накопи еще точек.")

        if notes:
            lines.append("")
            lines.append("Частые заметки")
            for note in notes[-5:]:
                lines.append(f"· {note}")

        mem = self.list_memory(user_id, limit=5)
        if mem:
            lines.append("")
            lines.append("Из памяти о тебе")
            for item in mem:
                lines.append(f"· {item.content}")

        return "\n".join(lines)

    def get_prefs(self, user_id: int) -> UserPrefs:
        with self._lock:
            with self._connect() as conn:
                row = conn.execute(
                    "SELECT * FROM user_prefs WHERE user_id=?",
                    (user_id,),
                ).fetchone()
        if not row:
            return UserPrefs()
        return UserPrefs(
            voice_enabled=bool(row["voice_enabled"]),
            remind_enabled=bool(row["remind_enabled"]),
            remind_hour=int(row["remind_hour"]),
            last_reminded_date=row["last_reminded_date"] or "",
        )

    def set_prefs(self, user_id: int, prefs: UserPrefs) -> None:
        with self._lock:
            with self._connect() as conn:
                conn.execute(
                    """
                    INSERT INTO user_prefs(
                        user_id, voice_enabled, remind_enabled, remind_hour, last_reminded_date
                    )
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(user_id) DO UPDATE SET
                        voice_enabled=excluded.voice_enabled,
                        remind_enabled=excluded.remind_enabled,
                        remind_hour=excluded.remind_hour,
                        last_reminded_date=excluded.last_reminded_date
                    """,
                    (
                        user_id,
                        1 if prefs.voice_enabled else 0,
                        1 if prefs.remind_enabled else 0,
                        int(prefs.remind_hour),
                        prefs.last_reminded_date,
                    ),
                )

    def list_due_reminders(self) -> list[int]:
        now = datetime.now(MSK)
        today = now.date().isoformat()
        hour = now.hour
        due: list[int] = []
        with self._lock:
            with self._connect() as conn:
                rows = conn.execute(
                    """
                    SELECT user_id, remind_hour, last_reminded_date
                    FROM user_prefs
                    WHERE remind_enabled=1
                    """
                ).fetchall()
        for row in rows:
            if int(row["remind_hour"]) != hour:
                continue
            if (row["last_reminded_date"] or "") == today:
                continue
            due.append(int(row["user_id"]))
        return due

    def mark_reminded(self, user_id: int) -> None:
        prefs = self.get_prefs(user_id)
        prefs.last_reminded_date = datetime.now(MSK).date().isoformat()
        self.set_prefs(user_id, prefs)

    def add_memory(self, user_id: int, content: str, source: str = "auto") -> None:
        text = content.strip()
        if not text:
            return
        with self._lock:
            with self._connect() as conn:
                exists = conn.execute(
                    """
                    SELECT id FROM user_memory
                    WHERE user_id=? AND lower(content)=lower(?)
                    LIMIT 1
                    """,
                    (user_id, text),
                ).fetchone()
                if exists:
                    return
                conn.execute(
                    """
                    INSERT INTO user_memory(user_id, content, source, created_at)
                    VALUES (?, ?, ?, ?)
                    """,
                    (user_id, text, source, self._now()),
                )
                # Держим не больше 40 фактов на человека.
                rows = conn.execute(
                    """
                    SELECT id FROM user_memory
                    WHERE user_id=?
                    ORDER BY id DESC
                    """,
                    (user_id,),
                ).fetchall()
                for old in rows[40:]:
                    conn.execute("DELETE FROM user_memory WHERE id=?", (old["id"],))

    def list_memory(self, user_id: int, limit: int = 20) -> list[MemoryItem]:
        with self._lock:
            with self._connect() as conn:
                rows = conn.execute(
                    """
                    SELECT id, content, source, created_at
                    FROM user_memory
                    WHERE user_id=?
                    ORDER BY id DESC
                    LIMIT ?
                    """,
                    (user_id, limit),
                ).fetchall()
        return [
            MemoryItem(
                id=row["id"],
                content=row["content"],
                source=row["source"],
                created_at=row["created_at"],
            )
            for row in rows
        ]

    def memory_prompt_block(self, user_id: int) -> str:
        items = list(reversed(self.list_memory(user_id, limit=12)))
        if not items:
            return ""
        lines = ["Что уже известно о человеке:"]
        for item in items:
            lines.append(f"- {item.content}")
        return "\n".join(lines)

    def add_message(self, user_id: int, role: str, content: str) -> None:
        with self._lock:
            with self._connect() as conn:
                conn.execute(
                    """
                    INSERT INTO messages(user_id, role, content, created_at)
                    VALUES (?, ?, ?, ?)
                    """,
                    (user_id, role, content, self._now()),
                )
                rows = conn.execute(
                    """
                    SELECT id FROM messages
                    WHERE user_id=?
                    ORDER BY id DESC
                    """,
                    (user_id,),
                ).fetchall()
                for old in rows[80:]:
                    conn.execute("DELETE FROM messages WHERE id=?", (old["id"],))

    def get_messages(self, user_id: int, limit: int = 40) -> list[dict]:
        with self._lock:
            with self._connect() as conn:
                rows = conn.execute(
                    """
                    SELECT role, content, created_at
                    FROM messages
                    WHERE user_id=?
                    ORDER BY id DESC
                    LIMIT ?
                    """,
                    (user_id, limit),
                ).fetchall()
        items = [
            {
                "role": row["role"],
                "content": row["content"],
                "created_at": row["created_at"],
            }
            for row in rows
        ]
        items.reverse()
        return items

    def export_text(self, user_id: int) -> str:
        prefs = self.get_prefs(user_id)
        mem = list(reversed(self.list_memory(user_id, limit=50)))
        checkups = self.get_checkups(user_id, days=90)
        messages = self.get_messages(user_id, limit=80)
        lines = [
            "Экспорт Агора",
            f"Дата · {self._now()}",
            f"Голос · {'вкл' if prefs.voice_enabled else 'выкл'}",
            f"Напоминания · {'вкл' if prefs.remind_enabled else 'выкл'} · час {prefs.remind_hour}",
            "",
            "Память",
        ]
        if mem:
            lines.extend(f"- {m.content}" for m in mem)
        else:
            lines.append("- пусто")
        lines.append("")
        lines.append("Чек-апы")
        if checkups:
            for c in checkups:
                note = f" · {c.note}" if c.note else ""
                lines.append(
                    f"- {c.created_at} · {c.mood}/{c.anxiety}/{c.energy}/{c.sleep}{note}"
                )
        else:
            lines.append("- пусто")
        lines.append("")
        lines.append("Недавние сообщения")
        if messages:
            for m in messages:
                lines.append(f"- [{m['created_at']}] {m['role']}: {m['content']}")
        else:
            lines.append("- пусто")
        return "\n".join(lines)

    def forget_user(self, user_id: int) -> None:
        with self._lock:
            with self._connect() as conn:
                for table in (
                    "checkups",
                    "user_state",
                    "user_prefs",
                    "user_memory",
                    "messages",
                ):
                    conn.execute(f"DELETE FROM {table} WHERE user_id=?", (user_id,))
                # Старая таблица, если осталась.
                try:
                    conn.execute("DELETE FROM checkins WHERE user_id=?", (user_id,))
                except sqlite3.OperationalError:
                    pass
