import lirc
sockid = lirc.init("myprogram")
try:
    while True:
        code = lirc.nextcode()
        if code:
            print("Received code:", code)
except KeyboardInterrupt:
    lirc.deinit()
