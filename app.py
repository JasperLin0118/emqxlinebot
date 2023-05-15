# from __future__ import unicode_literals
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import *
import datetime, random, json
from paho.mqtt import client as mqtt_client
import firebase_admin
from firebase_admin import credentials, firestore
# import random
# import requests, traceback, logging, boto3, json, sys, os
# from botocore.exceptions import ClientError

#load firebase data for history commands
cred = credentials.Certificate("toclinebot-80594-firebase-adminsdk-g85c3-2673698c57.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
document_ref_childs = db.collection("linebot_user_ids").document("child_plug_names")
child_names = document_ref_childs.get()

# load Json file for timezone
f1 = open('resources/timezone_id.json', encoding='utf-8', mode='r')
f2 = open('resources/timezone_index.json', encoding='utf-8', mode='r')
timezone_id = json.load(f1)
timezone_index = json.load(f2)

broker = 'broker.emqx.io'
port = 1883
topic = "esp32/smartstrip"
topic_result = "esp32/result"
# client_id = 'python-mqtt-jasper'
client_id = f'python-mqtt-{random.randint(0, 100)}'
app = Flask(__name__)

tmp_token = ''
tmp_text = ''

def timedelta_formatter(td):                        
    td_sec = td.seconds    
    hour_count, rem = divmod(td_sec, 3600)  
    minute_count, second_count = divmod(rem, 60)   
    msg = "{}天{}小時{}分鐘{}秒".format(td.days, hour_count, minute_count, second_count)
    return msg 

def help():
    textmessage = "Here are the following commands:\n\n"
    textmessage += "{:<25}: get device information\n".format("getInfo")
    textmessage += "{:<21}: get realtime Current and Voltage reading, 1<=id<=6\n".format("getEmeter [id]")
    textmessage += "{:<24}: turn on number [id] plug in the strip, 1<=id<=6\n".format("turnon [id]")
    textmessage += "{:<25}: turn off number [id] plug in the strip, 1<=id<=6\n".format("turnoff [id]")
    textmessage += "{:<21}: set alias of number [id] plug in the strip, 1<=id<=6\n".format("setAlias [id] [alias]")
    textmessage += "{:<25}: reboot the strip\n".format("reboot")
    textmessage += "{:<26}: reset to factory settings\n".format("reset")
    textmessage += "{:<25}: turn on/off Led light on the strip\n".format("led [1/0]")
    textmessage += "{:<25}: list all available networks\n".format("scan")
    textmessage += "{:<26}: get current time\n".format("time")
    textmessage += "{:<22}: get current timezone\n".format("timezone")
    textmessage += "{:<18}: set timezone (UTC), -12<=time<=14\n".format("settimezone [time]")
    
    textmessage += "{:<25}: show history commands\n".format("history")
    line_bot_api.reply_message(tmp_token, TextSendMessage(text=textmessage))

def on_message(client, userdata, msg):
    if(tmp_token == ""):
        return
    returnmsg = msg.payload.decode()
    if(returnmsg == "failed" or returnmsg == "No such command"):
        line_bot_api.reply_message(tmp_token, TextSendMessage(text=returnmsg))
    else:
        convertedDict = json.loads(returnmsg)
        if(tmp_text == "turnon" or tmp_text == "turnoff"):  #turn on/off
            if(convertedDict["system"]["set_relay_state"]["err_code"] != 0):
                line_bot_api.reply_message(tmp_token, TextSendMessage(text="Error:" + convertedDict["system"]["set_relay_state"]["err_msg"]))
            else:
                line_bot_api.reply_message(tmp_token, TextSendMessage(text="Success"))
        elif(tmp_text == "getEmeter"): #get emeter
            reply_msg = ""
            for key, value in convertedDict["emeter"]["get_realtime"].items():
                reply_msg += "{:<15}: {}\n".format(key, value)
            line_bot_api.reply_message(tmp_token, TextSendMessage(text=reply_msg))
        elif(tmp_text == "getInfo"): #get info
            reply_msg = ""
            ind = 1
            for dict in convertedDict["system"]["get_sysinfo"]["children"]:
                reply_msg += "Plug {}:\n".format(ind)
                for key, value in dict.items():
                    if(key == "state" and value == 1):
                        value = "ON"
                        reply_msg += "{:<12}: {}\n".format(key, value)
                    elif(key == "state" and value == 0):
                        value = "OFF"
                        reply_msg += "{:<12}: {}\n".format(key, value)
                    elif(key == "on_time"):
                        timestamp = value
                        reply_msg += "{:<12}: {}\n".format(key, timedelta_formatter(datetime.timedelta(seconds=timestamp)))
                    elif(key != "next_action" and key != "id"):
                        reply_msg += "{:<12}: {}\n".format(key, value)
                ind += 1
                reply_msg += "\n"
            line_bot_api.reply_message(tmp_token, TextSendMessage(text=reply_msg))
        elif(tmp_text == "setAlias"): #set alias
            if(convertedDict["system"]["set_dev_alias"]["err_code"] != 0):
                line_bot_api.reply_message(tmp_token, TextSendMessage(text="Error:" + convertedDict["system"]["set_dev_alias"]["err_msg"]))
            else:
                line_bot_api.reply_message(tmp_token, TextSendMessage(text="Success"))
        elif(tmp_text == "reboot"): #reboot
            line_bot_api.reply_message(tmp_token, TextSendMessage(text="Success"))
        elif(tmp_text == "reset"): #reset
            line_bot_api.reply_message(tmp_token, TextSendMessage(text="Success"))
        elif(tmp_text == "led"): #led
            if(convertedDict["system"]["set_led_off"]["err_code"] != 0):
                line_bot_api.reply_message(tmp_token, TextSendMessage(text="Error:" + convertedDict["system"]["set_led_off"]["err_msg"]))
            else:
                line_bot_api.reply_message(tmp_token, TextSendMessage(text="Success"))
        elif(tmp_text == "scan"): #scan
            if(convertedDict["netif"]["get_scaninfo"]["err_code"] != 0):
                line_bot_api.reply_message(tmp_token, TextSendMessage(text="Error:" + convertedDict["netif"]["get_scaninfo"]["err_msg"]))
            else:
                reply_msg = "Name:\n"
                for ap in convertedDict["netif"]["get_scaninfo"]["ap_list"]:
                    reply_msg += "{}\n".format(ap['ssid'])
                line_bot_api.reply_message(tmp_token, TextSendMessage(text=reply_msg))
        elif(tmp_text == "time"): #time
            times = []
            for key, value in convertedDict["time"]["get_time"].items():
                if(key != "err_code"):
                    times.append(value)
            reply_msg = f"{times[0]}年{times[1]}月{times[2]}日   {times[3]}:{times[4]}:{times[5]}"
            line_bot_api.reply_message(tmp_token, TextSendMessage(text=reply_msg))
        elif(tmp_text == "timezone"): #timezone
            curr_timezone = convertedDict["time"]["get_timezone"]["index"]
            reply_msg = ""
            for country in timezone_index:
                if(timezone_index[country]["index"] == curr_timezone):
                    reply_msg = timezone_index[country]['offset']
                    break
            line_bot_api.reply_message(tmp_token, TextSendMessage(text=reply_msg))
        elif(tmp_text == "settimezone"): #set timezone
            line_bot_api.reply_message(tmp_token, TextSendMessage(text="Success"))
            
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
        # print(body, signature)
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)    
def handle_text_message(event):
    global tmp_token
    tmp_token = event.reply_token
    messageText = event.message.text
    global tmp_text
    tmp_text = messageText.split()[0]
    if(messageText == "help"):
        help()
    elif(messageText == "history"):
        pass
    elif (messageText.startswith("settimezone")):
        str_args = messageText.split()
        if(str_args[1].isdigit() and int(str_args[1]) >= -12 and int(str_args[1]) <= 14):
            wanted_timezone = "UTC"
            if(int(str_args[1]) > 0 and int(str_args[1]) < 10):
                wanted_timezone += "+0" + str_args[1]
            elif(int(str_args[1]) >= 10):
                wanted_timezone += "+" + str_args[1]
            elif(int(str_args[1]) < 0 and int(str_args[1]) > -10):
                wanted_timezone += "-0" + str_args[1][1]
            elif(int(str_args[1]) <= -10):
                wanted_timezone += str_args[1]
            for country in timezone_index:
                if(wanted_timezone != "UTC" and timezone_index[country]["offset"].startswith(wanted_timezone)):
                    messageText = "settimezone " + str(timezone_index[country]['index'])
                    break
                elif(wanted_timezone == "UTC" and timezone_index[country]["offset"].endswith(wanted_timezone)):
                    messageText = "settimezone " + str(timezone_index[country]['index'])
                    break
            print(messageText)
            client.publish(topic, messageText)
            print("publish success")
        else:
            outputText = "Please enter a valid timezone"
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=outputText))
    else:
        client.publish(topic, messageText)
        print("publish success")
    document_ref = db.collection("linebot_user_ids").document(event.source.user_id)
    history = document_ref.get()
    # if(history.exists):
    #     history = history.to_dict()['history']
    #     history.append(messageText)
    #     document_ref.update({'history': history})
    # else:
    #     d = {'user_id': event.source.user_id, 'history': [messageText]}
    #     document_ref.set(d)
    if(messageText == "history"):
        history = document_ref.get().to_dict()['history']
        outputText = "Here are the history commands:\n"
        for i in range(len(history)):
            outputText += str(i+1) + " " + history[i] + "\n"
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=outputText))
        

if __name__ == "__main__":
    client = mqtt_client.Client(client_id)
    client.connect(broker, port)
    client.loop_start()
    client.subscribe(topic_result)
    client.on_message = on_message
    app.run(debug=True)