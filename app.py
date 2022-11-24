# from __future__ import unicode_literals
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import *
# import random
# import requests, traceback, logging, boto3, json, sys, os
# from botocore.exceptions import ClientError

app = Flask(__name__)

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

# === [ 定義回覆使用者輸入的文字訊息 - 依據使用者狀態，回傳組成 LINE 的 Template 元素 ] ===
def compose_textReplyMessage(userId, messageText):
    return TextSendMessage(text='好的！已收到您的文字 %s！' % messageText)

# ==== [ 處理文字 TextMessage 訊息程式區段 ] ===
@handler.add(MessageEvent, message=TextMessage)    
def handle_text_message(event):
    # userId = event.source.user_id
    # messageText = event.message.text
    # logger.info('收到 MessageEvent 事件 | 使用者 %s 輸入了 [%s] 內容' % (userId, messageText))
    # line_bot_api.reply_message(event.reply_token, compose_textReplyMessage(userId, messageText))
    print("\n\nok\n\n")
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text='hi'))

if __name__ == "__main__":
    app.run()