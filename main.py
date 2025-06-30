# SPDX-FileCopyrightText: 2025 M5Stack Technology CO LTD
#
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# M5PaperS3電卓アプリ - シンプル版
import M5
import time
import math
import gc

# ガベージコレクションを実行（メモリ最適化のため）
gc.collect()

# カラー定義
BLACK = 0x000000
WHITE = 0xFFFFFF
GRAY = 0xCCCCCC
LIGHT_GRAY = 0xDDDDDD
ORANGE = 0xFFA500

# 画面サイズ
SCREEN_WIDTH = 540
SCREEN_HEIGHT = 960

# バッテリー消費を抑えるための省電力設定
AUTO_SLEEP_TIMEOUT = 300000  # 自動スリープまでの時間（ミリ秒）- 5分
DEFAULT_BRIGHTNESS = 100  # デフォルトの輝度（0-100）
LOW_POWER_BRIGHTNESS = 30  # 省電力モード時の輝度（0-100）
SLEEP_BRIGHTNESS = 0  # スリープ時の輝度（0 = オフ）
SLEEP_CHECK_INTERVAL = 5000  # スリープ状態確認の間隔（ミリ秒）
DIM_TIMEOUT = 60000  # 輝度を下げるまでの時間（ミリ秒）: 1分

# 省電力制御用の変数
last_activity_time = time.ticks_ms()  # 最後の操作時間
is_sleeping = False  # スリープ中かどうか
power_save_mode = False  # 省電力モードかどうか
is_paused = False  # 一時停止中かどうか（電源ボタン押下時）
last_sleep_check = time.ticks_ms()  # 最後にスリープ状態をチェックした時間
last_power_button_check_time = 0  # 電源ボタンの最後のチェック時間

# 計算機の状態変数
display_text = "0"  # 画面に表示される文字列
previous_value = 0  # 前回の計算値
current_operation = None  # 現在の操作（+, -, *, /）
clear_on_next_input = True  # 次の入力で表示をクリアするかどうか

# ボタンの情報を格納する辞書
buttons = {}

# タッチ制御用の変数
is_touch_pressed = False  # 現在タッチされているかどうかのフラグ
last_touch_x = -1  # 最後にタッチが開始されたX座標
last_touch_y = -1  # 最後にタッチが開始されたY座標
last_touch_time = 0  # 最後にタッチが処理された時間
touch_debounce_time = 500  # タッチのデバウンス時間（ミリ秒）

# 省電力設定はファイル先頭に定義済み


# 初期設定
def setup():
    """初期設定を行う関数"""
    global is_touch_pressed, last_touch_x, last_touch_y, last_touch_time, last_activity_time

    # M5Stackの初期化
    M5.begin()

    # 画面の明るさを設定
    try:
        if hasattr(M5, "Lcd") and hasattr(M5.Lcd, "setBrightness"):
            M5.Lcd.setBrightness(DEFAULT_BRIGHTNESS)
    except Exception as e:
        print(f"Failed to set initial brightness: {e}")

    # 最後の操作時間を初期化
    last_activity_time = time.ticks_ms()

    # タッチ関連の変数をリセット
    is_touch_pressed = False
    last_touch_x = -1
    last_touch_y = -1
    last_touch_time = 0

    # 起動時に複数回デバイス状態を更新してクリア
    for _ in range(5):
        M5.update()
        empty_touch_buffer()
        time.sleep_ms(10)

    # 初期化情報を出力
    print("\n===== M5PaperS3 Calculator App Initialization Started =====")

    # 画面を白で初期化
    M5.Lcd.fillScreen(WHITE)

    # 表示エリアを描画
    draw_display_area()

    # ボタンを描画
    draw_buttons()

    # 初期表示
    update_display()

    # タッチバッファを再度クリア
    M5.update()
    empty_touch_buffer()

    print("===== Initialization Complete =====\n")


