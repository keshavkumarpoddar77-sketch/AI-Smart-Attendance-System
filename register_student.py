import cv2
import os


# ============================================================
# PROJECT PATH
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

FACE_DATA_DIR = os.path.join(
    BASE_DIR,
    "data",
    "faces"
)


# Create main face folder
os.makedirs(
    FACE_DATA_DIR,
    exist_ok=True
)


# ============================================================
# ENTER STUDENT ID
# ============================================================

student_id = input(
    "Enter Student ID: "
).strip()


if not student_id:

    print("ERROR: Student ID cannot be empty.")
    exit()


# ============================================================
# CREATE STUDENT FOLDER
# ============================================================

save_dir = os.path.join(
    FACE_DATA_DIR,
    student_id
)

os.makedirs(
    save_dir,
    exist_ok=True
)


print("\n====================================")
print("AI SMART ATTENDANCE SYSTEM")
print("FACE REGISTRATION")
print("====================================")

print(f"\nStudent ID: {student_id}")

print(f"\nImages will be saved to:")
print(save_dir)


# ============================================================
# OPEN CAMERA
# ============================================================

camera = cv2.VideoCapture(0)


if not camera.isOpened():

    print("\nERROR: Camera could not be opened.")

    exit()


print("\nCamera started successfully.")

print("\nInstructions:")
print("SPACE = Capture Image")
print("Q = Quit")

print("\nCapture 5 clear face images.")


# ============================================================
# CAPTURE IMAGES
# ============================================================

count = 0

while True:

    ret, frame = camera.read()


    if not ret:

        print("ERROR: Could not read camera.")

        break


    # Display instructions
    cv2.putText(
        frame,
        f"Student: {student_id} | Images: {count}/5",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2
    )


    cv2.putText(
        frame,
        "SPACE = Capture | Q = Quit",
        (20, 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )


    cv2.imshow(
        "Student Face Registration",
        frame
    )


    key = cv2.waitKey(1) & 0xFF


    # ========================================================
    # CAPTURE IMAGE
    # ========================================================

    if key == 32:

        count += 1


        filename = os.path.join(
            save_dir,
            f"{count}.jpg"
        )


        success = cv2.imwrite(
            filename,
            frame
        )


        if success:

            print(
                f"Image {count} saved successfully:"
            )

            print(
                filename
            )

        else:

            print(
                f"ERROR: Could not save image {count}"
            )


        # Stop after 5 images
        if count >= 5:

            print(
                "\n===================================="
            )

            print(
                "5 FACE IMAGES CAPTURED SUCCESSFULLY!"
            )

            print(
                "===================================="
            )

            break


    # ========================================================
    # QUIT
    # ========================================================

    elif key == ord("q"):

        print("\nRegistration cancelled.")

        break


# ============================================================
# RELEASE CAMERA
# ============================================================

camera.release()

cv2.destroyAllWindows()


print("\n====================================")
print("FACE REGISTRATION COMPLETED")
print("====================================")

print(f"Student ID: {student_id}")

print(f"Total Images Captured: {count}")

print(f"\nSaved Location:")
print(save_dir)