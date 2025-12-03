import cv2, time

cap = cv2.VideoCapture(0)
prev = time.time()
frames = 0
t0 = time.time()

while frames < 120:
    ret, frame = cap.read()
    if not ret:
        break
    frames += 1
    cv2.imshow("cam", frame)
    if cv2.waitKey(1) == 27:
        break

t1 = time.time()
print(f"Measured FPS: {frames / (t1 - t0):.2f}")

cap.release()
cv2.destroyAllWindows()
