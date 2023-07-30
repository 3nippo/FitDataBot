import schema
from sqlalchemy.orm import Session
from sqlalchemy import select
import datetime

def save_record(engine, record):
    with Session(engine) as session:
        session.add(record)
        session.commit()


def fetch_excercises(engine, user_id):
    stmt = select(schema.Excercise).where(schema.Excercise.user_id == user_id)

    with Session(engine) as session:
        return session.scalars(stmt).all()


def fetch_total_volume(engine, user_id, weeks):
    date_from = datetime.datetime.utcnow() - datetime.timedelta(weeks=weeks)

    stmt = select(
        (schema.Set.work * schema.Set.weight).label('volume'),
        schema.Set.datetime
    ).join(
        schema.Excercise
    ).where(
        schema.Excercise.unit == schema.ExcerciseUnit.repetitions
    ).where(
        schema.Set.datetime >= date_from
    ).where(
        schema.Set.user_id == user_id
    ).order_by(
        schema.Set.datetime
    )

    with Session(engine) as session:
        return session.execute(stmt).all()