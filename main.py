import paho.mqtt.client as mqtt
import mido

outport = mido.open_output()

mapping = [(('EC:DA:3B:AA:BF:2C', 1), 60),
           (('EC:DA:3B:AA:C1:60', 1), 61)]
# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    #client.subscribe("$SYS/#")
    #client.subscribe("topic/#")
    #client.subscribe("test/#")
    #client.subscribe("test/1")
    client.subscribe("#")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
    if msg.topic[:7] == 'device/':
        for ((mac, button_id), note) in mapping:
            #print (mac, button_id, note)
            if msg.topic[7:7+6*2+5] == mac:
                midi_msg = mido.Message('note_on', note=note, velocity=127)
                #cc = mido.control_change(channel=1, control=1, value=122, time=60)
                #cc = mido.Message.from_str('control_change channel=0 control=0 value=122')
                outport.send(midi_msg)
                #outport.send(cc)
                #print("sent")
                midi_msg = mido.Message('note_off', note=note, velocity=127)
                outport.send(midi_msg)

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("localhost", 1883, 60)

# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()
