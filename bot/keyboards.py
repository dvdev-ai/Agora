from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove


def hide_menu() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()


def start_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Чек-ап", callback_data="nav:checkup"),
                InlineKeyboardButton(text="Неделя", callback_data="nav:stats"),
            ],
            [
                InlineKeyboardButton(text="Insights", callback_data="nav:insights"),
                InlineKeyboardButton(text="Сводка", callback_data="nav:summary"),
            ],
            [
                InlineKeyboardButton(text="Идея", callback_data="nav:idea"),
                InlineKeyboardButton(text="Справка", callback_data="nav:help"),
            ],
        ]
    )


def score_keyboard(prefix: str = "cu") -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    row: list[InlineKeyboardButton] = []
    for n in range(0, 11):
        row.append(
            InlineKeyboardButton(text=str(n), callback_data=f"{prefix}:score:{n}")
        )
        if len(row) == 6:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append(
        [InlineKeyboardButton(text="Отмена", callback_data=f"{prefix}:cancel")]
    )
    return InlineKeyboardMarkup(inline_keyboard=rows)


def note_keyboard(prefix: str = "cu") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Пропустить", callback_data=f"{prefix}:skip"),
                InlineKeyboardButton(text="Отмена", callback_data=f"{prefix}:cancel"),
            ]
        ]
    )


def panic_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Чуть отпустило", callback_data="panic:ok"),
                InlineKeyboardButton(text="Чек-ап", callback_data="panic:checkup"),
            ],
            [
                InlineKeyboardButton(text="Нужна помощь", callback_data="panic:help"),
            ],
        ]
    )


def job_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Отмена", callback_data="job:cancel")]
        ]
    )


def idea_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Отмена", callback_data="idea:cancel")]
        ]
    )


def after_checkup_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Неделя", callback_data="nav:stats"),
                InlineKeyboardButton(text="Insights", callback_data="nav:insights"),
            ],
            [
                InlineKeyboardButton(text="Еще раз", callback_data="nav:checkup"),
            ],
        ]
    )


def after_stats_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Новый чек-ап", callback_data="nav:checkup"),
                InlineKeyboardButton(text="Insights", callback_data="nav:insights"),
            ]
        ]
    )


def after_idea_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Еще идея", callback_data="nav:idea")]
        ]
    )


def remind_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="21:00", callback_data="remind:21"),
                InlineKeyboardButton(text="22:00", callback_data="remind:22"),
                InlineKeyboardButton(text="10:00", callback_data="remind:10"),
            ],
            [
                InlineKeyboardButton(text="Выключить", callback_data="remind:off"),
            ],
        ]
    )
