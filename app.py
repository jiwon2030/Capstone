from flask import app, request, Flask
import socket as sc
import json
import os

app = Flask(__name__)
app.secret_key = 'qwer1234' #소켓 통신을 위한 Key 설정
path = 'C:\Git\Capstone\data.json'

HOST = '0.0.0.0'
port = 1004

# @app.route('/')

@app.route('/sendToRasp', method=["POST"])
def sendToRasp():
    if request.method == 'POST':
        return

# 이벤트 상태를 json형식으로 넘겨주는 api
@app.route('/returnEvent')
def returnName():
    path = "../data/"
    file_list = os.listdir(path)
    json = {}
    for i in range(len(file_list)):
        json[f'{i}'] = file_list[i]
    return json

if __name__ == "__main__":
    from waitress import serve

    socket = sc.socket(sc.AF_INET, sc.SOCK_STREAM)
    socket.setsockopt(sc.SOL_SOCKET, sc.SO_REUSEADDR, 1)
    socket.bind((HOST, port))
    socket.listen()
    client, addr = socket.accept()
    
    app.jinja_env.auto_reload = True
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    serve(app, host="0.0.0.0", port=5000)
    app.debug = True
    app.run(debugs = True, host = '0.0.0.0', port = 5000)

    app.run()