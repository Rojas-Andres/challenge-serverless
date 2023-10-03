"""
This module is used to send notifications to users
"""
import json

from lib_notifications.utils import send_email_change_price


def handler(event, context=None):
    """
    Handler
    """
    print("Event: {}".format(event))
    print("Context: {}".format(context))
    try:
        if not event.get("resources"):
            for eventData in event.get("Records"):
                payload = json.loads(eventData.get("body"))
                if payload.get("type") == "send_email_change_price":
                    print("Send email change price")
                    send_email_change_price(payload)
        return True
    except Exception as e:
        print("Error: {}".format(e))
        return False
