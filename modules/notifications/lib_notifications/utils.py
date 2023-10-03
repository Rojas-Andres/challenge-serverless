import os

import sendgrid
from sendgrid.helpers.mail import Mail


def send_email_sendgrid(to="", subject="no-reply", html_content=""):
    """
    Send an email
    """
    if "local" not in os.environ.get("ENVIRONMENT").lower():
        try:
            # 1. Instances
            sg = sendgrid.SendGridAPIClient(api_key=os.environ.get("SENDGRID_API_KEY"))
            from_email = os.environ.get("FROM_EMAIL")
            to_email = to  # Change to your recipient

            # 2 Build mail instance
            message = Mail(from_email=from_email, to_emails=[to_email], subject=subject, html_content=html_content)

            print("[ Challenge - Lambda ] - Sengrid Sending Email...")

            # 3. Send Email
            # 3.1 Send an HTTP POST request to /mail/send
            response = sg.send(message)

            print("[ Challenge - Lambda ] - Sengrid Response: {}".format(response))
            print("[ Challenge - Lambda ] - Sengrid Response status_code: {}".format(response.status_code))
            print("[ Challenge - Lambda ] - Sengrid Response body: {}".format(response.body))
            print("[ Challenge - Lambda ] - Sengrid Response headers: {}".format(response.headers))

            print("[ Challenge - Lambda ] - Sengrid Email Sent")

        except Exception as e:
            print("[ Challenge - Lambda ] - Error: {}".format(e))
    return True


def send_email_change_price(payload):
    send_email_sendgrid(to=payload["email"], subject="Change price", html_content=payload["message"])
