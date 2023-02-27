import imaplib
import email
import os
import requests

from time import sleep
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

MESSAGE_FILTER = os.getenv("MESSAGE_FILTER").split(",")
EMAIL_WHITELIST = os.getenv("EMAIL_WHITELIST").replace(" ", "").split(",")
set_webhook_link = os.getenv("SET_WEBHOOK_LINK")
send_message_link = os.getenv("SEND_MESSAGE_LINK")
get_account_info_link = os.getenv("GET_ACCOUNT_INFO_LINK")
imap_host = os.getenv("IMAP_HOST")
imap_psw = os.getenv("IMAP_PSW")
imap_user = os.getenv("IMAP_USER")
auth_token = os.getenv("AUTH_TOKEN_VIBER")

def main():
    try:
        imap = imaplib.IMAP4_SSL(imap_host)
        imap.login(imap_user, imap_psw)
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
                                    send_msg(auth_token, super_admin_id, msg)
                                    send_msg(auth_token, super_admin_id, "|= = = = = = = = = = = = = = = END = = = = = = = = = = = = = = =|")
                else:
                    # Make email as unseen
                    imap.store(msgnum, '-FLAGS', '\\Seen')
        imap.close()
    
    except Exception as e:
        with open("errors.txt", "a") as f:
            f.write(f"{datetime.now()}: {str(e)}\n")
            f.close()


def get_admin_id():
    payload = {
        "auth_token": auth_token
    }

    response = requests.post(get_account_info_link, json=payload)
    res_json = response.json()
    
    # Check for error in response
    if viber_api_error(res_json["status"]) != -1 :
        super_admin_id = res_json["members"][0]["id"]
        return super_admin_id


def send_msg(auth_token, super_admin_id, msg):
    payload_msg = {
        "auth_token": auth_token,
        "from": super_admin_id,
        "type": "text",
        "text": msg
    }
    try:
        response = requests.post(send_message_link, json=payload_msg)
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
                return -1
    return 0


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