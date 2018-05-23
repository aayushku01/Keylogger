import socket
from  _thread import *

host = ''
port = 55555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
	s.bind((host,port))
except socket.error as e:
	print(str(e))

s.listen(5)

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
		#conn.send(str.encode('>'))
		#conn.sendall(str.encode(reply))
	conn.close()

a = []

try :
    while True:

        conn, addr = s.accept()
        a.append(addr)
        print('connected to: '+addr[0]+':'+str(addr[1]))
        start_new_thread(threaded_client,(conn,))
        print(a)
except KeyboardInterrupt:
    s.shutdown(0)
    s.close()
