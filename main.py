# from ecobee import Ecobee
from tinydb import TinyDB, Query
from config import config


# ecobee = Ecobee
db = TinyDB(config.db_path)


def set_or_create_db_value(key: str, value: str):
    config_query = Query()
    if not db.update({'value': value}, config_query.key == key):
        db.insert({'key': key, 'value': value})


def get_db_value(key: str) -> str:
    config_query = Query()
    values = db.search(config_query.key == key)
    # assuming all writes are done using the above helper we will not get duplicates, but db supports it
    if len(values) > 0:
        return values[0]['value']
    else:
        return ''
