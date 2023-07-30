import schema
from sqlalchemy.orm import Session
from sqlalchemy import select, cast, Date, func
import datetime

def save_record(engine, record):
    with Session(engine) as session:
        session.add(record)
        session.commit()


def fetch_excercises(engine, user_id, only_rpe_tracked=False):
    stmt = select(schema.Excercise).where(schema.Excercise.user_id == user_id)

    if only_rpe_tracked:
        stmt = stmt.where(schema.Excercise.track_rpe)

    with Session(engine) as session:
        return session.scalars(stmt).all()


def fetch_total_volume(engine, user_id, weeks):
    date_from = datetime.datetime.utcnow() - datetime.timedelta(weeks=weeks)

    stmt = select(
        func.sum((schema.Set.work * schema.Set.weight)).label('volume'),
        cast(schema.Set.datetime, Date).label('date')
    ).join(
        schema.Excercise
    ).where(
        schema.Excercise.unit == schema.ExcerciseUnit.repetitions
    ).where(
        schema.Set.datetime >= date_from
    ).where(
        schema.Set.user_id == user_id
    ).order_by(
        'date'
    ).group_by(
        'date'
    )

    with Session(engine) as session:
        return session.execute(stmt).all()


def fetch_total_rpe(engine, user_id, weeks):
    date_from = datetime.datetime.utcnow() - datetime.timedelta(weeks=weeks)

    stmt = select(
        func.max(schema.Set.rpe).label('RPE'),
        cast(schema.Set.datetime, Date).label('date')
    ).join(
        schema.Excercise
    ).where(
        schema.Excercise.track_rpe
    ).where(
        schema.Set.datetime >= date_from
    ).where(
        schema.Set.user_id == user_id
    ).order_by(
        'date'
    ).group_by(
        'date'
    )

    with Session(engine) as session:
        return session.execute(stmt).all()


def fetch_excercise_volume(engine, user_id, weeks, excercise_id):
    date_from = datetime.datetime.utcnow() - datetime.timedelta(weeks=weeks)

    stmt = select(
        func.sum((schema.Set.work * schema.Set.weight)).label('volume'),
        cast(schema.Set.datetime, Date).label('date')
    ).join(
        schema.Excercise
    ).where(
        schema.Excercise.id == excercise_id
    ).where(
        schema.Set.datetime >= date_from
    ).where(
        schema.Set.user_id == user_id
    ).order_by(
        'date'
    ).group_by(
        'date'
    )

    with Session(engine) as session:
        return session.execute(stmt).all()


def fetch_excercise_rpe(engine, user_id, weeks, excercise_id):
    date_from = datetime.datetime.utcnow() - datetime.timedelta(weeks=weeks)

    stmt = select(
        func.max(schema.Set.rpe).label('RPE'),
        cast(schema.Set.datetime, Date).label('date')
    ).join(
        schema.Excercise
    ).where(
        schema.Excercise.id == excercise_id
    ).where(
        schema.Set.datetime >= date_from
    ).where(
        schema.Set.user_id == user_id
    ).order_by(
        'date'
    ).group_by(
        'date'
    )

    with Session(engine) as session:
        return session.execute(stmt).all()


def fetch_excercise_max_weight(engine, user_id, weeks, excercise_id):
    date_from = datetime.datetime.utcnow() - datetime.timedelta(weeks=weeks)

    stmt = select(
        func.max(schema.Set.weight).label('max weight'),
        cast(schema.Set.datetime, Date).label('date')
    ).join(
        schema.Excercise
    ).where(
        schema.Excercise.id == excercise_id
    ).where(
        schema.Set.datetime >= date_from
    ).where(
        schema.Set.user_id == user_id
    ).order_by(
        'date'
    ).group_by(
        'date'
    )

    with Session(engine) as session:
        return session.execute(stmt).all()