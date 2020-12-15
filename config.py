import os
from dotenv import load_dotenv
import json

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Twilio:
    phone_numbers: list = json.loads(os.environ.get('TW_PHONE_NUMBERS') or '[""]')
    sid: str = os.environ.get('TW_API_SID') or ''
    auth_token: str = os.environ.get('TW_API_AUTH_TOKEN') or ''
    from_number: str = os.environ.get('TW_FROM_NUMBER') or ''


class Ecobee:
    thermostat_name: str = os.environ.get('EB_THERMOSTAT_NAME') or 'My Ecobee'
    api_key: str = os.environ.get('EB_API_KEY') or ''


class Config:
    ecobee = Ecobee()
    twilio = Twilio()

    db_path: str = os.environ.get('HA_DB_PATH') or os.path.join(basedir, 'application.db')
    encryption_key: bytes = (os.environ.get('HA_ENCRYPTION_KEY') or '').encode('utf-8')


global config
config = Config
