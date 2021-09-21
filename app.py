# coding=utf-8
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import json
from datetime import datetime

import requests
from flask import Flask, request

app = Flask(__name__)

@app.route('/bot-telegram', methods=['GET'])
def verify_bot_telegram():
    r = requests.get("http://mobile.vtc.vn/tool/inside/aspnet_client/auto/bot-telegram/bot_services.aspx")
    return "Telegram- VTC Mobile", 200

@app.route('/bot-telegram', methods=['POST'])
def update_bot_telegram():
    data = request.get_json()

    stext_telegram = ''
    s_channel_id = '' 
    if data['message']:
        stext_telegram = data['message']['text']
    if data['edited_message']:
        stext_telegram = data['edited_message']['text']
    if data['message']:
        s_channel_id = data['message']['chat']['id']
    if data['edited_message']:
        s_channel_id   = data['edited_message']['chat']['id']
        
    log('stext_telegram=' + stext_telegram)
    log('s_channel_id=' + s_channel_id)
    
    payload = {'stext_telegram': stext_telegram,'s_channel_id': s_channel_id}
    r = requests.get("http://mobile.vtc.vn/tool/inside/aspnet_client/auto/bot-telegram/bot_services.aspx", params=payload)
    return "True", 200

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

                    send_message(sender_id, "Chào bạn, bạn vui lòng liên hệ kênh hỗ trợ Scoin của chúng tôi tại địa chỉ m.me/scoinvtcmobile hoặc gọi đến tổng đài 19001104 để được hỗ trợ.")

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
