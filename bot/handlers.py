from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram import F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from .keyboards import KEYBOARDS, keep_test_btn, old_or_new_test, main_keaybord, create_share_button, create_rating_button

import bd.requests as rq
from bd.requests import User

from copy import deepcopy


class AnswersForm(StatesGroup):
    progress = State()


router = Router()

QUESTIONS_COUNT = 5
QUESTIONS = ["Какое время года тебе больше всего привлекает?", "Как ты предпочтёшь провести выходной?", "Какая кухня тебе ближе всего?",
             "Что приносит тебе наибольшую радость?", "Как ты обычно справляешься со стрессом или проблемой?"]
FRIENDSHIP_LEVELS = ["Невидимый друг 🫥", "Пересекались один раз 🤔", "Знакомые 😌", "Хорошие друзья ☺️", "Крепкие друзья 🤩", "Братья 😎"]


@router.message(CommandStart())
async def greeting(message: Message, state: FSMContext):
    await rq.load_user(message.from_user.id, message.from_user.first_name, message.from_user.username)

    args = message.text.split(maxsplit=1)

    if len(args) > 1:
        friend_id = int(args[1]) # id пользователя, который поделился тестом

        if friend_id == message.from_user.id:
            await message.answer("Ты не можешь пройти свой тест 😊.")
            return
        
        friend = await rq.get_user(friend_id)
        if friend is None:
            await message.answer("К сожалению, такого пользователя у меня нет 😯.")
            return
        elif not friend.answers or len(friend.answers) <= 4:
            await message.answer("Этот пользователь ещё не создал тест 😶‍🌫️.")
            return
        
        cur_user = await rq.get_user(message.from_user.id)
        friend_test = await rq.get_passed_test(friend.id, cur_user.id)

        if friend_test is not None:
            results = get_passed_test_result(friend_test.correct_questions)
            await message.answer(f"Ты уже прошел тест пользователя {friend.first_name}.\nТвой результат: {results[0]}%\nУровень дружбы: {results[1]}")
            return
        
        await state.clear() # убираем состояние, которое могло быть до этого
        
        await state.set_state(AnswersForm.progress)
        await state.update_data(is_friend=friend)

        await message.answer(f"Выполни тест, составленный {friend.first_name}. Отвечай так, как думаешь ответил бы он.")
        await send_next_question(message, 0, friend)

    else:
        await message.answer("Привет! Это бот проверка дружбы! Напиши команду /start_test, чтобы создать свой тест про себя и отправить их друзьями.")


@router.message(Command("start_test"))
async def send_friend_test(message: Message, state: FSMContext):
    user_answers = await rq.get_user_answers(message.from_user.id) # Если пользователь прошель весь тест и результаты уже есть в БД
    cur_answers = await state.get_value("answers") # Если пользователь не до конца прошел тест (результаты еще не сохранены в БД)
    friend = await state.get_value("is_friend") # Если пользователь проходит чей-то тест

    if friend:
        friend_text = f"Сейчас ты проходишь тест пользователя {friend.first_name}. Ответь до конца на его вопросы 😉."
        await message.answer(friend_text, reply_markup=keep_test_btn)

    elif (user_answers is not None) and len(user_answers) > 0:
        # Копируем клавиатуру, чтобы не добавлять кнопки к одному и тому же объекту
        keyboard = create_main_keyboard(message)

        await message.answer("Вы уже завершили прохождение теста. Хотите перепройти?", reply_markup=keyboard)

    elif cur_answers is not None:
        await message.answer("Вы уже начали проходить тест. Хотите продолжить или начать с начала?", reply_markup=old_or_new_test)

    else:
        await state.set_state(AnswersForm.progress)
        await state.update_data(is_friend=False)

        await message.answer("Ответь на 5 вопросов ниже. Принимаются только честные ответы, а то друзья смогут ответить некорректно.")
        await send_next_question(message, 0)


@router.callback_query(F.data.startswith("test"), AnswersForm.progress)
async def process_button(callback: CallbackQuery, state: FSMContext):
    question_index, answer = callback.data.split("_")[1:]
    question_index = int(question_index)

    data = await state.get_data()
    last_answers = data.get('answers', '')

    # Если пользователь понажимал на несколько кнопкам подряд, обрабатываем только один из них
    if len(last_answers) >= question_index + 1:
        return
    
    new_answers = last_answers + answer

    if question_index <= 3:
        # Сохраняем промежуточные результаты в fsm
        await state.update_data(answers=new_answers)

        await send_next_question(callback.message, question_index + 1, await state.get_value('is_friend'))
    elif question_index == 4:
        # Если пользователь ответил на последний вопрос
        await process_last_question(callback, state, new_answers)
    

def create_main_keyboard(message: Message):
    keyboard = deepcopy(main_keaybord)

    share_button = create_share_button(f"t.me/BeautifulFriendsBot?start={message.from_user.id}").inline_keyboard[0][0]
    rating_button = create_rating_button(message.from_user.id)

    keyboard.inline_keyboard.append([rating_button])
    keyboard.inline_keyboard.append([share_button])

    return keyboard


async def send_next_question(message: Message, index: int, friend: User = None):
    if friend is None or not friend:
        if index == 0:
            await message.answer(QUESTIONS[index], reply_markup=KEYBOARDS[index])
        elif index <= 4:
            if message.text == QUESTIONS[index]:
                return
            
            await message.edit_text(QUESTIONS[index])
            await message.edit_reply_markup(reply_markup=KEYBOARDS[index])

    else:
        FRIEND_QUESTIONS = [f"Какое время года нравится больше всего {friend.first_name}", f"Как {friend.first_name} предпочтёт провести выходной?", f"Какая у {friend.first_name} кухня тебе ближе всего?", f"Что радует {friend.first_name} больше всего?", f"Как {friend.first_name} обычно справляеться со стрессом или проблемой?"]
        if index == 0:
            await message.answer(FRIEND_QUESTIONS[index], reply_markup=KEYBOARDS[index])
        elif index <= 4:
            if message.text == FRIEND_QUESTIONS[index]:
                return
            
            await message.edit_text(FRIEND_QUESTIONS[index])
            await message.edit_reply_markup(reply_markup=KEYBOARDS[index])


