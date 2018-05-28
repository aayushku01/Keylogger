#Update the host name if your server is at diffrent location.

import socket
from  _thread import *
from sys import exit

host = ''
port = 55555

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    sock.bind((host,port))
except socket.error as e:
    print(str(e))
    exit(1)

sock.listen(5)

print('Waiting...')

def threaded_client(conn):
    global a
    while True:
        data = conn.recv(2048)
        if not data:
            break
        print("Received from ("+ conn.getpeername()[0] + ":"+ str(conn.getpeername()[1])+") ->" + data.decode('utf-8'))
        if (data.decode('utf-8') == "Connection Closed"):
            a.remove(conn.getpeername())
            #break
        #conn.send(str.encode(input('>')))
        #conn.sendall(str.encode(reply))
    conn.shutdown(1)
    conn.close()

a = []

try :
    while True:

        conn, addr = sock.accept()
        a.append(addr)
        print('connected to: '+addr[0]+':'+str(addr[1]))
        start_new_thread(threaded_client,(conn,))
        print(a)
except KeyboardInterrupt:
    sock.shutdown(0)
    sock.close()
