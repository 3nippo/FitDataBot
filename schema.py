import enum
import datetime

from sqlalchemy import Integer, String, Enum, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import mapped_column, relationship


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
    id = mapped_column(Integer, primary_key=True)
    user_id = mapped_column(Integer)
    name = mapped_column(String)
    unit = mapped_column(Enum(ExcerciseUnit))
    track_rpe = mapped_column(Boolean)
    sets = relationship('Set', collection_class=set, back_populates='excercise')

    def __repr__(self) -> str:
        return "{} {} {} {}".format(self.user_id, self.name, self.unit, self.track_rpe)


class Set(Base):
    __tablename__ = 'set'
    id = mapped_column(Integer, primary_key=True)
    user_id = mapped_column(Integer)
    excercise_id = mapped_column(ForeignKey("excercise.id"))
    excercise = relationship('Excercise', back_populates='sets')
    work = mapped_column(Integer)
    weight = mapped_column(Integer)
    rpe = mapped_column(Integer)
    rest = mapped_column(Integer)
    datetime = mapped_column(DateTime, default=datetime.datetime.utcnow)

    def __repr__(self) -> str:
        return "{} {} {} {} {}".format(self.excercise_id, self.user_id, self.work, self.rpe, self.rest)
    
    def empty(self):
        return self.work is None