async def process_last_question(callback: CallbackQuery, state: FSMContext, user_answers: str):
    friend = await state.get_value('is_friend')

    if friend:
        # Если пользователь проходил теста друга - сравниваем ответы и отправляем результат
        results = await check_answers(friend.answers, user_answers)
        if not results:
            # Если пользователь как то ответил не на 5 вопросов, то выводим сообщение об ошибке и удаляем состояние
            await process_invalid_test(callback, state)
            return

        passer = await rq.get_user(callback.from_user.id)
        response = await rq.create_passed_test(friend.id, passer.id, results[2])
        if not response:
            await callback.message.answer("Не нажимайте кнопки подряд. Вы уже прошли тест. 😊")
            return

        await send_friend_test_results(callback, friend, results)
    else:
        # Если пользователь сам создал тест - сохраняем результаты в БД и отправляем ссылку для прохождения
        response = await rq.set_user_answers(callback.from_user.id, user_answers)
        if not response:
            await callback.message.answer("Не нажимайте кнопки подряд. Вы уже создали тест. 😊")
            return

        await callback.message.edit_text(f"""Ты ответил на все вопросы! Вот твоя ссылка: t.me/BeautifulFriendsBot?start={callback.from_user.id}\n
Поделись ей с друзьями, чтобы они прошли твой тест!""")
        await callback.message.edit_reply_markup(reply_markup=create_share_button(f"t.me/BeautifulFriendsBot?start={callback.from_user.id}"))
        
    # В конце очищаем текущее состояние    
    await state.clear()


async def check_answers(user_answers: str, friend_answers: str) -> tuple[int, str, int]:
    if len(user_answers) != len(friend_answers):
        return False

    correct_answers = 0
    for i in range(len(friend_answers)):
        if friend_answers[i] == user_answers[i]:
            correct_answers += 1
    
    return get_passed_test_result(correct_answers) # отправляем результат прохождения теста


def get_passed_test_result(correct_answers: int) -> tuple[int, str, int]:
    correct_percent = (correct_answers / 5) * 100
    friendship_level = FRIENDSHIP_LEVELS[correct_answers]

    return correct_percent, friendship_level, correct_answers


async def send_friend_test_results(callback: CallbackQuery, friend: User, results: tuple[int, str, int]):
    # Отправляем тому, кто прошел тест
    await callback.message.edit_text(f"Ты прошел тест пользователя <a href='https://t.me/{friend.username}'>{friend.first_name}</a>! 🥳\nТвой результат: {results[0]}%\nУровень дружбы: {results[1]}", parse_mode="HTML")
    # Отправляем тому, кто создал тест
    await callback.bot.send_message(chat_id=friend.tg_id, text=f"Пользователь <a href='https://t.me/{callback.from_user.username}'>{callback.from_user.first_name}</a> прошел твой тест!\nЕго результат: {results[0]}%\nУровень дружбы: {results[1]}", parse_mode="HTML")


async def process_invalid_test(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Упс! Что-то пошло не так.\nКажется ты ответил на большее число вопросов. Попробуй заново 😯.")


@router.callback_query(F.data == "continue", AnswersForm.progress)
async def continue_test(callback: CallbackQuery, state: FSMContext):
    answers = await state.get_value('answers')
    friend = await state.get_value('is_friend')

    await send_next_question(callback.message, len(answers), friend)


@router.callback_query(F.data == "new", AnswersForm.progress)
async def new_test(callback: CallbackQuery, state: FSMContext):
    await state.clear()

    await send_next_question(callback.message, 0)
    await state.set_state(AnswersForm.progress)


@router.callback_query(F.data == "restart")
async def start_new_test(callback: CallbackQuery, state: FSMContext):
    await rq.delete_user_answers(callback.from_user.id)
    await callback.message.edit_text("Твои прошлые результаты были очищены ✅.\nЗаново пройди тест, чтобы снова поделится с друзьями! 😉")

    await send_next_question(callback.message, 0)
    await state.set_state(AnswersForm.progress)


@router.callback_query(F.data.startswith("rating"))
async def show_test_rating(callback: CallbackQuery):
    owner_tg_id = int(callback.data.split("_")[1])

    owner = await rq.get_user(owner_tg_id)
    passed_tests = await rq.get_tests_by_owner(owner.id)

    rating_rows = ["Рейтинг пользователь, которые прошли твой тест:\n"]
    for test in passed_tests:
        results = get_passed_test_result(test.correct_questions)

        row = f"{test.passer.first_name} - результат {results[0]}%"
        rating_rows.append(row)
    
    if len(rating_rows) <= 1:
        if (owner.answers is not None) and len(owner.answers) > 0:
            user_test_link = f"t.me/BeautifulFriendsBot?start={owner_tg_id}"
            await callback.message.answer("Твой тест ещё не прошли. Скорее делись ссылкой с друзьями! 😊", reply_markup=create_share_button(user_test_link))
        else:
            await callback.message.answer("У тебя ещё нет теста. Нажимай /start_test, чтобы создать его 😉.")
        
        return

    rating_text = '\n'.join(rating_rows)
    await callback.message.answer(rating_text)