def draw_display_area():
    """表示エリアを描画する関数"""
    # タイトルを表示
    M5.Lcd.setTextColor(BLACK, WHITE)
    M5.Lcd.setTextSize(2)
    M5.Lcd.drawString("M5PaperS3 Calculator", 10, 10)

    # バッテリー情報を取得（利用可能な場合）
    try:
        if hasattr(M5, "Power"):
            bat_level = M5.Power.getBatteryLevel()
            bat_text = f"{bat_level}%"
            M5.Lcd.drawString(f"Batt: {bat_text}", SCREEN_WIDTH - 100, 10)
    except:
        pass

    # 表示エリア（結果表示部分）- 角を丸くして見栄えを良くする
    M5.Lcd.fillRoundRect(20, 50, 500, 80, 8, LIGHT_GRAY)
    M5.Lcd.drawRoundRect(20, 50, 500, 80, 8, BLACK)


def draw_buttons():
    """ボタンを描画する関数"""
    global buttons

    # ボタンのレイアウト設定
    button_width = 110  # 少し大きめのボタン
    button_height = 100
    button_gap = 10  # 間隔を少し小さく
    start_x = 15
    start_y = 160

    # キーパッドのレイアウト
    keypad = [
        ["7", "8", "9", "/"],  # ÷ を / に変更
        ["4", "5", "6", "*"],  # × を * に変更
        ["1", "2", "3", "-"],
        ["0", ".", "=", "+"],
        ["C", "+/-", "<", "rt"],  # ±, ←, √ を変更
    ]

    # フォントサイズ
    button_font_size = 5  # フォントサイズを大きく

    # ボタンを描画
    for row_idx, row in enumerate(keypad):
        y = start_y + row_idx * (button_height + button_gap)

        for col_idx, key in enumerate(row):
            x = start_x + col_idx * (button_width + button_gap)

            # ボタンの色を設定
            if key in "0123456789.":
                bg_color = WHITE  # 数字と小数点は白
            elif key in ["+", "-", "*", "/", "="]:  # "×", "÷" から "*", "/" に変更
                bg_color = ORANGE  # 演算子はオレンジ
            else:
                bg_color = GRAY  # その他のボタンはグレー

            # ボタンの情報を保存
            buttons[key] = {"x": x, "y": y, "width": button_width, "height": button_height, "color": bg_color}

            # ボタンを描画（角を少し丸く）
            M5.Lcd.fillRoundRect(x, y, button_width, button_height, 5, bg_color)
            M5.Lcd.drawRoundRect(x, y, button_width, button_height, 5, BLACK)

            # テキストを描画
            M5.Lcd.setTextColor(BLACK, bg_color)
            M5.Lcd.setTextSize(button_font_size)

            # 文字ごとのおおよその幅と高さを計算（フォントサイズに基づく）
            char_width = 6 * button_font_size
            char_height = 8 * button_font_size
            text_width = len(key) * char_width

            # テキストの位置を中央に調整
            text_x = x + (button_width - text_width) // 2
            text_y = y + (button_height - char_height) // 2

            M5.Lcd.drawString(key, text_x, text_y)


def update_display():
    """表示エリアを更新する関数"""
    global display_text

    # 長い数字の場合はフォーマット
    display_formatted = display_text
    if len(display_text) > 12:
        try:
            value = float(display_text)
            if abs(value) >= 1e10 or (abs(value) < 1e-3 and value != 0):
                display_formatted = "{:.3e}".format(value)  # 指数表記
            else:
                display_formatted = display_text[:12]  # 12桁までに制限
        except ValueError:
            display_formatted = display_text[:12]  # エラーの場合は単に切り詰め

    # 表示エリアをクリア（角丸を保持）
    M5.Lcd.fillRoundRect(20, 50, 500, 80, 8, LIGHT_GRAY)
    M5.Lcd.drawRoundRect(20, 50, 500, 80, 8, BLACK)

    # エラー時は赤色で表示
    if display_formatted == "Error":
        M5.Lcd.setTextColor(0xFF0000, LIGHT_GRAY)  # 赤色
    else:
        M5.Lcd.setTextColor(BLACK, LIGHT_GRAY)

    # フォントサイズと位置の調整
    display_font_size = 4  # 大きめのフォント
    M5.Lcd.setTextSize(display_font_size)

    # 右寄せで表示（数値が増えていく方向）
    char_width = 6 * display_font_size
    text_width = len(display_formatted) * char_width

    # 右端からマージンを取って表示位置を計算
    text_x = 500 - text_width - 20
    if text_x < 30:  # 左端の最小位置
        text_x = 30

    M5.Lcd.drawString(display_formatted, text_x, 75)


