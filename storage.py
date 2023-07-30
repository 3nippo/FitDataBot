import schema
from sqlalchemy.orm import Session
from sqlalchemy import select

def save_record(engine, record):
    with Session(engine) as session:
        session.add(record)
        session.commit()


def fetch_excercises(engine, user_id):
    stmt = select(schema.Excercise).where(schema.Excercise.user_id == user_id)

    with Session(engine) as session:
        return session.scalars(stmt).all()