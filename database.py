import os
from datetime import date
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, BigInteger, String, Date, ForeignKey

load_dotenv()




DATABASE_URL = os.getenv("DATABASE_URL").replace(
    "postgresql://",
    "postgresql+asyncpg://"
)

engine = create_async_engine(DATABASE_URL)


async_session = async_sessionmaker(engine, expire_on_commit=False)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class Users(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=True)
    user_name: Mapped[str] = mapped_column(String, nullable=True)
    nomer: Mapped[str] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(default="user", nullable=True) # default "user" qildik

# 🔥 YANGI QO'SHILGAN JADVAL (Tushumlar va kurs ruxsatlari uchun)
class Payments(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    course_name: Mapped[str] = mapped_column(String(50), nullable=False) # 'backend' yoki 'frontend'
    amount: Mapped[int] = mapped_column(Integer, nullable=False)         # to'lov summasi
    channel_id: Mapped[str] = mapped_column(String(50), nullable=False)   # qo'shilgan kanal ID'si
    created_at: Mapped[date] = mapped_column(Date, default=date.today)   # to'lov sanasi