def highlight_button(key):
    """ボタンをハイライト表示する関数"""
    if key not in buttons:
        return

    btn = buttons[key]
    x, y = btn["x"], btn["y"]
    width, height = btn["width"], btn["height"]
    original_color = btn["color"]

    # フォントサイズ - draw_buttonsと同じ値にする
    button_font_size = 3

    # ボタンを一時的に明るい色に変更（オペレータならオレンジを明るく、それ以外は薄いグレー）
    if key in ["+", "-", "*", "/", "="]:  # "×", "÷" から "*", "/" に変更
        highlight_color = 0xFFBB55  # 明るいオレンジ
    else:
        highlight_color = 0xDDDDDD  # より目立つ明るいグレー

    # ハイライト状態を描画（角を丸く）
    M5.Lcd.fillRoundRect(x, y, width, height, 5, highlight_color)
    M5.Lcd.drawRoundRect(x, y, width, height, 5, BLACK)

    # テキストを描画
    M5.Lcd.setTextColor(BLACK, highlight_color)
    M5.Lcd.setTextSize(button_font_size)

    # 文字ごとのおおよその幅と高さを計算（フォントサイズに基づく）
    char_width = 6 * button_font_size
    char_height = 8 * button_font_size
    text_width = len(key) * char_width

    # テキストの位置を中央に調整
    text_x = x + (width - text_width) // 2
    text_y = y + (height - char_height) // 2

    M5.Lcd.drawString(key, text_x, text_y)

    # 少し長めの待機時間で視覚フィードバックを明確に
    time.sleep_ms(150)

    # 元の状態に戻す（角を丸く）
    M5.Lcd.fillRoundRect(x, y, width, height, 5, original_color)
    M5.Lcd.drawRoundRect(x, y, width, height, 5, BLACK)

    # テキストを描画
    M5.Lcd.setTextColor(BLACK, original_color)
    M5.Lcd.setTextSize(button_font_size)

    # テキストの位置を中央に調整
    M5.Lcd.drawString(key, text_x, text_y)


def button_pressed(key):
    """ボタンが押されたときの処理を行う関数"""
    global display_text, previous_value, current_operation, clear_on_next_input

    # クリア
    if key == "C":
        display_text = "0"
        previous_value = 0
        current_operation = None
        clear_on_next_input = True

    # バックスペース
    elif key == "<":  # "←" から "<" に変更
        if len(display_text) > 1:
            display_text = display_text[:-1]
        else:
            display_text = "0"

    # 符号反転
    elif key == "+/-":  # "±" から "+/-" に変更
        if display_text != "0":
            if display_text[0] == "-":
                display_text = display_text[1:]
            else:
                display_text = "-" + display_text

    # 平方根
    elif key == "rt":  # "√" から "rt" に変更
        try:
            value = float(display_text)
            if value >= 0:
                result = math.sqrt(value)
                display_text = str(result)
                if display_text.endswith(".0"):
                    display_text = display_text[:-2]
            else:
                display_text = "Error"
            clear_on_next_input = True
        except ValueError:
            display_text = "Error"
            clear_on_next_input = True

    # 数字と小数点
    elif key in "0123456789.":
        if clear_on_next_input or display_text == "0" and key != ".":
            display_text = key
            clear_on_next_input = False
        else:
            # 小数点は1つまで
            if key == "." and "." in display_text:
                pass
            else:
                display_text += key

    # 演算子
    elif key in ["+", "-", "*", "/", "="]:  # "×", "÷" から "*", "/" に変更
        try:
            current_value = float(display_text)

            # 前回の計算があれば実行
            if current_operation is not None and not clear_on_next_input:
                if current_operation == "+":
                    result = previous_value + current_value
                elif current_operation == "-":
                    result = previous_value - current_value
                elif current_operation == "*":  # "×" から "*" に変更
                    result = previous_value * current_value
                elif current_operation == "/":  # "÷" から "/" に変更
                    if current_value == 0:
                        display_text = "Error"
                        clear_on_next_input = True
                        update_display()
                        return
                    result = previous_value / current_value

                # 結果を表示
                display_text = str(result)
                if display_text.endswith(".0"):
                    display_text = display_text[:-2]
                previous_value = result
            else:
                previous_value = current_value

            # 次の操作を設定
            if key == "=":
                current_operation = None
            else:
                current_operation = key

            clear_on_next_input = True

        except ValueError:
            display_text = "Error"
            clear_on_next_input = True

    # 表示を更新
    update_display()


