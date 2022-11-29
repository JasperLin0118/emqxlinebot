# from __future__ import unicode_literals
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import *
import time, random, json
from paho.mqtt import client as mqtt_client
# import random
# import requests, traceback, logging, boto3, json, sys, os
# from botocore.exceptions import ClientError

broker = 'broker.emqx.io'
port = 1883
topic = "esp32/smartstrip"
topic_result = "esp32/result"
client_id = 'python-mqtt-jasper'
client_id_sub = f'python-mqtt-{random.randint(0, 100)}'
app = Flask(__name__)

tmp_token = ''
tmp_userid = ''

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!\n")
        else:
            print("Failed to connect\n")
    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def connect_sub_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!\n")
        else:
            print("Failed to connect\n")
    client = mqtt_client.Client(client_id_sub)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

def subscribe(client):
    def on_message(client, userdata, msg):
        returnmsg = msg.payload.decode()
        convertedDict = json.loads(returnmsg)
        global tmp_userid
        # line_bot_api.push_message(tmp_userid, TextSendMessage(text=json.dumps(convertedDict, indent=4, separators=(" ", " = "))))
        global tmp_token
        line_bot_api.reply_message(tmp_token, TextSendMessage(text=json.dumps(convertedDict, indent=4, separators=(" ", " = "))))
    client.subscribe(topic_result)
    client.on_message = on_message

client = connect_mqtt()
client2 = connect_sub_mqtt()
            
#basic linebot info
line_bot_api = LineBotApi("aQR2IjGV0u1EtyXHWvpcysJoCL/77lL9Mw/JbALyeWcMmQZSblPc1xuvyiUhjIpNOsz65QFGObs4g4gvFuXSZvE6MC0n4NwwCM4L9vCReUt8TCsYAaV/NayQ5LGWfBpBDt0leJBIkgwAlye0siXQsgdB04t89/1O/w1cDnyilFU=")
handler = WebhookHandler("db28adadcf721c2d441da3c3e16121c2")

#getting line info
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    try:
        print(body, signature)
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# ==== [ 處理文字 TextMessage 訊息程式區段 ] ===
@handler.add(MessageEvent, message=TextMessage)    
def handle_text_message(event):
    global tmp_token
    tmp_token = event.reply_token
    global tmp_userid
    tmp_userid = event.source.user_id
    messageText = event.message.text
    client.publish(topic, messageText)

if __name__ == "__main__":
    app.run()
    client.loop_start()
    subscribe(client2)
    client2.loop_forever()