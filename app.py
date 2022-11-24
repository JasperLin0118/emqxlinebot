from __future__ import unicode_literals
import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import configparser
import random

app = Flask(__name__)

#basic linebot info
config = configparser.ConfigParser()
config.read("config.ini")
line_bot_api = LineBotApi(config.get("line-bot", "channel_access_token"))
handler = WebhookHandler(config.get("line-bot", "channel_secret"))

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

# test
@handler.add(MessageEvent, message=TextMessage)
def echo(event):
    if event.source.user_id != "Udeadbeefdeadbeefdeadbeefdeadbeef":
        pretty_note = '♫♪♬'
        pretty_text = ''
        for i in event.message.text:
            pretty_text += i
            pretty_text += random.choice(pretty_note)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=pretty_text))

if __name__ == "__main__":
    app.run()
    
    
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (LineBotApiError, InvalidSignatureError)
from linebot.models import *
import requests, traceback, logging, boto3, json, sys, os
from botocore.exceptions import ClientError

# ===[ 定義你的函式 ] ===
def get_userOperations(userId):
    return None

# === [ 定義回覆使用者輸入的文字訊息 - 依據使用者狀態，回傳組成 LINE 的 Template 元素 ] ===
def compose_textReplyMessage(userId, userOperations, messageText):
    return TextSendMessage(text='好的！已收到您的文字 %s！' % messageText)

# === [ 定義回覆使用者與程式使用者界面互動時回傳結果後的訊息 - 依據使用者狀態，回傳組成 LINE 的 Template 元素 ] ===
def compose_postbackReplyMessage(userId, userOperations, messageData):
    return TextSendMessage(text='好的！已收到您的動作 %s！' % messageData)

def lambda_handler(event, context):
    
    # ==== [ 處理文字 TextMessage 訊息程式區段 ] ===
    @handler.add(MessageEvent, message=TextMessage)    
    def handle_text_message(event):
        userId = event.source.user_id
        messageText = event.message.text
        userOperations = get_userOperations(userId)
        logger.info('收到 MessageEvent 事件 | 使用者 %s 輸入了 [%s] 內容' % (userId, messageText))
        line_bot_api.reply_message(event.reply_token, compose_textReplyMessage(userId, userOperations, messageText))

    # ==== [ 處理使用者按下相關按鈕回應後的後續動作 PostbackEvent 程式區段 ] ===
    @handler.add(PostbackEvent)   
    def handle_postback(event):
        userId = event.source.user_id 
        messageData = json.loads(event.postback.data)
        userOperations = get_userOperations(userId)        
        logger.info('收到 PostbackEvent 事件 | 使用者 %s' % userId)        
        line_bot_api.reply_message(event.reply_token, compose_postbackReplyMessage(userId, userOperations, messageData))

    # ==== [ 處理追縱 FollowEvent 的程式區段 ] === 
    @handler.add(FollowEvent)  
    def handle_follow(event):
        userId = event.source.user_id
        logger.info('收到 FollowEvent 事件 | 使用者 %s' % userId)
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='歡迎您的加入 !'))      
        
    try:
        signature = event['headers']['x-line-signature']  # === 取得 event (事件) x-line-signature 標頭值 (header value)
        body = event['body']  # === 取得事件本文內容(body)
        print(body)
        # eventheadershost = event['headers']['host']        
        handler.handle(body, signature)  # 處理 webhook 事件本文內容(body)
    except InvalidSignatureError:
        return {'statusCode': 400, 'body':json.dumps('InvalidSignature')}
    except LineBotApiError as e:
        logger.error('呼叫 LINE Messaging API 時發生意外錯誤: %s' % e.message)
        for m in e.error.details:
            logger.error('-- %s: %s' % (m.property, m.message))
        return {'statusCode': 400, 'body': json.dumps(traceback.format_exc())}
    return {'statusCode': 200, 'body': json.dumps('OK')}