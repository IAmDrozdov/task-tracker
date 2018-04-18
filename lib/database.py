import jsonpickle
import json


def serialize(container, path):
        with open(path, mode='w+', encoding='utf-8') as db:
            to_write = jsonpickle.encode(container)
            db.write(to_write)


def deserialize(path):
    try:
        with open(path, mode='r', encoding='utf-8') as db:
            json_file = db.read()
        return jsonpickle.decode(json_file)
    except json.decoder.JSONDecodeError:
        return {'current_user': None,
                'users': []}
    except FileNotFoundError:
        with open(path, mode='w+', encoding='utf-8') as db:
            db.write(jsonpickle.encode(({'current_user': None,
                                       'users': []})))
        with open(path, mode='r', encoding='utf-8') as db:
            json_file = db.read()
        return jsonpickle.decode(json_file)

