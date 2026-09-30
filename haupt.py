import threading 
import time
from camera2 import CameraTracker
from jarvis2 import JarvisBot

tracker = CameraTracker()
jarvis = JarvisBot()

jarvis_thread = threading.Thread(target=jarvis.run, args=(tracker,), daemon = True)

jarvis_thread.start()
try: 
    tracker.start()
except KeyboardInterrupt:
    print("Stopping threads")