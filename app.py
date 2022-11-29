# from __future__ import unicode_literals
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import *
import time, random
import json
from paho.mqtt import client as mqtt_client
# import random
# import requests, traceback, logging, boto3, json, sys, os
# from botocore.exceptions import ClientError

broker = 'broker.emqx.io'
port = 1883
topic = "esp32/smartstrip"
result_topic = "esp32/result"
client_id = 'python-mqtt-jasper'
app = Flask(__name__)

def help():
    print("-----------------------------------------------------------------------")
    print("Here are the following commands:\n")
    print("{:<14}: get device information".format("getInfo"), "{:<14}: get device emeter, 0<=id<=5".format("getEmeter [id]"), "{:<14}: turn on number [id] plug in the strip, 0<=id<=5".format("turnon [id]"), sep='\n')
    print("{:<14}: turn off number [id] plug in the strip, 0<=id<=5".format("turnoff [id]"), sep='\n')
    print("-----------------------------------------------------------------------")

def connect_mqtt():
    client = mqtt_client.Client(client_id)
    client.connect(broker, port)
    return client
            
converted_msg = ''            

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

def subscribe(client):
    def on_message(client, userdata, msg):
        returnmsg = msg.payload.decode()
        convertedDict = json.loads(returnmsg)
        global converted_msg
        converted_msg = json.dumps(convertedDict, indent=4, separators=(" ", " = "))
    client.subscribe(result_topic)
    client.on_message = on_message


# === [ 定義回覆使用者輸入的文字訊息 - 依據使用者狀態，回傳組成 LINE 的 Template 元素 ] ===
def compose_textReplyMessage(userId, messageText):
    result = client.publish(topic, messageText)
    if(result[0] == 0):
        messageText = "Message sent"
    else:
        messageText = "Failed to send message"
    return TextSendMessage(text=converted_msg)

# ==== [ 處理文字 TextMessage 訊息程式區段 ] ===
@handler.add(MessageEvent, message=TextMessage)    
def handle_text_message(event):
    userId = event.source.user_id
    messageText = event.message.text
    # logger.info('收到 MessageEvent 事件 | 使用者 %s 輸入了 [%s] 內容' % (userId, messageText))
    line_bot_api.reply_message(event.reply_token, compose_textReplyMessage(userId, messageText))

if __name__ == "__main__":
    app.run()
    client = connect_mqtt()
    client.loop_start()