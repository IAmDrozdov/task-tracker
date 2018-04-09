import jsonpickle


def serialize(container, path):
    with open(path, mode='w', encoding='utf-8') as db:
        to_write = jsonpickle.encode(container)
        db.write(to_write)


def deserialize(path):
    with open(path, mode='r', encoding='utf-8') as db:
        json_file = db.read()
    return jsonpickle.decode(json_file)
