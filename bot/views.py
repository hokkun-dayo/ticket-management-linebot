# coding: utf-8
import json
import os

from django.shortcuts import render
from django.conf import settings
from rest_framework.response import Response

from .models import Message
from rest_framework import viewsets, filters, views
from .serializer import MessageSerializer

import requests
import gspread
from oauth2client.client import SignedJwtAssertionCredentials


class MessageTaskSet(views.APIView):
    def post(self, request, format=None):

        json_data = json.load(open("bot/google_data.json"))

        # get information
        google_doc_id = json_data["doc_id"]

        json_key = json_data["google_api_data"]
        scope = ['https://spreadsheets.google.com/feeds']

        # credentialsを取得
        credentials = SignedJwtAssertionCredentials(json_key['client_email'],
                                                    json_key['private_key']
                                                    .encode(),
                                                    scope)

        gclient = gspread.authorize(credentials)
        gfile = gclient.open_by_key(google_doc_id)
        wsheet = gfile.get_worksheet(0)
        records = wsheet.get_all_records()

        received_text = request.data["result"][0]["content"]["text"]

        if "予約者" in received_text:
            count = 0
            for record in records:
                count += int(record["チケット枚数"])
            submission_text = "現在の予約数は{}枚です。".format(count)
            print(submission_text)
        else:
            submission_text = received_text  # オウム返し

        line_setting_json = json.load(open("bot/line_setting.json"))
        url = line_setting_json["url"]

        # ヘッダの追加
        headers = line_setting_json["header"]

        # データの追加
        data = {}
        # my mid for test
        data["to"] = [request.data["result"][0]["content"]["from"]]
        data["toChannel"] = 1383378250
        data["eventType"] = "138311608800106203"
        data["content"] = {}
        data["content"]["contentType"] = 1  # For Text
        data["content"]["toType"] = 1  # Fixed Value
        data["content"]["text"] = submission_text

        json_data = json.dumps(data)

        print(json_data)

        response = requests.post(url, data=json_data, headers=headers)

        return Response(response.text)
