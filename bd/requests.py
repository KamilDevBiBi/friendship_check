from bd.models import async_session
from bd.models import User, PassedTest
from sqlalchemy import select, desc
from sqlalchemy.orm import joinedload


async def load_user(tg_id: int, first_name: str, username: str) -> None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if not user:
            session.add(User(tg_id=tg_id, first_name=first_name, username=username))
            await session.commit()


async def get_user(tg_id: int) -> User:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        return user
    

async def set_user_answers(tg_id: int, answers: str) -> bool:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if user:
            if (user.answers is not None) and len(user.answers) > 0:
                # Если у пользователя уже были ответы, сообщаем об ошибке
                return False
            
            user.answers = answers
            await session.commit()

            return True


async def get_user_answers(tg_id: int) -> None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if user:
            return user.answers


async def delete_user_answers(tg_id: int) -> None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))

        if user:
            user.answers = None

            # Удаляем все записи, в которых пользователи прошли прошлый тесты
            tests = await get_tests_by_owner(user.id)
            for test in tests:
                await session.delete(test)

            await session.commit()


async def create_passed_test(owner_id: int, passer_id: int, result: int) -> bool:
    async with async_session() as session:
        passed_test = await session.scalar(select(PassedTest).where(PassedTest.passer_id == passer_id, PassedTest.owner_id == owner_id))

        if not passed_test:
            new_passed_test = PassedTest(
                passer_id=passer_id,
                owner_id=owner_id,
                correct_questions=result
            )

            session.add(new_passed_test)
            await session.commit()
            
            return True
        
        # Если такой объект уже есть, сообщаем об ошибке
        return False


async def get_passed_test(friend_id: int, passer_id: int) -> PassedTest:
    async with async_session() as session:
        passed_test = await session.scalar(select(PassedTest).where(PassedTest.passer_id == passer_id, PassedTest.owner_id == friend_id))

        return passed_test


async def get_tests_by_owner(owner_id: int) -> list[PassedTest]:
    async with async_session() as session:
        passed_tests = await session.scalars(select(PassedTest).where(PassedTest.owner_id == owner_id)
                                             .options(joinedload(PassedTest.passer))
                                             .order_by(desc(PassedTest.correct_questions)))

        return passed_tests

