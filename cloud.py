import os
import serial
import pyfirmata
from socket import *
import camera
from time import sleep
import numpy as np
from importlib import reload

pid = os.fork()

if pid == 0:
    HOST2 = '54.173.222.34' # 원격 서버
    PORT2 = 31005
    client_socket2 = socket(AF_INET, SOCK_STREAM)
    client_socket2.connect((HOST2, PORT2))