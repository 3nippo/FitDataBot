import enum

from sqlalchemy import Integer, String, Enum, Boolean
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'user'
    id = mapped_column(Integer, primary_key=True)


class ExcerciseUnit(enum.Enum):
    seconds = 1
    repetitions = 2


class Excercise(Base):
    __tablename__ = 'excercise'
    user_id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String)
    unit = mapped_column(Enum(ExcerciseUnit))
    track_rpe = mapped_column(Boolean)