# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
from django.shortcuts import render, render_to_response
from django.http import HttpResponse

from django.views.decorators.csrf import csrf_exempt
from text.models import Text

@csrf_exempt
def change(request, id):
    if request.method == "POST":
        text = Text.objects.get(pk=id)
        text.text = request.POST['text']
        text.save()
        return HttpResponse("saved")
    return HttpResponse("ok")

def text(request, id):
    text = Text.objects.get(pk=id)
    return HttpResponse(json.dumps({'text': text.text}))

def edit(request, id):
    text = Text.objects.get(pk=id)
    return render_to_response("edit-text.html", {'id': id, 'text': text.text})

def view(request, id):
    return render_to_response("view-text.html", {'id': id})
