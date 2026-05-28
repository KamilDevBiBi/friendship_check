from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped, relationship
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs

from sqlalchemy import BigInteger, ForeignKey

from config import settings

engine = create_async_engine(url=settings.database_url)
async_session = async_sessionmaker(engine)

class Base(DeclarativeBase, AsyncAttrs):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id = mapped_column(BigInteger)

    first_name: Mapped[str] = mapped_column()
    username: Mapped[str] = mapped_column()

    answers: Mapped[str] = mapped_column(nullable=True)

    passed_tests: Mapped[list["PassedTest"]] = relationship("PassedTest", foreign_keys="PassedTest.passer_id", back_populates="passer")



class PassedTest(Base):
    __tablename__ = 'passed_tests'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    passer_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    owner_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    correct_questions: Mapped[int] = mapped_column()

    passer: Mapped["User"] = relationship("User", foreign_keys=[passer_id], back_populates="passed_tests")


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)