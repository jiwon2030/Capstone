import cv2
import mediapipe as mp
import time
import requests
import json
import threading
import socket

# 플라스크 서버 URL
SERVER_URL = 'http://localhost:5000/events'

# 라즈베리 파이의 IP 주소와 포트 번호
RASPBERRY_PI_IP = '172.20.10.2'
RASPBERRY_PI_PORT = 1225

line_drawn = False

# 마우스 이벤트 핸들러
def draw_line(event, x, y, flags, params):
    global clickX, clickY, line_drawn
    if event == cv2.EVENT_LBUTTONDOWN:
        clickX, clickY = x, y
        line_drawn = True

def send_event_data(event_data):
    headers = {'Content-Type': 'application/json'}
    try:
        requests.post(SERVER_URL, data=json.dumps(event_data), headers=headers, timeout=0.001)
    except requests.Timeout:
        pass
    except requests.ConnectionError:
        pass

# 소켓 생성 및 연결
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((RASPBERRY_PI_IP, RASPBERRY_PI_PORT))

# 통신 함수
def send_event_type(event_type):
    # eventType 전달
    message = event_type.encode()
    client_socket.send(message)

# 영상 처리 스레드 함수
def process_video():
    # 웹캠에서 동영상 읽기
    cap = cv2.VideoCapture(1)

    # 윈도우 생성 및 마우스 이벤트 등록
    cv2.namedWindow("img")
    cv2.setMouseCallback("img", draw_line)

    # mediapipe를 이용하여 손 인식 모델 생성
    mp_hands = mp.solutions.hands
    my_hands = mp_hands.Hands()
    mp_draw = mp.solutions.drawing_utils

    # 최하단 지점이 직선 아래에 진입 시작한 시간
    start_time = None

    while True:
        # 웹캠으로부터 이미지를 가져와서 좌우 반전
        success, img = cap.read()
        # 좌우 반전
        img = cv2.flip(img, 1)

        if line_drawn:
            # RGB 이미지로 변환
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            # mediapipe를 이용하여 손 인식 수행
            results = my_hands.process(img_rgb)

            # 이미지 크기 가져오기
            h, w, c = img.shape

            # 손 랜드마크 중 최하단 지점 좌표
            max_x = 0
            max_y = 0

            # 마우스 클릭 이벤트 처리
            if 'clickX' in globals() and 'clickY' in globals():
                # 선 그리기
                cv2.line(img, (0, clickY), (w, clickY), (0, 255, 0), 2)

            if results.multi_hand_landmarks:
                # 손 모델 이용
                for hand_lms in results.multi_hand_landmarks:
                    for id, lm in enumerate(hand_lms.landmark):
                        # 손의 각 랜드마크 좌표를 가져오고 이미지 크기에 맞게 변환
                        cx, cy = int(lm.x * w), int(lm.y * h)
                        if cy > max_y:
                            max_x = cx
                            max_y = cy

                        # 랜드마크 표시
                        mp_draw.draw_landmarks(img, hand_lms, mp_hands.HAND_CONNECTIONS)

                    # 추출된 손 랜드마크 중 최하단 지점에 노란 원 그리기
                    cv2.circle(img, (max_x, max_y), 8, (0, 255, 255), cv2.FILLED)

                if max_y > clickY:
                    if start_time is None:
                        start_time = time.time()

                        # 작업자의 손이 위험 영역에 진입하는 순간에 이벤트 데이터 대기열에 추가
                        event_data = {
                            "eventType": "intrusion",
                            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime()),
                            "message": "A worker's hand has entered the mixer. Immediate action required!"
                        }
                        threading.Thread(target=send_event_data, args=(event_data,)).start()
                        threading.Thread(target=send_event_type, args=("intrusion",)).start()

                    elif start_time is not None:
                        elapsed_time = time.time() - start_time
                        text = f"Elapsed Time: {elapsed_time:.2f} sec"
                        cv2.putText(img, text, (10, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
                if max_y <= clickY:
                    # 작업자의 손이 안전 영역에 있는 상황에서 초록 원 그리기
                    cv2.circle(img, (w - 50, h - 50), 24, (0, 255, 0), cv2.FILLED)

                if max_y <= clickY and start_time is not None:
                    start_time = None

                    # 작업자의 손이 위험 영역을 탈출하는 순간에 이벤트 데이터 대기열에 추가
                    event_data = {
                        "eventType": "safety",
                        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime()),
                        "message": "A worker's hand has exited the mixer. The situation is under control."
                    }
                    threading.Thread(target=send_event_data, args=(event_data,)).start()
                    threading.Thread(target=send_event_type, args=("safety",)).start()

                # 최하단 지점이 직선 아래로 진입하면 측정 시작
                if max_y > clickY:
                    # 작업자의 손이 위험 영역에 진입한 상황에서 빨간 원 그리기
                    cv2.circle(img, (w - 50, h - 50), 24, (0, 0, 255), cv2.FILLED)

                    if start_time is None:
                        start_time = time.time()

                    # 최하단 지점이 직선 아래에 진입중인 동안 시간 계속 측정
                    elif start_time is not None:
                        elapsed_time = time.time() - start_time
                        text = f"Elapsed Time: {elapsed_time:.2f} sec"
                        cv2.putText(img, text, (10, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)


            # 화면에 이미지 표시
            cv2.imshow("img", img)

        else:
            # 직선이 그려지지 않으면 웹캠의 영상만 보여줍니다.
            cv2.imshow("img", img)

        # 사용자 입력으로 종료
        if cv2.waitKey(1) == ord('x'):
            break

    # 소켓 연결 종료
    client_socket.close()

# 영상 처리 스레드 시작
video_thread = threading.Thread(target=process_video)
video_thread.start()
