from tinydb import TinyDB, Query
from config import config
from utils import encrypt, decrypt


db = TinyDB(config.db_path)


def set_or_create_db_value(key: str, value: str, encrypt_value: bool = False):
    if encrypt_value and value:
        value = encrypt(value)

    config_query = Query()
    if not db.update({'value': value}, config_query.key == key):
        db.insert({'key': key, 'value': value})


def get_db_value(key: str, decrypt_value: bool = False) -> str:
    config_query = Query()
    values = db.search(config_query.key == key)
    # assuming all writes are done using the above helper we will not get duplicates, but db supports it
    if len(values) > 0:
        result = values[0]['value']
    else:
        result = ''

    if (not result) and decrypt_value:
        result = decrypt(result)

    return result
