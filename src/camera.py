import cv2
import logging

# Configure basic logging to console
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class CameraManager:
    """
    Manages the lifecycle, configuration, and capture of a webcam stream using OpenCV.
    """
    def __init__(self, device_index: int = 0):
        """
        Initializes the CameraManager with a target camera device index.
        """
        self.device_index = device_index
        self._cap = None

    def open(self) -> bool:
        """
        Attempts to open the camera device.
        
        Returns:
            bool: True if the camera opened successfully, False otherwise.
        """
        if self.is_open():
            logging.info("Camera is already open.")
            return True

        logging.info(f"Opening camera index {self.device_index}...")
        import platform
        if platform.system() == "Windows":
            self._cap = cv2.VideoCapture(self.device_index, cv2.CAP_DSHOW)
        else:
            self._cap = cv2.VideoCapture(self.device_index)

        if not self._cap.isOpened():
            logging.error(f"Could not open camera index {self.device_index}.")
            self._cap = None
            return False

        logging.info(f"Camera index {self.device_index} opened successfully.")
        return True

    def is_open(self) -> bool:
        """
        Checks if the camera device is currently open.
        
        Returns:
            bool: True if the camera is active/open, False otherwise.
        """
        return self._cap is not None and self._cap.isOpened()

    def read(self):
        """
        Reads a frame from the camera.
        
        Returns:
            tuple: (ret, frame) where ret is a boolean indicating success and frame is the captured image array.
        """
        if not self.is_open():
            logging.warning("Read called on a closed or uninitialized CameraManager.")
            return False, None
        return self._cap.read()

    def get_properties(self) -> dict:
        """
        Retrieves specific hardware properties of the camera stream.
        
        Returns:
            dict: A dictionary containing 'width', 'height', and 'fps'.
        """
        properties = {
            "width": 0,
            "height": 0,
            "fps": 0.0
        }
        if self.is_open():
            properties["width"] = int(self._cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            properties["height"] = int(self._cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            properties["fps"] = float(self._cap.get(cv2.CAP_PROP_FPS))
        return properties

    def release(self):
        """
        Safely releases the camera resource and resets internal state.
        """
        if self._cap is not None:
            logging.info("Releasing camera resource...")
            self._cap.release()
            self._cap = None
            logging.info("Camera resource released.")

    @staticmethod
    def find_available_cameras(max_to_check: int = 5) -> list[tuple[int, str]]:
        """
        Scans for available camera indices by attempting to open them.
        
        Returns:
            list[tuple[int, str]]: A list of (index, device_name) tuples of available cameras.
        """
        available_devices = []
        logging.info("Checking for available camera devices...")
        import platform
        is_windows = platform.system() == "Windows"
        
        # Attempt to retrieve device names on Windows via pygrabber
        device_names = {}
        if is_windows:
            try:
                from pygrabber.dshow_graph import FilterGraph
                devices = FilterGraph().get_input_devices()
                for idx, name in enumerate(devices):
                    device_names[idx] = name
            except ImportError:
                logging.info("pygrabber no esta instalado. Se usaran nombres genericos.")

        for i in range(max_to_check):
            # We try opening the camera
            if is_windows:
                cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            else:
                cap = cv2.VideoCapture(i)
            if cap.isOpened():
                # Verify we can read a frame to confirm it's actually working
                ret, _ = cap.read()
                if ret:
                    friendly_name = device_names.get(i, f"Camara {i}")
                    available_devices.append((i, friendly_name))
                cap.release()
        logging.info(f"Available camera devices found: {available_devices}")
        return available_devices

