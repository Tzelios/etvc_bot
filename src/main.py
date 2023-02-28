import imaplib
import email
import os
import requests
import time

from smtplib import SMTP_SSL, SMTP_SSL_PORT
from email.message import EmailMessage
from time import sleep
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# EMAIL RELATED ENV VARIABLES
MESSAGE_FILTER = os.getenv("MESSAGE_FILTER").split(",")
EMAIL_WHITELIST = os.getenv("EMAIL_WHITELIST").replace(" ", "").split(",")

# VIBER ENV VARIABLES
SET_WEBHOOK_LINK = os.getenv("SET_WEBHOOK_LINK")
SEND_MESSAGE_LINK = os.getenv("SEND_MESSAGE_LINK")
GET_ACCOUNT_INFO_LINK = os.getenv("GET_ACCOUNT_INFO_LINK")

# IMAP ENV VARIABLES
IMAP_HOST = os.getenv("IMAP_HOST")
IMAP_PSW = os.getenv("IMAP_PSW")
IMAP_USER = os.getenv("IMAP_USER")
AUTH_TOKEN = os.getenv("AUTH_TOKEN_VIBER")

# SMTP ENV VARIABLES
SMTP_SERVER_HOST = os.getenv("SMPT_SERVER")
FROM_EMAIL = os.getenv("FROM_EMAIL")
TO_EMAILS = os.getenv("TO_EMAILS").replace(" ", "").split(",")



def main():
    try:
        imap = imaplib.IMAP4_SSL(IMAP_HOST)
        imap.login(IMAP_USER, IMAP_PSW)
        imap.select("Inbox")

        status, msgnums = imap.search(None, "UnSeen")

        if status != "OK":
            with open("errors.txt", "a") as f:
                f.write("Could not recieve Unseen messages.")
                f.close()
            raise Exception ("Could not recieve Unseen messages.")
        
        for msgnum in msgnums[0].split():
            _, data = imap.fetch(msgnum, "(RFC822)") 

            message = email.message_from_bytes(data[0][1])

            for e in EMAIL_WHITELIST:
                if e in message.get("From"):

                    for part in message.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        try:
                            # get the email body
                            body = part.get_payload(decode=True).decode()
                        except:
                            pass
                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            for course in MESSAGE_FILTER:
                                if course in body:
                                    msg = f"From: {message.get('From')}\n\nMessage:\n\n{body}"
                                    send_msg(AUTH_TOKEN, super_admin_id, msg)
                                    send_msg(AUTH_TOKEN, super_admin_id, "|= = = = = = = = END = = = = = = = =|")
                else:
                    # Make email as unseen
                    imap.store(msgnum, '-FLAGS', '\\Seen')
        imap.close()
    
    except Exception as e:
        send_error_to_email(str(e))
        with open("errors.txt", "a") as f:
            f.write(f"{datetime.now()}: {str(e)}\n")
            f.close()


def get_admin_id():
    payload = {
        "auth_token": AUTH_TOKEN
    }

    response = requests.post(GET_ACCOUNT_INFO_LINK, json=payload)
    res_json = response.json()
    
    # Check for error in response
    if viber_api_error(res_json["status"]) != -1 :
        return res_json["members"][0]["id"]


def send_msg(auth_token, super_admin_id, msg):
    payload_msg = {
        "auth_token": auth_token,
        "from": super_admin_id,
        "type": "text",
        "text": msg
    }
    try:
        response = requests.post(SEND_MESSAGE_LINK, json=payload_msg)
        res_json = response.json()

        # Check for error in response
        if viber_api_error(res_json["status"]) != -1:
            return 0
        else:
            return -1
    except:
        return -1


def viber_api_error(status):
    '''
    Takes the status(int) if the status is zero(ok) returns 0 else returns -1
    '''
    for viber_error in viber_errors:
        if viber_error[0] == status:
            with open ("viber_errors.txt", "a") as f:
                f.write(f"{datetime.now()}: {viber_error[0]}, {viber_error[1]}, {viber_error[2]}.\n")
                f.close()
                try:
                    send_error_to_email(f"{datetime.now()}: {viber_error[0]}, {viber_error[1]}, {viber_error[2]}.\n")
                except:
                    pass
                return -1
    return 0

def send_error_to_email(e):
    email_message = EmailMessage()
    email_message.add_header('To', ','.join(TO_EMAILS))
    email_message.add_header('From', FROM_EMAIL)
    email_message.add_header('Subject', 'Error at eclass uth bot')
    email_message.add_header('X-Priority', '1')
    email_message.set_content(e)

    # Connect, authenticate, and send mail
    smtp_server = SMTP_SSL(SMTP_SERVER_HOST, port=SMTP_SSL_PORT)
    smtp_server.set_debuglevel(1)  # Show SMTP server interactions
    smtp_server.login(IMAP_USER, IMAP_PSW)
    smtp_server.sendmail(FROM_EMAIL, TO_EMAILS, email_message.as_bytes())

    # Disconnect
    smtp_server.quit()

if __name__ == "__main__":
    # Viber channel post API: https://developers.viber.com/docs/tools/channels-post-api/#error-codes
    viber_errors = [(1, "invalidUrl", "The webhook URL is not valid"),
                    (2, "invalidAuthTOken", "The authentication token is not valid"),
                    (3, "badData", "There is an error in the request itself ( missing comma, brackets, etc.)"),
                    (4, "missingData", "Some mandatory data is missing"),
                    (7, "publicAccountBlocked", "The account is blocked"),
                    (8, "publicAccountNotFound", "The account associated with the token is not a account"),
                    (9, "publicAccountSuspended", "The account is suspended"),
                    (10, "webhookNotSet", "No webhook was set for the account"),
                    (12, "tooManyRequests", "Rate control breach")
                    ]
    super_admin_id = get_admin_id()
    while True:
        main()
        print(datetime.now())
        print("Next call in 10 mins!")
        sleep(10*60) # sleep for 10 minutes