import json
import logging
import os
from datetime import datetime

import requests
from twilio.rest import Client

from .utils import shorten_url

states = json.loads(os.environ["STATES"])

account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
client = Client(account_sid, auth_token)

def format_available_message(locations):
    message = "Vaccine appointments available at {} location{}:".format(
        "these" if len(locations) > 1 else "this",
        "s" if len(locations) > 1 else "",
    )
    for location in locations:
        if "earliest_appointment_day" in location:
            if datetime.strptime(location["latest_appointment_day"], "%b %-d") >= datetime.strptime("04/09/2021", "%d/%m/%Y").date():
                if (
                    location["earliest_appointment_day"]
                    == location["latest_appointment_day"]
                ):
                    day_string = " on {}".format(location["earliest_appointment_day"])
                else:
                    day_string = " from {} to {}".format(
                        location["earliest_appointment_day"],
                        location["latest_appointment_day"],
                    )
            else:
                return
        else:
            day_string = ""

        message += "\n• {}{}{}. Sign up here: {}{}{}".format(
            "{}: ".format(location["state"])
            if (len(states) > 1 and "state" in location)
            else "",
            location["name"],
            day_string,
            shorten_url(location["link"]),
            ", zip code {}".format(location["zip"]) if "zip" in location else "",
            " (as of {})".format(location["appointments_last_fetched"])
            if location.get("appointments_last_fetched", None)
            else "",
        )
    return message


def format_unavailable_message(locations):
    message = "Vaccine appointments no longer available at {} location{}:".format(
        "these" if len(locations) > 1 else "this",
        "s" if len(locations) > 1 else "",
    )
    for location in locations:
        message += "\n• {}{}{}".format(
            "**{}**: ".format(location["state"])
            if (len(states) > 1 and "state" in location)
            else "",
            location["name"],
            " (as of {})".format(location["appointments_last_fetched"])
            if location.get("appointments_last_fetched", None)
            else "",
        )
    return message


def send_message_to_twilio(message):
    to = os.environ["TWILIO_TO_NUMBER"]
    from_ = os.environ["TWILIO_FROM_NUMBER"]
    try:
        message = client.api.account.messages.create(
            to=to,
            from_=from_,
            body=message
        )
        logging.info(
            "Payload delivered successfully, code {}.".format(message.status)
        )
    except:
        logging.exception("Error sending message to twilio")


def notify_twilio_available_locations(locations):
    send_message_to_twilio(format_available_message(locations))


def notify_twilio_unavailable_locations(locations):
    send_message_to_twilio(format_unavailable_message(locations))
