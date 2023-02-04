import cv2


class ObjectDetection:
    def __init__(self, config_path, weights_path, classes, use_rpi_cam=False):
        # For selection what web cam to use.
        self.use_rpi_cam = use_rpi_cam

        # YOLO paths.
        self.config_path = config_path
        self.weights_path = weights_path
        self.classes = classes

        # YOLO objects.
        # self.yolo = cv2.dnn.readNet(weights_path, config_path)
        # self.layer_names = yolo.getLayerNames()
        # self.output_layers = [
        #     self.layer_names[i - 1] for i in self.yolo.getUnconnectedOutLayers()
        # ]

        self.frame = None

        try:
            if not self.use_rpi_cam:
                self.capture = cv2.VideoCapture(0)
            else:
                self.camera = PiCamera(framerate=10)
                self.rawCapture = PiRGBArray(self.camera)
        except Exception as err:
            print(str(err))

    def get_frames(self):
        if not self.use_rpi_cam:
            _, self.frame = self.capture.read()
        elif self.use_rpi_cam:
            self.camera.capture(
                self.rawCapture, format="bgr", use_video_port=True)
            self.frame = self.rawCapture.array

        # In BGR format.
        img = self.frame.copy()
        # output = self.detect_image(img)

        if self.use_rpi_cam:
            self.rawCapture.truncate(0)

        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    def detect(self, img):
        height, width, _ = img.shape

        blob = cv2.dnn.blobFromImage(
            img, 1 / 255.0, (416, 416), swapRB=True, crop=False
        )
        self.yolo.setInput(blob)
        outputs = self.yolo.forwards(self.output_layers)

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

        for i in range(len(boxes)):
            if i in indices:
                x, y, w, h = boxes[i]
                label = str(self.classes[class_ids[i]])
                start = (x, y)
                end = (x + w, y + h)

                cv2.rectangle(img, start, end, (0, 255, 0), 2)
                cv2.putText(
                    img, label, (x, y -
                                 20), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 255), 2
                )

        return img

    def close_cam(self):
        if not self.use_rpi_cam:
            self.capture.release()
        else:
            return