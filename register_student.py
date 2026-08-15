import cv2
import os

student_id = input("Enter student ID: ").strip()

save_dir = os.path.join("data", "faces", student_id)
os.makedirs(save_dir, exist_ok=True)

camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("ERROR: Camera could not be opened.")
    exit()

print("Camera started.")
print("Look at the camera.")
print("Press SPACE to capture.")
print("Press Q to quit.")

count = 0

while True:
    ret, frame = camera.read()

    if not ret:
        print("Could not read camera.")
        break

    cv2.imshow("Student Registration", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord(" "):
        count += 1

        filename = os.path.join(
            save_dir,
            f"{count}.jpg"
        )

        cv2.imwrite(filename, frame)

        print(f"Saved: {filename}")

        if count == 5:
            print("5 face images captured successfully.")
            break

    elif key == ord("q"):
        break

camera.release()
cv2.destroyAllWindows()

print(f"Registration completed for student {student_id}.")