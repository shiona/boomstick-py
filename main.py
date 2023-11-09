import mido
import socket

outport = mido.open_output()

mapping = [(('EC:DA:3B:AA:BF:2C', 1), 60),
           (('EC:DA:3B:AA:C1:60', 1), 61)]

NPP_PORT = 6566

# The callback for when a PUBLISH message is received from the server.
def handle_button(recv_mac):
    for ((mac, button_id), note) in mapping:
        #print (mac, button_id, note)
        if recv_mac == mac:
            midi_msg = mido.Message('note_on', note=note, velocity=127)
            #cc = mido.control_change(channel=1, control=1, value=122, time=60)
            #cc = mido.Message.from_str('control_change channel=0 control=0 value=122')
            outport.send(midi_msg)
            #outport.send(cc)
            #print("sent")
            midi_msg = mido.Message('note_off', note=note, velocity=127)
            outport.send(midi_msg)


def main():

    sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP

    sock.bind(('', NPP_PORT))

    while True:
        data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        #print(f"received message: {data}")

        msg_type = data[0:1]
        mac = data[1:18]
        rest = data[18:]
        #print(f"msg type: {msg_type}")
        if msg_type == b'D': # Discovery
            print(f'Discovery received from MAC {mac}')
            sock.sendto(b'R', addr)
        elif msg_type == b'B':
            print(f'Button #{rest.decode("ascii")} received from MAC {mac}')
            handle_button(mac)
        elif msg_type == b'V':
            print(f'Voltage {rest.decode("ascii")} mV received from MAC {mac}')
        else:
            print(f'Unknown cmd {msg_type}')

if __name__ == '__main__':
    main()
