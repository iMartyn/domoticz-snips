#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import ConfigParser
import urllib2
import json
import io
import fuzzy
from hermes_python.hermes import Hermes

global global_conf
global domoticz_base_url

CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"

class SnipsConfigParser(ConfigParser.SafeConfigParser):
    def to_dict(self):
        return {section : {option_name : option for option_name, option in self.items(section)} for section in self.sections()}

def read_configuration_file(configuration_file):
    try:
        with io.open(configuration_file, encoding=CONFIGURATION_ENCODING_FORMAT) as f:
            conf_parser = SnipsConfigParser()
            conf_parser.readfp(f)
            return conf_parser.to_dict()
    except (IOError, ConfigParser.Error) as e:
        return dict()

def getSceneNames(base_url):
    response = urllib2.urlopen(global_conf.get("secret").get("domoticz url")+'/json.htm?type=scenes')
    jsonresponse = json.load(response)
    allscenes = dict()
    for scene in jsonresponse["result"]:
        allscenes[scene["idx"]] = scene["Name"]
    return allscenes

def listScenes_received(hermes, intent_message):
    sentence = "I found these scenes, "
    scenes = getSceneNames(domoticz_base_url)
    print scenes
    for idx,scene in scenes.items():
       sentence = sentence + ", "+scene
    hermes.publish_end_session(intent_message.session_id, sentence)

def sceneOn_received(hermes, intent_message):
    print('Intent {}'.format(intent_message.intent))

    for (slot_value, slot) in intent_message.slots.items():
        print('Slot {} -> \n\tRaw: {} \tValue: {}'.format(slot_value, slot[0].raw_value, slot[0].slot_value.value.value))

if __name__ == "__main__":
    global_conf = read_configuration_file(CONFIG_INI)
    domoticz_base_url = global_conf.get("secret").get("domoticz url")
    with Hermes('localhost:1883') as h:
        h.subscribe_intent("iMartyn:listScenes",listScenes_received).start()
