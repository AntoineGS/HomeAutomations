from pyecobee import *
from threading import Thread
from time import sleep
from config import config
from main import set_or_create_db_value, get_db_value


class Ecobee:
    # if we have done this before then we have another stored
    refresh_token = get_db_value('REFRESH_TOKEN')

    if refresh_token == '':
        refresh_token = config.initial_refresh_token  # first initialization

    service = EcobeeService(thermostat_name=config.thermostat_name,
                            refresh_token=refresh_token,
                            application_key=config.application_key)

    token_response = service.refresh_tokens()
    thermostat_summary_response = service.request_thermostats_summary(selection=Selection(
        selection_type=SelectionType.REGISTERED.value,
        selection_match='',
        include_equipment_status=True))
    thermostat_summary_response.pretty_format()


def start_ecobee_loop():
    thread = Thread(target=ecobee_loop)
    thread.start()


def ecobee_loop():
    ecobee = Ecobee

    while True:
        sleep(30)




