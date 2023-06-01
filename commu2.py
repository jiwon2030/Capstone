import socket as sc

HOST_3 = '0.0.0.0'
PORT_3 = 31005
path = 'C:\Git\Capstone/data.json'

socket_3 = sc.socket(sc.AF_INET, sc.SOCK_STREAM)
socket_3.setsockopt(sc.SOL_SOCKET, sc.SO_REUSEADDR, 1)

socket_3.bind((HOST_3, PORT_3))
socket_3.listen()

client, addr = socket_3.accept()
print(1)
while True: 
    print(2)
    data = client.recv(100)
    print(3)
    data = data.decode('utf-8')
    print(4)
    print(data)
    with open(path, 'a') as data.json:
        data.json.read(data)