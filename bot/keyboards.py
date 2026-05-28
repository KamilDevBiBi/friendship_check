from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, SwitchInlineQueryChosenChat

question_0 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🍂 Осень", callback_data="test_0_0"), InlineKeyboardButton(text="☀️ Лето", callback_data="test_0_1")],
    [InlineKeyboardButton(text="❄️ Зима", callback_data="test_0_2"), InlineKeyboardButton(text="🌷 Весна", callback_data="test_0_3")]
])

question_1 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="☕ Друзья в кафе", callback_data="test_1_0"), InlineKeyboardButton(text="📚 Дома с книгой", callback_data="test_1_1")],
    [InlineKeyboardButton(text="🌲 Пойти на природу", callback_data="test_1_2"), InlineKeyboardButton(text="⚡ Активный отдых", callback_data="test_1_3")]
])

question_2 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🍝 Итальянская", callback_data="test_2_0"), InlineKeyboardButton(text="🍣 Японская", callback_data="test_2_1")],
    [InlineKeyboardButton(text="🥟 Русская", callback_data="test_2_2"), InlineKeyboardButton(text="🍔 Фастфуд", callback_data="test_2_3")]
])

question_3 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="💬 Общение", callback_data="test_3_0"), InlineKeyboardButton(text="🏆 Достижения", callback_data="test_3_1")],
    [InlineKeyboardButton(text="✈️ Путешествия", callback_data="test_3_2"), InlineKeyboardButton(text="🍕 Уют/еда", callback_data="test_3_3")]
])

question_4 = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🗣️ Поговорить", callback_data="test_4_0"), InlineKeyboardButton(text="🏃 Спорт", callback_data="test_4_1")],
    [InlineKeyboardButton(text="🎮 Фильмы/игры", callback_data="test_4_2"), InlineKeyboardButton(text="⚡ Решать сразу", callback_data="test_4_3")]
])


KEYBOARDS = [question_0, question_1, question_2, question_3, question_4]

keep_test_btn = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Продолжить 👌", callback_data="continue")]
])

old_or_new_test = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Продолжить 👌", callback_data="continue"), InlineKeyboardButton(text="Перепройти 👍", callback_data="new")]
])


def create_share_button(user_test_link: str) -> InlineKeyboardMarkup:
    share_text = f"Как хорошо ты меня знаешь? \n\n {user_test_link}"
    share_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Отправить другу ➕", switch_inline_query_chosen_chat=SwitchInlineQueryChosenChat(query=share_text, allow_user_chats=True))]
    ])

    return share_keyboard

def create_rating_button(tg_id: int) -> InlineKeyboardButton:
    rating_button = InlineKeyboardButton(text="Рейтинг 📊", callback_data=f"rating_{tg_id}")
    return rating_button


main_keaybord = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Перепройти ✅", callback_data="restart")]
])