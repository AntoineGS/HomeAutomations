import twilio.rest
from config import config

if config.twilio.sid and config.twilio.auth_token:
    sms_client = twilio.rest.Client(config.twilio.sid, config.twilio.auth_token)


def send_sms(msg_text: str) -> bool:
    def send_single_sms(_phone_number: str):
        sms_client.messages.create(
            to=_phone_number,
            from_=config.twilio.from_number,
            body=msg_text)

    if sms_client:
        for phone_number in config.twilio.phone_numbers:
            if phone_number:
                send_single_sms(phone_number)
        return True
    else:
        return False