def check_touch():
    """タッチ入力をチェックし、指が離れた瞬間にボタン処理を実行する関数"""
    global is_touch_pressed, last_touch_x, last_touch_y, last_touch_time, last_activity_time, is_sleeping, is_paused

    # 現在の時刻を取得
    current_time = time.ticks_ms()

    # デバウンス処理（前回のタッチから一定時間内は無視）
    if time.ticks_diff(current_time, last_touch_time) < touch_debounce_time:
        empty_touch_buffer()  # バッファクリアだけ実行
        return

    # 注意: M5.update()はloop()で既に実行済み

    # タッチ情報を取得
    touch_count = M5.Touch.getCount()
    touch_detected = touch_count > 0

    # スリープ中にタッチがあればスリープ解除
    if touch_detected and is_sleeping:
        wake_from_sleep()
        update_last_activity_time()  # 活動時間を更新
        return

    # 一時停止画面からの復帰
    if touch_detected and is_paused:
        is_paused = False
        print("Resuming from pause screen due to touch")
        update_last_activity_time()  # 活動時間を更新
        redraw_calculator()  # 電卓画面を再描画
        return

    # タッチ状態の変化を検出
    if touch_detected:
        # タッチがある場合
        x = M5.Touch.getX()
        y = M5.Touch.getY()

        # 残りのバッファをクリア
        empty_touch_buffer()

        # 座標が有効範囲内かチェック
        if x < 0 or y < 0 or x >= SCREEN_WIDTH or y >= SCREEN_HEIGHT:
            return

        if not is_touch_pressed:
            # 新しいタッチの開始
            is_touch_pressed = True
            last_touch_x = x
            last_touch_y = y
            print(f"Touch start: x={last_touch_x}, y={last_touch_y}")

            # 最後の操作時間を更新
            update_last_activity_time()

            # 省電力モードから復帰
            if power_save_mode:
                power_save_mode = False
                try:
                    if hasattr(M5, "Lcd") and hasattr(M5.Lcd, "setBrightness"):
                        M5.Lcd.setBrightness(DEFAULT_BRIGHTNESS)
                except Exception as e:
                    print(f"Failed to restore brightness: {e}")
    else:
        # タッチがない場合で、前回はタッチがあった場合（指が離れた瞬間）
        if is_touch_pressed:
            is_touch_pressed = False
            print(f"Touch release: x={last_touch_x}, y={last_touch_y}")

            # 有効な座標かチェック
            if last_touch_x >= 0 and last_touch_y >= 0:
                # ボタン検索
                button_found = False
                for key, btn in buttons.items():
                    btn_x, btn_y = btn["x"], btn["y"]
                    btn_w, btn_h = btn["width"], btn["height"]

                    if btn_x <= last_touch_x < btn_x + btn_w and btn_y <= last_touch_y < btn_y + btn_h:
                        print(f"Executing action for button '{key}'")
                        button_pressed(key)
                        highlight_button(key)
                        button_found = True
                        break

                if button_found:
                    # ボタンが見つかった場合は次のタッチまでの時間を長めにとる
                    last_touch_time = current_time

            # 座標をリセット
            last_touch_x = -1
            last_touch_y = -1


