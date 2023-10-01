import schema
from sqlalchemy.orm import Session
from sqlalchemy import select, cast, Date, func
import datetime


class ExcerciseSearchOptions:
    def __init__(self, unit=None, only_rpe_tracked=False):
        self.unit = unit
        self.only_rpe_tracked = only_rpe_tracked


def save_record(engine, record):
    with Session(engine) as session:
        session.add(record)
        session.commit()


def save_record_with_session(session, record):
    session.add(record)
    session.commit()


def fetch_excercises(engine, user_id, search_options=ExcerciseSearchOptions()):
    with Session(engine) as session:
        return fetch_excercises_with_session(session, user_id, search_options)


def fetch_excercises_with_session(session, user_id, search_options=ExcerciseSearchOptions()):
    stmt = select(schema.Excercise).where(schema.Excercise.user_id == user_id)

    if search_options.only_rpe_tracked:
        stmt = stmt.where(schema.Excercise.track_rpe)

    if search_options.unit:
        stmt = stmt.where(schema.Excercise.unit == search_options.unit)

    return session.scalars(stmt).all()


def fetch_total_volume(engine, user_id, weeks):
    date_from = datetime.datetime.utcnow() - datetime.timedelta(weeks=weeks)

    stmt = select(
        cast(schema.Set.datetime, Date).label('date'),
        func.sum((schema.Set.work * schema.Set.weight)).label('volume')
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
        return stmt.columns.keys(), session.execute(stmt).all()


def fetch_total_rpe(engine, user_id, weeks):
    date_from = datetime.datetime.utcnow() - datetime.timedelta(weeks=weeks)

    stmt = select(
        cast(schema.Set.datetime, Date).label('date'),
        func.max(schema.Set.rpe).label('RPE')
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
        return stmt.columns.keys(), session.execute(stmt).all()


def fetch_excercise_volume(engine, user_id, weeks, excercise_id):
    date_from = datetime.datetime.utcnow() - datetime.timedelta(weeks=weeks)

    stmt = select(
        cast(schema.Set.datetime, Date).label('date'),
        func.sum((schema.Set.work * schema.Set.weight)).label('volume')
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
        return stmt.columns.keys(), session.execute(stmt).all()


def fetch_excercise_rpe(engine, user_id, weeks, excercise_id):
    date_from = datetime.datetime.utcnow() - datetime.timedelta(weeks=weeks)

    stmt = select(
        cast(schema.Set.datetime, Date).label('date'),
        func.max(schema.Set.rpe).label('RPE')
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
        return stmt.columns.keys(), session.execute(stmt).all()


def fetch_excercise_max_weight(engine, user_id, weeks, excercise_id):
    date_from = datetime.datetime.utcnow() - datetime.timedelta(weeks=weeks)

    stmt = select(
        cast(schema.Set.datetime, Date).label('date'),
        func.max(schema.Set.weight).label('max weight')
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
        return stmt.columns.keys(), session.execute(stmt).all()


def fetch_excercise_time(engine, user_id, weeks, excercise_id):
    date_from = datetime.datetime.utcnow() - datetime.timedelta(weeks=weeks)

    stmt = select(
        cast(schema.Set.datetime, Date).label('date'),
        func.max(schema.Set.work).label('time')
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
        return stmt.columns.keys(), session.execute(stmt).all()