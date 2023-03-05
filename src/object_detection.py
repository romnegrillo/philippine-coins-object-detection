import sys
import numpy as np
import cv2
import imutils


class ObjectDetection:
    """Class used to load the deep learning model and perform detections."""

    def __init__(self, config_path, weights_path, classes):
        """
        Construct the object detection class.

        It just needs the path for
        config, weights and the classes labels.
        """

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
            self.capture = cv2.VideoCapture(0)
        except Exception as err:
            print(str(err))
            sys.exit(1)

    def get_frames(self):
        """
        Returns the current frame of the initialized camera
        in BGR format.
        """

        # In BGR format.
        _, self.frame = self.capture.read()
        img = self.frame.copy()
        img = imutils.resize(img, width=600)
        # img = cv2.flip(img, 1)

        return img

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
        num_five_pesos = 0
        num_ten_pesos = 0
        num_twenty_pesos = 0
        num_one_pesos = 0

        for index, _ in enumerate(boxes):
            if index in indices:
                x, y, w, h = boxes[index]

                label = str(self.classes[class_ids[index]])

                if label == self.classes[0]:
                    num_five_pesos += 1
                    mask_color = (0, 255, 255)
                elif label == self.classes[1]:
                    num_ten_pesos += 1
                    mask_color = (0, 255, 0)
                elif label == self.classes[2]:
                    num_twenty_pesos += 1
                    mask_color = (255, 0, 255)
                elif label == self.classes[3]:
                    num_one_pesos += 1
                    mask_color = (255, 255, 0)

                cv2.rectangle(img, (x, y), (x + w, y + h), mask_color, 1)
                cv2.rectangle(img, (x, y - 30), (x + w, y), mask_color, -1)
                cv2.putText(
                    img,
                    label,
                    (x, y - 10),
                    cv2.FONT_HERSHEY_PLAIN,
                    1,
                    (0, 0, 0),
                    1
                )

                overlay = img.copy()
                cv2.circle(img, ((x+w)-w//2, (y+h)-h//2),
                           int(w//2 * 0.90), mask_color, -1)

                alpha = 0.7
                img = cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)

        return (
            img,
            num_one_pesos,
            num_five_pesos,
            num_ten_pesos,
            num_twenty_pesos
        )

    def close_cam(self):
        """
        Close the initiazed camera.
        """

        self.capture.release()
