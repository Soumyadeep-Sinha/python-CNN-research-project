import cv2
import mediapipe as mp
import random
import time

mp_drawing = mp.solutions.drawing_utils
mphands = mp.solutions.hands

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

button_positions = {"button": (random.randint(0, cap.get(3) - 100), random.randint(0, cap.get(4) - 100))}
button_score = random.randint(-5, 10)

score = 0
speed_factor = 1
game_over = False
timeout_duration = 2
timeout_start_time = time.time()

def is_hand_on_button(hand_landmarks, button_position):
    if hand_landmarks is None:
        return False

    x, y = button_position
    button_rect = (x, y, 100, 100)
    tip_of_index_finger = hand_landmarks.landmark[mphands.HandLandmark.INDEX_FINGER_TIP]
    tip_coordinates = (int(tip_of_index_finger.x * cap.get(3)), int(tip_of_index_finger.y * cap.get(4)))
    return button_rect[0] < tip_coordinates[0] < button_rect[0] + button_rect[2] and \
           button_rect[1] < tip_coordinates[1] < button_rect[1] + button_rect[3]

hands = mphands.Hands()

while True:
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)

    if not game_over:
        data, image = cap.read()
        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        results = hands.process(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        button_x, button_y = button_positions["button"]
        button_color = (r, g, b)
        cv2.rectangle(image, (button_x, button_y), (button_x + 100, button_y + 100), button_color, cv2.FILLED)
        cv2.putText(image, f"COLOR BLOCKS", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (178,3,82), 4)
        cv2.putText(image, f"Score: {score}", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 4)
        cv2.putText(image, f"Button Score: {button_score}", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        cv2.putText(image, str(button_score), (button_x + 10, button_y + 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                button_x, button_y = button_positions["button"]
                if is_hand_on_button(hand_landmarks, (button_x, button_y)):
                    if button_score == 0:
                        game_over = True
                    else:
                        score += button_score
                        button_positions["button"] = (random.randint(0, int(cap.get(3)) - 100), random.randint(0, int(cap.get(4)) - 100))
                        button_score = random.randint(-5, 10)
                        timeout_start_time = time.time()
                    break

                if time.time() - timeout_start_time > timeout_duration:
                    button_positions["button"] = (random.randint(0, int(cap.get(3)) - 100), random.randint(0, int(cap.get(4)) - 100))
                    button_score = random.randint(-5, 10)
                    timeout_start_time = time.time()

                mp_drawing.draw_landmarks(image, hand_landmarks, mphands.HAND_CONNECTIONS)

        cv2.imshow("Color Blocks", image)
        cv2.waitKey(1)

        if score % 10 == 0:
            speed_factor += 0.1
            
    if game_over:
        cv2.putText(image, "WASTED!", (400, 200), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 0), 6)
        cv2.imshow("Color Blocks", image)
        cv2.waitKey(0)
        break

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