def empty_touch_buffer():
    """タッチバッファをクリアする関数"""
    try:
        # バッファに残っているタッチイベントをすべてクリア
        for _ in range(10):  # 確実にクリアするため複数回試行
            if M5.Touch.getCount() <= 0:
                break
            M5.Touch.getX()
            M5.Touch.getY()
    except Exception as e:
        print(f"Touch buffer clear error: {e}")
        pass


def update_last_activity_time():
    """最後の操作時間を更新する関数"""
    global last_activity_time
    last_activity_time = time.ticks_ms()


def enter_sleep_mode():
    """スリープモードに入る関数"""
    global is_sleeping, power_save_mode

    if not is_sleeping:
        print("Entering sleep mode to save power...")
        is_sleeping = True
        power_save_mode = False

        # 画面を暗くする
        try:
            if hasattr(M5, "Lcd") and hasattr(M5.Lcd, "setBrightness"):
                M5.Lcd.setBrightness(SLEEP_BRIGHTNESS)  # 画面をオフ
        except Exception as e:
            print(f"Failed to adjust brightness for sleep: {e}")

        # スリープ状態を示す表示
        M5.Lcd.setTextColor(BLACK, WHITE)
        M5.Lcd.setTextSize(2)
        M5.Lcd.fillScreen(WHITE)
        M5.Lcd.drawString("Touch screen to wake up", SCREEN_WIDTH // 4, SCREEN_HEIGHT // 3)

        # 省電力処理を追加（デバイスによって異なる可能性あり）
        try:
            gc.collect()  # メモリ解放
        except:
            pass


def wake_from_sleep():
    """スリープモードから復帰する関数"""
    global is_sleeping, power_save_mode, last_activity_time

    if is_sleeping:
        print("Waking up from sleep mode...")
        is_sleeping = False
        power_save_mode = False

        # 画面明るさを元に戻す
        try:
            if hasattr(M5, "Lcd") and hasattr(M5.Lcd, "setBrightness"):
                M5.Lcd.setBrightness(DEFAULT_BRIGHTNESS)
        except Exception as e:
            print(f"Failed to restore brightness: {e}")

        # 画面を再描画
        M5.Lcd.fillScreen(WHITE)
        draw_display_area()
        draw_buttons()
        update_display()

        # 最後の操作時間を更新
        update_last_activity_time()

        # タッチバッファをクリア
        empty_touch_buffer()


def enter_power_save_mode():
    """省電力モードに入る関数（画面輝度を下げる）"""
    global power_save_mode

    if not is_sleeping and not power_save_mode:
        print("Entering power save mode (reducing brightness)...")
        power_save_mode = True

        try:
            if hasattr(M5, "Lcd") and hasattr(M5.Lcd, "setBrightness"):
                M5.Lcd.setBrightness(LOW_POWER_BRIGHTNESS)
        except Exception as e:
            print(f"Failed to adjust brightness for power save: {e}")


def check_power_management():
    """省電力管理をチェックする関数"""
    global last_sleep_check

    # 現在の時間を取得
    current_time = time.ticks_ms()

    # スリープ中はチェックしない
    if is_sleeping:
        return

    # 一定間隔でのみチェック（頻繁なチェックを避ける）
    if time.ticks_diff(current_time, last_sleep_check) < SLEEP_CHECK_INTERVAL:
        return

    # 最後のチェック時間を更新
    last_sleep_check = current_time

    # 最後の操作からの経過時間を計算
    idle_time = time.ticks_diff(current_time, last_activity_time)

    # 自動スリープのタイミングになったらスリープモードへ
    if idle_time >= AUTO_SLEEP_TIMEOUT:
        enter_sleep_mode()
    # 省電力モードのタイミングになったら輝度を下げる
    elif idle_time >= DIM_TIMEOUT and not power_save_mode:
        enter_power_save_mode()


def check_power_button():
    """電源ボタンが押されたかどうかをチェックする関数"""
    # グローバル変数を使用して前回のチェック時間を管理
    global last_power_button_check_time

    try:
        # 短時間の連続検出を防止するためのデバウンス処理
        current_time = time.ticks_ms()
        if last_power_button_check_time > 0:
            if time.ticks_diff(current_time, last_power_button_check_time) < 1000:  # 1秒間隔でチェック
                return False

        # 最終チェック時刻を更新
        last_power_button_check_time = current_time

        # M5Stack製品によって電源ボタンの検出方法が異なるため、複数の方法を試す
        button_pressed = False

        # 方法1: BtnPWRクラスを使用（一部のM5Stack製品で利用可能）
        if hasattr(M5, "BtnPWR") and hasattr(M5.BtnPWR, "isPressed"):
            button_pressed = M5.BtnPWR.isPressed()

        # 方法2: Axpクラスを使用（電源管理チップを持つ製品で利用可能）
        elif hasattr(M5, "Axp") and hasattr(M5.Axp, "GetBtnPress"):
            button_pressed = M5.Axp.GetBtnPress()

        # 方法3: Power.getBtnPress()を使用（一部の製品で利用可能）
        elif hasattr(M5, "Power") and hasattr(M5.Power, "getBtnPress"):
            button_pressed = M5.Power.getBtnPress()

        # 電源ボタンが押された場合の処理
        if button_pressed:
            print("Power button detected - showing shutdown screen")

            # 2回目の押下を防ぐため、長めの間隔をデバウンスに設定
            global last_power_button_check_time
            last_power_button_check_time = current_time + 5000

            # シャットダウン画面を表示
            show_shutdown_screen()
            return True

    except Exception as e:
        print(f"Power button check error: {e}")

    return False


# 以前の方法（関数属性を使用）は削除し、グローバル変数を使用


def show_shutdown_screen():
    """一時停止画面を表示する関数"""
    global is_paused

    print("Power button pressed - Showing pause screen")
    is_paused = True  # 一時停止状態に設定

    # 画面を白くクリア
    M5.Lcd.fillScreen(WHITE)

    # 一時停止メッセージを表示
    M5.Lcd.setTextColor(BLACK, WHITE)
    M5.Lcd.setTextSize(3)
    M5.Lcd.drawString("Calculator Paused", SCREEN_WIDTH // 4, SCREEN_HEIGHT // 3)
    M5.Lcd.setTextSize(2)
    M5.Lcd.drawString("Application still running", SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2)
    M5.Lcd.drawString("Touch screen to return", SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2 + 40)
    M5.Lcd.drawString("Or long-press power button", SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2 + 70)
    M5.Lcd.drawString("to turn off the device", SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2 + 100)

    # バッテリー情報を表示（利用可能な場合）
    try:
        if hasattr(M5, "Power"):
            bat_level = M5.Power.getBatteryLevel()
            bat_text = f"Battery: {bat_level}%"
            M5.Lcd.drawString(bat_text, SCREEN_WIDTH // 4, SCREEN_HEIGHT // 2 + 140)
    except:
        pass

    # メモリをクリーンアップ
    gc.collect()

    # 画面が表示されるまで少し待機
    time.sleep(1)

    # 制御をメインループに戻す


# メインループ
def loop():
    """メインループ関数"""
    try:
        # デバイスの状態を更新（ここでまとめて更新）
        M5.update()

        # 省電力管理をチェック
        check_power_management()

        # スリープ中は最小限の処理のみ行う
        if is_sleeping:
            # 電源ボタンとタッチ以外の処理はスキップ
            check_touch()  # タッチでの復帰を検知するためにタッチチェックは実行
            time.sleep_ms(500)  # スリープ中は長めの待機でCPU使用を減らす
            return

        # 通常時の処理
        # タッチ入力をチェック
        check_touch()

        # メモリ使用状況をモニタリング（10秒に1回程度）
        current_ms = time.ticks_ms()
        if hasattr(gc, "mem_free") and current_ms % 10000 < 20:
            free = gc.mem_free()
            total = gc.mem_alloc() + free
            print(
                f"Memory usage: {gc.mem_alloc()/1024:.1f}KB used / {total/1024:.1f}KB total ({100 - free*100/total:.1f}% used)"
            )

            # メモリ使用率が高い場合は明示的にGC実行
            if free < total * 0.3:  # 30%以下になったら
                print("Low memory: Running garbage collection")
                gc.collect()

        # 少し長めの遅延を入れることでタッチ検出を安定させる
        time.sleep_ms(100)

    except Exception as e:
        print(f"Error occurred: {e}")
        time.sleep_ms(100)
        # エラー回復を試みる
        gc.collect()


def redraw_calculator():
    """電卓画面全体を再描画する関数"""
    print("Redrawing calculator screen")

    # 画面を白くクリア
    M5.Lcd.fillScreen(WHITE)

    # 表示エリアを描画
    draw_display_area()

    # ボタンを描画
    draw_buttons()

    # 表示を更新
    update_display()

    # メモリクリーンアップ
    gc.collect()


# プログラム開始
if __name__ == "__main__":
    try:
        # 起動時のメモリ確保
        gc.collect()

        # 初期化
        setup()

        print("Calculator app running...")

        # メインループ
        error_count = 0
        last_error_time = 0  # 実行継続フラグ
        running = True

        while running:
            try:
                # 電源ボタンのチェックを追加（最優先）
                M5.update()  # 電源ボタンの状態を確実に更新

                # 電源ボタンが押されたら処理
                if check_power_button():
                    print("Power button pressed - Pausing application")
                    # ここで例外は発生させず、単に一時停止画面に遷移
                    continue

                # 通常のループ処理
                loop()
                error_count = 0  # 正常動作中はエラーカウンタをリセット

            except Exception as e:
                # エラー頻度を制限（連続エラー防止）
                current_time = time.ticks_ms()
                if time.ticks_diff(current_time, last_error_time) < 5000:
                    error_count += 1
                else:
                    error_count = 1

                last_error_time = current_time

                # エラーログ
                import sys

                sys.print_exception(e)
                print(f"Loop error {error_count}: {type(e).__name__} - {str(e)}")

                # 短時間の回復待機
                time.sleep_ms(500)

                # 連続エラーが多すぎる場合はエラーメッセージを表示して再起動
                if error_count > 5:
                    M5.Lcd.fillScreen(WHITE)
                    M5.Lcd.setTextColor(0xFF0000, WHITE)  # 赤色
                    M5.Lcd.setTextSize(2)
                    M5.Lcd.drawString("Error occurred", 10, 10)
                    M5.Lcd.drawString(f"Type: {type(e).__name__}", 10, 40)
                    M5.Lcd.drawString(str(e), 10, 70)
                    M5.Lcd.drawString("Restarting in 3 seconds...", 10, 130)

                    # メモリ使用状況を表示
                    free = gc.mem_free()
                    total = gc.mem_alloc() + free
                    M5.Lcd.drawString(f"Memory: {free/1024:.1f}KB free / {total/1024:.1f}KB total", 10, 160)

                    time.sleep(3)
                    break  # メインループを終了して再起動

    except Exception as e:
        import sys

        sys.print_exception(e)

        # エラーメッセージを表示
        M5.Lcd.fillScreen(WHITE)
        M5.Lcd.setTextColor(0xFF0000, WHITE)  # 赤色
        M5.Lcd.setTextSize(2)
        M5.Lcd.drawString(f"Fatal error: {type(e).__name__}", 10, 10)
        M5.Lcd.drawString(str(e), 10, 40)
        M5.Lcd.drawString("Please restart the device", 10, 100)
