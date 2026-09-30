import json 
import cv2
from ultralytics import YOLO

class CameraTracker:
    def __init__(self, model_path="/Users/jamie.wiebe/Hack Club/yolov8n.pt"):
        self.model = YOLO(model_path)
        self.detected_objects = []
        self.is_running = False

    def start(self):
        cam = cv2.VideoCapture(0)
        self.is_running = True

        while self.is_running and cam.isOpened():
            ret, frame = cam.read()
            if not ret:
                break

            results = self.model(frame)
            class_ids = results[0].boxes.cls.tolist()
            self.detected_objects = list(set([self.model.names[int(cls)] for cls in class_ids]))
            
            annotated_frame = results[0].plot()
            cv2.imshow("Camera", annotated_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.is_running = False
                break
        cam.release()
        cv2.destroyAllWindows()
if __name__ == "__main__":
    camera = CameraTracker()
    camera.start()