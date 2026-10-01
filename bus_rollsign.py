#!/usr/bin/python3

import os
from pathlib import Path
import sys
import time
from PIL import Image

os.environ["GPIOZERO_PIN_FACTORY"] = "lgpio"
os.chdir("/tmp")

sys.path.insert(
    0,
    str(Path.home() / "LCD_Module_RPI_code/RaspberryPi/python")
)

from lib import LCD_1inch47

# -------------------------
# 設定
# -------------------------

# このPythonファイルがある場所
BASE_DIR = Path(__file__).resolve().parent

# リポジトリ内のimagesフォルダ
IMAGE_DIR = BASE_DIR / "images"

IMAGE_FILES = [
    "bus_rollsign_01.png",
    "bus_rollsign_02.png",
    "bus_rollsign_03.png",
    "bus_rollsign_04.png",
]

DISPLAY_Y = 40
ROLLSIGN_HEIGHT = 92

STEP = 4
FRAME_TIME = 0.02
WAIT_TIME = 1.0

# -------------------------
# LCD初期化
# -------------------------

lcd = LCD_1inch47.LCD_1inch47()
lcd.Init()
lcd.clear()
lcd.bl_DutyCycle(100)

WIDTH = lcd.height     # 320
HEIGHT = lcd.width     # 172

# -------------------------
# 画像読み込み
# -------------------------

rollsigns = []

for filename in IMAGE_FILES:
    img = Image.open(
        IMAGE_DIR / filename
    ).convert("RGB")

    rollsigns.append(img)

# -------------------------
# LCD表示
# -------------------------

def show_image(image):
    lcd.ShowImage(
        image.rotate(90, expand=True)
    )

# -------------------------
# 初期表示
# -------------------------

current_index = 0

screen = Image.new(
    "RGB",
    (WIDTH, HEIGHT),
    "black"
)

screen.paste(
    rollsigns[current_index],
    (0, DISPLAY_Y)
)

show_image(screen)

time.sleep(WAIT_TIME)

# -------------------------
# メインループ
# -------------------------

try:
    while True:

        next_index = (
            current_index + 1
        ) % len(rollsigns)

        current_img = rollsigns[current_index]
        next_img = rollsigns[next_index]

        # 0 → 92pxまで上方向へ移動
        for offset in range(
            0,
            ROLLSIGN_HEIGHT + 1,
            STEP
        ):

            # 毎フレーム黒背景から作成
            screen = Image.new(
                "RGB",
                (WIDTH, HEIGHT),
                "black"
            )

            # 現在画像を上へ
            screen.paste(
                current_img,
                (0, DISPLAY_Y - offset)
            )

            # 次画像を下から
            screen.paste(
                next_img,
                (
                    0,
                    DISPLAY_Y
                    + ROLLSIGN_HEIGHT
                    - offset
                )
            )

            # 表示領域92pxだけを残す
            visible = screen.crop(
                (
                    0,
                    DISPLAY_Y,
                    WIDTH,
                    DISPLAY_Y + ROLLSIGN_HEIGHT
                )
            )

            screen = Image.new(
                "RGB",
                (WIDTH, HEIGHT),
                "black"
            )

            screen.paste(
                visible,
                (0, DISPLAY_Y)
            )

            show_image(screen)

            time.sleep(FRAME_TIME)

        current_index = next_index

        # 完全に切り替わった状態で待機
        screen = Image.new(
            "RGB",
            (WIDTH, HEIGHT),
            "black"
        )

        screen.paste(
            rollsigns[current_index],
            (0, DISPLAY_Y)
        )

        show_image(screen)

        time.sleep(WAIT_TIME)

except KeyboardInterrupt:
    pass

finally:
    lcd.clear()
    lcd.module_exit()
