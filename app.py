from flask import Flask, request, abort
import json

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, BeaconEvent
)

from datetime import *

app = Flask(__name__)

data = []
with open('storekeys.json','r') as f:
	data = json.load(f)
ACCESS_TOKEN = data["ACCESS_TOKEN"]
SECRET = data["SECRET"]
line_bot_api = LineBotApi(ACCESS_TOKEN)
handler = WebhookHandler(SECRET)

udata = []
with open('store_udata.json', 'r') as f:
	udata = json.load(f)
user_list = []
userid_list = []
pt_list = []
for cs in udata:
	userid_list.append(cs)
	user_list.append(udata[cs])
#	pt_list[cs] = 0

@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@app.route("/")
def hello_world():
    return "hello, world!"

def test_output(ss):
	line_bot_api.push_message(userid_list[1], TextSendMessage(text=ss))



# 門限18:00	
curfew = 1800
@handler.add(BeaconEvent)
def handle_beacon(event):
	if(event.beacon.type == 'enter'):
		type_message = "帰宅"
	elif(event.beacon.type == 'leave'):
		type_message = "外出"
	evsu = event.source.user_id
	ts = event.timestamp
	dts = datetime.fromtimestamp(int(ts/1000))
	time = dts.strftime("%H%M")

#	line_bot_api.reply_message(
#        event.reply_token,
#        TextSendMessage(
#            text='ビーコンが反応しました。 hwid={}, user:{}さんが{}'.format(
#			event.beacon.hwid, udata[evsu], type_message)))
	line_bot_api.reply_message(
		event.reply_token, 
		TextSendMessage(text='ビーコンがあなたの'+type_message+'を検知しました。'))

	
	for j in range(len(udata)):
		if(user_list[j] == udata[evsu]):
			num = j
	for i in range(len(udata)):
		line_bot_api.push_message(userid_list[i], TextSendMessage(text=user_list[num]+'が'+type_message+'しました。'))

	curfew_message = ""
	if(type_message == '帰宅'):
		if(int(time) > curfew):
			curfew_message = str(user_list[num])+'は門限を過ぎています。'
#			test_output(curfew_message)
		else:
			curfew_message = str(user_list[num])+'は門限を守って帰宅しました。'
#			pt_list[userid_list[num]] += 10

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
	text = event.message.text
	ts = event.timestamp
	dts = datetime.fromtimestamp(int(ts/1000))
	time = dts.strftime("%H%M")

	if(text in '在宅確認'):
#		line_bot_api.reply_message(event.reply_token, TextSendMessage('お家にいますか？'))
		for i in range(len(udata)):
			line_bot_api.push_message(userid_list[i], TextSendMessage(text='お家にいますか？'))
	else:
		line_bot_api.reply_message(event.reply_token, TextSendMessage('すみません、わかりません'))

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=5000)
