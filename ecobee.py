from pyecobee import *
from threading import Thread
from time import sleep
from config import config
from database import set_or_create_db_value, get_db_value
from datetime import datetime
from communication import send_sms
import pytz

# consts
AUTH_TOKEN = 'AUTH_TOKEN'


class Ecobee:
    def __init__(self):
        refresh_token = get_db_value(AUTH_TOKEN)

        self.service = EcobeeService(thermostat_name=config.ecobee.thermostat_name,
                                     authorization_token=None if not refresh_token else refresh_token,
                                     application_key=config.ecobee.api_key)

        if not self.service.authorization_token:  # no code has been used yet, need to do that on the portal
            authorize_response = self.service.authorize()
            set_or_create_db_value(AUTH_TOKEN, authorize_response.code)
            # todo: text pin and wait for user to reply DONE to continue
            if not send_sms(authorize_response.ecobee_pin):
                with open("pinToActivate.txt", "w") as file:
                    file.write(authorize_response.ecobee_pin)
            quit()  # user intervention needed to activate the pin
        elif not self.service.access_token:
            token_response = self.service.refresh_tokens()
            if token_response.refresh_token:
                set_or_create_db_value(AUTH_TOKEN, token_response.refresh_token)
            else:
                quit()  # huston we have a problem

    def refresh_tokens_if_needed(self):
        do_refresh = not self.service.refresh_token
        if not do_refresh:
            now_utc = datetime.now(pytz.utc)
            do_refresh = now_utc > self.service.refresh_token_expires_on
        if do_refresh:
            self.service.refresh_tokens()


        # thermostat_summary_response = self.service.request_thermostats_summary(selection=Selection(
        #     selection_type=SelectionType.REGISTERED.value,
        #     selection_match='',
        #     include_equipment_status=True))
        #
        # thermostat_summary_response.pretty_format()


# Note to reader, the use of threads is to facilitate the use of the different timers and division of who does what
# in addition to being a teaching experience. There will be no real performance boost with this approach due to GIL.
def start_ecobee_thread() -> Thread:
    thread = Thread(target=ecobee_loop)
    thread.start()
    return thread


def ecobee_loop():
    ecobee = Ecobee

    while True:
        sleep(30)
