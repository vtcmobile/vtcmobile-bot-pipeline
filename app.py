# coding=utf-8
import os
import sys
import json
from datetime import datetime

import requests
from flask import Flask, request

app = Flask(__name__)


@app.route('/', methods=['GET'])
def verify():
    # when the endpoint is registered as a webhook, it must echo back
    # the 'hub.challenge' value it receives in the query arguments
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == os.environ["VERIFY_TOKEN"]:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200

    return "Hello world - VTC Mobile", 200


@app.route('/', methods=['POST'])
def webhook():

    # endpoint for processing incoming messaging events

    data = request.get_json()
    log(data)  # you may not want to log every incoming message in production, but it's good for testing

    if data["object"] == "page":

        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):  # someone sent us a message

                    sender_id = messaging_event["sender"]["id"]        # the facebook ID of the person sending you the message
                    recipient_id = messaging_event["recipient"]["id"]  # the recipient's ID, which should be your page's facebook ID
                    message_text = messaging_event["message"]["text"]  # the message's text

                    send_message(sender_id, "\x43\x68\xC3\xA0\x6F\x20\x62\xE1\xBA\xA1\x6E\x2C\x20\x62\xE1\xBA\xA1\x6E\x20\x76\x75\x69\x20\x6C\xC3\xB2\x6E\x67\x20\x6C\x69\xC3\xAA\x6E\x20\x68\xE1\xBB\x87\x20\x6B\xC3\xAA\x6E\x68\x20\x68\xE1\xBB\x97\x20\x74\x72\xE1\xBB\xA3\x20\x53\x63\x6F\x69\x6E\x20\x63\xE1\xBB\xA7\x61\x20\x63\x68\xC3\xBA\x6E\x67\x20\x74\xC3\xB4\x69\x20\x74\xE1\xBA\xA1\x69\x20\xC4\x91\xE1\xBB\x8B\x61\x20\x63\x68\xE1\xBB\x89\x20\x6D\x2E\x6D\x65\x2F\x73\x63\x6F\x69\x6E\x76\x74\x63\x6D\x6F\x62\x69\x6C\x65\x20\x68\x6F\xE1\xBA\xB7\x63\x20\x67\xE1\xBB\x8D\x69\x20\xC4\x91\xE1\xBA\xBF\x6E\x20\x74\xE1\xBB\x95\x6E\x67\x20\xC4\x91\xC3\xA0\x69\x20\x31\x39\x30\x30\x31\x31\x30\x34\x20\xC4\x91\xE1\xBB\x83\x20\xC4\x91\xC6\xB0\xE1\xBB\xA3\x63\x20\x68\xE1\xBB\x97\x20\x74\x72\xE1\xBB\xA3\x2E.".decode('utf-8'))

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200


def send_message(recipient_id, message_text):

    log("sending message to {recipient}: {text}".format(recipient=recipient_id, text=message_text))

    params = {
        "access_token": os.environ["PAGE_ACCESS_TOKEN"]
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v2.6/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        log(r.status_code)
        log(r.text)


def log(msg, *args, **kwargs):  # simple wrapper for logging to stdout on heroku
    try:
        if type(msg) is dict:
            msg = json.dumps(msg)
        else:
            msg = unicode(msg).format(*args, **kwargs)
        print u"{}: {}".format(datetime.now(), msg)
    except UnicodeEncodeError:
        pass  # squash logging errors in case of non-ascii text
    sys.stdout.flush()


if __name__ == '__main__':
    app.run(debug=True)
