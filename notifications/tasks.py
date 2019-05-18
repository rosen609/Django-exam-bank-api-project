from os import environ

from twilio.rest import Client


def send_sms(to_phone_number, message_body):
    # Account SID from twilio.com/console
    account_sid = environ["TWILIO_ACCOUNT_SID"]
    # Auth Token from twilio.com/console
    auth_token = environ["TWILIO_AUTH_TOKEN"]
    # Active Number from twilio.com/console/phone-numbers
    from_number = environ["TWILIO_NUMBER"]

    client = Client(account_sid, auth_token)

    message = client.messages.create(
        to=to_phone_number,  # "+359885001483",
        from_=from_number,  # "+17094002369",
        body=message_body)  # "Hello from Python!")

    print(f"Twilio SMS message SID = {message.sid}")
