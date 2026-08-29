import cv2
import serial
import time
import mediapipe as mp
from flask import Flask, render_template, Response, jsonify

app = Flask(__name__)


try:
    esp = serial.Serial(port='COM3', baudrate=9600, timeout=1)
    time.sleep(2)
    print("Ket noi ESP8266 thanh cong!")
except Exception as e:
    print(f"Loi ket noi Serial: {e}")
    esp = None


mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands()

current_finger_states = [0, 0, 0, 0, 0]

def detect_fingers(image, hand_landmarks):
    finger_tips = [8, 12, 16, 20]  # Trỏ, Giữa, Áp út, Út
    thumb_tip = 4
    finger_states = [0, 0, 0, 0, 0]

    # Kiểm tra ngón cái
    if hand_landmarks.landmark[thumb_tip].x < hand_landmarks.landmark[thumb_tip - 1].x:
        finger_states[0] = 1

    # Kiểm tra 4 ngón còn lại
    for idx, tip in enumerate(finger_tips):
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y:
            finger_states[idx + 1] = 1

    return finger_states

#  BỌC VÒNG LẶP XỬ LÝ CAMERA ĐỂ ĐƯA LÊN WEB 
def generate_frames():
    global current_finger_states
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        success, image = cap.read()
        if not success:
            break

        
        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        results = hands.process(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                fingers_state = detect_fingers(image, hand_landmarks)
                current_finger_states = fingers_state
                
                
                if esp and esp.is_open:
                    esp.write(bytes(fingers_state))
                print(f"Fingers State: {fingers_state}")

                
                fingers_up = sum(fingers_state)
                cv2.putText(image, f'Fingers Up: {fingers_up}', (10, 50), 
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Đưa khung hình ra dạng luồng byte hiển thị trên HTML 
        ret, buffer = cv2.imencode('.jpg', image)
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

    cap.release()


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_status')
def get_status():
    return jsonify(current_finger_states)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)