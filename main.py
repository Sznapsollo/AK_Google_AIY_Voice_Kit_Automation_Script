#!/usr/bin/env python3
# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Run a recognizer using the Google Assistant Library.

The Google Assistant Library has direct access to the audio API, so this Python
code doesn't need to record audio. Hot word detection "OK, Google" is supported.

It is available for Raspberry Pi 2/3 only; Pi Zero is not supported.
"""

import logging
import platform
import subprocess
import sys

import aiy.assistant.auth_helpers
from aiy.assistant.library import Assistant
import aiy.audio
import aiy.voicehat
from google.assistant.library.event import EventType

import requests
import json
import threading


logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
)

_remoteUrl = 'http://8.8.8.8/home/executables/';
_items = []

def power_off_pi():
    aiy.audio.say('Good bye!')
    subprocess.call('sudo shutdown now', shell=True)


def reboot_pi():
    aiy.audio.say('See you in a bit!')
    subprocess.call('sudo reboot', shell=True)
    
def terminate():
    aiy.audio.say('See you')
    exit(-1)

def runItem(itemId, status):
    #aiy.audio.say('ok')
    print('runItem ' + itemId + ' with status ' + status)
    url = _remoteUrl + 'toggle.php';
    postData = {'outletId' : itemId, 'outletStatus'  : status, 'outletDelayed': '0'}
    headers = {'content-type': 'application/json'}
    r = requests.post(url, data=json.dumps(postData), headers=headers)
    
def getDevicesData():
    try:
        global _items
        url = _remoteUrl + 'Services.php';
        postData = {'service':'CheckItemsData', 'receive' : '1', 'category'  : 'general'}
        headers = {'content-type': 'application/json'}
        r = requests.post(url, data=json.dumps(postData), headers=headers)
        
        #print(r.text)
        items = json.loads(r.text)
        if 'items' not in items:
            return
        
        for item in items['items']:
            if 'hotword' in item and item['hotword'] is not None:
                print('Found configured device ' + item['id'] + ' by hotword ' + item['hotword'])
                _items.append(item)
        
    except Exception as e:
        print('Error during getDevicesData')
        print(str(e))
        pass

def checkItem(name):
    
    status = None
    if name.endswith(' off'):
        status = 'off'
        name = name[:-4]
    elif name.endswith(' on'):
        status = 'on'
        name = name[:-3]
    else:
        return None
    
    for item in _items:
        if item['hotword'] == name:
            print('Found configured device ' + name)
            return {'name':item['id'], 'status':status}
    return None

def say_ip():
    ip_address = subprocess.check_output("hostname -I | cut -d' ' -f1", shell=True)
    aiy.audio.say('My IP address is %s' % ip_address.decode('utf-8'))


def process_event(assistant, event):
    print(event)
    status_ui = aiy.voicehat.get_status_ui()
    if event.type == EventType.ON_START_FINISHED:
        status_ui.status('ready')
        if sys.stdout.isatty():
            print('Say "OK, Google" then speak, or press Ctrl+C to quit...')

    elif event.type == EventType.ON_CONVERSATION_TURN_STARTED:
        #status_ui.set_trigger_sound_wave('/home/pi/AIY_stuff/yup_sil.wav')
        status_ui.status('listening')

    elif event.type == EventType.ON_RECOGNIZING_SPEECH_FINISHED and event.args:
        print('You said:', event.args['text'])
        text = event.args['text'].lower()
        if text == 'power off':
            assistant.stop_conversation()
            power_off_pi()
        elif text == 'reboot':
            assistant.stop_conversation()
            reboot_pi()
        elif text == 'ip address':
            assistant.stop_conversation()
            say_ip()
        elif text == 'terminate':
            assistant.stop_conversation()
            terminate()
        else:
            checked = checkItem(text)
            if checked is not None:
                t = threading.Thread(target=runItem, args=(checked['name'], checked['status']))
                t.start()
                assistant.stop_conversation()

    elif event.type == EventType.ON_END_OF_UTTERANCE:
        status_ui.status('thinking')

    elif (event.type == EventType.ON_CONVERSATION_TURN_FINISHED
          or event.type == EventType.ON_CONVERSATION_TURN_TIMEOUT
          or event.type == EventType.ON_NO_RESPONSE):
        status_ui.status('ready')

    elif event.type == EventType.ON_ASSISTANT_ERROR and event.args and event.args['is_fatal']:
        sys.exit(1)


def main():
    if platform.machine() == 'armv6l':
        print('Cannot run hotword demo on Pi Zero!')
        exit(-1)

    getDevicesData()

    credentials = aiy.assistant.auth_helpers.get_assistant_credentials()
    with Assistant(credentials) as assistant:
        for event in assistant.start():
            process_event(assistant, event)


if __name__ == '__main__':
    main()
