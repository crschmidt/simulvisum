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
from django.shortcuts import render_to_response
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from django.conf import settings

from chat.models import Message
from main.models import Lounge

from main.views import next_video, fetch_next_video
import main.playlist as playlist
import cgi, json

from pusher import Pusher
pusherclient = Pusher(app_id=settings.PUSHER_APP_ID, key=settings.PUSHER_APP_KEY, secret=settings.PUSHER_APP_SECRET, cluster=settings.PUSHER_APP_CLUSTER)

def chat(request, id):
    recent_messages = Message.objects.filter(lounge=id).order_by("-timestamp")
    msgs = []
    for i in reversed(recent_messages[0:30]):
        msgs.append({"message": i.message, "user": i.user})
    d = json.dumps(msgs)
    return render_to_response("chat.html", {'id': id, 'messages': d})

def handle_commands(id, message):
    message = message.replace(u"\xa0", " ")
    if message.startswith("!skip"):
        l = Lounge.objects.get(pk=id)
        next_video(l)
        pusherclient.trigger("public-chat-"+id, "message-added", {"user": "LoungeBot", "message": "Skipping to next video"})
    if message.startswith("!next"):
        l = Lounge.objects.get(pk=id)
        v = fetch_next_video(l.playlist, l.current_video)
        pusherclient.trigger("public-chat-"+id, "message-added", {"user": "LoungeBot", "message": "Next video: %s" % v})
    if message.startswith("!add"):
        l = Lounge.objects.get(pk=id)
        bits = message.split(" ")
        if len(bits) == 2 and len(bits[1]) == 11:
            _, video_id = bits
            o = playlist.get_ordinal(l.playlist, l.current_video)
            print l.playlist, l.current_video, o
            results = playlist.add_video_id(l.playlist, video_id, o)
            results = json.loads(results)
            title = results['snippet']['title']
            pusherclient.trigger("public-chat-"+id, "message-added", {"user": "LoungeBot", "message": "Added: %s" % title})


        

@csrf_exempt
def message(request, id):
    if request.method != "POST":
        return HttpResponse("")
    user, msg = request.POST.get("user", "unknown"), request.POST.get("message", "")
    msg = msg.strip()
    if not len(msg):
        return HttpResponse("")
    msg = cgi.escape(msg)
    pusherclient.trigger("public-chat-"+id, "message-added", {"user": user, "message": msg})
    handle_commands(id, msg)
    try:
        m = Message(message=msg, lounge=id, user=user)
        m.save()
    except Exception, E:
        print E
    return HttpResponse("")
