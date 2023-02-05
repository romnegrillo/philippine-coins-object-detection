import numpy as np
import cv2

try:
    from picamera import PiCamera
    from picamera.array import PiRGBArray
except ImportError as exp:
    print(str(exp))
    print("Not in Raspberry Pi.")


class ObjectDetection:
    """Class used to load the deep learning model and perform detections."""

    def __init__(self, config_path, weights_path, classes, use_rpi_cam=False):
        """
        Construct the object detection class.

        It just needs the path for
        config, weights and the classes labels. It also needs if we will use
        the Raspberry Pi camera or USB camera.
        """
        # For selection what web cam to use and if detection will be enabled.
        self.use_rpi_cam = use_rpi_cam

        # YOLO paths.
        self.config_path = config_path
        self.weights_path = weights_path
        self.classes = classes

        # YOLO objects.
        self.yolo = cv2.dnn.readNet(self.weights_path, self.config_path)
        self.layer_names = self.yolo.getLayerNames()

        self.output_layers = [
            self.layer_names[i - 1] for i in self.yolo.getUnconnectedOutLayers()
        ]

        self.frame = None

        try:
            if not self.use_rpi_cam:
                self.capture = cv2.VideoCapture(0)
            else:
                self.camera = PiCamera(framerate=10)
                self.raw_capture = PiRGBArray(self.camera)
        except Exception as err:
            print(str(err))

    def get_frames(self):
        """
        Returns the current frame of the initialized camera.
        """
        if not self.use_rpi_cam:
            _, self.frame = self.capture.read()
        elif self.use_rpi_cam:
            self.camera.capture(
                self.raw_capture, format="bgr", use_video_port=True)
            self.frame = self.raw_capture.array

        # In BGR format.
        img = self.frame.copy()
        img = cv2.flip(img, 1)

        if self.use_rpi_cam:
            self.raw_capture.truncate(0)

        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    def detect(self, img):
        """
        Accepts a image in OpenCV format and runs the detection
        algorithm. Returns the new image with detected objects.
        """

        height, width, _ = img.shape
        blob = cv2.dnn.blobFromImage(
            img, 1 / 255.0, (416, 416), swapRB=True, crop=False
        )
        self.yolo.setInput(blob)
        outputs = self.yolo.forward(self.output_layers)

        class_ids = []
        confidences = []
        boxes = []

        for output in outputs:
            for detection in output:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]

                if confidence > 0.1:
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)

                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        indices = cv2.dnn.NMSBoxes(boxes, confidences, 0.1, 0.1)
        num_one_pesos = 0
        num_five_pesos = 0
        num_ten_pesos = 0
        num_twenty_pesos = 0

        for i in range(len(boxes)):
            if i in indices:
                x, y, w, h = boxes[i]

                label = str(self.classes[class_ids[i]])

                if label == self.classes[0]:
                    num_one_pesos += 1
                elif label == self.classes[1]:
                    num_five_pesos += 1
                elif label == self.classes[2]:
                    num_ten_pesos += 1
                elif label == self.classes[3]:
                    num_twenty_pesos += 1

                start = (x, y)
                end = (x + w, y + h)

                cv2.rectangle(img, start, end, (0, 255, 0), 2)
                cv2.putText(
                    img,
                    label,
                    (x, y - 10),
                    cv2.FONT_HERSHEY_PLAIN,
                    2,
                    (0, 0, 255),
                    2
                )

        return (
            cv2.cvtColor(img, cv2.COLOR_BGR2RGB),
            num_one_pesos,
            num_five_pesos,
            num_ten_pesos,
            num_twenty_pesos
        )

    def close_cam(self):
        """
        Close the initiazed camera.
        """
        if not self.use_rpi_cam:
            self.capture.release()
        else:
            return
