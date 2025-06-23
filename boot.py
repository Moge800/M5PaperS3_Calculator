# SPDX-FileCopyrightText: 2025 M5Stack Technology CO LTD
#
# SPDX-License-Identifier: Apache-2.0

# Boot file for M5PaperS3 Calculator App
# Only performs simple initialization

import M5
from M5 import *
import time
import gc

# 起動時のメモリ最適化
gc.collect()


# 初期化処理
def initialize():
    """Initialize the M5PaperS3 device"""
    try:
        print("\n===== M5PaperS3 Calculator App - Startup Process Started =====")

        # M5Stackの初期化
        M5.begin()

        # 画面を白で初期化
        M5.Lcd.fillScreen(0xFFFFFF)

        # ロゴの表示
        M5.Lcd.setTextColor(0x000000, 0xFFFFFF)
        M5.Lcd.setTextSize(3)
        M5.Lcd.drawString("M5PaperS3", 160, 200)
        M5.Lcd.setTextSize(2)
        M5.Lcd.drawString("Calculator App Ver 2.0", 160, 240)

        # 起動メッセージを表示
        M5.Lcd.drawString("Starting...", 200, 280)

        # バッテリー情報を表示（利用可能な場合）
        try:
            if hasattr(M5, "Power"):
                bat_level = M5.Power.getBatteryLevel()
                bat_text = f"{bat_level}%"

                # バッテリーレベルに応じた色設定
                bat_color = 0x00CC00  # 緑（正常）
                if bat_level < 30:
                    bat_color = 0xFF9900  # オレンジ（警告）
                if bat_level < 15:
                    bat_color = 0xFF0000  # 赤（危険）

                M5.Lcd.setTextColor(bat_color, 0xFFFFFF)
                M5.Lcd.drawString(f"Battery: {bat_text}", 10, 10)
                M5.Lcd.setTextColor(0x000000, 0xFFFFFF)  # テキストカラーを戻す
        except Exception as e:
            print(f"Failed to get battery information: {e}")

        # メモリ情報を表示
        try:
            free = gc.mem_free()
            total = gc.mem_alloc() + free
            print(f"Memory status: {free/1024:.1f}KB free / {total/1024:.1f}KB total")
        except:
            pass

        # 短い待機時間
        time.sleep(0.8)

        print("===== Startup Process Completed =====\n")

    except Exception as e:
        print(f"Initialization error: {e}")
        import sys

        sys.print_exception(e)

        # エラーメッセージを画面に表示
        M5.Lcd.fillScreen(0xFFFFFF)
        M5.Lcd.setTextColor(0xFF0000, 0xFFFFFF)  # 赤色
        M5.Lcd.setTextSize(2)
        M5.Lcd.drawString("Startup Error", 10, 10)
        M5.Lcd.drawString(str(e), 10, 40)
        time.sleep(3)


# 起動時に初期化を実行
if __name__ == "__main__":
    initialize()
