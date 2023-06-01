import socket as sc
from time import sleep

HOST_1 = '192.168.137.219' # 클라이언트
HOST_2 = '0.0.0.0' # 서버
PORT_1 = 1004
PORT_2 = 31004

socket_1 = sc.socket(sc.AF_INET, sc.SOCK_STREAM)
socket_2 = sc.socket(sc.AF_INET, sc.SOCK_STREAM)
socket_2.setsockopt(sc.SOL_SOCKET, sc.SO_REUSEADDR, 1)

socket_1.connect((HOST_1, PORT_1))

socket_2.bind((HOST_2, PORT_2))
socket_2.listen()

client, addr = socket_2.accept()

while True:
    signal = socket_1.recv(8)

    if signal.decode() == 'add':
        client.sendall(signal)

        name = socket_1.recv(64)
        print(len(name.decode('utf-8')))
        client.sendall(name);sleep(0.01)

        data = socket_1.recv(4096)
        print(len(data.decode()))
        client.sendall(data)

    # caution 시그널은 라즈베리파이 모터 속도 늦춤
    elif signal.decode() == 'caution':
        # 라즈베리파이로 시그널 전송
        client.sendall(signal)

    # danger 시그널은 라즈베리파이 모터 멈춤
    elif signal.decode() == 'intrusion':
        # 라즈베리파이에 시그널 전송
        client.sendall(signal)
