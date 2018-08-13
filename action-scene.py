
import urllib2
from hermes_python.hermes import Hermes

def intent_received(hermes, intent_message):
    print('Intent {}'.format(intent_message.intent))
​
    for (slot_value, slot) in intent_message.slots.items():
        print('Slot {} -> \n\tRaw: {} \tValue: {}'.format(slot_value, slot[0].raw_value, slot[0].slot_value.value.value))
​
    hermes.publish_end_session(intent_message.session_id,  "I'm sorry dave, I can't do that.")
​
with Hermes('localhost:1883') as h:
    h.subscribe_intents(intent_received).start()

# current_session_id = intentMessage.session_id
# response = urllib2.urlopen(['global']['Domoticz URL']+'/json.htm?type=scenes')
# jsonresponse = json.load(response)
# sentence = "I found these scenes : "
# for scene in jsonresponse.result[]:
#   sentence = sentence + scene.name
# #hermes.publish_end_session(current_session_id, "I'm sorry dave, I can't do that.")
# hermes.publish_end_session(current_session_id, sentence)