import cv2

class Camera:
    def __init__(self):
        try:
            self.video = cv2.VideoCapture(0)
            # If VideoCapture failed to open, normalize to None
            if not self.video or (hasattr(self.video, 'isOpened') and not self.video.isOpened()):
                self.video = None
        except Exception:
            self.video = None

    def get_frame(self):
        if not getattr(self, 'video', None):
            return None
        success, frame = self.video.read()
        return frame if success else None

    def __del__(self):
        if getattr(self, 'video', None):
            try:
                self.video.release()
            except Exception:
                pass
