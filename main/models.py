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
from django.db import models

class Lounge(models.Model):
    playlist = models.CharField(max_length=255)
    current_time = models.IntegerField(default=0)
    current_video = models.CharField(max_length=15, null=True, blank=True)
    chat_id = models.CharField(max_length=255)

class Video(models.Model):
    video_id = models.CharField(max_length=12)
    length = models.IntegerField()
