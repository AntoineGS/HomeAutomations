from pyecobee import *
from threading import Thread
from time import sleep
from config import config
from database import set_or_create_db_value, get_db_value
from datetime import datetime
from communication import send_sms
from utils import fahrenheit_to_celsius
import pytz
import logging
from pyecobee.utilities import logger as pyecobee_logger

# consts
AUTH_TOKEN = 'AUTH_TOKEN'
ACCESS_TOKEN = 'ACCESS_TOKEN'
REFRESH_TOKEN = 'REFRESH_TOKEN'
MAX_BASEMENT_TEMP = 23
MIN_BASEMENT_TEMP = 20

logger = logging.getLogger(__name__)


class Ecobee:
    def __init__(self):
        formatter = logging.Formatter('%(asctime)s %(name)-18s %(levelname)-8s %(message)s')

        logging.basicConfig(filename='app.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)

        logger.addHandler(stream_handler)
        logger.setLevel(logging.DEBUG)
        pyecobee_logger.addHandler(stream_handler)
        pyecobee_logger.setLevel(logging.DEBUG)

        auth_token = get_db_value(AUTH_TOKEN)
        access_token = get_db_value(ACCESS_TOKEN)
        refresh_token = get_db_value(REFRESH_TOKEN)

        self.service = EcobeeService(thermostat_name=config.ecobee.thermostat_name,
                                     authorization_token=None if not auth_token else auth_token,
                                     access_token=None if not access_token else access_token,
                                     refresh_token=None if not refresh_token else refresh_token,
                                     application_key=config.ecobee.api_key)

        if not self.service.authorization_token:  # no code has been used yet, need to do that on the portal
            authorize_response = self.service.authorize()
            # todo: text pin and wait for user to reply DONE to continue
            if not send_sms('Your Ecobee security PIN: ' + authorize_response.ecobee_pin):
                with open("pinToActivate.txt", "w") as file:
                    file.write(authorize_response.ecobee_pin)
            # quit()  # user intervention needed to activate the pin
            input()

        self.refresh_tokens_if_needed()

        # todo: extract threading into main so that all threads are started and managed in the same unit
        start_ecobee_thread(self)

    def save_object(self):
        set_or_create_db_value(AUTH_TOKEN, self.service.authorization_token)
        set_or_create_db_value(ACCESS_TOKEN, self.service.access_token)
        set_or_create_db_value(REFRESH_TOKEN, self.service.refresh_token)

    def refresh_tokens_if_needed(self, force_refresh: bool = False):
        refreshed = False
        do_refresh = False
        token_response = None

        if (not self.service.refresh_token) or force_refresh:
            token_response = self.service.request_tokens()
            refreshed = True
        if not refreshed:
            now_utc = datetime.now(pytz.utc)
            do_refresh = (not self.service.refresh_token_expires_on) or \
                         (now_utc > self.service.refresh_token_expires_on) or \
                         (not self.service.access_token_expires_on) or \
                         (now_utc > self.service.access_token_expires_on)
        if do_refresh:
            token_response = self.service.refresh_tokens()

        if (refreshed or do_refresh) and (token_response is not None):
            self.save_object()

    def monitor_basement_temp(self):
        selection = Selection(selection_type=SelectionType.REGISTERED.value,
                              selection_match='',
                              include_sensors=True)
        thermostat_response = self.service.request_thermostats(selection)
        found_basement = False

        for remote_sensor in thermostat_response.thermostat_list[0].remote_sensors:
            if remote_sensor.name == 'Basement':
                for capability in remote_sensor.capability:
                    if capability.type == 'temperature':
                        found_basement = True
                        temperature_f = fahrenheit_to_celsius(float(capability.value)/10)
                        if temperature_f > MAX_BASEMENT_TEMP:
                            send_sms('Basement temperature is too high ({:.2f}), adjusting...'.format(temperature_f))

                        elif temperature_f < MIN_BASEMENT_TEMP:
                            send_sms('Basement temperature is too low ({:.2f}), adjusting...'.format(temperature_f))
                        break  # found the temperature
                break  # found the basement

        if not found_basement:
            send_sms('Basement sensor not found')


# Note to reader, the use of threads is to facilitate the use of the different timers and division of who does what
# in addition to being a teaching experience. There will be no real performance boost with this approach due to GIL.
def start_ecobee_thread(ecobee: Ecobee) -> Thread:
    thread = Thread(target=ecobee_loop, args=(ecobee,))
    thread.start()
    return thread


def ecobee_loop(ecobee: Ecobee):
    while True:
        try:
            ecobee.monitor_basement_temp()
        except EcobeeApiException as e:
            if e.status_code == 14:
                ecobee.refresh_tokens_if_needed(True)

        sleep(10)
