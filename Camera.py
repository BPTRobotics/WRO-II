import cv2

def init_camera(camera_index=0):
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        raise IOError("Cannot open camera")
    return cap

def get_frame(cap,flip_vertical = True):
    ret, frame = cap.read()
    if not ret:
        raise IOError("Cannot read frame")

    if flip_vertical:
        frame = cv2.flip(frame, 0)
    return frame

def normalize_point(point, frame):
    h, w = frame.shape[:2]
    x, y = point
    return x / float(w), y / float(h)

def normalize_2_middle(point, frame):
    new_point = normalize_point(point, frame)
    return (new_point[0] - 0.5) * 2, (new_point[1] - 0.5) * 2
    

if __name__ == "__main__":
    cap = init_camera()
    while True:
        frame = get_frame(cap)
        cv2.imshow('frame', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
