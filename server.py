#Update the host name if your server is at diffrent location.
#update log file address

import socket
from  _thread import *
from sys import exit

host = ''
port = 55555	#Update it

log_file = '/root/Desktop/server_log.txt'	#Update it
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

fopen = open(log_file,'a')
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
#        print("Received from ("+ conn.getpeername()[0] + ":"+ str(conn.getpeername()[1])+") ->" + data.decode('utf-8'))
        if (data.decode('utf-8') == "Connection Closed"):
            a.remove(conn.getpeername())
            fopen.close()
            break
        fopen.write("From("+ conn.getpeername()[0] + ":"+ str(conn.getpeername()[1])+")->" + data.decode('utf-8'))
        fopen.write('\n')
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
    fopen.close()
    sock.shutdown(0)
    sock.close()
