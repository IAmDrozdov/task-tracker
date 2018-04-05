import json
from edcoder import Encoder


def serialize(container, path):
    with open(path, mode='w', encoding='utf-8') as db:
        json.dump(container, db, cls=Encoder, indent=4)


def deserialize(path):
    return json.loads(open(path).read())
