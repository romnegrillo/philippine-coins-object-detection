# Thesis PH Coin Detection

Thesis project from Mapua to detect and count the number of the new Philippine coins using computer vision. This repository contains only the files needed for darknet YOLO tiny v4 training and the final program with PyQt5 interface. It doesn't contain the full setup of the darknet.

## Languages and Tools Used

- Python
- Darknet YOLO tiny v4
- PyQt5
- Raspberry Pi 4

## Setup on Windows and Raspberry Pi

- Python 3.8 above and pip must be installed in your computer.
- Clone this repository.
- Install virtualenv package.

```
pip install virtualenv
```

- Create a virtual environment. Lets name it `my-venv`.

```
virtualenv my-venv
```

- Activate virtual environment.

For Windows:

```
my-venv\Scripts\activate
```

For Raspberry Pi:

```
source my-venv/bin/activate
```

- Change directory to `app` folder and run `main.py`.

For Windows

```
python main.py
```

For Linux/Raspberry Pi:

```
python3 main.py
```

The program `main.py` will automatically detects if you are on Windows or Raspberry Pi. If you are on Windows, the program will expect a built-in camera or USB camera to be connected. If you are on Raspberry Pi, it will expect a Raspberry Pi camera to be connected.

## How to Train?

Fill later.
