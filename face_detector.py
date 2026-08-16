import cv2


# =====================================
# LOAD HAAR CASCADE FACE DETECTOR
# =====================================

face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades +
    "haarcascade_frontalface_default.xml"
)


# =====================================
# DETECT FACES
# =====================================

def detect_faces(image):

    # Convert image to grayscale
    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    # Detect faces
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(80, 80)
    )

    return faces


# =====================================
# DRAW FACE BOX
# =====================================

def draw_face_boxes(image):

    faces = detect_faces(
        image
    )

    for (
        x,
        y,
        w,
        h
    ) in faces:

        cv2.rectangle(
            image,
            (x, y),
            (x + w, y + h),
            (0, 255, 0),
            2
        )

    return image, len(faces)


# =====================================
# TEST WEBCAM
# =====================================

if __name__ == "__main__":

    camera = cv2.VideoCapture(
        0
    )

    if not camera.isOpened():

        print(
            "Error: Cannot open webcam"
        )

        exit()


    print(
        "Face detector started. Press Q to close."
    )


    while True:

        success, frame = camera.read()

        if not success:

            print(
                "Failed to capture frame"
            )

            break


        frame, total_faces = draw_face_boxes(
            frame
        )


        cv2.putText(
            frame,
            f"Faces Detected: {total_faces}",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2
        )


        cv2.imshow(
            "AI Face Detector",
            frame
        )


        if cv2.waitKey(1) & 0xFF == ord("q"):

            break


    camera.release()

    cv2.destroyAllWindows()