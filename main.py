import mido
import platform
import socket
import sys



try:
    from config import mapping
except:
    print("Could not load config.py, please copy config.py.example into config.py and edit it to your needs")
    sys.exit(1)

outport = None

if platform.system() == 'Darwin':
    outport = mido.open_output('IAC Driver Bus 1')
elif platform.system() == 'Linux':
    outport = mido.open_output()
else:
    print("Unknown / unsupported system")
    sys.exit(1)


NPP_PORT = 6566

# The callback for when a PUBLISH message is received from the server.
def handle_button(recv_mac):
    for ((mac, button_id), note) in mapping:
        #print (mac, button_id, note)
        if recv_mac == mac:
            print("sending midi")
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

    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    sock.bind(('', NPP_PORT))

    print("Running")

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
