"""
This module is used to send notifications to users
"""
import json


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
                print("payload", payload)
        return True
    except Exception as e:
        print("Error: {}".format(e))
        return False
