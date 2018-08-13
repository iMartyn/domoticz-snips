#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import ConfigParser
import urllib2
import json
from hermes_python.hermes import Hermes

def listScenes_received(hermes, intent_message):
    print('Intent {}'.format(intent_message.intent))

    for (slot_value, slot) in intent_message.slots.items():
        print('Slot {} -> \n\tRaw: {} \tValue: {}'.format(slot_value, slot[0].raw_value, slot[0].slot_value.value.value))

    response = urllib2.urlopen('http://domoticz.k.mar1.uk/json.htm?type=scenes')
    jsonresponse = json.load(response)
    sentence = "I found these scenes, "
    print jsonresponse["result"]
    for scene in jsonresponse["result"]:
       sentence = sentence + ", "+scene["Name"]
    hermes.publish_end_session(intent_message.session_id, sentence)

with Hermes('localhost:1883') as h:
    h.subscribe_intent("listScenes",listScenes_received).start()
