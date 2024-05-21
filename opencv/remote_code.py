#!/usr/bin/env python

import socket

SOCKPATH = "/var/run/lirc/lircd"

sock = None

def init_irw():
    global sock
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    print ('starting up on %s' % SOCKPATH)
    sock.connect(SOCKPATH)

def next_key():
    '''Get the next key pressed. Return keyname, updown.
    '''
    while True:
        data = sock.recv(128)
        data = data.strip()
        if data:
            break

    words = data.split()
    return words[2], words[1]

if __name__ == '__main__':
    init_irw()

    while True:
        keyname, updown = next_key()
        if keyname == 'KEY_.':
            print('Button 1 pressed')
        elif keyname == 'KEY_1':
            print('Button 2 pressed')
        elif keyname == 'KEY_2':
            print('Button 3 pressed')
