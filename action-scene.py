#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import ConfigParser
import urllib2
import json
import io
import jellyfish
from hermes_python.hermes import Hermes

global global_conf
global domoticz_base_url

CONFIGURATION_ENCODING_FORMAT = "utf-8"
CONFIG_INI = "config.ini"
MAX_JARO_DISTANCE = 0.4

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

def getSwitchNames(base_url):
    response = urllib2.urlopen(global_conf.get("secret").get("domoticz url")+'/json.htm?type=command&param=getlightswitches')
    jsonresponse = json.load(response)
    allswitches = dict()
    for switch in jsonresponse["result"]:
        allswitches[switch["idx"]] = switch["Name"]
    return allswitches

def listScenes_received(hermes, intent_message):
    sentence = "I found these scenes, "
    scenes = getSceneNames(domoticz_base_url)
    print scenes
    for idx,scene in scenes.items():
       sentence = sentence + ", "+scene
    hermes.publish_end_session(intent_message.session_id, sentence)

def listSwitches_received(hermes, intent_message):
    sentence = "I found these switches, "
    switches = getSwitchNames(domoticz_base_url)
    print switches
    for idx,switch in switches.items():
       sentence = sentence + ", "+switch
    hermes.publish_end_session(intent_message.session_id, sentence)

def sceneOn_received(hermes, intent_message):
    
    print('Intent {}'.format(intent_message.intent))

    for (slot_value, slot) in intent_message.slots.items():
        print('Slot {} -> \n\tRaw: {} \tValue: {}'.format(slot_value, slot[0].raw_value, slot[0].slot_value.value.value))
    scenes = getSceneNames(domoticz_base_url)
    lowest_distance = MAX_JARO_DISTANCE
    lowest_idx = 65534
    lowest_name = "Unknown"
    for idx,scene in scenes.items():
        print "Comparing "+ scene +" and "+ slot[0].slot_value.value.value
        distance = 1-jellyfish.jaro_distance(scene, unicode(slot[0].slot_value.value.value, "utf-8"))
        print "Distance is "+str(distance)
        if distance < lowest_distance:
            print "Low enough and lowest!"
            lowest_distance = distance
            lowest_idx = idx
            lowest_name = scene
    if lowest_distance < MAX_JARO_DISTANCE:
        command_url = global_conf.get("secret").get("domoticz url")+'/json.htm?type=command&param=switchscene&idx='+str(lowest_idx)+'&switchcmd=On'
        print '"curl"ing '+command_url
        ignore_result = urllib2.urlopen(command_url)
        #ignore_result.read() # So we finish the connection correctly.
        hermes.publish_end_session(intent_message.session_id, "Turning on scene "+lowest_name)
    else:
        hermes.publish_end_session(intent_message.session_id, "I'm sorry, I couldn't find a scene like "+lowest_name)

if __name__ == "__main__":
    global_conf = read_configuration_file(CONFIG_INI)
    domoticz_base_url = global_conf.get("secret").get("domoticz url")
    with Hermes('localhost:1883') as h:
        h.subscribe_intent("iMartyn:listScenes",listScenes_received) \
         .subscribe_intent("iMartyn:sceneOn",sceneOn_received) \
         .subscribe_intent("iMartyn:listSwitches",listSwitches_received) \
         .start()
