# -*- coding: utf-8 -*-

#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

import os
import sys
import random
from argparse import ArgumentParser

from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv("LINE_CHANNEL_SECRET", None)
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)
if channel_secret is None:
    print("Specify LINE_CHANNEL_SECRET as environment variable.")
    sys.exit(1)
if channel_access_token is None:
    print("Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.")
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)


@app.route("/callback", methods=["POST"])
def callback():
    # get X-Line-Signature header value
    signature = request.headers["X-Line-Signature"]

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return "OK"


def prime_judge(N):
    if N == 1:
        return "1は素数ではありません。"
    if N == 57:
        return "57はグロタンディーク素数です。"
    for a in range(2, int(N ** 0.5) + 1):
        if N % a == 0:
            return str(a) + "で割れるよ。"
    return "素数です。"

def Miller_Rabin_prime_judge(N):
    if N%2==0:
        return "2で割れるよ。"
    M=N-1
    s=0
    while M%2==0:
        M=M//2
        s+=1
    d=M
    for _ in range(7):
        a=random.choice(range(1,N))
        if pow(a,d,N)!=1 and all([pow(a,d*pow(2,r),N)!=N-1 for r in range(s)]):
            return "素数ではありません。"
    return "99.99%素数です。"

def new_prime_judge(N):
    if N>2**63-1:
        return "64ビット整数に収まってないので無理です。"
    if len(str(N))<14:
        return prime_judge(N)
    else:
        return Miller_Rabin_prime_judge(N)


@handler.add(MessageEvent, message=TextMessage)
def message_text(event):
    user_message = event.message.text
    try:
        N = int(user_message)
        reply_message = new_prime_judge(N)
    except:
        reply_message = "数字を入力してね"
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_message))


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
