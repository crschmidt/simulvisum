#!/usr/bin/python
#
# Copyright 2018 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import httplib2
import os
import sys
import time
import json
import random

from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow


try:
    from django.conf import settings
    secrets_file = settings.CLIENT_SECRETS_FILE
    oauth_storage = settings.OAUTH_STORAGE_JSON
except Exception, E:
    print "Unable to load config from settings. Using ../client_secrets.json instead and ../google-oauth.json instead"
    secrets_file = "../client_secrets.json"
    oauth_storage = "../google-oauth.json"

YOUTUBE_READONLY_SCOPE = "https://www.googleapis.com/auth/youtube"

MISSING_CLIENT_SECRETS_MESSAGE = """configure"""

def get_authenticated_service():
  flow = flow_from_clientsecrets(secrets_file,
    scope=YOUTUBE_READONLY_SCOPE,
    message=MISSING_CLIENT_SECRETS_MESSAGE)
  flow.params['approval_prompt'] = 'force'
  flow.params['authuser'] = '15'
  flow.params['access_type'] = 'offline'

  storage = Storage(oauth_storage)
  credentials = storage.get()
  if credentials is None or credentials.invalid:
    credentials = run_flow(flow, storage)
  http = credentials.authorize(httplib2.Http())
  return http

def get_playlist_ids(playlist):
    http = get_authenticated_service()
    pageToken = ""
    ids = []
    while pageToken != None:
        url = "https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults=50&playlistId=%s" % playlist
        if pageToken:
            url = "%s&pageToken=%s" % (url, pageToken)
        status, response = http.request(url)
        data = json.loads(response)
        for i in data['items']:
            ids.append(i['contentDetails']['videoId'])
        pageToken = data.get('nextPageToken')
    return ids

def video_info_length(video_info):
    t = video_info['contentDetails']['duration']
    t = t.replace("PT", "")
    hour = minutes = secs = 0
    bits = {}
    for bit in ['H', 'M', 'S']:
        if bit in t:
            x, t = t.split(bit)
            bits[bit] = int(x)

    seconds = int(bits.get('H', 0))*3600  + bits.get('M', 0) * 60 + bits.get('S', 0)
    return seconds

def get_video_length(video):
    http = get_authenticated_service()
    url = "https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics,contentDetails&maxResults=50&id=%s" % video
    status, response = http.request(url)
    data = json.loads(response)
    vid = data['items'][0]
    secs = video_info_length(vid)
    return secs 

def get_ordinal(playlist, video_id):
    r = -1
    videos = get_playlist_ids(playlist)
    for order, i in enumerate(videos):
        if i == video_id:
            return order
    return r

def add_video_id(playlist, video_id, ordinal=None):
    http = get_authenticated_service()
    status, response = http.request('https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&maxResults=50&id=%s' % video_id)
    data = json.loads(response)
    if data['pageInfo']['totalResults'] != 1:
        raise Exception("No such video!")
    item = {
        'snippet': {
            'playlistId': playlist,
            'resourceId': {
                'kind': 'youtube#video',
                'videoId': video_id
            },
        }
    }
    if ordinal:
      item['snippet']['position'] = ordinal + 1
    pl_item = json.dumps(item)
    meta, response = http.request("https://www.googleapis.com/youtube/v3/playlistItems?part=snippet", method="POST", body=pl_item, headers={"Content-Type": "application/json"})
    return response

if __name__ == "__main__":
    get_authenticated_service()
