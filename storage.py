import schema

def save_record(engine, record):
    print(record)


def fetch_excercises(engine, user_id):
    names = ['spooky', 'scary', 'skeletons']
    
    excercises = []
    for idx, name in enumerate(names):
        excercise = schema.Excercise()
        excercise.id = idx
        excercise.user_id = user_id
        excercise.name = name
        excercise.unit = schema.ExcerciseUnit.repetitions
        excercise.track_rpe = True

        excercises.append(excercise)

    return excercises