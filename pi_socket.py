import socket

def on_connect():
    print('Connected to the motor control namespace')

def on_motor_control(data):
    action = data.get('action')
    if action == 'start':
        start_motor()
    elif action == 'stop':
        stop_motor()

def start_motor():
    # 모터를 가동하는 코드 작성
    # 예: GPIO 핀을 HIGH로 설정하여 모터를 작동시킴
    print("모터 가동")
    pass

def stop_motor():
    # 모터를 정지시키는 코드 작성
    # 예: GPIO 핀을 LOW로 설정하여 모터를 정지시킴
    print("모터 정지")
    pass

if __name__ == '__main__':
    # 소켓 객체 생성
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    host = '127.0.0.1'  # 웹 서버의 IP 주소
    port = 5001  # 웹 서버의 포트 번호

    # 서버에 연결
    s.connect((host, port))

    # 서버로부터 데이터 수신
    response = s.recv(1024)

    # 수신된 데이터 디코딩
    data = json.loads(response.decode())

    # 모터 제어 동작 실행
    on_motor_control(data)

    # 소켓 연결 종료
    s.close()
