    print("{:<14}: turn off number [id] plug in the strip, 0<=id<=5".format("turnoff [id]"), sep='\n')
    print("-----------------------------------------------------------------------")
def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    client = mqtt_client.Client(client_id)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client
client = connect_mqtt()
            
#basic linebot info
line_bot_api = LineBotApi("aQR2IjGV0u1EtyXHWvpcysJoCL/77lL9Mw/JbALyeWcMmQZSblPc1xuvyiUhjIpNOsz65QFGObs4g4gvFuXSZvE6MC0n4NwwCM4L9vCReUt8TCsYAaV/NayQ5LGWfBpBDt0leJBIkgwAlye0siXQsgdB04t89/1O/w1cDnyilFU=")
handler = WebhookHandler("db28adadcf721c2d441da3c3e16121c2")
# === [ 定義回覆使用者輸入的文字訊息 - 依據使用者狀態，回傳組成 LINE 的 Template 元素 ] ===
def compose_textReplyMessage(userId, messageText):
    result = client.publish(topic, messageText)
    if(result[0] == 0):
        messageText = "Message sent"
    else:
        messageText = "Failed to send message"
    return TextSendMessage(text=messageText)
# ==== [ 處理文字 TextMessage 訊息程式區段 ] ===
@handler.add(MessageEvent, message=TextMessage)    
def handle_text_message(event):
    userId = event.source.user_id
    messageText = event.message.text
    # logger.info('收到 MessageEvent 事件 | 使用者 %s 輸入了 [%s] 內容' % (userId, messageText))
    line_bot_api.reply_message(event.reply_token, compose_textReplyMessage(userId, messageText))
if __name__ == "__main__":
    app.run()
    client.loop_start()