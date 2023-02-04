import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.uic import loadUi
from ObjectDetection import ObjectDetection

IN_RPI = False
try:
    import RPi.GPIO

    IN_RPI = True
except Exception as e:
    print(str(e))
    print("Not in Raspberry Pi")


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi("mainwindow.ui", self)

        self.capture_button.clicked.connect(self.capture_button_clicked)
        self.reset_button.clicked.connect(self.reset_button_clicked)

        if IN_RPI:
            use_rpi_cam = True
            self.showFullScreen()
        else:
            use_rpi_cam = False

        self.object_detection = ObjectDetection(
            config_path="<insert_path_here>",
            weights_path="<insert_path_here>",
            classes=["1 Pesos", "5 Pesos", "10 Pesos", "20 Pesos"],
            use_rpi_cam=use_rpi_cam,
        )

        self.is_captured = False

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_frames)
        self.timer.start(1)

    def capture_button_clicked(self):
        if not self.is_captured:
            self.is_captured = True
            self.timer.stop()

    def reset_button_clicked(self):
        if self.is_captured:
            self.is_captured = False
            self.timer.start(1)

    def update_frames(self):
        image = self.object_detection.get_frames()

        # If there is only 2 items in shape, it means the
        # image is one channel.
        if len(image.shape) == 2:
            imageFormat = QtGui.QImage.Format_Indexed8
        # Else, it may be 3 or 4
        else:
            # Get third item which is the number of channels.
            num_channels = image.shape[2]
            if num_channels == 1:
                imageFormat = QtGui.QImage.Format_Indexed8
            elif num_channels == 3:
                imageFormat = QtGui.QImage.Format_RGB888
            elif num_channels == 4:
                imageFormat = QtGui.QImage.Format_RGBA8888

        out_image = QtGui.QImage(
            image,
            image.shape[1],
            image.shape[0],
            image.strides[0],
            imageFormat,
        )

        self.image_label.setPixmap(QtGui.QPixmap.fromImage(out_image))
        self.image_label.setScaledContents(True)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    app.exec_()
