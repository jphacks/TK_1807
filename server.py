# coding: utf-8

from flask import Flask, request, jsonify
import cek

app = Flask(__name__)

clova = cek.Clova(
    application_id="com.tk_1807.sample.destination",
    default_language="ja",
    debug_mode=True)

# /clova に対してのPOSTリクエストを受け付けるサーバーを立てる
@app.route('/clova', methods=['POST'])
def my_service():
    body_dict = clova.route(body=request.data, header=request.headers)
    response = jsonify(body_dict)
    response.headers['Content-Type'] = 'application/json;charset-UTF-8'
    return response

# 起動時の処理
@clova.handle.launch
def launch_request_handler(clova_request):
    welcome_japanese = cek.Message(message="あなたは誰？どこに行くんですか？", language="ja")
    response = clova.response([welcome_japanese])
    return response

# 誰がどこに行くのかを聞く
@clova.handle.intent("DestinationMessage")
def who_and_where_handle(clova_request):
    print("伝言板")
    family       = clova_request.slot_value("family")
    destinations = clova_request.slot_value("destination")
    message_japanese  = '{}さんは，{}に行くんですか？'.format(
        family,
        destinations
    )
    
    response = clova.response([message_japanese])
    return response

# 終了時
@clova.handle.end
def end_handler(clova_request):
    # Session ended, this handler can be used to clean up
    logger.info("Session ended.")

# 認識できなかった場合
@clova.handle.default
def default_handler(request):
    return clova.response("Sorry I don't understand! Could you please repeat?")
