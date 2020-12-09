import os
from dotenv import load_dotenv


basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    thermostat_name = os.environ.get('THERMOSTAT_NAME') or 'My Ecobee'
    application_key = os.environ.get('ECOBEE_APPLICATION_KEY')
    initial_refresh_token = os.environ.get('INITIAL_REFRESH_TOKEN')
    db_path = os.environ.get('HOME_AUTOMATION_DB_PATH') or os.path.join(basedir, 'application.db')
    secret = os.environ.get('SECRET') or ''


global config
config = Config
