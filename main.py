import cv2
import serial
import time
import math
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


def distance_3d(point1, point2):
    dx = point1.x - point2.x
    dy = point1.y - point2.y
    dz = point1.z - point2.z

    distance = math.sqrt(
        dx**2 +
        dy**2 +
        dz**2
    )

    return distance


def angle_3d(point_a, point_b, point_c):
    ba_x = point_a.x - point_b.x
    ba_y = point_a.y - point_b.y
    ba_z = point_a.z - point_b.z

    bc_x = point_c.x - point_b.x
    bc_y = point_c.y - point_b.y
    bc_z = point_c.z - point_b.z

    dot_product = (
        ba_x * bc_x +
        ba_y * bc_y +
        ba_z * bc_z
    )

    magnitude_ba = math.sqrt(
        ba_x**2 +
        ba_y**2 +
        ba_z**2
    )

    magnitude_bc = math.sqrt(
        bc_x**2 +
        bc_y**2 +
        bc_z**2
    )

    if magnitude_ba == 0 or magnitude_bc == 0:
        return 0

    cos_angle = dot_product / (magnitude_ba * magnitude_bc)

    cos_angle = max(-1.0, min(1.0, cos_angle))

    angle = math.degrees(
        math.acos(cos_angle)
    )

    return angle


def detect_fingers(image, hand_landmarks):
    lm = hand_landmarks.landmark

    finger_states = [0, 0, 0, 0, 0]

    wrist = lm[0]

    ANGLE_THRESHOLD = 150

    thumb_mcp = lm[2]
    thumb_ip = lm[3]
    thumb_tip = lm[4]

    thumb_d2 = distance_3d(wrist, thumb_mcp)
    thumb_d3 = distance_3d(wrist, thumb_ip)
    thumb_d4 = distance_3d(wrist, thumb_tip)

    thumb_angle1 = angle_3d(
        lm[1],
        lm[2],
        lm[3]
    )

    thumb_angle2 = angle_3d(
        lm[2],
        lm[3],
        lm[4]
    )

    thumb_distance_ok = (
        thumb_d4 > thumb_d3 > thumb_d2
    )

    thumb_angle_ok = (
        thumb_angle1 > ANGLE_THRESHOLD
        and
        thumb_angle2 > ANGLE_THRESHOLD
    )

    if thumb_distance_ok and thumb_angle_ok:
        finger_states[0] = 1

    d6 = distance_3d(wrist, lm[6])
    d7 = distance_3d(wrist, lm[7])
    d8 = distance_3d(wrist, lm[8])

    angle_6 = angle_3d(
        lm[5],
        lm[6],
        lm[7]
    )

    angle_7 = angle_3d(
        lm[6],
        lm[7],
        lm[8]
    )

    distance_ok = (
        d8 > d7 > d6
    )

    angle_ok = (
        angle_6 > ANGLE_THRESHOLD
        and
        angle_7 > ANGLE_THRESHOLD
    )

    if distance_ok and angle_ok:
        finger_states[1] = 1

    d10 = distance_3d(wrist, lm[10])
    d11 = distance_3d(wrist, lm[11])
    d12 = distance_3d(wrist, lm[12])

    angle_10 = angle_3d(
        lm[9],
        lm[10],
lm[11]
    )

    angle_11 = angle_3d(
        lm[10],
        lm[11],
        lm[12]
    )

    distance_ok = (
        d12 > d11 > d10
    )

    angle_ok = (
        angle_10 > ANGLE_THRESHOLD
        and
        angle_11 > ANGLE_THRESHOLD
    )

    if distance_ok and angle_ok:
        finger_states[2] = 1

    d14 = distance_3d(wrist, lm[14])
    d15 = distance_3d(wrist, lm[15])
    d16 = distance_3d(wrist, lm[16])

    angle_14 = angle_3d(
        lm[13],
        lm[14],
        lm[15]
    )

    angle_15 = angle_3d(
        lm[14],
        lm[15],
        lm[16]
    )

    distance_ok = (
        d16 > d15 > d14
    )

    angle_ok = (
        angle_14 > ANGLE_THRESHOLD
        and
        angle_15 > ANGLE_THRESHOLD
    )

    if distance_ok and angle_ok:
        finger_states[3] = 1

    d18 = distance_3d(wrist, lm[18])
    d19 = distance_3d(wrist, lm[19])
    d20 = distance_3d(wrist, lm[20])

    angle_18 = angle_3d(
        lm[17],
        lm[18],
        lm[19]
    )

    angle_19 = angle_3d(
        lm[18],
        lm[19],
        lm[20]
    )

    distance_ok = (
        d20 > d19 > d18
    )

    angle_ok = (
        angle_18 > ANGLE_THRESHOLD
        and
        angle_19 > ANGLE_THRESHOLD
    )

    if distance_ok and angle_ok:
        finger_states[4] = 1

    return finger_states


def generate_frames():
    global current_finger_states

    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        success, image = cap.read()

        if not success:
            break

        image = cv2.cvtColor(
            cv2.flip(image, 1),
            cv2.COLOR_BGR2RGB
        )

        results = hands.process(image)

        image = cv2.cvtColor(
            image,
            cv2.COLOR_RGB2BGR
        )

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS
                )

                fingers_state = detect_fingers(
                    image,
                    hand_landmarks
                )

                current_finger_states = fingers_state

                if esp and esp.is_open:
                    esp.write(bytes(fingers_state))

                print(
                    f"Fingers State: {fingers_state}"
                )

                fingers_up = sum(fingers_state)

                cv2.putText(
                    image,
                    f'Fingers Up: {fingers_up}',
                    (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2
                )

        ret, buffer = cv2.imencode(
            '.jpg',
            image
        )

        frame_bytes = buffer.tobytes()

        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n'
            +
            frame_bytes
            +
b'\r\n'
        )

    cap.release()


@app.route('/')
def index():
    return render_template(
        'index.html'
    )


@app.route('/video_feed')
def video_feed():
    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


@app.route('/get_status')
def get_status():
    return jsonify(
        current_finger_states
    )


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False
    )
