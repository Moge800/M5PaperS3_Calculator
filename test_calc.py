# 電卓ロジックのセルフチェック（実機不要）。fake M5 を挿して本物の button_pressed を叩く。
# 実行: python test_calc.py
import sys


class _Any:
    """どんな属性アクセス/呼び出しも飲み込むダミー（M5.Lcd.* などの描画を無効化）"""

    def __getattr__(self, _):
        return _Any()

    def __call__(self, *a, **k):
        return 0


sys.modules["M5"] = _Any()

import main  # noqa: E402


def press(seq):
    main.display_text = "0"
    main.previous_value = 0
    main.current_operation = None
    main.clear_on_next_input = True
    for k in seq:
        main.button_pressed(k)
    return main.display_text


# 基本四則
assert press(["1", "2", "+", "3", "="]) == "15", press(["1", "2", "+", "3", "="])
assert press(["8", "/", "0", "="]) == "Error"
assert press(["9", "rt"]) == "3"
# 小数点まわり（今回の修正対象）
assert press(["5", ".", "3"]) == "5.3"
assert press(["5", ".", ".", "3"]) == "5.3"  # 小数点は1つまで
assert press(["+", "."]) == "0."             # 演算直後の "." は "0." 始まり（旧版は Error）
assert press(["."]) == "0."                  # クリア状態の "." も "0."
# 符号反転・バックスペース・クリア
assert press(["5", "+/-"]) == "-5"
assert press(["1", "2", "<"]) == "1"
assert press(["1", "2", "C"]) == "0"

print("OK: all calculator self-checks passed")
