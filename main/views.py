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
from main.models import Lounge, Video
from django.http import HttpResponse
from django.shortcuts import render_to_response
import json
from main.playlist import get_playlist_ids, get_video_length
from django.views.decorators.csrf import csrf_exempt

def home(request):
    l = Lounge.objects.all()
    return render_to_response("home.html", {'lounges': l})

def cache_video_web(request, video_id):
    s = cache_video_length(video_id)
    return HttpResponse(s)

def cache_video_length(video_id):
    v = Video.objects.filter(video_id=video_id)
    if v.count() == 0:
        secs = get_video_length(video_id)
        v = Video(video_id=video_id, length=secs)
        v.save()
    else:
        v = v[0]
    return v.length


def fetch_next_video(playlist, current):
    ids = get_playlist_ids(playlist)
    if current == None:
        cache_video_length(ids[0])
        return ids[0]
    else:
        for i, id in enumerate(ids):
            if id == current:
                if len(ids) > i+1:
                    cache_video_length(ids[i+1])
                    return ids[i+1]
                else:
                    cache_video_length(ids[0])
                    return ids[0]
        else:
            return ids[0]

def lounge(request, id):
    l = Lounge.objects.get(pk=id)
    return render_to_response("lounge.html", {'lounge': l})

@csrf_exempt
def update_position(request, id):
    l = Lounge.objects.get(pk=id)
    if request.method != "POST":
        return HttpResponse("")
    vid, time = request.POST.get('video'), int(float(request.POST.get('time',0)))
    vid, time, state = request.POST.get('video'), int(float(request.POST.get('time',0))), int(request.POST.get("state", 1))
    if vid == l.current_video and time >= l.current_time:
        v = Video.objects.filter(video_id=vid)
        if v.count() > 0:
            v = v[0]
        else:    
            cache_video_length(vid)
            v = Video.objects.get(video_id=vid)
        if (time + 2 > v.length and v.length != 0) or (v.length == 0 and state == 0):
            next_video(l)
        else:
            l.current_time = time
        l.save()
    o = {'video': l.current_video, 'time': l.current_time}
    return HttpResponse(json.dumps(o))

def next_video(l):
    new = fetch_next_video(l.playlist, l.current_video)
    l.current_time = 0
    l.current_video = new
    l.save()
    return l

def get_position(request, id):
    l = Lounge.objects.get(pk=id)
    if l.current_video == None:
        vid = fetch_next_video(l.playlist, l.current_video)        
        l.current_video = vid
        l.save()
    o = {'video': l.current_video, 'time': l.current_time}
    return HttpResponse(json.dumps(o))
    
